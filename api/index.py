import os
import sys
from pathlib import Path

# Set environment flags for serverless runtime
os.environ["VERCEL"] = "1"

# Add project root and backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from flask_gateway.app import create_app

flask_app = create_app()

class VercelWSGIHandler:
    """WSGI Middleware for Vercel Serverless Python execution."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        
    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        raw_uri = environ.get("RAW_URI", "") or environ.get("REQUEST_URI", "")
        
        # When Vercel rewrites /api/* to /api/index.py, restore original PATH_INFO
        if "index.py" in path or not path or path == "/":
            if raw_uri:
                clean_path = raw_uri.split("?")[0]
                environ["PATH_INFO"] = clean_path
                
        # If route does not start with /api, normalize it
        if not environ["PATH_INFO"].startswith("/api") and raw_uri.startswith("/api"):
            environ["PATH_INFO"] = raw_uri.split("?")[0]
            
        return self.wsgi_app(environ, start_response)

app = VercelWSGIHandler(flask_app)

if __name__ == "__main__":
    flask_app.run()
