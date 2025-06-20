import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "app", "speeddial-f2572-firebase-adminsdk-fbsvc-19fdde59c7.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)