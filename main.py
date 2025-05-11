from fastapi import FastAPI, Request
import requests

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API en ligne."}

@app.get("/files")
def list_files(token: str, query: str = ""):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query}
    r = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)
    return r.json()
