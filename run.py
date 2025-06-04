# Running this effectively runs everything

import os
import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    print(base_dir)
    style_path = os.path.join(base_dir, "app", "resources", "style.qss")
    with open(style_path, "r") as file:
        app.setStyleSheet(file.read())

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()