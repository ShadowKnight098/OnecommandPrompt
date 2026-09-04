"""FastAPI Main Application Entrypoint."""
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload import router as upload_router
from app.api.projects import router as projects_router
from app.api.installers import router as installers_router

app = FastAPI(
    title="One-Command Project Installer API",
    description="Transforms Python projects into reproducible, one-command installations across Windows, macOS, and Linux.",
    version="1.0.0",
)


# Explicitly Whitelisted Domains
DEFAULT_ALLOWED_ORIGINS = [
    "https://onecommand-prompt.vercel.app",
    "https://onecommand-prompt-p46rlx72v-shadowknight098s-projects.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

env_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
ALLOWED_ORIGINS = env_origins if env_origins else DEFAULT_ALLOWED_ORIGINS + ["*"]


# Global Middleware: Explicitly inject CORS headers on EVERY response (including errors & preflight)
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    origin = request.headers.get("origin") or "*"
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true" if origin != "*" else "false"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    try:
        response = await call_next(request)
    except Exception as exc:
        from fastapi.responses import JSONResponse
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    if origin != "*":
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# Standard Starlette CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(upload_router)
app.include_router(projects_router)
app.include_router(installers_router)


@app.get("/", tags=["system"])
async def root():
    """Root endpoint to verify backend service is online."""
    return {"status": "ok", "service": "onecommand-installer-backend", "version": "1.0.0"}


@app.get("/api/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "onecommand-installer-backend"}


# Mount static frontend build if present
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if dist_dir.exists() and (dist_dir / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = dist_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")

