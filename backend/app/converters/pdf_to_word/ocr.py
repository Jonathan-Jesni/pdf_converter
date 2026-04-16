import os
import io
import traceback
import pdfplumber
from docx import Document

print("🚨 OCR FILE LOADED 🚨")

try:
    import pytesseract
    HAS_OCR = True
    
    # ⚠️ ANTIGRAVITY FIX: Set Windows path for Tesseract executable
    # Change this path if you installed Tesseract somewhere else
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
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
            left = data['left'][i]
            top = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]
            
            words.append({
                "text": text,
                "x0": left,
                "top": top,
                "x1": left + width,
                "bottom": top + height,
                "size": height,
            })
            
    return words

# ---------------------------------------------------------------------------
# OCR post-processing helpers
# ---------------------------------------------------------------------------

_LINE_Y_THRESHOLD = 8
_MIN_TOKEN_LEN = 1

def _clean_ocr_words(words):
    cleaned = []
    for w in words:
        text = w["text"].strip()
        if not text:
            continue
        if len(text) < _MIN_TOKEN_LEN:
            if text not in ("I", "A", "a", "&", "-", "–", "—"):
                continue
        cleaned.append({**w, "text": text})
    return cleaned

def _group_into_lines(words):
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

    merged = []
    for line in lines:
        line_sorted = sorted(line, key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in line_sorted)
        if not text.strip():
            continue
        sized_words = [w for w in line_sorted if "size" in w]
        average_size = (
            sum(w["size"] for w in sized_words) / len(line_sorted)
            if sized_words
            else 10
        )
        merged.append({
            "text": text,
            "x0": min(w["x0"] for w in line_sorted),
            "x1": max(w["x1"] for w in line_sorted),
            "top": line_sorted[0]["top"],
            "bottom": max(w["bottom"] for w in line_sorted),
            "size": average_size,
        })

    return merged

def _sort_and_clean_ocr_output(raw_words):
    sorted_words = sorted(raw_words, key=lambda w: (w["top"], w["x0"]))
    cleaned = _clean_ocr_words(sorted_words)
    if not cleaned:
        return []
    grouped = _group_into_lines(cleaned)
    return grouped

def pdf_to_word_ocr(
    input_pdf_path,
    output_docx_path,
    report_path=None,
    pages=None
):
    print("🚨 OCR FUNCTION CALLED 🚨")

    if not HAS_OCR:
        raise RuntimeError("pytesseract is not installed. Please install it to use OCR mode, or use no-OCR mode instead.")

    doc = Document()
    output_dir = os.path.dirname(output_docx_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    decision_log = []

    with pdfplumber.open(input_pdf_path) as pdf:
        page_items = [
            (idx, page)
            for idx, page in enumerate(pdf.pages, start=1)
            if pages is None or idx in pages
        ]

        profiles = []
        for idx, page in page_items:
            print(f"🚨 PROCESSING PAGE {idx} 🚨")
            try:
                img = page.to_image(resolution=300).original
                raw_ocr_words = extract_words_ocr(img)
                ocr_words = _sort_and_clean_ocr_output(raw_ocr_words)

                safe_words = []
                for w in ocr_words:
                    try:
                        safe_words.append({
                            "text": str(w.get("text", "")),
                            "x0": float(w.get("x0", 0)),
                            "x1": float(w.get("x1", 0)),
                            "top": float(w.get("top", 0)),
                            "bottom": float(w.get("bottom", 0)),
                            "size": float(w.get("size", 10)),
                        })
                    except Exception:
                        continue

                profile = build_page_profile(
                    page_number=idx,
                    words=safe_words,
                    images=[]
                )
                profiles.append(profile)

            except Exception as e:
                # ⚠️ ANTIGRAVITY FIX: Catch the error and use image fallback instead of crashing!
                print(f"[OCR CRASH CAUGHT] Page {idx}: {e}")
                traceback.print_exc()
                
                # Create an empty profile to trigger the full-width image fallback
                profile = build_page_profile(page_number=idx, words=[], images=[])
                profiles.append(profile)

        render_profiles_to_doc(doc, pdf, profiles, decision_log)

    if report_path and decision_log:
        import json
        with open(report_path, "w") as f:
            json.dump(decision_log, f, indent=2)

    doc.save(output_docx_path)