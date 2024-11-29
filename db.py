import certifi
from pymongo.mongo_client import MongoClient

# UNIFORM RESOURCE IDENTIFIER
# SSL - Secure Sockets Layer
# TLS - Transport  Layer Security
uri = "mongodb+srv://pvalluri:yerukam09@cluster0.3g5covl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def get_client() -> MongoClient:
    client = MongoClient(uri, tlsCAFile=certifi.where())
    try:
        client.admin.command("ping")
        return client
    except Exception as e:
        print(e)
