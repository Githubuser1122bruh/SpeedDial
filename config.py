import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "app", "speeddialkey.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)