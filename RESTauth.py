import requests
from urllib.parse import urlencode
from google_auth_oauthlib.flow import InstalledAppFlow

API_KEY = "AIzaSyC_0wIiqOtmnznlm75oDUzdrIqMvgPfGJE"

from auth_thread import GoogleOAuthThread  # or from .auth_thread if inside module

def start_google_sign_in(self):
    self.oauth_thread = GoogleOAuthThread()
    self.oauth_thread.finished.connect(self.on_google_login_success)
    self.oauth_thread.start()

def on_google_login_success(self, id_token):
    if id_token:
        print("Got token, continuing with Firebase auth...")
        from RESTauth import firebase_google_sign_in
        result = firebase_google_sign_in(id_token)
        print(result)
    else:
        print("Google sign-in was cancelled or failed.")

def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Signed in failed:", response.json())
        return None

def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Signed up successfully!")
        return response.json()
    else:
        print("Sign up failed:", response.json())
        return None

def firebase_google_sign_in(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={API_KEY}"
    post_body = urlencode({
        "id_token": id_token,
        "providerId": "google.com"
    })

    payload = {
        "postBody": post_body,
        "requestUri": "http://localhost",
        "returnSecureToken": True
    }

    res = requests.post(url, json=payload)
    if res.status_code == 200:
        result = res.json()
        print("Signed in as:", result.get("email"))
        return result
    else:
        print("Google sign-in failed:", res.json())
        return None
    
def get_google_oauth_token():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        scopes=["openid", "email"]
    )
    creds = flow.run_local_server(port=8080)
    return creds.id_token