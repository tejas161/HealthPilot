"""Prescription decoder UI: paste or upload image, then send to agent for decoding."""

import streamlit as st
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def extract_text_from_uploaded_image(uploaded_file) -> str:
    """Run OCR on an uploaded image; return extracted text."""
    if uploaded_file is None:
        return ""
    try:
        from utils.ocr import extract_text_from_image, is_ocr_available
        if not is_ocr_available():
            return ""
        path = PROJECT_ROOT / ".tmp_prescription_image"
        path.write_bytes(uploaded_file.getvalue())
        try:
            return extract_text_from_image(path)
        finally:
            if path.exists():
                path.unlink(missing_ok=True)
    except Exception:
        return ""


def render_prescription_section(handle_new_message_fn) -> str | None:
    """
    Render the 'Decode a prescription' expander.
    Returns the message to send if user clicked Decode, else None.
    """
    with st.expander("📋 Decode a prescription", expanded=False):
        st.caption("Paste prescription text below, or upload an image to extract text (OCR).")
        prescription_text = st.text_area(
            "Prescription text",
            placeholder="Paste prescription here, or upload an image first to extract text...",
            height=120,
            key="prescription_text",
            label_visibility="collapsed",
        )
        uploaded = st.file_uploader(
            "Or upload prescription image",
            type=["png", "jpg", "jpeg"],
            key="prescription_upload",
        )
        extracted = ""
        if uploaded is not None:
            with st.spinner("Extracting text from image..."):
                extracted = extract_text_from_uploaded_image(uploaded)
            if extracted:
                st.success("Text extracted. You can edit below before decoding.")
            else:
                st.warning(
                    "Could not extract text. Install Tesseract (system) and Pillow/pytesseract, or paste text manually."
                )
        text_to_decode = (prescription_text or extracted).strip()
        if st.button("Decode this prescription", type="primary", key="decode_btn"):
            if not text_to_decode:
                st.error("Please paste prescription text or upload an image first.")
                return None
            return f"Please decode and explain this prescription:\n\n{text_to_decode}"
    return None
