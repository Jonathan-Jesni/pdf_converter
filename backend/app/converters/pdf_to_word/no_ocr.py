import pdfplumber
from docx import Document
from .layout import pdf_to_word_layout
from backend.app.core.auto_mode import detect_mode
import io
import os


LINE_Y_THRESHOLD = 3
PARAGRAPH_Y_GAP = 12
HEADING_SCALE = 1.25
MIN_TEXT_CHARS = 30
COLUMN_GAP_THRESHOLD = 50
ROW_Y_THRESHOLD = 10


def add_full_width_image(doc, image_buffer):
    section = doc.sections[-1]
    max_width = section.page_width - section.left_margin - section.right_margin
    doc.add_picture(image_buffer, width=max_width)


def is_meaningful_text(words, min_chars=MIN_TEXT_CHARS):
    total_chars = sum(len(w["text"].strip()) for w in words)
    return total_chars >= min_chars


def group_words_into_lines(words):
    lines = []
    current = []

    for w in sorted(words, key=lambda x: (x["top"], x["x0"])):
        if not current:
            current.append(w)
            continue

        if abs(w["top"] - current[-1]["top"]) <= LINE_Y_THRESHOLD:
            current.append(w)
        else:
            lines.append(current)
            current = [w]

    if current:
        lines.append(current)

    return lines


def split_into_columns(words):
    words = sorted(words, key=lambda w: w["x0"])
    columns = []
    current = [words[0]]

    for w in words[1:]:
        if abs(w["x0"] - current[-1]["x0"]) > COLUMN_GAP_THRESHOLD:
            columns.append(current)
            current = [w]
        else:
            current.append(w)

    columns.append(current)
    return columns


def extract_lines(words):
    lines = group_words_into_lines(words)
    result = []
    for line in lines:
        text = " ".join(w["text"] for w in line).strip()
        top = line[0]["top"]
        if text:
            result.append((top, text))
    return result


def pair_form_rows(left_lines, right_lines):
    pairs = []
    used = set()

    for l_top, l_text in left_lines:
        best = None
        best_diff = None

        for i, (r_top, r_text) in enumerate(right_lines):
            if i in used:
                continue
            diff = abs(l_top - r_top)
            if diff <= ROW_Y_THRESHOLD and (best_diff is None or diff < best_diff):
                best = (i, r_text)
                best_diff = diff

        if best:
            idx, r_text = best
            used.add(idx)
            pairs.append((l_text, r_text))
        else:
            pairs.append((l_text, ""))

    return pairs


def pdf_to_word_no_ocr(
    input_pdf_path,
    output_docx_path,
    mode="semantic",
    report_path=None,
    pages=None
):
    if mode == "layout":
        pdf_to_word_layout(input_pdf_path, output_docx_path)
        return

    doc = Document()
    output_dir = os.path.dirname(output_docx_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    decision_log = []

    with pdfplumber.open(input_pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            if pages is not None and idx not in pages:
                continue

            words = page.extract_words(use_text_flow=True)

            page_mode = mode
            reason = None

            if page_mode == "auto":
                blocks = [
                    (w["x0"], w["top"], w["x1"], w["bottom"], w["text"])
                    for w in words
                    if "x0" in w and "x1" in w and "top" in w and "bottom" in w
                ]

                page_mode, reason = detect_mode(blocks, page.width)

                decision_log.append({
                    "page": idx,
                    "mode": page_mode,
                    "reason": reason
                })

            if not words or not is_meaningful_text(words):
                img = page.to_image(resolution=300).original
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                add_full_width_image(doc, buf)
                doc.add_page_break()
                continue

            if page_mode == "form":
                columns = split_into_columns(words)
                if len(columns) == 2:
                    left_lines = extract_lines(columns[0])
                    right_lines = extract_lines(columns[1])
                    pairs = pair_form_rows(left_lines, right_lines)

                    table = doc.add_table(rows=len(pairs), cols=2)
                    for i, (l, r) in enumerate(pairs):
                        table.cell(i, 0).text = l
                        table.cell(i, 1).text = r

                    doc.add_page_break()
                    continue

            font_sizes = [w["size"] for w in words if "size" in w]
            avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else 10

            lines = group_words_into_lines(words)
            paragraphs = []
            current = []
            last_top = None

            for line in lines:
                top = line[0]["top"]
                if last_top and abs(top - last_top) > PARAGRAPH_Y_GAP:
                    paragraphs.append(current)
                    current = []
                current.append(line)
                last_top = top

            if current:
                paragraphs.append(current)

            for para in paragraphs:
                text = " ".join(
                    " ".join(w["text"] for w in line) for line in para
                ).strip()

                if not text:
                    continue

                mean_size = sum(
                    w["size"] for line in para for w in line if "size" in w
                ) / max(1, sum(1 for line in para for w in line if "size" in w))

                if mean_size > avg_size * HEADING_SCALE:
                    doc.add_heading(text, level=1)
                else:
                    doc.add_paragraph(text)

            doc.add_page_break()

    if report_path and decision_log:
        import json
        with open(report_path, "w") as f:
            json.dump(decision_log, f, indent=2)

    doc.save(output_docx_path)
