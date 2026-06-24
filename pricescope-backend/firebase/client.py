import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

_db = None


def init_firebase():
    """
    Initializes Firebase using credentials from an environment variable.
    On Render: set FIREBASE_CREDENTIALS_JSON as an env var containing the
    full contents of your Firebase service account JSON key file.
    """
    global _db
    if _db is not None:
        return _db

    if firebase_admin._apps:
        _db = firestore.client()
        return _db

    cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if not cred_json:
        raise RuntimeError(
            "FIREBASE_CREDENTIALS_JSON env var not set. "
            "Paste your Firebase service account JSON as this env var on Render."
        )

    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db


def get_db():
    if _db is None:
        return init_firebase()
    return _db
