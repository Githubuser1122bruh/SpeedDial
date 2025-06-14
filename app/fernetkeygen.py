from cryptography.fernet import Fernet
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
key_path = os.path.join(base_dir, "secret.key")

def gen_key():
    if os.path.exists(key_path):
        with open(key_path, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
        return key

key = Fernet(gen_key())