"""
SynCAD — Main Application Window
"""
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QLabel,
    QMessageBox, QFileDialog, QApplication
)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import QAction
import csv

from version import APP_NAME, APP_VERSION, WINDOW_TITLE, APP_AUTHOR, APP_DESCRIPTION
from core import Job, optimize, save_job, load_job, load_zad_file, get_recent_jobs
from core.persistence import DEFAULT_JOBS_DIR
from ui.job_tab import JobTab
from ui.sheets_tab import SheetsTab
from ui.pieces_tab import PiecesTab
from ui.cutplan_tab import CutPlanTab
from ui.costs_tab import CostsTab

JOBS_DIR = str(DEFAULT_JOBS_DIR)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file: str | None = None
        self.job = Job()
        self._dirty = False

        os.makedirs(JOBS_DIR, exist_ok=True)

        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(1100, 750)
        self._restore_geometry()

        self._build_menu()
        self._build_toolbar()
        self._build_tabs()
        self._build_statusbar()
        self._refresh_all()

    # ── Geometry ──────────────────────────────────────────────────────────────
    def _restore_geometry(self):
        settings = QSettings(APP_AUTHOR, APP_NAME)
        geo = settings.value("geometry")
        if geo:
            self.restoreGeometry(geo)
        else:
            self.resize(1240, 820)

    def closeEvent(self, event):
        if self._dirty:
            r = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
            )
            if r == QMessageBox.StandardButton.Save:
                self._save()
            elif r == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        settings = QSettings(APP_AUTHOR, APP_NAME)
        settings.setValue("geometry", self.saveGeometry())
        event.accept()

    # ── Menu ──────────────────────────────────────────────────────────────────
    def _build_menu(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("&File")
        self._action(file_menu, "&New Job",
                     self._new_job,    "Ctrl+N")
        self._action(file_menu, "&Open…",
                     self._open,       "Ctrl+O")
        file_menu.addSeparator()
        self._action(file_menu, "&Save",
                     self._save,       "Ctrl+S")
        self._action(file_menu, "Save &As…",
                     self._save_as,    "Ctrl+Shift+S")
        file_menu.addSeparator()
        self._action(file_menu, "Import Legacy .ZAD…", self._import_zad)
        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu("Recent Jobs")
        self._rebuild_recent_menu()
        file_menu.addSeparator()
        self._action(file_menu, "Export &PDF…",
                     self._export_pdf, "Ctrl+E")
        self._action(file_menu, "Export &CSV…",        self._export_csv)
        file_menu.addSeparator()
        self._action(file_menu, "E&xit",
                     self.close,       "Ctrl+Q")

        # Optimise
        opt_menu = mb.addMenu("&Optimise")
        self._action(opt_menu, "▶  Run Optimisation",
                     self._run_optimize, "F5")
        self._action(opt_menu, "Clear Results",         self._clear_results)

        # Help
        help_menu = mb.addMenu("&Help")
        self._action(help_menu, f"About {APP_NAME}", self._about)

    def _action(self, menu, label, slot, shortcut=None):
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
            return
        for item in recent:
            act = QAction(f"{item['name']}  ({item['modified']})", self)
            act.triggered.connect(
                lambda checked, p=item["path"]: self._open_file(p))
            self.recent_menu.addAction(act)

    # ── Toolbar ───────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))

        def btn(label, slot, tip=""):
            act = QAction(label, self)
            act.setToolTip(tip)
            act.triggered.connect(slot)
            tb.addAction(act)

        btn("🆕  New",      self._new_job,      "New Job  (Ctrl+N)")
        btn("📂  Open",     self._open,         "Open Job  (Ctrl+O)")
        btn("💾  Save",     self._save,         "Save Job  (Ctrl+S)")
        tb.addSeparator()
        btn("▶  Optimise", self._run_optimize, "Run Optimisation  (F5)")
        tb.addSeparator()
        btn("📄  PDF",      self._export_pdf,   "Export PDF  (Ctrl+E)")

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
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)

    def set_status(self, msg: str):
        self.status_label.setText(msg)

    # ── Data Flow ─────────────────────────────────────────────────────────────
    def mark_dirty(self):
        self._dirty = True
        self._update_title(dirty=True)

    def _update_title(self, dirty=False):
        base = f"{APP_NAME} — {self.job.name}"
        if self.current_file:
            base += f"  [{Path(self.current_file).name}]"
        self.setWindowTitle(base + (" *" if dirty else ""))

    def _refresh_all(self):
        self.job_tab.load_from_job(self.job)
        self.sheets_tab.load_from_job(self.job)
        self.pieces_tab.load_from_job(self.job)
        self.cutplan_tab.load_from_job(self.job)
        self.costs_tab.load_from_job(self.job)
        self._update_title()
        self._dirty = False

    def collect_from_ui(self):
        """Pull current UI state into self.job before saving / optimising."""
        self.job_tab.save_to_job(self.job)
        self.sheets_tab.save_to_job(self.job)
        self.pieces_tab.save_to_job(self.job)

    # ── File Actions ──────────────────────────────────────────────────────────
    def _new_job(self):
        if self._dirty:
            r = QMessageBox.question(
                self, "Unsaved Changes",
                "Discard unsaved changes and start a new job?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if r != QMessageBox.StandardButton.Yes:
                return
        self.job = Job()
        self.current_file = None
        self._refresh_all()
        self.set_status("New job created.")

    def _open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Job", JOBS_DIR,
            "SynCAD jobs (*.zcad);;All files (*)",
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
            QMessageBox.critical(self, "Error opening file", str(e))

    def _save(self):
        if not self.current_file:
            self._save_as()
            return
        self.collect_from_ui()
        try:
            save_job(self.job, self.current_file)
            self._dirty = False
            self._update_title()
            self._rebuild_recent_menu()
            self.set_status(f"Saved — {Path(self.current_file).name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _save_as(self):
        self.collect_from_ui()
        default = str(Path(JOBS_DIR) / (self.job.name or "job"))
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Job As", default,
            "SynCAD jobs (*.zcad)",
        )
        if path:
            if not path.endswith(".zcad"):
                path += ".zcad"
            self.current_file = path
            self._save()

    def _import_zad(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Z-CAD Job", "",
            "Z-CAD files (*.ZAD *.zad);;All files (*)",
        )
        if path:
            try:
                self.job = load_zad_file(path)
                self.current_file = None
                self._refresh_all()
                self.mark_dirty()
                self.set_status(
                    f"Imported: {Path(path).name} — save as .zcad to keep changes."
                )
            except Exception as e:
                QMessageBox.critical(self, "Import Error", str(e))

    # ── Optimise ──────────────────────────────────────────────────────────────
    def _run_optimize(self):
        self.collect_from_ui()

        if not any(s.active and s.width > 0 for s in self.job.sheets):
            QMessageBox.warning(self, "No Sheets",
                                "Add at least one active stock sheet before optimising.")
            return
        if not any(p.quantity > 0 and p.width > 0 for p in self.job.pieces):
            QMessageBox.warning(self, "No Pieces",
                                "Add at least one piece with a quantity > 0 before optimising.")
            return

        self.set_status("Optimising…")
        QApplication.processEvents()

        optimize(self.job)

        self.cutplan_tab.load_from_job(self.job)
        self.costs_tab.load_from_job(self.job)
        self.tabs.setCurrentWidget(self.cutplan_tab)

        placed = self.job.total_pieces_placed
        needed = self.job.total_pieces_needed
        eff = self.job.overall_efficiency
        unplaced = len(self.job.unplaced)

        msg = (f"Done — {placed}/{needed} pieces placed on "
               f"{self.job.sheets_used} sheet(s)  |  "
               f"Efficiency: {eff:.1f}%")
        if unplaced:
            msg += f"  ⚠  {unplaced} piece(s) unplaced — add more sheets."
        self.set_status(msg)

    def _clear_results(self):
        self.job.layouts = []
        self.job.unplaced = []
        self.cutplan_tab.load_from_job(self.job)
        self.costs_tab.load_from_job(self.job)
        self.set_status("Results cleared.")

    # ── Export ────────────────────────────────────────────────────────────────
    def _export_pdf(self):
        if not self.job.layouts:
            QMessageBox.information(self, "No Results",
                                    "Run optimisation first, then export.")
            return
        default = str(Path(JOBS_DIR) / f"{self.job.name or 'job'}_cutplan.pdf")
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", default, "PDF files (*.pdf)"
        )
        if path:
            try:
                from core.export_pdf import export_pdf
                export_pdf(self.job, path)
                self.set_status(f"PDF saved — {Path(path).name}")
                QMessageBox.information(
                    self, "PDF Exported", f"Saved to:\n{path}")
            except ImportError:
                QMessageBox.critical(self, "Missing Library",
                                     "PDF export requires 'reportlab'.\n\n"
                                     "Install it with:\n    pip install reportlab")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def _export_csv(self):
        if not self.job.pieces:
            return
        self.collect_from_ui()
        default = str(Path(JOBS_DIR) / f"{self.job.name or 'job'}_pieces.csv")
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Piece List CSV", default, "CSV files (*.csv)"
        )
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["#", "Label", "Qty", "Width (mm)", "Height (mm)",
                            "Area (mm²)", "Can Rotate"])
                for i, p in enumerate(self.job.pieces):
                    if p.quantity > 0:
                        w.writerow([i + 1, p.label, p.quantity,
                                    p.width, p.height, p.area,
                                    "Yes" if p.can_rotate else "No"])
            self.set_status(f"CSV saved — {Path(path).name}")

    # ── About ─────────────────────────────────────────────────────────────────
    def _about(self):
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<h2>{APP_NAME} v{APP_VERSION}</h2>"
            f"<p>{APP_DESCRIPTION}</p>"
            "<p>Uses the <b>MaxRects BSSF</b> bin-packing algorithm "
            "for optimal material yield.</p>"
            "<p>Supports import of legacy <b>Z-CAD 2.1d</b> (.ZAD) files.</p>",
        )
