import firebase_admin
from firebase_admin import credentials, db
import json

cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://salonandspa-7b832-default-rtdb.firebaseio.com"
    }
)

ref = db.reference("/")

data = ref.get()

print(json.dumps(data, indent=2))