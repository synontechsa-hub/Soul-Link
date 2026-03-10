"""
Z-CAD Python — Main Application Window
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QStatusBar,
    QMenuBar, QMenu, QToolBar, QLabel, QMessageBox,
    QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import QAction, QIcon, QFont, QKeySequence

from core import Job, Sheet, Piece, optimize, save_job, load_job, load_zad_file, get_recent_jobs
from ui.job_tab import JobTab
from ui.sheets_tab import SheetsTab
from ui.pieces_tab import PiecesTab
from ui.cutplan_tab import CutPlanTab
from ui.costs_tab import CostsTab


JOBS_DIR = str(Path.home() / "ZCADPython" / "jobs")
APP_VERSION = "1.0.0"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file: str | None = None
        self.job = Job()
        self._dirty = False

        os.makedirs(JOBS_DIR, exist_ok=True)

        self.setWindowTitle("Z-CAD Python")
        self.setMinimumSize(1100, 750)
        self._restore_geometry()

        self._build_menu()
        self._build_toolbar()
        self._build_tabs()
        self._build_statusbar()

        self._refresh_all()

    # ── Geometry ──────────────────────────────────────────────────────────────
    def _restore_geometry(self):
        settings = QSettings("ZCADPython", "ZCADPython")
        geo = settings.value("geometry")
        if geo:
            self.restoreGeometry(geo)
        else:
            self.resize(1200, 800)

    def closeEvent(self, event):
        if self._dirty:
            r = QMessageBox.question(self, "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel)
            if r == QMessageBox.StandardButton.Save:
                self._save()
            elif r == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        settings = QSettings("ZCADPython", "ZCADPython")
        settings.setValue("geometry", self.saveGeometry())
        event.accept()

    # ── Menu ──────────────────────────────────────────────────────────────────
    def _build_menu(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("&File")
        self._add_action(file_menu, "&New Job", self._new_job, "Ctrl+N")
        self._add_action(file_menu, "&Open…", self._open, "Ctrl+O")
        file_menu.addSeparator()
        self._add_action(file_menu, "&Save", self._save, "Ctrl+S")
        self._add_action(file_menu, "Save &As…", self._save_as, "Ctrl+Shift+S")
        file_menu.addSeparator()
        self._add_action(file_menu, "Import Legacy .ZAD…", self._import_zad)
        file_menu.addSeparator()

        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Jobs")
        self._rebuild_recent_menu()
        file_menu.addSeparator()

        self._add_action(file_menu, "E&xport PDF…", self._export_pdf, "Ctrl+E")
        self._add_action(file_menu, "Export &CSV…", self._export_csv)
        file_menu.addSeparator()
        self._add_action(file_menu, "E&xit", self.close, "Ctrl+Q")

        # Optimize
        opt_menu = mb.addMenu("&Optimize")
        self._add_action(opt_menu, "▶  Run Optimization", self._run_optimize, "F5")
        self._add_action(opt_menu, "Clear Results", self._clear_results)

        # Help
        help_menu = mb.addMenu("&Help")
        self._add_action(help_menu, "About Z-CAD Python", self._about)

    def _add_action(self, menu, label, slot, shortcut=None):
        act = QAction(label, self)
        if shortcut:
            act.setShortcut(shortcut)
        act.triggered.connect(slot)
        menu.addAction(act)
        return act

    def _rebuild_recent_menu(self):
        self.recent_menu.clear()
        recent = get_recent_jobs(JOBS_DIR)
        if not recent:
            self.recent_menu.addAction("(no recent files)").setEnabled(False)
        for item in recent:
            act = QAction(f"{item['name']}  ({item['modified']})", self)
            act.setData(item["path"])
            act.triggered.connect(lambda checked, p=item["path"]: self._open_file(p))
            self.recent_menu.addAction(act)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(20, 20))

        def btn(label, slot, tip=""):
            act = QAction(label, self)
            act.setToolTip(tip)
            act.triggered.connect(slot)
            tb.addAction(act)
            return act

        btn("🆕 New", self._new_job, "New Job (Ctrl+N)")
        btn("📂 Open", self._open, "Open Job (Ctrl+O)")
        btn("💾 Save", self._save, "Save Job (Ctrl+S)")
        tb.addSeparator()
        btn("▶ Optimize", self._run_optimize, "Run Optimization (F5)")
        tb.addSeparator()
        btn("📄 PDF", self._export_pdf, "Export PDF")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.job_tab = JobTab(self)
        self.sheets_tab = SheetsTab(self)
        self.pieces_tab = PiecesTab(self)
        self.cutplan_tab = CutPlanTab(self)
        self.costs_tab = CostsTab(self)

        self.tabs.addTab(self.job_tab,     "📋  Job Info")
        self.tabs.addTab(self.sheets_tab,  "📐  Stock Sheets")
        self.tabs.addTab(self.pieces_tab,  "✂️   Pieces")
        self.tabs.addTab(self.cutplan_tab, "🗺️   Cut Plan")
        self.tabs.addTab(self.costs_tab,   "💶  Costs")

        self.setCentralWidget(self.tabs)

    # ── Status Bar ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        self.status = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status.addWidget(self.status_label)

    def set_status(self, msg: str):
        self.status_label.setText(msg)

    # ── Data flow ─────────────────────────────────────────────────────────────
    def mark_dirty(self):
        self._dirty = True
        title = f"Z-CAD Python — {self.job.name}"
        if self.current_file:
            title += f" [{Path(self.current_file).name}]"
        self.setWindowTitle(title + " *")

    def _refresh_all(self):
        self.job_tab.load_from_job(self.job)
        self.sheets_tab.load_from_job(self.job)
        self.pieces_tab.load_from_job(self.job)
        self.cutplan_tab.load_from_job(self.job)
        self.costs_tab.load_from_job(self.job)
        title = f"Z-CAD Python — {self.job.name}"
        if self.current_file:
            title += f" [{Path(self.current_file).name}]"
        self.setWindowTitle(title)
        self._dirty = False

    def collect_from_ui(self):
        """Pull current UI state into self.job before saving/optimizing."""
        self.job_tab.save_to_job(self.job)
        self.sheets_tab.save_to_job(self.job)
        self.pieces_tab.save_to_job(self.job)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _new_job(self):
        if self._dirty:
            r = QMessageBox.question(self, "Unsaved Changes",
                "Discard unsaved changes and start a new job?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                return
        self.job = Job()
        self.current_file = None
        self._refresh_all()
        self.set_status("New job created.")

    def _open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Job", JOBS_DIR, "Z-CAD Python jobs (*.zcad);;All files (*)"
        )
        if path:
            self._open_file(path)

    def _open_file(self, path: str):
        try:
            self.job = load_job(path)
            self.current_file = path
            self._refresh_all()
            self._rebuild_recent_menu()
            self.set_status(f"Opened: {Path(path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def _save(self):
        if not self.current_file:
            self._save_as()
            return
        self.collect_from_ui()
        try:
            save_job(self.job, self.current_file)
            self._dirty = False
            self.setWindowTitle(f"Z-CAD Python — {self.job.name} [{Path(self.current_file).name}]")
            self.set_status("Saved.")
            self._rebuild_recent_menu()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _save_as(self):
        self.collect_from_ui()
        default = str(Path(JOBS_DIR) / (self.job.name or "job"))
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Job As", default, "Z-CAD Python jobs (*.zcad)"
        )
        if path:
            if not path.endswith(".zcad"):
                path += ".zcad"
            self.current_file = path
            self._save()

    def _import_zad(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Z-CAD Job", "", "Z-CAD files (*.ZAD *.zad);;All files (*)"
        )
        if path:
            try:
                self.job = load_zad_file(path)
                self.current_file = None
                self._refresh_all()
                self.mark_dirty()
                self.set_status(f"Imported: {Path(path).name} — review and save as .zcad")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", str(e))

    def _run_optimize(self):
        self.collect_from_ui()
        if not self.job.sheets or not any(s.active and s.width > 0 for s in self.job.sheets):
            QMessageBox.warning(self, "No Sheets", "Add at least one active stock sheet first.")
            return
        if not self.job.pieces or not any(p.quantity > 0 and p.width > 0 for p in self.job.pieces):
            QMessageBox.warning(self, "No Pieces", "Add at least one piece with quantity > 0 first.")
            return

        self.set_status("Optimizing…")
        QApplication.processEvents()

        optimize(self.job)

        self.cutplan_tab.load_from_job(self.job)
        self.costs_tab.load_from_job(self.job)
        self.tabs.setCurrentWidget(self.cutplan_tab)

        msg = (f"Done: {self.job.total_pieces_placed}/{self.job.total_pieces_needed} pieces placed "
               f"on {self.job.sheets_used} sheet(s). "
               f"Efficiency: {self.job.overall_efficiency:.1f}%")
        if self.job.unplaced:
            msg += f"  ⚠ {len(self.job.unplaced)} piece(s) unplaced."
        self.set_status(msg)

    def _clear_results(self):
        self.job.layouts = []
        self.job.unplaced = []
        self.cutplan_tab.load_from_job(self.job)
        self.costs_tab.load_from_job(self.job)
        self.set_status("Results cleared.")

    def _export_pdf(self):
        if not self.job.layouts:
            QMessageBox.information(self, "No Results", "Run optimization first.")
            return
        default = str(Path(JOBS_DIR) / f"{self.job.name or 'job'}_cutplan.pdf")
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", default, "PDF files (*.pdf)")
        if path:
            try:
                from core.export_pdf import export_pdf
                export_pdf(self.job, path)
                self.set_status(f"PDF saved: {Path(path).name}")
                QMessageBox.information(self, "PDF Exported", f"Saved to:\n{path}")
            except ImportError:
                QMessageBox.critical(self, "Missing Library",
                    "PDF export requires 'reportlab'.\n\nInstall it with:\n  pip install reportlab")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def _export_csv(self):
        if not self.job.pieces:
            return
        self.collect_from_ui()
        default = str(Path(JOBS_DIR) / f"{self.job.name or 'job'}_pieces.csv")
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", default, "CSV files (*.csv)")
        if path:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["#", "Label", "Quantity", "Width (mm)", "Height (mm)", "Area (mm²)", "Can Rotate"])
                for i, p in enumerate(self.job.pieces):
                    if p.quantity > 0:
                        w.writerow([i+1, p.label, p.quantity, p.width, p.height, p.area,
                                    "Yes" if p.can_rotate else "No"])
            self.set_status(f"CSV saved: {Path(path).name}")

    def _about(self):
        QMessageBox.about(self, "About Z-CAD Python",
            f"<h2>Z-CAD Python v{APP_VERSION}</h2>"
            "<p>A modern rectangular cut optimization tool.</p>"
            "<p>Uses the <b>MaxRects</b> bin-packing algorithm for optimal yield.</p>"
            "<p>Inspired by the original Z-CAD 2.1d (German, ~2000).</p>"
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Z-CAD Python")
    app.setOrganizationName("ZCADPython")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Apply a clean stylesheet
    app.setStyleSheet("""
        QMainWindow { background: #f5f5f5; }
        QTabWidget::pane { border: 1px solid #cccccc; background: white; }
        QTabBar::tab { padding: 6px 16px; font-size: 10pt; }
        QTabBar::tab:selected { background: white; border-bottom: 2px solid #2d6a9f; font-weight: bold; }
        QGroupBox { font-weight: bold; border: 1px solid #cccccc; border-radius: 4px;
                    margin-top: 8px; padding-top: 8px; }
        QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
        QPushButton { padding: 5px 14px; border-radius: 4px;
                      border: 1px solid #aaaaaa; background: #ffffff; }
        QPushButton:hover { background: #e8f0fe; border-color: #2d6a9f; }
        QPushButton:pressed { background: #c8d8f0; }
        QPushButton#primary { background: #2d6a9f; color: white; border: none; font-weight: bold; }
        QPushButton#primary:hover { background: #1a5276; }
        QTableWidget { gridline-color: #e0e0e0; selection-background-color: #cce0ff; }
        QHeaderView::section { background: #f0f4f8; padding: 4px; border: 1px solid #ddd;
                               font-weight: bold; }
        QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
            border: 1px solid #cccccc; border-radius: 3px; padding: 3px; }
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #2d6a9f; }
        QStatusBar { background: #f0f4f8; border-top: 1px solid #cccccc; }
        QToolBar { background: #f0f4f8; border-bottom: 1px solid #cccccc; spacing: 4px; }
    """)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
