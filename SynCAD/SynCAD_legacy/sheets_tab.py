"""Stock Sheets Tab — add/edit/remove stock sheet sizes."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QGroupBox, QHeaderView, QAbstractItemView,
    QCheckBox, QSpinBox, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSignalBlocker
from PyQt6.QtGui import QColor, QFont
from core.models import Sheet


COLUMNS = ["Active", "Width (mm)", "Height (mm)", "Qty in Stock",
           "Buy Price (€)", "Sell Price (€)", "Thickness (mm)", "Label"]
COL_ACTIVE, COL_W, COL_H, COL_QTY, COL_BUY, COL_SELL, COL_THICK, COL_LABEL = range(8)


class SheetsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_win = parent
        self._loading = False
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Toolbar
        bar = QHBoxLayout()
        self.add_btn = QPushButton("➕  Add Sheet")
        self.add_btn.clicked.connect(self._add_sheet)
        self.remove_btn = QPushButton("🗑  Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.dup_btn = QPushButton("⧉  Duplicate")
        self.dup_btn.clicked.connect(self._duplicate)

        # Quick-add common sizes
        self.quick_label = QLabel("Quick add:")
        self.q2440 = QPushButton("2440×1220")
        self.q2440.clicked.connect(lambda: self._quick_add(2440, 1220))
        self.q4100 = QPushButton("4100×1200")
        self.q4100.clicked.connect(lambda: self._quick_add(4100, 1200))
        self.q2800 = QPushButton("2800×1850")
        self.q2800.clicked.connect(lambda: self._quick_add(2800, 1850))

        bar.addWidget(self.add_btn)
        bar.addWidget(self.dup_btn)
        bar.addWidget(self.remove_btn)
        bar.addSpacing(20)
        bar.addWidget(self.quick_label)
        bar.addWidget(self.q2440)
        bar.addWidget(self.q4100)
        bar.addWidget(self.q2800)
        bar.addStretch()
        layout.addLayout(bar)

        # Table
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(COL_LABEL, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)

        hint = QLabel("💡 Tip: Set Qty in Stock to control how many sheets the optimizer may use.")
        hint.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(hint)

    def _add_sheet(self, sheet: Sheet = None):
        if sheet is None:
            sheet = Sheet(width=2440, height=1220, active=True, quantity=10)
        self._append_row(sheet)
        self.main_win.mark_dirty()

    def _quick_add(self, w, h):
        self._add_sheet(Sheet(width=w, height=h, active=True, quantity=10))

    def _remove_selected(self):
        rows = sorted({i.row() for i in self.table.selectedItems()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)
        self.main_win.mark_dirty()

    def _duplicate(self):
        rows = {i.row() for i in self.table.selectedItems()}
        for r in rows:
            sheet = self._read_row(r)
            self._append_row(sheet)
        self.main_win.mark_dirty()

    def _append_row(self, sheet: Sheet):
        self._loading = True
        r = self.table.rowCount()
        self.table.insertRow(r)

        chk = QTableWidgetItem()
        chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk.setCheckState(Qt.CheckState.Checked if sheet.active else Qt.CheckState.Unchecked)
        chk.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(r, COL_ACTIVE, chk)

        self.table.setItem(r, COL_W, self._num_item(sheet.width))
        self.table.setItem(r, COL_H, self._num_item(sheet.height))
        self.table.setItem(r, COL_QTY, self._num_item(sheet.quantity))
        self.table.setItem(r, COL_BUY, self._float_item(sheet.buy_price))
        self.table.setItem(r, COL_SELL, self._float_item(sheet.sell_price))
        self.table.setItem(r, COL_THICK, self._float_item(sheet.thickness))
        self.table.setItem(r, COL_LABEL, QTableWidgetItem(sheet.label))

        self._loading = False

    def _num_item(self, val):
        item = QTableWidgetItem(str(val))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _float_item(self, val):
        item = QTableWidgetItem(f"{val:.2f}" if val else "0.00")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _on_item_changed(self, item):
        if not self._loading:
            self.main_win.mark_dirty()

    def _read_row(self, r: int) -> Sheet:
        def safe_int(col):
            try: return int(self.table.item(r, col).text())
            except: return 0

        def safe_float(col):
            try: return float(self.table.item(r, col).text())
            except: return 0.0

        active = self.table.item(r, COL_ACTIVE).checkState() == Qt.CheckState.Checked
        return Sheet(
            width=safe_int(COL_W),
            height=safe_int(COL_H),
            active=active,
            quantity=max(1, safe_int(COL_QTY)),
            buy_price=safe_float(COL_BUY),
            sell_price=safe_float(COL_SELL),
            thickness=safe_float(COL_THICK),
            label=self.table.item(r, COL_LABEL).text() if self.table.item(r, COL_LABEL) else "",
        )

    def load_from_job(self, job):
        self._loading = True
        self.table.setRowCount(0)
        self._loading = False
        for sheet in job.sheets:
            self._append_row(sheet)

    def save_to_job(self, job):
        job.sheets = [self._read_row(r) for r in range(self.table.rowCount())]
