"""
File upload helpers: validation, safe filenames, save to disk.
Backend never trusts client-provided filename or extension.
"""
import os
import uuid
from werkzeug.utils import secure_filename

from backend.utils.constants import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES


def get_extension(filename: str) -> str:
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def is_allowed_extension(filename: str) -> bool:
    return get_extension(filename) in ALLOWED_EXTENSIONS


def is_allowed_mime(mime_type: str) -> bool:
    return mime_type in ALLOWED_MIME_TYPES


def generate_safe_filename(original_filename: str) -> str:
    """Return uuid.ext — never uses user input as actual filename."""
    ext = get_extension(original_filename) or 'bin'
    return f'{uuid.uuid4().hex}.{ext}'


def save_upload(file_storage, subfolder: str, upload_root: str):
    """
    Save an uploaded file to upload_root/subfolder/<uuid>.<ext>.
    Returns dict {file_path, original_filename, mime_type, file_size} or raises ValueError.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError('No file provided.')

    original_filename = secure_filename(file_storage.filename) or file_storage.filename
    mime_type = (file_storage.mimetype or '').lower()

    if not is_allowed_extension(original_filename):
        raise ValueError('File type not allowed. Use JPG, JPEG, PNG or WEBP.')
    if not is_allowed_mime(mime_type):
        raise ValueError('Invalid file type (MIME).')

    safe_name = generate_safe_filename(original_filename)

    target_dir = os.path.join(upload_root, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    target_path = os.path.join(target_dir, safe_name)
    file_storage.save(target_path)

    file_size = os.path.getsize(target_path)
    rel_path = os.path.join(subfolder, safe_name).replace('\\', '/')

    return {
        'file_path': rel_path,
        'original_filename': original_filename,
        'mime_type': mime_type,
        'file_size': file_size,
    }