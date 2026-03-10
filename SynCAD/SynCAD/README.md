# SynCAD

**Rectangular Cut Optimiser** — a modern Python desktop application for planning sheet material cuts in workshops.

Built with **PyQt6** and the **MaxRects BSSF** bin-packing algorithm.

---

## Project Structure

```
syncad/
│
├── main.py              # Entry point (3 lines — just calls ui/app.py)
├── version.py           # Single source of truth for name, version, branding
├── requirements.txt
├── README.md
│
├── core/                # Business logic — no UI dependencies
│   ├── models.py        # Job, Sheet, Piece, PlacedPiece, SheetLayout
│   ├── optimizer.py     # MaxRects bin-packing algorithm
│   ├── persistence.py   # Save / load .zcad (JSON), import .ZAD
│   └── export_pdf.py    # PDF report generation (requires reportlab)
│
├── ui/                  # PyQt6 interface
│   ├── app.py           # QApplication setup, stylesheet loading
│   ├── main_window.py   # Main window, menus, toolbar, file I/O
│   ├── job_tab.py       # Job Info tab
│   ├── sheets_tab.py    # Stock Sheets tab
│   ├── pieces_tab.py    # Pieces tab
│   ├── cutplan_tab.py   # Cut Plan visualisation tab
│   └── costs_tab.py     # Cost & Quote tab
│
├── assets/
│   └── style.qss        # Qt stylesheet (edit without touching Python)
│
├── jobs/                # Default saved jobs directory (.zcad files)
│   └── .gitkeep
│
└── tests/
    ├── test_optimizer.py    # Optimizer unit tests
    └── test_persistence.py  # Save/load/import unit tests
```

---

## Installation

```bash
pip install PyQt6 reportlab
```

## Run

```bash
python main.py
```

## Run Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Workflow

1. **Job Info** — set job name, customer, blade kerf, labour rate
2. **Stock Sheets** — add sheet sizes and quantities available
3. **Pieces** — enter all pieces needed (qty × width × height)
4. **F5** — run optimisation
5. **Cut Plan** — visual colour-coded layout per sheet
6. **Costs** — material cost, labour estimate, customer quote price
7. **Export PDF** — printable cut plan + cost summary

---

## File Formats

| Extension | Description |
|---|---|
| `.zcad` | SynCAD job file (JSON) — save/load natively |
| `.ZAD`  | Legacy Z-CAD 2.1d file — importable via File → Import |

---

## Algorithm

SynCAD uses **MaxRects BSSF** (Best Short Side Fit), a well-studied 2D rectangle packing algorithm that achieves 85–95%+ efficiency on typical workshop jobs — a major improvement over the simple guillotine approach in the original Z-CAD.

Pieces are sorted by area (largest first) before placement. Rotation is attempted for each piece unless grain-lock is enabled.
