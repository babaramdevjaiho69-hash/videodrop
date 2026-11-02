from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from urllib.parse import urlparse
import ipaddress

app = FastAPI(title="VideoDrop Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def validate_media_url(url: str):
    parsed = urlparse(url.strip())

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(400, "Invalid URL")

    if parsed.username or parsed.password:
        raise HTTPException(400, "URLs with credentials are not allowed")

    host = parsed.hostname.lower()

    if host == "localhost" or host.endswith(".localhost"):
        raise HTTPException(400, "Local URLs are not allowed")

    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global:
            raise HTTPException(400, "Private IP addresses are not allowed")
    except ValueError:
        pass

    extension = parsed.path.lower().rsplit(".", 1)[-1]

    if extension not in ("mp4", "webm"):
        raise HTTPException(400, "Only direct MP4 and WebM links are supported")

    return extension

@app.get("/")
def home():
    return {"message": "VideoDrop backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/prepare")
def prepare_video(data: VideoRequest):
    extension = validate_media_url(data.url)
    return {
        "status": "checked",
        "format": extension,
        "message": "Direct media link accepted"
    }

@app.post("/download")
def download_video(data: VideoRequest):
    validate_media_url(data.url)
    return RedirectResponse(
        url=data.url.strip(),
        status_code=302
    )
@app.get("/download")
def download_video_get(url: str):
    validate_media_url(url)
    return RedirectResponse(url=url, status_code=302)
