"""Pieces Tab — add/edit/remove pieces to be cut."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QAbstractItemView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from core.models import Piece

COLUMNS = ["Qty", "Width (mm)", "Height (mm)", "Label", "Can Rotate", "Area (mm²)"]
COL_QTY, COL_W, COL_H, COL_LABEL, COL_ROT, COL_AREA = range(6)


class PiecesTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_win = parent
        self._loading = False
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        bar = QHBoxLayout()
        self.add_btn = QPushButton("➕  Add Row")
        self.add_btn.clicked.connect(lambda: self._add_piece())
        self.remove_btn = QPushButton("🗑  Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.dup_btn = QPushButton("⧉  Duplicate")
        self.dup_btn.clicked.connect(self._duplicate)
        self.import_btn = QPushButton("📥  Import CSV")
        self.import_btn.setToolTip("Import piece list from a CSV file (qty, width, height, label)")
        self.import_btn.clicked.connect(self._import_csv)

        bar.addWidget(self.add_btn)
        bar.addWidget(self.dup_btn)
        bar.addWidget(self.remove_btn)
        bar.addSpacing(20)
        bar.addWidget(self.import_btn)
        bar.addStretch()

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #2d6a9f; font-weight: bold;")
        bar.addWidget(self.total_label)
        layout.addLayout(bar)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(COL_LABEL, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(COL_QTY, 60)
        self.table.setColumnWidth(COL_W, 100)
        self.table.setColumnWidth(COL_H, 100)
        self.table.setColumnWidth(COL_ROT, 90)
        self.table.setColumnWidth(COL_AREA, 110)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.itemChanged.connect(self._on_changed)
        layout.addWidget(self.table)

        hint = QLabel("💡 Tip: 'Can Rotate' allows the optimizer to turn pieces 90° for a better fit. "
                      "Disable if grain direction matters.")
        hint.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(hint)

    def _add_piece(self, piece: Piece = None):
        if piece is None:
            piece = Piece(quantity=1, width=500, height=300, can_rotate=True)
        self._append_row(piece)
        self.main_win.mark_dirty()
        self._update_total()

    def _remove_selected(self):
        rows = sorted({i.row() for i in self.table.selectedItems()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)
        self._update_total()
        self.main_win.mark_dirty()

    def _duplicate(self):
        rows = {i.row() for i in self.table.selectedItems()}
        for r in rows:
            self._add_piece(self._read_row(r))

    def _import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV files (*.csv);;All files (*)")
        if not path:
            return
        import csv
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # Accept flexible column names
                    qty = int(row.get("qty", row.get("quantity", row.get("Qty", 1))))
                    w = int(row.get("width", row.get("Width", row.get("w", 0))))
                    h = int(row.get("height", row.get("Height", row.get("h", 0))))
                    label = row.get("label", row.get("Label", row.get("name", "")))
                    rotate = str(row.get("can_rotate", row.get("rotate", "yes"))).lower() not in ("no", "0", "false")
                    if w > 0 and h > 0:
                        self._add_piece(Piece(quantity=qty, width=w, height=h, label=label, can_rotate=rotate))
                        count += 1
            QMessageBox.information(self, "Import Done", f"Imported {count} piece(s).")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))

    def _append_row(self, piece: Piece):
        self._loading = True
        r = self.table.rowCount()
        self.table.insertRow(r)

        self.table.setItem(r, COL_QTY, self._num_item(piece.quantity))
        self.table.setItem(r, COL_W, self._num_item(piece.width))
        self.table.setItem(r, COL_H, self._num_item(piece.height))
        self.table.setItem(r, COL_LABEL, QTableWidgetItem(piece.label))

        chk = QTableWidgetItem()
        chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk.setCheckState(Qt.CheckState.Checked if piece.can_rotate else Qt.CheckState.Unchecked)
        chk.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(r, COL_ROT, chk)

        area_item = QTableWidgetItem(f"{piece.area:,}")
        area_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        area_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(r, COL_AREA, area_item)

        self._loading = False

    def _num_item(self, val):
        item = QTableWidgetItem(str(val))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _on_changed(self, item):
        if self._loading:
            return
        r = item.row()
        # Recalculate area
        try:
            w = int(self.table.item(r, COL_W).text())
            h = int(self.table.item(r, COL_H).text())
            area_item = self.table.item(r, COL_AREA)
            if area_item:
                area_item.setText(f"{w * h:,}")
        except (ValueError, AttributeError):
            pass
        self._update_total()
        self.main_win.mark_dirty()

    def _update_total(self):
        total_qty = 0
        total_area = 0
        for r in range(self.table.rowCount()):
            try:
                qty = int(self.table.item(r, COL_QTY).text())
                w = int(self.table.item(r, COL_W).text())
                h = int(self.table.item(r, COL_H).text())
                total_qty += qty
                total_area += qty * w * h
            except (ValueError, AttributeError):
                pass
        self.total_label.setText(
            f"Total: {self.table.rowCount()} row(s), {total_qty} pieces, "
            f"{total_area / 1_000_000:.3f} m²"
        )

    def _read_row(self, r: int) -> Piece:
        def safe_int(col):
            try: return int(self.table.item(r, col).text())
            except: return 0

        rotate = True
        rot_item = self.table.item(r, COL_ROT)
        if rot_item:
            rotate = rot_item.checkState() == Qt.CheckState.Checked

        return Piece(
            quantity=safe_int(COL_QTY),
            width=safe_int(COL_W),
            height=safe_int(COL_H),
            label=self.table.item(r, COL_LABEL).text() if self.table.item(r, COL_LABEL) else "",
            can_rotate=rotate,
        )

    def load_from_job(self, job):
        self._loading = True
        self.table.setRowCount(0)
        self._loading = False
        for piece in job.pieces:
            self._append_row(piece)
        self._update_total()

    def save_to_job(self, job):
        job.pieces = [self._read_row(r) for r in range(self.table.rowCount())
                      if self.table.item(r, COL_QTY)]
