# store/tests/test_sweep_orphan_pending_vault_files.py
"""
Behaviour tests for the _pending/ orphan sweeper.

Covered:
  * Empty / missing _pending/ exits cleanly.
  * Files with a matching non-empty staged_filename are not orphans,
    for every status that carries a filename (the referenced-set rule).
  * Files with no matching row are orphans; only --delete removes them.
  * Files matching a blank staged_filename (EXTERNAL_PENDING) are
    orphans — a blank filename references nothing.
  * Files with an unrecognized name are reported and swept.
  * Dotfiles and directories are skipped, not deleted.
  * _retired/ and the vault root are never touched.
  * --dry-run and no flag are equivalent; --dry-run + --delete is an
    error.
  * Idempotency: a second --delete after a successful run reports zero.
"""

from __future__ import annotations

import io
import uuid
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_root(tmp_path, settings):
    vault = tmp_path / "private_digital_vault"
    (vault / "_pending").mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


@pytest.fixture
def pending_root(vault_root) -> Path:
    return vault_root / "_pending"


@pytest.fixture
def artisan_chain(db, django_user_model):
    """Minimal artisan + digital product + variation for FK targets."""
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="sweep_artisan",
        email="sweep-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Sweep Artisan",
        slug="sweep-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Sweep Digital",
        slug="sweep-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Sweep Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Published",
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )
    return {
        "user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
    }


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _write_staged(pending_root: Path, name: str | None = None) -> tuple[Path, str]:
    """Write a file in _pending/ and return (path, basename)."""
    if name is None:
        name = f"{uuid.uuid4()}.pdf"
    path = pending_root / name
    path.write_bytes(b"%PDF-1.4\n% sweeper test\n%%EOF\n")
    return path, name


def _make_upload(chain, *, staged_filename: str, status_value: str = "PENDING"):
    from store.models import ArtisanVaultUpload
    return ArtisanVaultUpload.objects.create(
        artisan=chain["profile"],
        product=chain["product"],
        variation=chain["variation"],
        status=status_value,
        staged_filename=staged_filename,
    )


