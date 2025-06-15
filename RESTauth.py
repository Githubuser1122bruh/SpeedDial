import requests

API_KEY = "AIzaSyC_0wIiqOtmnznlm75oDUzdrIqMvgPfGJE" # server url auth key, safe to share

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
