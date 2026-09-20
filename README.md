# PDF Ingestion Pipeline

A multi-stage agentic pipeline for ingesting academic physics textbooks from raw PDF into verified, modernized Markdown and LaTeX.

## Quick Start

```bash
# Ingest a new book (all stages)
bash scripts/ingest_book.sh baym_quantum_mechanics_1969

# Skip OCR (resume from saved segmentation state)
bash scripts/ingest_book.sh baym_quantum_mechanics_1969 --skip-ocr

# Compile the final PDF
python3 src/main.py compile books/baym_quantum_mechanics_1969/book.yaml
```

## Directory Structure

```
pdf_ingestion_pipeline/
├── books/                          # Per-book data (contents gitignored)
│   └── {author}_{topic}_{year}/
│       ├── book.yaml               # Book metadata and pipeline config
│       ├── 00_raw/                 # Source PDFs and chapter slices
│       ├── 01_segmented/           # OCR JSON state + extracted images
│       ├── 02_stitched/            # Cross-page stitched JSON
│       ├── 03_verified_md/         # Stage 3: verified Markdown chunks
│       ├── 04_final_tex/           # Stage 4: LaTeX chunks
│       ├── 05_figures/
│       │   ├── raw/                # fitz-extracted PNGs from PDF
│       │   └── enhanced/           # TikZ/Python reproductions
│       └── 06_compiled/
│           ├── {book_id}.tex       # Master LaTeX file
│           └── {book_id}.pdf       # Final compiled PDF
│
├── src/
│   ├── main.py                     # CLI entry point (book.yaml driven)
│   ├── pipeline/                   # Core pipeline stages
│   │   ├── extractor.py            # Stage 1: OCR via marker-pdf + fitz
│   │   ├── stitcher.py             # Stage 2: Cross-page stitching
│   │   └── assembler.py            # Stage 4: MD → TeX assembly
│   ├── agents/                     # Agent orchestration
│   │   └── orchestrator.py
│   └── core/                       # Shared schemas and utilities
│
├── skills/                         # Agentic skill guides (SKILL.md format)
│   ├── 00_ingest_new_book/         # Complete onboarding guide
│   ├── 01_ocr_extraction/
│   ├── 02_stage3_verification/
│   ├── 03_stage4_latex/
│   ├── 04_figure_enhancement/      # Classifier + TikZ/Python specialists
│   └── 05_notation_upgrade/        # Notation standardization
│
├── config/
│   ├── notation.json               # Canonical physics notation table
│   ├── ocr_cognates.json           # OCR error patterns (from Baym project)
│   ├── style_guide.yaml            # Figure style constants
│   ├── macros.tex                  # Global LaTeX macros
│   └── books/
│       └── {book_id}.yaml          # Per-book overrides
│
└── scripts/
    ├── ingest_book.sh              # One-command pipeline launcher
    ├── slice_pdf.py                # PDF chapter slicer
    ├── fix_html_contamination.py   # Strip HTML from .tex files
    └── stage3_fixer.py             # OCR regex pre-processor
```

## Pipeline Stages

| Stage | Name | Model | Notes |
|-------|------|-------|-------|
| 1 | OCR Extraction | `flash` | 3-page chunks; resumable |
| 1.5 | Figure Extraction | CPU (`fitz`) | bounding-box clipping |
| 2 | Cross-Page Stitching | CPU | deterministic |
| 3 | MD Verification | `flash` + sliced PDF | visual QA against source |
| 4 | LaTeX Conversion | `flash` | text-to-text; no PDF needed |
| 4.5 | Figure Enhancement | `pro` (classifier) + `flash` (specialist) | TikZ/Python |
| 5 | Notation Upgrade | `flash` | uses `config/notation.json` |
| 6 | Compilation | `pdflatex` | generates final book PDF |

## Adding a New Book

1. Create `books/{author}_{topic}_{year}/book.yaml` (copy from template)
2. Place the PDF in `books/{book_id}/00_raw/`
3. Run: `bash scripts/ingest_book.sh {book_id}`

See `skills/00_ingest_new_book/SKILL.md` for the full guide.

## Naming Convention

| Object | Convention | Example |
|--------|-----------|---------|
| Book ID | `{lastname}_{topic}_{year}` | `baym_quantum_mechanics_1969` |
| Source PDF | `{book_id}.pdf` | `baym_quantum_mechanics_1969.pdf` |
| Chapter chunks | `{chNN}_{TITLE_SLUG}.md/.tex` | `03_05_THE_FREE_PARTICLE.tex` |
| Compiled master | `{book_id}.tex/.pdf` | `baym_qm_1969.tex` |

## Books Processed

| Book ID | Title | Status |
|---------|-------|--------|
| `baym_quantum_mechanics_1969` | Lectures on Quantum Mechanics — Gordon Baym | ✅ Stage 4 complete |