def _run(*args) -> tuple[str, str]:
    """Run the command, return (stdout, stderr). Swallows CommandError."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        call_command("sweep_orphan_pending_vault_files", *args)
    return out.getvalue(), err.getvalue()


# ──────────────────────────────────────────────────────────────────
# Directory state
# ──────────────────────────────────────────────────────────────────

class TestDirectoryState:

    def test_missing_pending_dir_exits_cleanly(self, tmp_path, settings):
        vault = tmp_path / "no_pending_here"
        vault.mkdir()
        settings.XINDENG_VAULT_ROOT = vault

        out, _ = _run()
        assert "nothing to sweep" in out.lower()

    def test_missing_vault_root_raises(self, tmp_path, settings):
        settings.XINDENG_VAULT_ROOT = tmp_path / "does-not-exist"
        with pytest.raises(CommandError):
            _run()

    def test_empty_pending_dir_reports_zero(self, pending_root):
        out, _ = _run()
        assert "Orphans: 0" in out


# ──────────────────────────────────────────────────────────────────
# Reference rule — non-empty staged_filename protects its file
# ──────────────────────────────────────────────────────────────────

class TestReferenceRule:

    @pytest.mark.parametrize("status_value", [
        "PENDING", "APPROVED", "REJECTED", "SUPERSEDED",
    ])
    def test_any_status_with_filename_protects_its_file(
        self, pending_root, artisan_chain, status_value,
    ):
        """
        The load-bearing assertion: a non-empty staged_filename is a
        reference, regardless of status. For APPROVED/REJECTED/
        SUPERSEDED rows the file *shouldn't* still be in _pending/
        (approve moved it, reject/supersede deleted it), but if a file
        with that name is present, the row's reference protects it —
        the sweeper never deletes a file whose name matches a row.
        """
        _, name = _write_staged(pending_root)
        _make_upload(artisan_chain, staged_filename=name, status_value=status_value)

        out, _ = _run()
        assert "Orphans: 0" in out
        assert (pending_root / name).is_file()

    def test_blank_staged_filename_does_not_protect(
        self, pending_root, artisan_chain,
    ):
        """
        EXTERNAL_PENDING rows carry staged_filename="" — no file has
        been placed in _pending/ for them. A file whose name matches
        nothing must be treated as an orphan even though a row with
        an empty staged_filename exists.
        """
        from store.models import ArtisanVaultUpload
        path, name = _write_staged(pending_root)
        ArtisanVaultUpload.objects.create(
            artisan=artisan_chain["profile"],
            product=artisan_chain["product"],
            variation=artisan_chain["variation"],
            status="PENDING",
            storage_kind="EXTERNAL_PENDING",
            staged_filename="",
        )

        out, _ = _run()
        assert "Orphans: 1" in out
        assert path.is_file()  # not deleted without --delete

    def test_one_referenced_one_orphan(self, pending_root, artisan_chain):
        _, referenced_name = _write_staged(pending_root)
        _make_upload(artisan_chain, staged_filename=referenced_name)
        orphan_path, orphan_name = _write_staged(pending_root)

        out, _ = _run()
        assert "Orphans: 1" in out
        assert referenced_name not in out
        assert orphan_name in out


# ──────────────────────────────────────────────────────────────────
# Delete / dry-run
# ──────────────────────────────────────────────────────────────────

class TestDeleteSemantics:

    def test_no_flag_does_not_delete(self, pending_root, artisan_chain):
        path, name = _write_staged(pending_root)

        _run()
        assert path.is_file()

    def test_dry_run_does_not_delete(self, pending_root, artisan_chain):
        path, name = _write_staged(pending_root)

        _run("--dry-run")
        assert path.is_file()

    def test_delete_removes_orphans(self, pending_root, artisan_chain):
        path, name = _write_staged(pending_root)

        out, _ = _run("--delete")
        assert "Deleted: 1" in out
        assert not path.exists()

    def test_delete_preserves_referenced(self, pending_root, artisan_chain):
        _, ref_name = _write_staged(pending_root)
        _make_upload(artisan_chain, staged_filename=ref_name)
        orphan_path, _ = _write_staged(pending_root)

        _run("--delete")
        assert (pending_root / ref_name).is_file()
        assert not orphan_path.exists()

    def test_dry_run_plus_delete_is_rejected(self, pending_root):
        with pytest.raises(CommandError):
            _run("--dry-run", "--delete")

    def test_second_delete_is_idempotent(self, pending_root, artisan_chain):
        path, _ = _write_staged(pending_root)
        _run("--delete")
        assert not path.exists()

        out, _ = _run("--delete")
        assert "Nothing to delete" in out


# ──────────────────────────────────────────────────────────────────
# Unrecognized names, dotfiles, directories
# ──────────────────────────────────────────────────────────────────

class TestNameRecognition:

    def test_unrecognized_filename_is_reported_and_swept(
        self, pending_root,
    ):
        path, _ = _write_staged(pending_root, name="not-a-uuid.pdf")

        out, _ = _run()
        assert "unrecognized filenames: 1" in out.lower() or "unrecognized filenames:" in out
        assert "Orphans: 1" in out

        _run("--delete")
        assert not path.exists()

    def test_dotfile_is_skipped(self, pending_root):
        dot = pending_root / ".DS_Store"
        dot.write_bytes(b"\x00")

        out, _ = _run()
        assert "Orphans: 0" in out
        assert dot.is_file()

    def test_directory_is_skipped(self, pending_root):
        subdir = pending_root / "nested"
        subdir.mkdir()

        out, _ = _run()
        assert "Orphans: 0" in out
        assert subdir.is_dir()


# ──────────────────────────────────────────────────────────────────
# Boundary: the sweeper never touches outside _pending/
# ──────────────────────────────────────────────────────────────────

class TestBoundary:

    def test_vault_root_files_are_untouched(
        self, vault_root, pending_root,
    ):
        # A file in the vault root (approved, live) and a file in
        # _pending/ that shares its name (impossible in practice
        # because UUIDs do not collide, but the test proves the
        # boundary anyway).
        live = vault_root / "live-file.pdf"
        live.write_bytes(b"%PDF-1.4 live\n")
        orphan = pending_root / "live-file.pdf"
        orphan.write_bytes(b"%PDF-1.4 orphan\n")

        _run("--delete")
        assert live.is_file()
        assert not orphan.exists()

    def test_retired_files_are_untouched(
        self, vault_root, pending_root,
    ):
        retired = vault_root / "_retired"
        retired.mkdir()
        retired_file = retired / "old.pdf"
        retired_file.write_bytes(b"%PDF-1.4 old\n")

        _run("--delete")
        assert retired_file.is_file()

    def test_backup_directory_outside_vault_is_untouched(
        self, tmp_path, vault_root, pending_root,
    ):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        backup_file = backup_dir / "some-backup.pdf"
        backup_file.write_bytes(b"%PDF-1.4 backup\n")

        _write_staged(pending_root)
        _run("--delete")
        assert backup_file.is_file()