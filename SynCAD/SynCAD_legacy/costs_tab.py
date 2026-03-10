"""Costs Tab — material cost, labour, quote summary."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QFormLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class CostsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_win = parent
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        top = QHBoxLayout()

        # ── Summary cards ─────────────────────────────────────────────────────
        cards = QVBoxLayout()

        self.summary_group = QGroupBox("Job Summary")
        self.summary_form = QFormLayout(self.summary_group)
        self.summary_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.summary_form.setSpacing(6)
        cards.addWidget(self.summary_group)

        self.cost_group = QGroupBox("Cost Breakdown")
        self.cost_form = QFormLayout(self.cost_group)
        self.cost_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.cost_form.setSpacing(6)
        cards.addWidget(self.cost_group)

        self.quote_group = QGroupBox("Quote")
        self.quote_form = QFormLayout(self.quote_group)
        self.quote_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.quote_form.setSpacing(6)
        cards.addWidget(self.quote_group)

        cards.addStretch()
        top.addLayout(cards, 1)

        # ── Per-sheet table ────────────────────────────────────────────────────
        sheet_box = QGroupBox("Sheet Usage Detail")
        sheet_vbox = QVBoxLayout(sheet_box)

        self.sheet_table = QTableWidget(0, 5)
        self.sheet_table.setHorizontalHeaderLabels(
            ["Sheet", "Size", "Pieces", "Efficiency", "Material Cost (€)"]
        )
        self.sheet_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.sheet_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sheet_table.setAlternatingRowColors(True)
        self.sheet_table.verticalHeader().hide()
        sheet_vbox.addWidget(self.sheet_table)
        top.addWidget(sheet_box, 2)

        layout.addLayout(top)

        self.no_results = QLabel("Run optimization first to see cost breakdown.")
        self.no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results.setStyleSheet("color: #888; font-size: 12pt; padding: 40px;")
        layout.addWidget(self.no_results)

    def _clear_form(self, form: QFormLayout):
        while form.rowCount():
            form.removeRow(0)

    def _row(self, form, label, value, bold=False, color=None):
        lbl = QLabel(value)
        if bold:
            f = lbl.font()
            f.setBold(True)
            lbl.setFont(f)
        if color:
            lbl.setStyleSheet(f"color: {color};")
        form.addRow(label, lbl)

    def load_from_job(self, job):
        has_results = bool(job.layouts)
        self.no_results.setVisible(not has_results)
        self.summary_group.setVisible(has_results)
        self.cost_group.setVisible(has_results)
        self.quote_group.setVisible(has_results)

        if not has_results:
            self.sheet_table.setRowCount(0)
            return

        # Summary
        self._clear_form(self.summary_form)
        self._row(self.summary_form, "Sheets used:", str(job.sheets_used))
        self._row(self.summary_form, "Pieces placed:",
                  f"{job.total_pieces_placed} / {job.total_pieces_needed}")
        eff_color = "#1a7a1a" if job.overall_efficiency >= 75 else "#cc6600"
        self._row(self.summary_form, "Overall efficiency:",
                  f"{job.overall_efficiency:.1f}%", bold=True, color=eff_color)
        if job.unplaced:
            self._row(self.summary_form, "⚠ Unplaced pieces:",
                      str(len(job.unplaced)), color="#cc0000")

        # Costs
        self._clear_form(self.cost_form)
        mat = job.total_material_cost
        labour = job.estimated_labor_cost
        self._row(self.cost_form, "Material cost:", f"€ {mat:.2f}")
        if job.hourly_rate > 0:
            self._row(self.cost_form, "Estimated cuts:", str(job.estimated_cuts))
            self._row(self.cost_form, "Labour time:", f"{job.estimated_labor_minutes:.0f} min")
            self._row(self.cost_form, "Labour cost:", f"€ {labour:.2f}")
            self._row(self.cost_form, "Total cost:", f"€ {mat + labour:.2f}", bold=True)
        else:
            self._row(self.cost_form, "Total material:", f"€ {mat:.2f}", bold=True)
            self._row(self.cost_form, "(Set labour rate in Job Info for full breakdown)", "")

        # Quote
        self._clear_form(self.quote_form)
        sell = job.total_sell_price
        if sell > 0:
            self._row(self.quote_form, "Sell price (sheets):", f"€ {sell:.2f}")
            if job.markup_percent > 0:
                self._row(self.quote_form, f"Markup ({job.markup_percent:.1f}%):",
                          f"€ {sell - job.total_sell_price / (1 + job.markup_percent/100):.2f}")
            total_quote = sell + labour
            self._row(self.quote_form, "Total quote price:", f"€ {total_quote:.2f}",
                      bold=True, color="#2d6a9f")
            if mat > 0 and total_quote > mat:
                margin = (total_quote - mat - labour) / total_quote * 100
                self._row(self.quote_form, "Gross margin:", f"{margin:.1f}%",
                          color="#1a7a1a" if margin > 20 else "#cc6600")
        else:
            self._row(self.quote_form, "(Set sell prices on sheets for quote)", "")

        # Sheet table
        self.sheet_table.setRowCount(0)
        for i, layout in enumerate(job.layouts):
            r = self.sheet_table.rowCount()
            self.sheet_table.insertRow(r)
            items = [
                f"Sheet {i+1}",
                f"{layout.sheet.width} × {layout.sheet.height} mm",
                str(len(layout.placed)),
                f"{layout.efficiency:.1f}%",
                f"€ {layout.sheet.buy_price:.2f}",
            ]
            for col, txt in enumerate(items):
                item = QTableWidgetItem(txt)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.sheet_table.setItem(r, col, item)

            # Colour-code efficiency
            eff_item = self.sheet_table.item(r, 3)
            if layout.efficiency >= 80:
                eff_item.setForeground(QColor("#1a7a1a"))
            elif layout.efficiency >= 60:
                eff_item.setForeground(QColor("#cc6600"))
            else:
                eff_item.setForeground(QColor("#cc0000"))
