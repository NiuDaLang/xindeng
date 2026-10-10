# core/management/commands/backup_vault.py
"""
Backup the private digital vault and the database to a configurable
target directory.

Usage:
    python manage.py backup_vault
    python manage.py backup_vault --dry-run
    python manage.py backup_vault --target /path/to/backups

Reads:
    settings.XINDENG_VAULT_ROOT              — source directory (vault)
    settings.XINDENG_VAULT_BACKUP_TARGET     — default target directory
                                                (empty string disables)
    settings.DATABASES['default']            — DB engine + name

Writes (one directory per run, keyed by timestamp):
    <target>/<YYYY-MM-DD_HHMMSS>/db.sqlite3    — if SQLite
    <target>/<YYYY-MM-DD_HHMMSS>/db.dump       — if PostgreSQL
    <target>/<YYYY-MM-DD_HHMMSS>/vault/        — rsync of the vault

Retention: this command does NOT delete old backups. Add a separate
cleanup script (or extend this one) once a retention policy is decided.

Rationale:
    - `sqlite3 .backup` is the only safe way to snapshot a live SQLite
      database. A plain `cp` can capture a partially-written state if
      another process is mid-transaction.
    - The vault is rsynced, not copied, so the operation is incremental
      and cheap on re-runs.
    - Timestamping the run directory keeps the DB snapshot and the
      vault snapshot paired, so a restore from date X gets a
      consistent view.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Backup the private digital vault and the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--target",
            type=str,
            default=None,
            help="Override the backup target directory "
                 "(defaults to settings.XINDENG_VAULT_BACKUP_TARGET).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be done, without writing anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # ── Resolve target ────────────────────────────────────────
        target_str = options["target"] or getattr(
            settings, "XINDENG_VAULT_BACKUP_TARGET", ""
        )
        if not target_str:
            raise CommandError(
                "No backup target configured. Set XINDENG_VAULT_BACKUP_TARGET "
                "in settings (or via env var) or pass --target."
            )

        target_root = Path(target_str).expanduser().resolve()
        if not dry_run:
            target_root.mkdir(parents=True, exist_ok=True)
        self.stdout.write(f"Backup target: {target_root}")

        # ── Resolve vault ─────────────────────────────────────────
        vault_root = Path(settings.XINDENG_VAULT_ROOT).resolve()
        if not vault_root.is_dir():
            raise CommandError(f"Vault root does not exist: {vault_root}")

        # ── Create timestamped run directory ──────────────────────
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        run_dir = target_root / stamp
        if not dry_run:
            run_dir.mkdir(parents=True, exist_ok=False)

        self.stdout.write(f"Run directory: {run_dir}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — nothing will be written"))

        # ── Database backup ───────────────────────────────────────
        db_conf = settings.DATABASES["default"]
        engine = db_conf["ENGINE"]
        db_name = db_conf["NAME"]

        if "sqlite3" in engine:
            self._backup_sqlite(db_name, run_dir, dry_run)
        elif "postgresql" in engine:
            self._backup_postgres(db_conf, run_dir, dry_run)
        else:
            self.stdout.write(self.style.WARNING(
                f"DB engine '{engine}' not supported for backup — skipping database."
            ))

        # ── Vault backup ──────────────────────────────────────────
        self._backup_vault(vault_root, run_dir, dry_run)

        self.stdout.write(self.style.SUCCESS(f"Backup complete: {run_dir}"))

    # ── helpers ───────────────────────────────────────────────────

    def _backup_sqlite(self, db_path, run_dir, dry_run):
        db_path = Path(str(db_path)).resolve()
        if not db_path.is_file():
            raise CommandError(f"SQLite database not found: {db_path}")

        dest = run_dir / "db.sqlite3"
        self.stdout.write(f"DB (SQLite): {db_path} -> {dest}")

        if dry_run:
            return

        if not shutil.which("sqlite3"):
            raise CommandError(
                "The 'sqlite3' CLI is required for safe SQLite backups. "
                "Install it (brew install sqlite / apt install sqlite3) "
                "or switch to pg_dump for production."
            )

        # .backup is atomic within the SQLite API — safe against a live
        # reader/writer process. Do NOT substitute with shutil.copy2.
        result = subprocess.run(
            ["sqlite3", str(db_path), f".backup '{dest}'"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise CommandError(f"sqlite3 .backup failed: {result.stderr.strip()}")

    def _backup_postgres(self, db_conf, run_dir, dry_run):
        dest = run_dir / "db.dump"
        self.stdout.write(f"DB (PostgreSQL): {db_conf['NAME']} -> {dest}")

        if dry_run:
            return

        if not shutil.which("pg_dump"):
            raise CommandError("pg_dump not found on PATH.")

        env = os.environ.copy()
        if db_conf.get("PASSWORD"):
            env["PGPASSWORD"] = db_conf["PASSWORD"]

        cmd = [
            "pg_dump",
            "-h", db_conf.get("HOST") or "localhost",
            "-p", str(db_conf.get("PORT") or 5432),
            "-U", db_conf.get("USER") or "postgres",
            "-Fc",  # custom format — compressed, parallel-restorable
            "-f", str(dest),
            db_conf["NAME"],
        ]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            raise CommandError(f"pg_dump failed: {result.stderr.strip()}")

    def _backup_vault(self, vault_root, run_dir, dry_run):
        dest = run_dir / "vault"
        self.stdout.write(f"Vault: {vault_root} -> {dest}")

        if dry_run:
            return

        if not shutil.which("rsync"):
            raise CommandError("rsync not found on PATH.")

        # Trailing slash on source copies the *contents* of the vault
        # into the destination, so we get <run_dir>/vault/ebooks/…
        # rather than <run_dir>/vault/private_digital_vault/ebooks/…
        src = str(vault_root) + "/"
        dst = str(dest) + "/"
        dest.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            ["rsync", "-a", src, dst],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise CommandError(f"rsync failed: {result.stderr.strip()}")