# This file contains all the code for running the main window

from PySide6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from app.ui_main import Ui_MainWindow

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