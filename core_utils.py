import re
from pathlib import Path

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


def validate_phone(value):
    if value and not re.fullmatch(r"[+\d][\d\s()-]{6,14}", value):
        raise ValidationError("Enter a valid phone number.")
    return value


def validate_image(upload, max_mb=5, extensions=(".jpg", ".jpeg", ".png", ".webp")):
    if not upload:
        return upload
    if Path(upload.name).suffix.lower() not in extensions:
        raise ValidationError("Upload a JPG, PNG, or WEBP image.")
    if upload.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Image must be smaller than {max_mb} MB.")
    try:
        image = Image.open(upload)
        image.verify()
        upload.seek(0)
    except (UnidentifiedImageError, OSError):
        raise ValidationError("The uploaded file is not a readable image.")
    return upload


def validate_video(upload, max_mb=100, extensions=(".mp4", ".webm", ".mov")):
    if not upload:
        return upload
    if Path(upload.name).suffix.lower() not in extensions:
        raise ValidationError("Upload an MP4, WEBM, or MOV video.")
    if upload.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Video must be smaller than {max_mb} MB.")
    return upload
