"""Application configuration settings."""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = Path(os.environ.get("STORAGE_DIR", BASE_DIR / "storage"))
GENERATED_DIR = Path(os.environ.get("GENERATED_DIR", BASE_DIR / "generated"))

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

# Security Limits
MAX_UPLOAD_SIZE_BYTES = int(os.environ.get("MAX_UPLOAD_SIZE_BYTES", 50 * 1024 * 1024))  # 50 MB
MAX_EXTRACTED_SIZE_BYTES = int(os.environ.get("MAX_EXTRACTED_SIZE_BYTES", 200 * 1024 * 1024))  # 200 MB
MAX_FILE_COUNT = int(os.environ.get("MAX_FILE_COUNT", 2000))
MAX_PATH_DEPTH = int(os.environ.get("MAX_PATH_DEPTH", 20))

# Server Host & Base URL
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 8000))
BASE_URL = os.environ.get("BASE_URL", f"http://{HOST}:{PORT}")


def get_effective_base_url(request=None) -> str:
    """
    Dynamically determines the public base URL:
    1. If BASE_URL environment variable is explicitly configured, use it.
    2. If a Request object is available, derive base URL from headers (supports reverse proxies).
    3. Fallback to default BASE_URL.
    """
    env_base = os.environ.get("BASE_URL")
    if env_base:
        return env_base.rstrip("/")
    if request:
        proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("x-forwarded-host", request.headers.get("host", f"{HOST}:{PORT}"))
        return f"{proto}://{host}".rstrip("/")
    return BASE_URL.rstrip("/")

# Supabase Settings
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://sohmmvanrnrnwwrjedan.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvaG1tdmFucm5ybnd3cmplZGFuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxNzU5OTAsImV4cCI6MjEwMzc1MTk5MH0.dT4PFLY87nJXD5wBktOr9SFgr22JyN6U5semogacU2o"
)
SUPABASE_BUCKET_NAME = os.environ.get("SUPABASE_BUCKET_NAME", "project-archives")

# Initialize Supabase client
supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Supabase client: {e}")
