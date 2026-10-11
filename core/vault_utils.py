# core/vault_utils.py
"""
Vault-specific helpers: byte-level content sniffing, format validation.

Kept separate from core/image_utils.py and core/pdf_utils.py because the
vault only cares about three formats (PDF, EPUB, ZIP) and the sniff
logic is small enough to test in isolation.
"""

from __future__ import annotations

import zipfile


def sniff_mime_kind(file_obj, filename: str = "") -> str | None:
    """
    Inspect the head of a file-like object and return one of:

        "pdf"   — %PDF- magic
        "epub"  — ZIP container whose first entry is 'mimetype'
                  containing exactly b'application/epub+zip'
        "zip"   — any other ZIP container (e.g. a bundle of PDFs)
        None    — unrecognised bytes

    file_obj must be seekable. It is left at position 0 on return.
    `filename` is unused at present, but kept in the signature so a
    future extension-consistency check can be layered in without a
    breaking change at call sites.
    """
    file_obj.seek(0)
    head = file_obj.read(8)
    file_obj.seek(0)

    if head.startswith(b"%PDF-"):
        return "pdf"

    if head.startswith(b"PK\x03\x04"):
        # ZIP-family: could be a plain .zip or an .epub (which is a ZIP
        # with a specific first entry).
        try:
            file_obj.seek(0)
            with zipfile.ZipFile(file_obj) as zf:
                names = zf.namelist()
                if names and names[0] == "mimetype":
                    try:
                        with zf.open("mimetype") as m:
                            if m.read() == b"application/epub+zip":
                                return "epub"
                    except KeyError:
                        pass
                return "zip"
        except (zipfile.BadZipFile, OSError):
            return None
        finally:
            file_obj.seek(0)

    return None