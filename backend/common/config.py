import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Load local .env if available
load_dotenv(ROOT_DIR / ".env")
load_dotenv(BASE_DIR / ".env")

# On Vercel / AWS Lambda serverless environments, the filesystem is read-only except /tmp
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    INSTANCE_DIR = Path("/tmp")
else:
    INSTANCE_DIR = BASE_DIR / "instance"

INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

# Microservice Network Configurations
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", f"http://{FASTAPI_HOST}:{FASTAPI_PORT}")

# Security & Secrets
SECRET_KEY = os.getenv("SECRET_KEY", "tejaswini-portfolio-secret-key-2026-secure-token")
CAPTCHA_SALT = os.getenv("CAPTCHA_SALT", "captcha-salt-teja-secure-x99")
JWT_ALGORITHM = "HS256"

# Relational / Local Database Configuration
DATABASE_PATH = INSTANCE_DIR / "portfolio.db"
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

# Cloud Database (MongoDB Atlas) Configuration
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or ""
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "tejaswini_portfolio")
MONGODB_TIMEOUT_MS = int(os.getenv("MONGODB_TIMEOUT_MS", "4000"))

# CORS Allowed Origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://tejaswini-portfolio-six.vercel.app",
    "*"
]
