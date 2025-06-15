# This file contains all the code for running the main window

from PySide6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, QDialog
from PySide6.QtGui import QColor
from app.ui_main import Ui_MainWindow
from app.ui_main import loginDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
            self.user_token = login.token
            print("Authenticated user token:", self.user_token)
        else:
            print("Login cancelled or failed")