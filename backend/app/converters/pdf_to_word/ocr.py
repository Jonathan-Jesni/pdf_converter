import os
import io
import pdfplumber
from docx import Document

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

from backend.app.core.analysis.build_profile import build_page_profile
from backend.app.converters.pdf_to_word.no_ocr import render_profiles_to_doc

def extract_words_ocr(page_image):
    """
    Use pytesseract to extract words with bounding boxes.
    Returns a list of dictionaries compatible with pdfplumber's extract_words format.
    """
    if not HAS_OCR:
        return []
        
    data = pytesseract.image_to_data(page_image, output_type=pytesseract.Output.DICT)
    words = []
    
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text:
            # Map coordinates to pdfplumber format
            # pdfplumber format: {"text": "...", "x0": left, "top": top, "x1": right, "bottom": bottom}
            left = data['left'][i]
            top = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]
            
            words.append({
                "text": text,
                "x0": left,
                "top": top,
                "x1": left + width,
                "bottom": top + height
            })
            
    return words

def pdf_to_word_ocr(
    input_pdf_path,
    output_docx_path,
    report_path=None,
    pages=None
):
    """
    End-to-end PDF to Word converter using OCR for text extraction.
    Reuses the exact same layout analysis and rendering logic as no_ocr.py.
    """
    if not HAS_OCR:
        raise RuntimeError("pytesseract is not installed. Please install it to use OCR mode, or use no-OCR mode instead.")

    doc = Document()
    output_dir = os.path.dirname(output_docx_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    decision_log = []

    with pdfplumber.open(input_pdf_path) as pdf:
        # -------- COLLECT PAGES --------
        page_items = [
            (idx, page)
            for idx, page in enumerate(pdf.pages, start=1)
            if pages is None or idx in pages
        ]

        # -------- PASS 1: ANALYSIS (WITH OCR) --------
        profiles = []
        for idx, page in page_items:
            # Render page to image at 300 DPI for OCR
            # Note: Tesseract performs better with higher resolution
            img = page.to_image(resolution=300).original
            
            # Extract words using OCR
            ocr_words = extract_words_ocr(img)

            # Build profile EXACTLY as we do in no_ocr, but with OCR words
            profile = build_page_profile(
                page_number=idx,
                words=ocr_words,
                images=[]
            )

            profiles.append(profile)

        # -------- PASS 2: RENDER --------
        # Reuse identical rendering pipeline
        render_profiles_to_doc(doc, pdf, profiles, decision_log)

    if report_path and decision_log:
        import json
        with open(report_path, "w") as f:
            json.dump(decision_log, f, indent=2)

    doc.save(output_docx_path)
