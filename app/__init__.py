from PySide6.QtWidgets import QApplication
import sys

def create_app():
    app = QApplication(sys.argv)
    return app

from .main_window import MainWindow

__all__ = ["create_app", "MainWindow"]