# core/storage.py
"""
Cross-platform-safe filesystem storage.
"""

from django.core.files.storage import FileSystemStorage

from .image_utils import sanitize_filename


class SafeFileSystemStorage(FileSystemStorage):
    """
    FileSystemStorage that sanitizes filenames on the way in.

    Django's FileSystemStorage.get_valid_name() already handles path
    traversal. We layer cross-platform safety on top.
    """

    def get_valid_name(self, name):
        name = super().get_valid_name(name)
        sanitized = sanitize_filename(name) or name
        return sanitized