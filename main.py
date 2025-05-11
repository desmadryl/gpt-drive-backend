from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
import os

app = FastAPI()

# Variables d'environnement à configurer dans Render
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://gpt-drive-backend.onrender.com/oauth/callback"
FOLDER_ID = os.getenv("TARGET_FOLDER_ID")  # L'ID du dossier Google Drive ciblé

@app.get("/")
def home():
    return {"message": "API en ligne avec rafraîchissement et accès dossier Drive."}

@app.get("/refresh_token")
def refresh_token(refresh_token: str = Query(...)):
    token_data = refresh_token_request(refresh_token)
    if not token_data.get("access_token"):
        raise HTTPException(status_code=400, detail="Échec de rafraîchissement du token.")
    return token_data

@app.get("/folder_files")
def list_folder_files(refresh_token: str = Query(...)):
    # Rafraîchir automatiquement le token
    token_data = refresh_token_request(refresh_token)
    access_token = token_data.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Token d'accès manquant ou invalide.")
    
    # Filtrer les fichiers dans le dossier cible
    query = f"'{FOLDER_ID}' in parents"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": query}
    
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
