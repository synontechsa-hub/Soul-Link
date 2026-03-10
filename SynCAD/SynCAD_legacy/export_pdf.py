"""
Z-CAD Python — PDF Export
Generates a professional cut plan + cost summary PDF.
Requires: reportlab
"""
from pathlib import Path


def export_pdf(job, filepath: str) -> None:
    """Export job results to a PDF report."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer, HRFlowable)
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.graphics.shapes import Drawing, Rect as RLRect, String, Group
        from reportlab.graphics import renderPDF
    except ImportError:
        raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=4)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11, spaceAfter=2)
    normal = styles["Normal"]

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(f"Cut Plan: {job.name}", title_style))
    if job.customer:
        story.append(Paragraph(f"Customer: {job.customer}", normal))
    if job.material_name:
        story.append(Paragraph(f"Material: {job.material_name}", normal))
    if job.notes:
        story.append(Paragraph(f"Notes: {job.notes}", normal))
    story.append(Spacer(1, 6*mm))

    # ── Summary ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Summary", h2))
    summary_data = [
        ["Sheets used", str(job.sheets_used)],
        ["Pieces placed", f"{job.total_pieces_placed} / {job.total_pieces_needed}"],
        ["Overall efficiency", f"{job.overall_efficiency:.1f}%"],
        ["Blade kerf", f"{job.blade_kerf} mm"],
    ]
    if job.total_material_cost > 0:
        summary_data.append(["Material cost", f"€ {job.total_material_cost:.2f}"])
    if job.hourly_rate > 0:
        summary_data.append(["Labour cost", f"€ {job.estimated_labor_cost:.2f}"])
        summary_data.append(["Est. labour time", f"{job.estimated_labor_minutes:.0f} min"])
    if job.total_sell_price > 0:
        summary_data.append(["Sell price (incl. markup)", f"€ {job.total_sell_price:.2f}"])

    t = Table(summary_data, colWidths=[60*mm, 60*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 6*mm))

    # ── Cut Layouts ───────────────────────────────────────────────────────────
    page_w = 180 * mm  # usable width

    for idx, layout in enumerate(job.layouts):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Spacer(1, 3*mm))
        eff = layout.efficiency
        story.append(Paragraph(
            f"Sheet {idx+1}: {layout.sheet.width} × {layout.sheet.height} mm "
            f"— {len(layout.placed)} pieces — Efficiency: {eff:.1f}%",
            h2
        ))

        # Scale to fit page width
        scale = min(page_w / layout.sheet.width, 100*mm / layout.sheet.height)
        dw = layout.sheet.width * scale
        dh = layout.sheet.height * scale

        d = Drawing(dw, dh + 2)

        # Sheet background
        d.add(RLRect(0, 0, dw, dh, fillColor=colors.HexColor("#e8e8e8"), strokeColor=colors.black, strokeWidth=1))

        for pp in layout.placed:
            x = pp.x * scale
            # Flip Y: PDF coords start bottom-left
            y = dh - (pp.y + pp.height) * scale
            w = pp.width * scale
            h = pp.height * scale

            r, g, b = pp.color
            fill = colors.Color(r/255, g/255, b/255, alpha=0.75)
            d.add(RLRect(x, y, w, h, fillColor=fill, strokeColor=colors.black, strokeWidth=0.5))

            # Label
            lbl = pp.piece.label or f"{pp.width}×{pp.height}"
            if pp.rotated:
                lbl += " ↺"
            font_size = max(5, min(8, int(h * 0.25)))
            if w > 15 and h > 8:
                d.add(String(x + 2, y + h/2 - font_size/2, lbl,
                             fontSize=font_size, fillColor=colors.black,
                             fontName="Helvetica"))

        story.append(d)
        story.append(Spacer(1, 4*mm))

    # ── Piece List ────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Piece List", h2))

    piece_data = [["#", "Label", "Qty", "Width (mm)", "Height (mm)", "Area (mm²)", "Rotate"]]
    for i, p in enumerate(job.pieces):
        if p.quantity > 0:
            piece_data.append([
                str(i + 1),
                p.label or "—",
                str(p.quantity),
                str(p.width),
                str(p.height),
                f"{p.area:,}",
                "Yes" if p.can_rotate else "No",
            ])

    pt = Table(piece_data, colWidths=[10*mm, 50*mm, 15*mm, 22*mm, 22*mm, 30*mm, 15*mm])
    pt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a9f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ]))
    story.append(pt)

    if job.unplaced:
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(
            f"⚠ {len(job.unplaced)} piece(s) could not be placed — add more sheets.",
            ParagraphStyle("warn", parent=normal, textColor=colors.red)
        ))

    doc.build(story)
