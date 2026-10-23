# backend/app/services/firebase_auth.py
import json
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def initialize_firebase():
    from pathlib import Path
    from app.core.config import settings

    if firebase_admin._apps:
        return
    if settings.FIREBASE_JSON:
        cred = credentials.Certificate(json.loads(settings.FIREBASE_JSON))
    else:
        path = Path(settings.FIREBASE_CREDENTIALS)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[2] / path
        if not path.is_file():
            raise RuntimeError("Configure FIREBASE_JSON or a valid FIREBASE_CREDENTIALS file before starting the API.")
        cred = credentials.Certificate(str(path))
    firebase_admin.initialize_app(cred)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    This is the function your endpoints.py is trying to import.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"--- AUTH FAILED: {str(e)} ---")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )
