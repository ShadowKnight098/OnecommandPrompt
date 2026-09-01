"""Launcher script for local backend development."""
import uvicorn
import os

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(backend_dir, "app")
    print(f"Starting One-Command Project Installer Backend on http://{host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[app_dir],
        reload_excludes=["storage", "generated", ".pytest_cache", "*.json", "*.zip"],
    )
