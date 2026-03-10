# Z-CAD Python

A modern Python remake of the German **Z-CAD 2.1d** rectangular cut optimization program.

## Features

- **MaxRects bin-packing** algorithm — significantly better material yield than the original
- Unlimited stock sheets and pieces (original: 10 sheets / 50 pieces)
- Grain direction / rotation lock per piece
- Blade kerf (saw width) baked into all placements
- **Job management**: save/load as `.zcad` (JSON), recent files, import legacy `.ZAD` files
- **Cost sheet**: material cost, labour estimate, markup, quote price
- **Visual cut plan**: colour-coded, zoomable, hover tooltips showing piece info
- **PDF export** of cut plan + cost summary (requires `reportlab`)
- **CSV import** of piece lists

## Installation

```bash
pip install PyQt6 reportlab
```

## Running

```bash
cd zcad_python
python main.py
```

## File formats

| Extension | Description |
|---|---|
| `.zcad` | Z-CAD Python job file (JSON) |
| `.ZAD` | Legacy Z-CAD 2.1d job file (importable) |

## Data format (Mat. line in .ZAD files)

```
Mat.  [idx]  [active]  [-1]  [width]  [height]  [?]  [buy_price]  [sell_price]  [thickness]  [kerf]  [hourly_rate]
Pos.  [idx]  [qty]  [width]  [height]  [rotation_flag]
```

## Quick start workflow

1. **Job Info tab** — enter job name, customer, blade kerf
2. **Stock Sheets tab** — add your available sheet sizes + quantities
3. **Pieces tab** — enter all pieces needed (qty, width × height)
4. Press **F5** or click **▶ Optimize**
5. View results in **Cut Plan** and **Costs** tabs
6. **Export PDF** for printing / customer quote

## Algorithm

Uses **MaxRects BSSF** (Best Short Side Fit), a well-studied 2D bin-packing algorithm that
consistently achieves 85–95%+ efficiency on typical workshop jobs.

## Extending

All business logic lives in `core/`:
- `models.py` — data classes
- `optimizer.py` — MaxRects algorithm
- `persistence.py` — save/load/import
- `export_pdf.py` — PDF generation

The UI (`ui/`) is cleanly separated. You can swap the frontend or add new tabs without touching the core.
