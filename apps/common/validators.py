"""
Input validation utilities for uploaded plant leaf images.
Provides file size, extension, MIME type, and Pillow integrity checks.
"""

from __future__ import annotations

import logging
from typing import Optional, Set, Tuple
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

logger = logging.getLogger(__name__)

DEFAULT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES: Set[str] = {
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
}
ALLOWED_EXTENSIONS: Set[str] = {'.jpg', '.jpeg', '.png', '.webp'}


def validate_uploaded_image(file: Optional[UploadedFile]) -> Tuple[bool, Optional[str]]:
    """
    Validate that the uploaded file is present, within the size limit, has a supported
    format/MIME type, and is a structurally valid image readable by Pillow.

    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    if file is None:
        return False, "No image file was provided. Please choose a leaf image to upload."

    # Size limit
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', DEFAULT_MAX_UPLOAD_SIZE)
    if hasattr(file, 'size') and file.size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"File size ({file.size / (1024 * 1024):.1f}MB) exceeds the maximum allowed size of {max_mb:.0f}MB."

    # Check extension
    filename = getattr(file, 'name', '') or ''
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext and ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Only JPG, PNG, and WebP are supported."

    # Check content_type if available
    content_type = getattr(file, 'content_type', '') or ''
    if content_type and content_type.lower() not in ALLOWED_MIME_TYPES:
        return False, f"Unsupported image type '{content_type}'. Please upload a valid JPG or PNG image."

    # Verify structural integrity using Pillow
    try:
        # Seek back to 0 just in case
        if hasattr(file, 'seek'):
            file.seek(0)
        img = Image.open(file)
        img.verify()
        # Reset file pointer after verify() for subsequent reading
        if hasattr(file, 'seek'):
            file.seek(0)
    except Exception as e:
        logger.warning("Uploaded image failed Pillow validation: %s", e)
        return False, "The uploaded file is corrupt or not a recognized image format."

    return True, None
