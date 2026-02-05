# 📄 PDF to Word Converter (No OCR) — v1.0

A deterministic PDF → Word (.docx) converter that preserves editable text, handles structured forms, and gracefully falls back to images for scanned PDFs, without using OCR.

---

## 🎯 Project Goal

Convert any PDF into a Word document such that:

* **Selectable text stays editable**
* **Scanned / handwritten content becomes images**
* **No OCR is used**
* **Nothing is silently dropped**
* **Behavior is predictable and explainable**

This project focuses on **semantic correctness and safety**, not pixel-perfect visual replication.

---

## ✨ Features (v1.0)

### ✅ Text-based PDFs
* Extracts real text into editable Word paragraphs.
* Detects headings using font-size heuristics.
* Preserves reading order.

### ✅ Form-aware conversion (`form_mode`)
* Converts two-column forms into clean Word tables.
* Row-wise label–value pairing using vertical alignment.
* Ideal for receipts, challans, marksheets, and applications.

### ✅ Scanned / handwritten PDFs
* Automatically detected.
* Entire page rendered as an image.
* Inserted into Word without OCR.

### ✅ Multi-column documents
* Column-aware text processing in semantic mode.
* Prevents left/right column text interleaving.

### ❌ OCR (intentionally disabled)
* No text recognition from images.
* Guarantees no hallucinated or incorrect text.

---

## 🧠 Core Design Philosophy

**Structure over appearance.**

The system prioritizes:
1.  Editability
2.  Semantic meaning
3.  Deterministic behavior

Over:
1.  Pixel-perfect layout
2.  Exact visual cloning

This mirrors how professional document tools are designed internally.

---

## 🏗️ Architecture Overview

    PDF
     ↓
    Page-by-page processing
     ↓
    Detect page type:
       ├─ Text-based
       ├─ Form-like
       └─ Scanned / image-only
     ↓
    Mode-specific processing:
       ├─ semantic mode → paragraphs & headings
       └─ form mode → row-wise tables
     ↓
    Word (.docx) output

---

## 🔧 Conversion Modes

### 1️⃣ Semantic Mode (default)
**Best for:** essays, reports, articles, academic papers.

**Behavior:**
* Preserves text flow
* Supports multi-column reading order
* No tables unless explicitly detected

    mode="semantic"

### 2️⃣ Form Mode
**Best for:** receipts, challans, marksheets, structured forms.

**Behavior:**
* Detects two-column layouts
* Pairs labels and values row-wise
* Outputs a single clean Word table

    mode="form"

---

## 🧪 Test Coverage (v1.0)

| Test | Description | Result |
| :--- | :--- | :--- |
| **Test 1** | Simple two-column form | ✅ Pass |
| **Test 2** | Misaligned rows | ⚠️ Conditional (geometry-dependent) |
| **Test 3** | Normal essay | ✅ Pass |
| **Test 4** | Scanned / handwritten PDF | ✅ Pass |

*All failures are documented boundaries, not bugs.*

---

## ⚠️ Known Limitations (by design)

* **Multi-pair rows on the same line** (e.g. `Label : Value  Label : Value`) are not split yet.
* **Inline label–value pairs** without clear column separation fall back to semantic mode.
* **No pixel-perfect layout replication.**
* **No OCR.**

These are explicitly not handled in v1.0 to avoid unsafe guessing.

---

## 🛠️ Tech Stack

* **Python**
* **pdfplumber** — PDF text & geometry inspection
* **python-docx** — Word document generation

---

## ▶️ How to Run

Run the script from the root directory:

    python app/converters/pdf_to_word/no_ocr.py

Update input/output paths inside the file:

    pdf_to_word_no_ocr(
        "app/storage/uploads/input.pdf",
        "app/storage/outputs/output.docx",
        mode="semantic"  # or "form"
    )

---

## 🚀 Future Work

**Planned (optional):**
* Inline label–value detection
* Multi-pair row splitting
* Auto-detection of semantic vs form mode
* FastAPI backend
* OCR as an optional stage

---

## 🧩 Why This Project Matters

This project demonstrates:
* Understanding of PDF internals
* Safe heuristic design
* Mode-based processing
* Real-world document engineering tradeoffs

It is designed to be **explainable, extensible, and honest**.

---

## 📌 Version
**v1.0 — Frozen**