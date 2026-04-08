from fastapi.testclient import TestClient
from backend.app.main import app
import os
import io

client = TestClient(app)

def test_convert_no_ocr_invalid_file():
    # Test with a non-pdf file
    response = client.post(
        "/convert",
        files={"file": ("test.txt", b"not a pdf content", "text/plain")},
        data={"use_ocr": "false"}
    )
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]

def test_convert_ocr_not_installed_if_requested():
    # This test assumes HAS_OCR might be False in the test environment
    # Since we can't easily mock HAS_OCR without more effort, we just check the endpoint existence
    response = client.post(
        "/convert",
        files={"file": ("test.pdf", b"%PDF-1.4...", "application/pdf")},
        data={"use_ocr": "true"}
    )
    # If HAS_OCR is False, it should return 500 with a specific message
    from backend.app.converters.pdf_to_word.ocr import HAS_OCR
    if not HAS_OCR:
        assert response.status_code == 500
        assert "pytesseract is not installed" in response.json()["detail"]
    else:
        # If HAS_OCR is True, it might fail because of invalid PDF content, but status should not be 400
        assert response.status_code != 400
