"""Initializes firestore client."""
import os

import firebase_admin
from firebase_admin import credentials, firestore


def initialize_firebase_app():
    """
    Pulls in the token and initializes the firebase authentication.
    """
    temp_file_path = "temp_firebase.json"
    with open(temp_file_path, "w+") as temp_file:
        temp_file.write(os.environ["FIREBASE_JSON"])
    cred = credentials.Certificate(temp_file_path)
    os.remove(temp_file_path)
    firebase_admin.initialize_app(cred)


def get_firestore_client():
    """
    Returns a firestore client. Initializes the firebase app if necessary.
    """
    if not firebase_admin._apps:  # pylint: disable=protected-access
        initialize_firebase_app()

    return firestore.client()


firestore_client = get_firestore_client()
