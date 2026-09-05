import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common.config import CORS_ORIGINS
from common.logger import setup_logger
from fastapi_engine.routes.spam_detector import router as spam_router
from fastapi_engine.routes.face_biometrics import router as face_router
from fastapi_engine.routes.captcha_security import router as captcha_router
from fastapi_engine.routes.disease_prediction import router as disease_router
from fastapi_engine.routes.ai_assistant import router as assistant_router

logger = setup_logger("FastAPIEngine")

app = FastAPI(
    title="Tejaswini Portfolio - AI & Algorithmic Compute Engine",
    description="High-performance asynchronous microservice for NLP Spam Detection, Biometric Face Attendance, Procedural CAPTCHA, Clinical Disease Prediction, and Portfolio QA Bot.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing & Telemetry Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response

# Include Subsystem Routers
app.include_router(spam_router)
app.include_router(face_router)
app.include_router(captcha_router)
app.include_router(disease_router)
app.include_router(assistant_router)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Returns the operational status of the FastAPI compute microservice."""
    return {
        "service": "FastAPI AI & Compute Engine",
        "status": "HEALTHY",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0.0"
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Tejaswini's AI & Algorithmic Compute Engine (FastAPI).",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    from common.config import FASTAPI_HOST, FASTAPI_PORT
    uvicorn.run("fastapi_engine.main:app", host=FASTAPI_HOST, port=FASTAPI_PORT, reload=True)
