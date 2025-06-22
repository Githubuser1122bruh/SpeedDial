import os
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv

load_dotenv()

cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
if not cred_path:
    raise ValueError("FIREBASE_CREDENTIAL_PATH not set in environment variables")

cred = credentials.Certificate(cred_path)
initialize_app(cred)

db = firestore.client()
