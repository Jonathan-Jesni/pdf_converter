# 📄 PDF to Word Converter (No OCR) — v1.1

A deterministic PDF → Word (.docx) conversion engine that preserves editable text, handles structured forms, and safely falls back to images for scanned PDFs — without using OCR.

The system prioritizes correctness, safety, and explainability over pixel-perfect layout replication.

---

## 🎯 Project Goal

Convert PDFs into Word documents such that:

* **Selectable text remains editable**
* **Scanned or handwritten pages are embedded as images**
* **OCR is explicitly disabled**
* **No content is silently dropped**
* **All behavior is deterministic and explainable**

This project focuses on **semantic correctness**, not visual imitation.

---

## ✨ Features (v1.1)

### ✅ Text-based PDFs
* Extracts real text into editable Word paragraphs.
* Detects headings using font-size heuristics.
* Preserves logical reading order.

### ✅ Layout-preserving conversion (`mode="layout"`)
* Column-aware reading for multi-column PDFs.
* Prevents left/right text interleaving.
* Safely handles mixed text and embedded images.
* Preserves editability without semantic guessing.

### ✅ Form-aware conversion (`mode="form"`)
* Converts clean two-column forms into Word tables.
* Row-wise label–value pairing using vertical alignment.
* Suitable for receipts, challans, marksheets, and applications.

### ✅ Scanned / handwritten PDFs
* Automatically detected.
* Entire page rendered as an image.
* Inserted into Word without OCR.

### ❌ OCR (intentionally disabled)
* No text recognition from images.
* Guarantees zero hallucinated or incorrect text.

> **v1.1** introduces layout-preserving conversion and a command-line interface while maintaining deterministic, no-OCR behavior.

---

## 🧠 Core Design Philosophy

**Structure over appearance.**

The system prioritizes:
1. Editability
2. Semantic meaning
3. Deterministic behavior

Over:
1. Pixel-perfect layout cloning
2. Unsafe inference or guessing

This mirrors how professional document-processing systems are designed internally.

---

## 🏗️ Architecture Overview

```text
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
   ├─ layout mode → column-aware visual order
   └─ form mode → row-wise tables
 ↓
Word (.docx) output
```

---

## 🔧 Conversion Modes

### 1️⃣ Semantic Mode (default)
**Best for:** essays, reports, articles, academic PDFs.

**Behavior:**
* Preserves logical reading order
* Outputs clean, editable paragraphs
* Avoids forcing tables or layout assumptions

```python
mode="semantic"
```

### 2️⃣ Layout Mode
**Best for:** multi-column documents, reports with images, visually structured PDFs.

**Behavior:**
* Column-aware reading order
* Preserves visual structure safely
* Extracts embedded images on text pages
* No semantic guessing

```python
mode="layout"
```

### 3️⃣ Form Mode
**Best for:** receipts, challans, marksheets, structured forms.

**Behavior:**
* Detects true two-column layouts
* Pairs labels and values row-wise
* Outputs a single clean Word table

```python
mode="form"
```

---

## 🧪 Test Coverage (v1.1)

| Test | Description | Result |
| :--- | :--- | :--- |
| **Test 1** | Two-column document | ✅ Pass |
| **Test 2** | Lists & indentation | ✅ Pass |
| **Test 3** | Mixed text + image | ✅ Pass |
| **Test 4** | Scanned / handwritten PDF | ✅ Pass |
| **Test 5** | Long paragraph wrapping | ✅ Pass |

*All limitations are documented boundaries, not bugs.*

---

## ⚠️ Known Limitations (By Design)

* **Inline label–value pairs** without clear column separation fall back to semantic mode.
* **Multi-pair rows** on the same line are not split.
* **Pixel-perfect layout replication** is not attempted.
* **OCR** is deliberately excluded.

These constraints exist to avoid unsafe guessing or silent corruption.

---

## 🛠️ Tech Stack

* **Python**
* **pdfplumber** — PDF text and geometry inspection
* **python-docx** — Word document generation

---

## ▶️ How to Run (CLI)

Run all commands from the project root.

### Semantic mode (default)
```bash
python -m backend.app.cli \
  --input backend/app/storage/uploads/input.pdf \
  --output backend/app/storage/outputs/output_semantic.docx
```

### Layout mode
```bash
python -m backend.app.cli \
  --input backend/app/storage/uploads/input.pdf \
  --output backend/app/storage/outputs/output_layout.docx \
  --mode layout
```

### Form mode
```bash
python -m backend.app.cli \
  --input backend/app/storage/uploads/input.pdf \
  --output backend/app/storage/outputs/output_form.docx \
  --mode form
```

> **Windows PowerShell note:** Run commands on a single line or use the PowerShell line-continuation character ` instead of \.

---

## 🚀 Future Work (Optional)

* Inline label–value detection
* Multi-pair row handling
* Automatic mode selection
* FastAPI backend
* OCR as an explicit, optional stage

---

## 🧩 Why This Project Matters

This project demonstrates:
* Understanding of PDF internals
* Geometry-based document analysis
* Safe heuristic design
* Mode-based system architecture
* Real-world engineering trade-offs

It is designed to be **honest, extensible, and explainable**.

---

## 📌 Version
**v1.1 — Stable**