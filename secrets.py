import os

TOKEN = os.environ.get("GCB_TOKEN")
TEST_TOKEN = os.environ.get("GCB_TEST_TOKEN")
MONGO_TOKEN = os.environ.get("GCB_DB_TOKEN")
CLIENT_ID = os.environ.get("GCB_CLIENT_ID")
REDDIT_INFO = {
    "client_id": os.environ.get("GCB_REDDIT_CLIENT_ID"),
    "client_secret": os.environ.get("GCB_REDDIT_CLIENT_SECRET"),
    "password": os.environ.get("GCB_REDDIT_PASSWORD"),
    "user_agent": os.environ.get("GCB_REDDIT_USER_AGENT"),
    "username": os.environ.get("GCB_REDDIT_USERNAME"),
}