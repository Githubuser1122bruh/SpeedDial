 # Running this effectively runs everything

import os
import sys
from PySide6.QtWidgets import QApplication
import threading
from app.main_window import MainWindow, loginDialog
import app.serverside

def main():
    app = QApplication(sys.argv)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    style_path = os.path.join(base_dir, "app", "resources", "style.qss")
    with open(style_path, "r") as file:
        app.setStyleSheet(file.read())

    login = loginDialog()
    if login.exec() != login.accepted:
        sys.exit()

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()