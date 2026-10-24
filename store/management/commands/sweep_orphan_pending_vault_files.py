# store/management/commands/sweep_orphan_pending_vault_files.py
"""
Delete staged files in private_digital_vault/_pending/ that no
ArtisanVaultUpload row references.

The _pending/ directory is the staging area for artisan-submitted
digital files. Files land there on direct upload
(creators.views.self_supersede_and_create) and stay there until an
admin approves them (moved into the vault root) or rejects them
(deleted on commit). Three paths are known to leak files here:

  1. Supersession. self_supersede_and_create deletes the previous
     staged file with `unlink(missing_ok=True)` inside a try/except
     OSError. If that unlink fails, the DB is correct (old row is
     SUPERSEDED, new row is PENDING) but the old file lingers. The
     view's docstring names this command as the backstop.

  2. Rejection. review_vault_upload_reject schedules the same
     unlink(missing_ok=True) on transaction.on_commit. Same failure
     mode, same backstop. The view's docstring also names this
     command.

  3. Hard deletion of a parent. ProductVariation.delete() cascades
     to ArtisanVaultUpload (on_delete=CASCADE), so a variation removed
     via dashboard_product_variation_remove leaves its PENDING or
     terminal upload rows deleted but the staged file still on disk.
     Product hard-deletes cascade the same way. (Product soft-deletes
     do NOT leak — is_deleted=True keeps the ArtisanVaultUpload rows
     and their staged_filename references intact.)

This command is the contract those three paths already assume. It is
NOT a general vault reconciliation. Specifically, it does not touch:

  * the vault root (a post-crash orphan after approve's rename-then-
    commit window is a separate concern, named in the
    review_vault_upload_approve docstring — a future
    reconcile_vault_root command would be its sibling, not a widening
    of this one);
  * _retired/ (retired files are kept for audit; retention is its
    own future decision);
  * backups (backup_vault rsyncs _pending/ into each timestamped run
    directory; this command only ever writes to the live vault).

## What counts as a reference

A row references a staged file if its `staged_filename` is non-empty.
Status is irrelevant. Specifically:

  * PENDING   — the file is waiting for review. Referenced.
  * APPROVED  — the file was moved to the vault root, so the row's
                 staged_filename names a file that is no longer in
                 _pending/. If a file with that name IS still in
                 _pending/, it is not the approved file (UUIDs do not
                 collide) and the row's reference does not protect
                 it. The file is an orphan.
  * REJECTED  — the file was deleted on commit. Same reasoning as
                 APPROVED: a file with this name still in _pending/
                 is not the rejected file, and the row does not
                 protect it.
  * SUPERSEDED — the file was deleted on supersession. Same
                 reasoning again.
  * any status with staged_filename="" (EXTERNAL_PENDING pre-
                 staging) — no file has been placed in _pending/ yet,
                 so nothing to reference.

The rule above is deliberately symmetric across statuses: for every
terminal status, the row's staged_filename is an *audit record* of a
file that has already left _pending/, not a *live claim* on a file
that is still there. A file whose name matches a terminal row's
staged_filename is not the terminal row's file, and the terminal row
does not protect it. This is the invariant the twelve tests in
test_sweep_orphan_pending_vault_files.py pin.

## Why "unrecognized names" are swept, not skipped

self_supersede_and_create writes `f"{uuid.uuid4()}.{ext}"` where
`ext` is one of {pdf, epub, zip} — enforced by the upload form's
extension whitelist and content sniff, and by
XINDENG_VAULT_ALLOWED_EXTENSIONS. Nothing else is expected to appear
in _pending/. The command therefore treats any file whose name does
not match that shape as an orphan too: either it is a leftover from
a manual test, or it is a file written by a future code path that
has not yet been updated to reference it, and in both cases it
cannot belong to a live row by the write path's own contract. The
alternative (a "report and refuse" mode with a --force flag) was
considered and rejected — it adds a decision point without changing
what a careful operator would do.

## Usage

    python manage.py sweep_orphan_pending_vault_files
    python manage.py sweep_orphan_pending_vault_files --dry-run
    python manage.py sweep_orphan_pending_vault_files --delete

--dry-run and no flag are equivalent (report only). --delete removes
the orphans.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from store.models import ArtisanVaultUpload


# The write path's filename shape:
#   uuid.uuid4()              → 36 chars, 8-4-4-4-12 hex groups
#   "." + ext                 → one of the whitelisted extensions
# Anything else in _pending/ is treated as an orphan (see module
# docstring). The pattern is intentionally tight: 8-4-4-4-12 lower-
# or upper-case hex, then a dot, then a whitelisted extension.
_STAGED_NAME_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\.(pdf|epub|zip)$"
)


class Command(BaseCommand):
    help = (
        "Delete staged files in private_digital_vault/_pending/ that no "
        "ArtisanVaultUpload row references. Report-only by default; pass "
        "--delete to remove them."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Actually delete the orphans (default: report only).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Report what would be done, without writing anything. "
                "Equivalent to passing no flag."
            ),
        )

    def handle(self, *args, **options):
        do_delete = options["delete"]
        # --dry-run is an explicit alias for the default behaviour.
        # It exists so a caller who has read audit_missing_settlement_lines
        # or backup_vault does not have to relearn the flag names for
        # this command. It has no effect if --delete is also passed;
        # --delete wins, and we say so below.
        dry_run = options["dry_run"]
        if dry_run and do_delete:
            raise CommandError(
                "--dry-run and --delete are mutually exclusive. "
                "Pass one or neither."
            )

        # ── Resolve the pending root ─────────────────────────────
        vault_root = Path(settings.XINDENG_VAULT_ROOT).resolve()
        if not vault_root.is_dir():
            raise CommandError(
                f"XINDENG_VAULT_ROOT does not exist or is not a directory: "
                f"{vault_root}"
            )

        pending_root = vault_root / "_pending"

        # Belt-and-braces: _pending/ must be *inside* the vault root.
        # A settings drift (e.g. a symlinked vault root, a path that
        # resolves to "/") must fail here rather than letting --delete
        # point at an unintended directory.
        if not pending_root.is_relative_to(vault_root):
            raise CommandError(
                f"Refusing to sweep: {pending_root} is not inside "
                f"XINDENG_VAULT_ROOT ({vault_root})."
            )

        if not pending_root.is_dir():
            self.stdout.write(
                self.style.SUCCESS(
                    f"No _pending/ directory at {pending_root}; "
                    f"nothing to sweep."
                )
            )
            return

        # ── Build the referenced set ─────────────────────────────
        # Non-empty staged_filename is a reference, regardless of
        # status or storage_kind. Blank filenames (EXTERNAL_PENDING
        # pre-staging) reference nothing. See module docstring.
        referenced = set(
            ArtisanVaultUpload.objects
            .exclude(staged_filename="")
            .values_list("staged_filename", flat=True)
            .iterator()
        )
        self.stdout.write(
            self.style.NOTICE(
                f"Found {len(referenced)} referenced staged file(s) in DB "
                f"(rows with non-empty staged_filename)."
            )
        )

        # ── Scan _pending/ ───────────────────────────────────────
        files_scanned = 0
        orphans: list[tuple[Path, int]] = []  # (path, size_bytes)
        unrecognized: list[Path] = []

        for entry in pending_root.iterdir():
            # Skip directories and dotfiles. Directories should not
            # exist in _pending/ (the write path is flat), but
            # skipping rather than erroring is the right shape for a
            # sweeper: a stray directory is a maintenance signal, not
            # a delete-candidate.
            if entry.is_dir():
                continue
            if entry.name.startswith("."):
                continue

            files_scanned += 1

            # Shape check. Anything outside the write path's shape
            # is reported separately and swept under --delete; see
            # module docstring ("Why unrecognized names are swept").
            if not _STAGED_NAME_RE.match(entry.name):
                unrecognized.append(entry)
                # fall through to the orphan test too — a file can be
                # both unrecognized and unreferenced, and the report
                # should show both facts if so.

            if entry.name in referenced:
                continue

            try:
                size = entry.stat().st_size
            except OSError:
                size = 0
            orphans.append((entry, size))

        total_bytes = sum(s for _, s in orphans)

        # ── Report ───────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(
            self.style.NOTICE(f"▶ {pending_root}/")
        )
        self.stdout.write(
            f"   files scanned: {files_scanned}"
        )
        if unrecognized:
            self.stdout.write(
                self.style.WARNING(
                    f"   unrecognized filenames: {len(unrecognized)}"
                )
            )
            for entry in sorted(unrecognized):
                self.stdout.write(f"      ? {entry.name}")

        if orphans:
            self.stdout.write("")
            for entry, size in sorted(orphans, key=lambda x: x[0].name):
                self.stdout.write(
                    f"   {size / 1024:8.1f} KB  {entry.name}"
                )
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                f"Orphans: {len(orphans)} "
                f"({total_bytes / 1024 / 1024:.2f} MB)"
            )
        )

        # ── Delete ───────────────────────────────────────────────
        if not do_delete:
            self.stdout.write(
                self.style.NOTICE(
                    "Report-only. Pass --delete to remove the orphans."
                )
            )
            return

        if not orphans:
            self.stdout.write(
                self.style.SUCCESS("Nothing to delete.")
            )
            return

        deleted = 0
        errors = 0
        for entry, _ in orphans:
            try:
                os.unlink(entry)
                deleted += 1
            except OSError as exc:
                self.stderr.write(
                    f"   FAILED {entry.name}: {exc}"
                )
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted: {deleted} | Errors: {errors}"
            )
        )