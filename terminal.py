import requests
import os
from dotenv import load_dotenv

load_dotenv('.vscode/.env')
url = os.getenv("TERMINAL_WEBHOOK_URL")

while True:
    text = input("$ ")
    requests.post(url, {"content": text})