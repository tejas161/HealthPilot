"""
OCR helper for prescription images.
Uses Tesseract to extract text. Optional: can be extended for Vision API later.
"""

from pathlib import Path
from typing import Union

# Optional: PIL for image handling with pytesseract
try:
    import pytesseract
    from PIL import Image
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False


def extract_text_from_image(image_path: Union[str, Path]) -> str:
    """
    Extract text from an image file (e.g. prescription photo) using Tesseract OCR.

    Args:
        image_path: Path to the image file (PNG, JPG, etc.).

    Returns:
        Extracted text, or empty string on failure or if OCR not available.
    """
    if not _OCR_AVAILABLE:
        return ""
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        return ""
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return (text or "").strip()
    except Exception:
        return ""


def is_ocr_available() -> bool:
    """Return True if pytesseract and PIL are installed and Tesseract is usable."""
    if not _OCR_AVAILABLE:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False
