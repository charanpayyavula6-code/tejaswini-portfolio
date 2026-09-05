import sys
import os
import time
import signal
import threading
import subprocess
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from common.config import FLASK_HOST, FLASK_PORT, FASTAPI_HOST, FASTAPI_PORT
from common.logger import setup_logger

logger = setup_logger("MasterServicesRunner")

def run_fastapi():
    """Runs FastAPI microservice on uvicorn."""
    import uvicorn
    from fastapi_engine.main import app as fastapi_app
    logger.info(f"Starting FastAPI AI Engine on http://{FASTAPI_HOST}:{FASTAPI_PORT}")
    uvicorn.run(fastapi_app, host=FASTAPI_HOST, port=FASTAPI_PORT, log_level="info")

def run_flask():
    """Runs Flask Gateway."""
    from flask_gateway.app import create_app
    flask_app = create_app()
    logger.info(f"Starting Flask API Gateway on http://{FLASK_HOST}:{FLASK_PORT}")
    flask_app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)

def main():
    logger.info("=" * 70)
    logger.info("  TEJASWINI PORTFOLIO BACKEND - DUAL MICROSERVICE RUNNER")
    logger.info("  [1] Flask API Gateway    -> http://127.0.0.1:5000")
    logger.info("  [2] FastAPI AI Engine    -> http://127.0.0.1:8000 (Swagger: /docs)")
    logger.info("=" * 70)
    
    # Start FastAPI in thread 1
    t_fastapi = threading.Thread(target=run_fastapi, daemon=True, name="FastAPI-Worker")
    t_fastapi.start()
    
    # Allow FastAPI a moment to bind socket
    time.sleep(1.0)
    
    # Start Flask in thread 2
    t_flask = threading.Thread(target=run_flask, daemon=True, name="Flask-Gateway")
    t_flask.start()
    
    logger.info("All microservices initialized successfully. Press Ctrl+C to terminate.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Terminating all services gracefully...")
        sys.exit(0)

if __name__ == "__main__":
    main()
