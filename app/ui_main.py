import os
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit
from PySide6.QtGui import QGuiApplication, QImage, QPixmap
from PySide6.QtCore import Qt 
import random
import sqlite3
from cryptography.fernet import Fernet
import socket
import threading
from app import serverside
import socketio

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
style_path = os.path.join(base_dir, "assets", "logo.png")

host_ip = "192.168.1.11"

from app.fernetkeygen import key

def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

class Ui_MainWindow:
    def setupUi(self, MainWindow):
        screen = QGuiApplication.primaryScreen().geometry()
        MainWindow.move((screen.width() - MainWindow.width()) // 2, (screen.height() - MainWindow.height()) // 2)
        MainWindow.resize(screen.width() - 50, screen.height() - 100)
        MainWindow.setWindowTitle("SpeedDial V1")

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        self.main_layout = QVBoxLayout(self.centralwidget)

        self.top_bar_layout = QHBoxLayout()
        self.logo_layout = QVBoxLayout()
        self.logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(150, 150)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_layout.addWidget(self.logo_label)

        self.version1namelabel = QLabel("V1 SpeedDial")
        self.version1namelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_layout.addWidget(self.version1namelabel)

        self.top_bar_layout.addStretch()
        self.top_bar_layout.addLayout(self.logo_layout)
        self.main_layout.addLayout(self.top_bar_layout)

        image = QImage(style_path)
        self.logo_label.setPixmap(QPixmap.fromImage(image).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)) if not image.isNull() else self.logo_label.setText("Failed to load image")

        self.button = QPushButton("New Meeting")
        self.joinbutton = QPushButton("Join Meeting")
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.joinbutton)
        self.main_layout.setAlignment(self.button, Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setAlignment(self.joinbutton, Qt.AlignmentFlag.AlignCenter)
        self.button.clicked.connect(self.makenewmeeting)
        self.joinbutton.clicked.connect(self.joinmeeting)

    def makenewmeeting(self):
        self.new_meeting_window = QMainWindow()
        self.newmeeting = meeting()
        self.newmeeting.setupMeeting(self.new_meeting_window)
        self.new_meeting_window.show()

    def joinmeeting(self):
        self.newDialogue = QMainWindow()
        self.meetingDialogue = joinmeetingdialog()
        self.meetingDialogue.dialogue(self.newDialogue)
        self.newDialogue.show()

class meeting():
    def setupMeeting(self, MainWindow):
        MainWindow.setWindowTitle("Meeting")
        screen = QGuiApplication.primaryScreen().geometry()
        MainWindow.resize(screen.width() - 50, screen.height() - 100)


        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id TEXT UNIQUE,
                passcode TEXT,
                port INTEGER
            )
        """)
        conn.commit()

        meeting_id, passcode = self.generate_unique_meeting(cursor)
        encrypted_id = encrypt_data(meeting_id)
        encrypted_passcode = encrypt_data(passcode)

        port = get_free_port()
        cursor.execute("INSERT INTO meetings (meeting_id, passcode, port) VALUES (?, ?, ?)",
                            (encrypted_id, encrypted_passcode, port))
        conn.commit()
        conn.close()

        threading.Thread(target=serverside.start_server, args=(port,), daemon=True).start()

        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        self.main_layout = QVBoxLayout(self.centralwidget)

        self.top_bar_widget = QWidget()
        self.top_bar_widget.setFixedHeight(60)
        self.top_bar_widget.setStyleSheet("background-color: #2c3e50;")
        self.top_bar_layout = QHBoxLayout(self.top_bar_widget)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(30, 30)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image = QImage(style_path)
        self.logo_label.setPixmap(QPixmap.fromImage(image).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)) if not image.isNull() else self.logo_label.setText("Logo")
        self.top_bar_layout.addWidget(self.logo_label)

        self.id_label = QLabel(f"Meeting ID: {meeting_id}")
        self.id_label.setStyleSheet("color: white; font-size: 16px;")
        self.top_bar_layout.addWidget(self.id_label)

        self.passcodelabel = QLabel(f"Passcode: {passcode}")
        self.passcodelabel.setStyleSheet("color: white; font-size: 16px;")
        self.top_bar_layout.addWidget(self.passcodelabel)

        self.main_layout.addWidget(self.top_bar_widget)
        self.main_layout.addStretch(1)

        self.button_h_layout = QHBoxLayout()
        self.close_button = QPushButton("Close Meeting")
        self.close_button.setFixedSize(80, 20)
        self.close_button.clicked.connect(MainWindow.close)
        self.button_h_layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        self.button_h_layout.addStretch(1)
        self.main_layout.addLayout(self.button_h_layout)

    def generate_unique_meeting(self, cursor):
        while True:
            meeting_id = str(random.randint(100000, 999999))
            passcode = str(random.randint(1000, 9999))
            cursor.execute("SELECT * FROM meetings WHERE meeting_id = ?", (encrypt_data(meeting_id),))
            if cursor.fetchone() is None:
                return meeting_id, passcode

def encrypt_data(data):
    return key.encrypt(str(data).encode()).decode()

def decrypt_data(data):
    return key.decrypt(data.encode()).decode()

class joinmeetingdialog():
    def dialogue(self, MainWindow):
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        MainWindow.setWindowTitle("Join Meeting")
        MainWindow.resize(400, 600)

        self.requestedid = ""
        self.requestedpasscode = ""

        self.id_label = QLabel("Input meeting ID")
        self.inputidbox = QLineEdit()
        self.inputidbox.setPlaceholderText("e.g., 101010")
        self.inputidbox.setClearButtonEnabled(True)

        self.passcode_label = QLabel("Input meeting password")
        self.inputpasswordbox = QLineEdit()
        self.inputpasswordbox.setPlaceholderText("e.g., 1010")
        self.inputpasswordbox.setClearButtonEnabled(True)

        self.confirmbutton = QPushButton("Join Meeting")
        self.confirmedornotlabel = QLabel("")

        self.main_layout.addWidget(self.id_label)
        self.main_layout.addWidget(self.inputidbox)
        self.main_layout.addWidget(self.passcode_label)
        self.main_layout.addWidget(self.inputpasswordbox)
        self.main_layout.addWidget(self.confirmbutton)
        self.main_layout.addWidget(self.confirmedornotlabel)

        central_widget = QWidget(MainWindow)
        central_widget.setLayout(self.main_layout)
        MainWindow.setCentralWidget(central_widget)
        self.confirmbutton.clicked.connect(self.onclickconfirm)
        self.confirmbutton.setProperty("class", "confirmbutton")

    def onclickconfirm(self, status):
        conn = sqlite3.connect("meetings.db")
        cursor = conn.cursor()
        cursor.execute("SELECT meeting_id, passcode FROM meetings")
        rows = cursor.fetchall()
        self.requestedid = self.inputidbox.text()
        self.requestedpasscode = self.inputpasswordbox.text()
        conn.close()
        print(f"ID: {self.requestedid} Passcode: {self.requestedpasscode}")
        for encrypted_id, encrypted_pass in rows:
            decrypted_id = decrypt_data(encrypted_id)
            decrypted_pass = decrypt_data(encrypted_pass)
            if self.requestedid == decrypted_id and self.requestedpasscode == decrypted_pass:
                self.connect_meeting(confirmornot=True)
                return

        self.confirmedornotlabel.setText("Invalid meeting ID or passcode")

    def connect_meeting(self, confirmornot):
        if confirmornot:
            conn = sqlite3.connect("meetings.db")
            cursor = conn.cursor()
            cursor.execute("SELECT passcode, port FROM meetings WHERE meeting_id = ?", (self.requestedid,))
            row = cursor.fetchone()
            conn.close()

            if row:
                stored_passcode_encrypted, port = row
                stored_passcode = decrypt_data(stored_passcode_encrypted)

                if stored_passcode == self.requestedpasscode: 
                    self.sio = socketio.Client()
                    host_ip = "192.168.1.11" 

                    try:
                        self.sio.connect(f"http://{host_ip}:{port}")
                        print("Connected user to port")
                        self.sio.emit("join", {
                            "room": self.requestedid,
                            "peer_id": "client_" + self.requestedid
                        })
                    except Exception as e:
                        print("Connection failed:", e)
                        self.confirmedornotlabel.setText("Failed to connect")