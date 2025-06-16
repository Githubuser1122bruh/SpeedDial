from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"]
)
creds = flow.run_local_server(port=8081)
print("Token:", creds.id_token)