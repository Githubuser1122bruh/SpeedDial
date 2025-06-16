from PyQt6.QtCore import QThread, pyqtSignal
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleOAuthThread(QThread):
    finished = pyqtSignal(str)

    def run(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                scopes=["openid", "email"]
            )
            creds = flow.run_local_server(port=8080)
            self.finished.emit(creds.id_token)
        except Exception as e:
            print("OAuth failed:", e)
            self.finished.emit("")