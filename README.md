# 📄 PDF to Word Converter (No OCR) — v1.2

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

## ✨ Features (v1.2)

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

### 🧠 Automatic Mode Selection (`mode="auto"`) — **NEW in v1.2**
* Analyzes each page independently.
* Chooses the best mode per page based on geometry (no ML):
    * **Form** for aligned label–value pages.
    * **Layout** for multi-column structure.
    * **Semantic** for continuous text flow.
* Fully deterministic and explainable.

### 📄 Per-Page Explainability Report — **NEW in v1.2**
* Optional JSON report describing what mode was chosen per page and why.

    [
      { "page": 1, "mode": "semantic", "reason": "single continuous text flow" },
      { "page": 2, "mode": "layout",   "reason": "2 distinct columns detected" },
      { "page": 3, "mode": "form",     "reason": "consistent left-right alignment detected" }
    ]

### 🔢 Selective Page Processing (`--pages`) — **NEW in v1.2**
* Process only specific pages (e.g., `1-3`, `2,5,7`, or `all`).
* Skipped pages are not converted and not logged.
* Useful for debugging, large PDFs, and review workflows.

### ❌ OCR (intentionally disabled)
* No text recognition from images.
* Guarantees zero hallucinated or incorrect text.

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

    PDF
     ↓
    Page-by-page processing
     ↓
    Structural analysis (geometry-based)
     ↓
    Mode selection:
       ├─ semantic
       ├─ layout
       ├─ form
     ↓
    Mode-specific processing
     ↓
    Word (.docx) output
     + Optional JSON explainability report

---

## 🔧 Conversion Modes

### 1️⃣ Semantic Mode (default)
**Best for:** essays, reports, articles, academic PDFs.

**Behavior:**
* Preserves logical reading order
* Outputs clean, editable paragraphs
* Avoids forcing tables or layout assumptions

    mode="semantic"

### 2️⃣ Layout Mode
**Best for:** multi-column documents, reports with images, visually structured PDFs.

**Behavior:**
* Column-aware reading order
* Preserves visual structure safely
* Extracts embedded images on text pages
* No semantic guessing

    mode="layout"

### 3️⃣ Form Mode
**Best for:** receipts, challans, marksheets, structured forms.

**Behavior:**
* Detects true two-column layouts
* Pairs labels and values row-wise
* Outputs a single clean Word table

    mode="form"

### 4️⃣ Auto Mode (v1.2)
**Best for:** mixed-content PDFs.

**Behavior:**
* Automatically selects the best mode per page
* Never invents new behavior
* Decisions are logged and explainable

    mode="auto"

---

## 🧪 Test Coverage

| Test | Description | Result |
| :--- | :--- | :--- |
| **Test 1** | Two-column document | ✅ Pass |
| **Test 2** | Lists & indentation | ✅ Pass |
| **Test 3** | Mixed text + image | ✅ Pass |
| **Test 4** | Scanned / handwritten PDF | ✅ Pass |
| **Test 5** | Long paragraph wrapping | ✅ Pass |
| **Test 6** | Auto-mode mixed PDF | ✅ Pass |
| **Test 7** | Selective page processing | ✅ Pass |

*All limitations are documented boundaries, not bugs.*

---

## ⚠️ Known Limitations (By Design)

* **Inline label–value pairs** without clear column separation fall back to semantic mode.
* **Multi-pair rows** on the same line are not split.
* **Pixel-perfect layout replication** is not attempted.
* **Auto-mode** uses conservative heuristics (no ML).
* **OCR** is deliberately excluded.

These constraints exist to avoid unsafe guessing or silent corruption.

---

## ▶️ How to Run (CLI)

Run all commands from the project root.

### Semantic mode (default)
    python -m backend.app.cli --input input.pdf --output out.docx

### Layout mode
    python -m backend.app.cli --input input.pdf --output out.docx --mode layout

### Form mode
    python -m backend.app.cli --input input.pdf --output out.docx --mode form

### Auto mode + explainability (v1.2)
    python -m backend.app.cli --input input.pdf --output out.docx --mode auto --report report.json

### Auto mode + selective pages
    python -m backend.app.cli --input input.pdf --output out.docx --mode auto --pages 1-3 --report report.json

> **Windows PowerShell note:** Use a single line or the PowerShell line-continuation character ` instead of \.

---

## 🛠️ Tech Stack

* **Python**
* **pdfplumber** — PDF text & geometry inspection
* **python-docx** — Word document generation

---

## 🧩 Why This Project Matters

This project demonstrates:
* Understanding of PDF internals
* Geometry-based document analysis
* Safe heuristic design
* Mode-based system architecture
* Explainability without ML
* Real-world engineering trade-offs

It is designed to be **honest, extensible, and explainable**.

---

## 📌 Version
**v1.2 — Auto mode, explainability, and selective page processing**
