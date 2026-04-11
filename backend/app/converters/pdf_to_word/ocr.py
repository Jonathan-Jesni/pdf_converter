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


# ---------------------------------------------------------------------------
# OCR post-processing helpers
# ---------------------------------------------------------------------------

# Threshold (in pts / pixels) for grouping words onto the same line.
_LINE_Y_THRESHOLD = 8

# Minimum token length to keep (filters single-char OCR noise).
_MIN_TOKEN_LEN = 2


def _clean_ocr_words(words):
    """
    Remove obvious OCR noise:
      - empty or whitespace-only tokens
      - very short tokens likely to be artifacts (single chars)
    """
    cleaned = []
    for w in words:
        text = w["text"].strip()
        if not text:
            continue
        if len(text) < _MIN_TOKEN_LEN:
            # Keep single chars only if they are common standalone characters
            if text not in ("I", "A", "a", "&", "-", "–", "—"):
                continue
        cleaned.append({**w, "text": text})
    return cleaned


def _group_into_lines(words):
    """
    Group words into lines based on vertical proximity, then merge each
    line into a single synthetic word spanning the full line width.
    This produces cleaner, better-ordered input for downstream analysis.
    """
    if not words:
        return []

    sorted_words = sorted(words, key=lambda w: (w["top"], w["x0"]))

    lines = []
    current_line = [sorted_words[0]]

    for w in sorted_words[1:]:
        if abs(w["top"] - current_line[0]["top"]) <= _LINE_Y_THRESHOLD:
            current_line.append(w)
        else:
            lines.append(current_line)
            current_line = [w]

    if current_line:
        lines.append(current_line)

    # Merge each line into a single word dict (preserves pdfplumber format)
    merged = []
    for line in lines:
        line_sorted = sorted(line, key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in line_sorted)
        if not text.strip():
            continue
        merged.append({
            "text": text,
            "x0": min(w["x0"] for w in line_sorted),
            "x1": max(w["x1"] for w in line_sorted),
            "top": line_sorted[0]["top"],
            "bottom": max(w["bottom"] for w in line_sorted),
        })

    return merged


def _sort_and_clean_ocr_output(raw_words):
    """
    Orchestrator: sort → clean → group OCR words into well-ordered lines.
    Returns a list of word dicts in correct reading order.
    """
    # 1. Sort by reading order (top → left)
    sorted_words = sorted(raw_words, key=lambda w: (w["top"], w["x0"]))

    # 2. Strip noise
    cleaned = _clean_ocr_words(sorted_words)

    # 3. Group into lines and return individual words (not merged)
    #    We keep individual words so column detection still works.
    if not cleaned:
        return []

    # Re-sort after cleaning (already sorted, but defensive)
    return sorted(cleaned, key=lambda w: (w["top"], w["x0"]))


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
            raw_ocr_words = extract_words_ocr(img)

            # Clean and sort OCR output before analysis
            ocr_words = _sort_and_clean_ocr_output(raw_ocr_words)

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
