import os
import sys
from PySide6.QtWidgets import QApplication, QDialog
from app.main_window import MainWindow, loginDialog

def main():
    app = QApplication(sys.argv)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    style_path = os.path.join(base_dir, "app", "resources", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as file:
            app.setStyleSheet(file.read())

    print("Opening login dialog...")
    login = loginDialog()
    result = login.exec()
    print(f"Login dialog result: {result} (Accepted={QDialog.Accepted})")

    if result == QDialog.Accepted:
        print("Login accepted, showing main window...")
        user_info = login.user_info
        main_window = MainWindow(user_info)
        main_window.show()
        sys.exit(app.exec())
    else:
        print("Login cancelled, exiting application.")
        sys.exit()

if __name__ == "__main__":
    main()