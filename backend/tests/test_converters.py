import pytest
import os
from backend.app.converters.pdf_to_word.no_ocr import pdf_to_word_no_ocr
from backend.app.converters.pdf_to_word.ocr import pdf_to_word_ocr, HAS_OCR

def test_no_ocr_basic_execution(tmp_path):
    # We don't have a real PDF for unit testing here easily without dependencies, 
    # but we can check if the function handles missing files correctly.
    input_pdf = tmp_path / "non_existent.pdf"
    output_docx = tmp_path / "output.docx"
    
    with pytest.raises(Exception):
        pdf_to_word_no_ocr(str(input_pdf), str(output_docx))

def test_ocr_fallback_logic():
    # If OCR is not installed, it should raise RuntimeError
    if not HAS_OCR:
        with pytest.raises(RuntimeError) as excinfo:
            pdf_to_word_ocr("any.pdf", "any.docx")
        assert "pytesseract is not installed" in str(excinfo.value)
