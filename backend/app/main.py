import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.routes import upload, analyze

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(title="FinBot.AI API", version="0.1.0")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

if FRONTEND_ASSETS.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_ASSETS),
        name="frontend-assets",
    )


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    return JSONResponse(
        {
            "detail": "Frontend build not found. Run `npm run build` in the frontend directory.",
            "api": "/health",
        },
        status_code=404,
    )
