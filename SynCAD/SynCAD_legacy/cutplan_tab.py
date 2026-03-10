"""Cut Plan Tab — visual rendering of the optimized sheet layouts."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QSlider, QFrame, QSizePolicy, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QRect, QPoint, QSize
from PyQt6.QtGui import (QPainter, QColor, QFont, QPen, QBrush,
                          QFontMetrics, QPalette)


class SheetCanvas(QWidget):
    """Renders a single SheetLayout."""

    MARGIN = 20

    def __init__(self, layout, sheet_index: int, scale: float = 0.15):
        super().__init__()
        self.layout = layout
        self.sheet_index = sheet_index
        self._scale = scale
        self._hovered = -1
        self.setMouseTracking(True)
        self._update_size()

    def set_scale(self, scale: float):
        self._scale = scale
        self._update_size()
        self.update()

    def _update_size(self):
        m = self.MARGIN
        w = int(self.layout.sheet.width * self._scale) + m * 2
        h = int(self.layout.sheet.height * self._scale) + m * 2 + 30
        self.setFixedSize(w, h)

    def _to_screen(self, x, y):
        return (
            int(x * self._scale) + self.MARGIN,
            int(y * self._scale) + self.MARGIN + 24,
        )

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        m = self.MARGIN
        sw = int(self.layout.sheet.width * self._scale)
        sh = int(self.layout.sheet.height * self._scale)
        ox, oy = m, m + 24

        # Title bar
        p.fillRect(0, 0, self.width(), 24, QColor("#2d6a9f"))
        p.setPen(QColor("white"))
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        label = (f"Sheet {self.sheet_index}: "
                 f"{self.layout.sheet.width}×{self.layout.sheet.height} mm  |  "
                 f"{len(self.layout.placed)} pcs  |  "
                 f"Efficiency {self.layout.efficiency:.1f}%")
        p.drawText(8, 16, label)

        # Sheet background (waste)
        p.fillRect(ox, oy, sw, sh, QColor("#d0d0d0"))
        p.setPen(QPen(QColor("#888888"), 1))
        p.drawRect(ox, oy, sw, sh)

        # Pieces
        font = QFont("Segoe UI", 7)
        p.setFont(font)
        fm = QFontMetrics(font)

        for i, pp in enumerate(self.layout.placed):
            px = ox + int(pp.x * self._scale)
            py = oy + int(pp.y * self._scale)
            pw = max(2, int(pp.width * self._scale))
            ph = max(2, int(pp.height * self._scale))

            r, g, b = pp.color
            fill = QColor(r, g, b, 200 if i != self._hovered else 255)
            stroke = QColor(r // 2, g // 2, b // 2)

            p.fillRect(px, py, pw, ph, fill)
            p.setPen(QPen(stroke, 1))
            p.drawRect(px, py, pw, ph)

            # Label
            lbl = pp.piece.label or f"{pp.width}×{pp.height}"
            if pp.rotated:
                lbl += " ↺"
            if pw > 30 and ph > 14:
                p.setPen(QColor("#111111"))
                elided = fm.elidedText(lbl, Qt.TextElideMode.ElideRight, pw - 4)
                p.drawText(px + 2, py + ph // 2 + fm.ascent() // 2, elided)

        # Dimensions
        p.setPen(QColor("#444444"))
        p.setFont(QFont("Segoe UI", 7))
        p.drawText(ox, oy + sh + 14,
                   f"{self.layout.sheet.width} mm")
        p.save()
        p.translate(ox - 4, oy)
        p.rotate(-90)
        p.drawText(0, 0, f"{self.layout.sheet.height} mm")
        p.restore()

    def mouseMoveEvent(self, event):
        ox = self.MARGIN
        oy = self.MARGIN + 24
        for i, pp in enumerate(self.layout.placed):
            px = ox + int(pp.x * self._scale)
            py = oy + int(pp.y * self._scale)
            pw = int(pp.width * self._scale)
            ph = int(pp.height * self._scale)
            if QRect(px, py, pw, ph).contains(event.pos()):
                if self._hovered != i:
                    self._hovered = i
                    self.update()
                self.setToolTip(
                    f"{pp.piece.label or 'Piece'}\n"
                    f"{pp.width} × {pp.height} mm\n"
                    f"Position: ({pp.x}, {pp.y})\n"
                    f"{'[Rotated]' if pp.rotated else ''}"
                )
                return
        if self._hovered != -1:
            self._hovered = -1
            self.update()
        self.setToolTip("")


class CutPlanTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_win = parent
        self._scale = 0.14
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Controls bar
        bar = QHBoxLayout()

        bar.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(5, 40)
        self.zoom_slider.setValue(14)
        self.zoom_slider.setFixedWidth(160)
        self.zoom_slider.valueChanged.connect(self._on_zoom)
        bar.addWidget(self.zoom_slider)

        self.zoom_label = QLabel("14%")
        self.zoom_label.setFixedWidth(36)
        bar.addWidget(self.zoom_label)

        bar.addSpacing(20)
        self.stats_label = QLabel("Run optimization to see results.")
        self.stats_label.setStyleSheet("color: #555;")
        bar.addWidget(self.stats_label)
        bar.addStretch()

        layout.addLayout(bar)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.StyledPanel)

        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_container)
        self.canvas_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.canvas_layout.setSpacing(16)

        self.scroll.setWidget(self.canvas_container)
        layout.addWidget(self.scroll)

        self.no_results_label = QLabel("No results yet — press F5 or use Optimize → Run Optimization.")
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setStyleSheet("color: #888; font-size: 13pt; padding: 60px;")

    def _on_zoom(self, val):
        self._scale = val / 100
        self.zoom_label.setText(f"{val}%")
        for i in range(self.canvas_layout.count()):
            w = self.canvas_layout.itemAt(i).widget()
            if isinstance(w, SheetCanvas):
                w.set_scale(self._scale)

    def load_from_job(self, job):
        # Clear existing canvases
        while self.canvas_layout.count():
            item = self.canvas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not job.layouts:
            self.canvas_layout.addWidget(self.no_results_label)
            self.stats_label.setText("No results yet.")
            return

        for i, layout in enumerate(job.layouts):
            canvas = SheetCanvas(layout, i + 1, self._scale)
            self.canvas_layout.addWidget(canvas)

        placed = job.total_pieces_placed
        needed = job.total_pieces_needed
        eff = job.overall_efficiency
        unplaced = len(job.unplaced)
        txt = (f"✅ {placed}/{needed} pieces placed on {job.sheets_used} sheet(s)  |  "
               f"Overall efficiency: {eff:.1f}%")
        if unplaced:
            txt += f"  ⚠️  {unplaced} piece(s) unplaced — add more sheets!"
        self.stats_label.setText(txt)
        color = "#cc0000" if unplaced else "#1a7a1a"
        self.stats_label.setStyleSheet(f"color: {color}; font-weight: bold;")
