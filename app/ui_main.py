import os
import firebase_admin
from firebase_admin import credentials, firestore
from PySide6.QtWidgets import QMainWindow, QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit
from PySide6.QtGui import QGuiApplication, QImage, QPixmap
from PySide6.QtCore import Qt 
import random
import sqlite3
import socket
import threading
import socketio
from app import serverside
from app.fernetkeygen import key
from RESTauth import sign_in, get_google_oauth_token, firebase_google_sign_in

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
style_path = os.path.join(base_dir, "assets", "logo.png")

cred = credentials.Certificate(os.path.join(base_dir, "app/speeddial-f2572-firebase-adminsdk-fbsvc-19fdde59c7.json"))
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print("IP found")
        return ip
    except Exception:
        print("IP couldnt be found, reverting to fallback IP")
        return "127.0.0.1"

host_ip = get_local_ip() # changed to the users local ip

def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def encrypt_data(data):
    return key.encrypt(str(data).encode()).decode()

def decrypt_data(data):
    return key.decrypt(data.encode()).decode()

class loginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(300, 300)
        self.user_info = None
        self.token = None

        layout = QVBoxLayout()

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        self.google_login_btn = QPushButton("Sign in with Google")
        self.google_login_btn.clicked.connect(self.handle_google_signin)
        layout.addWidget(self.google_login_btn)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_google_signin(self):
        try:
            id_token = get_google_oauth_token()
            credentials = firebase_google_sign_in(id_token)
            if credentials:
                print("Google Sign-In successful!")
                self.user_info = {
                    "uid": credentials.get("localId"),
                    "id_token": credentials.get("idToken"),
                    "email": credentials.get("email")
                }
                self.token = credentials["idToken"]
                self.on_login_success()
                self.accept()
            else:
                print("Google Sign-In failed.")
                self.status_label.setText("Google Sign-In failed.")
        except Exception as e:
            print(f"Error during Google Sign-In: {e}")
            self.status_label.setText("Error during Google Sign-In")

    def attempt_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        credentials = sign_in(email, password)
        if not credentials:
            print("Login failed, attempting to register...")
            sign_up_result = sign_up(email, password)
            if sign_up_result:
                print("Registration successful, trying login again...")
                credentials = sign_in(email, password)

        if credentials:
            self.user_info = {
                "uid": credentials.get("localId"),
                "id_token": credentials.get("idToken"),
                "email": credentials.get("email")
            }
            self.token = credentials["idToken"]
            self.status_label.setText("Login successful")
            self.on_login_success()
            self.accept()
        else:
            self.status_label.setText("Login/Registration failed, try again.")

    def on_login_success(self):
        print("User successfully logged in!")
        print(f"UID: {self.user_info.get('uid')}")
        print(f"Email: {self.user_info.get('email')}")
        print(f"Token: {self.user_info.get('id_token')[:20]}...")
        self.status_label.setText("Login success!\nWelcome: " + self.user_info.get("email"))
        
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
        if not image.isNull():
            self.logo_label.setPixmap(QPixmap.fromImage(image).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("Failed to load image")

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
        self.newDialog = QMainWindow()
        self.meetingDialog = joinmeetingdialog()
        self.meetingDialog.Dialog(self.newDialog)
        self.newDialog.show()

class meeting():
    def setupMeeting(self, MainWindow):
        MainWindow.setWindowTitle("Meeting")
        screen = QGuiApplication.primaryScreen().geometry()
        MainWindow.resize(screen.width() - 50, screen.height() - 100)

        meeting_id, passcode = self.generate_unique_meeting()
        encrypted_id = encrypt_data(meeting_id)
        encrypted_passcode = encrypt_data(passcode)
        port = get_free_port()
        doc_ref = db.collection("meetings").add({
            "meeting_id": encrypted_id,
            "passcode": encrypted_passcode,
            "port": port
        })[1]
        self.firestore_doc = doc_ref

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
        if not image.isNull():
            self.logo_label.setPixmap(QPixmap.fromImage(image).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("Logo")
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

        self.shutdown_event = threading.Event()
        self.server_thread = threading.Thread(target=serverside.start_server, args=(port, self.shutdown_event), daemon=True)
        self.server_thread.start()

        self.MainWindow = MainWindow
        self.MainWindow.closeEvent = self.on_close

    def generate_unique_meeting(self):
        while True:
            meeting_id = str(random.randint(100000, 999999))
            passcode = str(random.randint(1000, 9999))
            encrypted_id = encrypt_data(meeting_id)
            docs = db.collection("meetings").where("meeting_id", "==", encrypted_id).stream()
            if not any(docs):
                return meeting_id, passcode

    def on_close(self, event):
        self.shutdown_event.set()
        self.server_thread.join()
        event.accept()
        if hasattr(self, "firestore_doc"):
            try:
                self.firestore_doc.delete()
                print("Firestore meeting deleted!")
            except Exception as e:
                print(f"Failed to delete doc: {e}")

class joinmeetingdialog():
    def Dialog(self, MainWindow):
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

    def onclickconfirm(self, status=None):
        docs = db.collection("meetings").stream()
        rows = [(doc.to_dict()["meeting_id"], doc.to_dict()["passcode"]) for doc in docs]
        self.requestedid = self.inputidbox.text().strip()
        self.requestedpasscode = self.inputpasswordbox.text().strip()
        print(f"ID: {self.requestedid} Passcode: {self.requestedpasscode}")
        for encrypted_id, encrypted_pass in rows:
            try:
                decrypted_id = decrypt_data(encrypted_id).strip()
                decrypted_pass = decrypt_data(encrypted_pass).strip()
                if self.requestedid == decrypted_id and self.requestedpasscode == decrypted_pass:
                    print("Match found! Connecting to meeting...")
                    self.connect_meeting(confirmornot=True)
                    return
            except Exception as e:
                print(f"Decryption error: {e}")

        self.confirmedornotlabel.setText("Invalid meeting ID or passcode")

    def connect_meeting(self, confirmornot):
        if confirmornot:
            encrypted_id = encrypt_data(self.requestedid)
            docs = db.collection("meetings").where("meeting_id", "==", encrypted_id).stream()
            row = next(docs, None)
            if row:
                data = row.to_dict()
                stored_passcode_encrypted = data["passcode"]
                port = data["port"]
                stored_passcode = decrypt_data(stored_passcode_encrypted).strip()

                if stored_passcode == self.requestedpasscode:
                    self.sio = socketio.Client(logger=True, engineio_logger=True)

                    @self.sio.event
                    def connect():
                        print("[Client] Connected to server")

                    @self.sio.event
                    def connect_error(data):
                        print(f"[Client] Connection failed: {data}")

                    @self.sio.event
                    def disconnect():
                        print("[Client] Disconnected from server")

                    try:
                        print(f"[Client] Trying to connect to http://{host_ip}:{port}")
                        self.sio.connect(f"http://{host_ip}:{port}")
                        print("[Client] Connected, emitting join event")
                        self.sio.emit("join", {
                            "room": self.requestedid,
                            "peer_id": "client_" + self.requestedid
                        })
                    except Exception as e:
                        print(f"[Client] Exception during connection or emit: {e}")
                        self.confirmedornotlabel.setText("Failed to connect")
                else:
                    self.confirmedornotlabel.setText("Incorrect passcode")
            else:
                self.confirmedornotlabel.setText("Meeting not found")