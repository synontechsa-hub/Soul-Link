"""
SynCAD — Application Bootstrap
Creates the QApplication, loads stylesheet, launches main window.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from version import APP_NAME, APP_AUTHOR
from ui.main_window import MainWindow

STYLE_PATH = Path(__file__).parent.parent / "assets" / "style.qss"


def load_stylesheet() -> str:
    if STYLE_PATH.exists():
        return STYLE_PATH.read_text(encoding="utf-8")
    return ""


def launch() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_AUTHOR)

    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(load_stylesheet())

    win = MainWindow()
    win.show()
    return app.exec()
