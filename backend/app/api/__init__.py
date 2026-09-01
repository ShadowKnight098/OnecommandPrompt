"""API Package."""
from .upload import router as upload_router
from .projects import router as projects_router
from .installers import router as installers_router

__all__ = ["upload_router", "projects_router", "installers_router"]
