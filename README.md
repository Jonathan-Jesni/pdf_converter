# 📄 PDF to Word Converter (No OCR) — v2.0

A deterministic, two-pass PDF → Word (.docx) document engine that performs explicit structural analysis before rendering.

The system prioritizes editability, correctness, and explainability over pixel-perfect layout imitation — without using OCR or machine learning.

---

## 🚀 What Changed in v2.0

v2.0 introduces a **two-pass structural analysis engine**:

**Pass 1 — Analysis**
* Page-level structural modeling
* Explicit `PageProfile` abstraction
* Paragraph reconstruction
* List detection
* Heading detection
* Deterministic table detection

**Pass 2 — Rendering**
* Structured content rendering
* Mode-based output (semantic / layout / form / table)
* Safe fallbacks
* No re-analysis during rendering

> This moves the system from heuristic rendering to a proper document-processing architecture.

---

## 🎯 Project Goal

Convert PDFs into Word documents such that:

* **Selectable text remains fully editable**
* **Structural meaning is preserved**
* **Tables are detected conservatively**
* **Scanned pages are embedded as images**
* **No OCR is used**
* **No content is silently dropped**
* **All decisions are explainable**

---

## 🧠 Core Design Philosophy

**Structure first. Rendering second.**

The engine separates:
1. **Analysis** (what the page is)
2. **Rendering** (how we output it)

This mirrors real-world document-processing systems. 

---

## 🏗️ Architecture Overview (v2.0)

    PDF
     ↓
    PASS 1: Structural Analysis 
     ├─ Detect columns
     ├─ Detect forms
     ├─ Reconstruct paragraphs
     ├─ Detect lists
     ├─ Detect headings
     ├─ Detect tables (grid + width consistency)
     ↓
    PageProfile (explicit page model)
     ↓
    PASS 2: Structured Rendering
     ├─ semantic
     ├─ layout
     ├─ form
     └─ table
     ↓
    Word (.docx)
     + Optional JSON explainability report

---

## ✨ Features (v2.0)

### ✅ Two-Pass Structural Engine
* Document-level analysis before rendering.
* Stable mode decisions.
* No layout oscillation.

### ✅ Paragraph Reconstruction
* Merges broken PDF line wraps.
* Preserves logical paragraph flow.
* Deterministic (no NLP).

### ✅ List & Heading Detection
* **Lists:** Detects bullet and numbered lists (requires ≥2 items).
* **Headings:** Font-size based with short-line filtering.
* **Conservative:** Uses strict heuristics to reduce false positives.

### ✅ Deterministic Table Detection (NEW in v2.0)
* Requires ≥3 stable column anchors.
* Requires ≥3 hits per row.
* Requires row-width consistency.
* Rejects layout-based false positives.
* Falls back safely.

### ✅ Layout Mode
* Column-aware rendering.
* Prevents text interleaving.
* Handles embedded images.

### ✅ Form Mode
* Label–value alignment detection.
* Clean two-column table output.

### ✅ Auto Mode
* Page-level decision making.
* No ML.
* Fully explainable.

### ✅ Explainability Report
Example:
    [
      { "page": 1, "mode": "layout", "reason": "multi-column text layout" },
      { "page": 2, "mode": "semantic", "reason": "normal flowing text" }
    ]

---

## 🔧 Conversion Modes

| Mode | Purpose |
| :--- | :--- |
| **semantic** | Continuous flowing text |
| **layout** | Multi-column structured text |
| **form** | Label–value structured pages |
| **table** | True grid-aligned tables |
| **auto** | Per-page deterministic selection |

---

## ⚠️ Known Limitations (Intentional)

* **No OCR**
* **No ML-based inference**
* **No pixel-perfect layout cloning**
* **Conservative table detection** (false negatives preferred over false positives)
* **Inline label–value pairs** without geometry separation fall back to semantic

These are design decisions, not bugs.

---

## ▶️ How to Run

From project root:

### Default (semantic)
    python -m backend.app.cli --input input.pdf --output out.docx

### Auto mode + report
    python -m backend.app.cli --input input.pdf --output out.docx --mode auto --report report.json

### Select specific pages
    python -m backend.app.cli --input input.pdf --output out.docx --mode auto --pages 1-3

---

## 🛠️ Tech Stack

* **Python**
* **pdfplumber**
* **python-docx**

**No OCR. No ML. No external services.**

---

## 🧩 Engineering Highlights

This project demonstrates:
* Two-pass document architecture
* Geometry-based structural inference 
* Conservative heuristic design
* Deterministic fallback strategy
* Explicit page modeling (`PageProfile` abstraction)
* Separation of analysis and rendering
* Safe table detection via structural consistency checks

---

## 🏷️ Version
**v2.0.0 — Two-pass structural document engine with semantic reconstruction and deterministic table detection**