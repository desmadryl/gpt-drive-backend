from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import requests
import os

app = FastAPI()

# Identifiants OAuth et Drive
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://gpt-drive-backend.onrender.com/oauth/callback"
FOLDER_ID = os.getenv("TARGET_FOLDER_ID")  # ID du dossier dans le Drive partagé
SHARED_DRIVE_ID = os.getenv("TARGET_SHARED_DRIVE_ID")  # ID du Drive partagé

@app.get("/")
def home():
    return {"message": "API active avec support complet du Drive partagé."}

@app.get("/refresh_token")
def refresh_token(refresh_token: str = Query(...)):
    token_data = refresh_token_request(refresh_token)
    if not token_data.get("access_token"):
        raise HTTPException(status_code=400, detail="Échec de rafraîchissement du token.")
    return token_data

@app.get("/folder_files")
def list_folder_files(refresh_token: str = Query(...)):
    token_data = refresh_token_request(refresh_token)
    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Token d'accès manquant ou invalide.")

    query = f"'{FOLDER_ID}' in parents"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "q": query,
        "includeItemsFromAllDrives": "true",
        "supportsAllDrives": "true",
        "corpora": "drive",
        "driveId": SHARED_DRIVE_ID
    }

    r = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Erreur Google Drive : {r.text}")

    return r.json()

def refresh_token_request(refresh_token: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    r = requests.post(token_url, data=data)
    return r.json() if r.status_code == 200 else {}

@app.get("/oauth/login")
def login():
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=https://www.googleapis.com/auth/drive.readonly"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return RedirectResponse(auth_url)

@app.get("/oauth/callback")
def callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return {"error": "OAuth callback failed", "detail": r.text}
    return r.json()
