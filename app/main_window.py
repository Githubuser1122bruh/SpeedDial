# This file contains all the code for running the main window

from PySide6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, QDialog
from PySide6.QtGui import QColor
from app.ui_main import Ui_MainWindow
from app.ui_main import loginDialog

class MainWindow(QMainWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(5, 5)
        shadow.setColor(QColor(0, 0, 0, 160))

        self.ui.button.setGraphicsEffect(shadow)
    def show_login(self):
        login = loginDialog()
        if login.exec() == QDialog.Accepted:
            self.user_info = login.user_info
            print("Authenticated user token:", self.user_info.get("id_token"))
            self.load_user_info()
            self.show()
        else:
            print("Login cancelled or failed")

    def load_user_info(self):
        # Add logic to update UI with new user_info if needed
        print("User info loaded:", self.user_info)