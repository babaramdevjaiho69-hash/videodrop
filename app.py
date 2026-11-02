from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse

app = FastAPI(title="VideoDrop Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {"message": "VideoDrop backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/prepare")
def prepare_video(data: VideoRequest):
    url = data.url.strip()
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(400, "Invalid URL")

    if parsed.hostname in ("localhost", "127.0.0.1"):
        raise HTTPException(400, "Local URLs are not allowed")

    extension = parsed.path.lower().split(".")[-1]

    if extension not in ("mp4", "webm"):
        raise HTTPException(400, "Only direct MP4 and WebM links are supported")

    return {
        "status": "checked",
        "format": extension,
        "message": "Link format accepted. Download processing is not enabled yet."
    }
