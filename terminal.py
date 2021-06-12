TERMINAL_WEBHOOK_URL = "https://discord.com/api/webhooks/853323956655620116/W2gWIeA_xvIye5aalHYAsDWfGG6uTWQLbCk6AJdLXXeh9F61BQjENey25fXLcqXxyozv"

import requests

while True:
    text = input("$ ")
    requests.post(TERMINAL_WEBHOOK_URL, {"content": text})