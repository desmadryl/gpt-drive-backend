from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import os

app = FastAPI()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://gpt-drive-backend.onrender.com/oauth/callback"
SCOPE = "https://www.googleapis.com/auth/drive.readonly"

@app.get("/")
def home():
    return {"message": "API prête pour Google Drive OAuth"}

@app.get("/oauth/login")
def login():
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPE}"
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
    if r.status_code == 200:
        return JSONResponse(content=r.json())
    return JSONResponse(status_code=400, content={"error": "Erreur OAuth", "detail": r.text})

@app.get("/files")
def list_files(token: str, query: str = ""):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query}
    r = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)
    return r.json()
