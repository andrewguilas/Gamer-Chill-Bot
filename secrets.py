import os

TOKEN = os.getenv("GCB_TOKEN")
TEST_TOKEN = os.getenv("GCB_TEST_TOKEN")
MONGO_TOKEN = os.getenv("GCB_DB_TOKEN")
CLIENT_ID = os.getenv("GCB_CLIENT_ID")
REDDIT_INFO = {
    "client_id": os.getenv("GCB_REDDIT_CLIENT_ID"),
    "client_secret": os.getenv("GCB_REDDIT_CLIENT_SECRET"),
    "password": os.getenv("GCB_REDDIT_PASSWORD"),
    "user_agent": os.getenv("GCB_REDDIT_USER_AGENT"),
    "username": os.getenv("GCB_REDDIT_USERNAME"),
}

print("---------- ENV VARS ----------")
print(TOKEN)
print(TEST_TOKEN)
print(MONGO_TOKEN)
print(CLIENT_ID)
print(REDDIT_INFO)
print("------------------------------")