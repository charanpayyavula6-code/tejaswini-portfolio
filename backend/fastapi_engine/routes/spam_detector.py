from fastapi import APIRouter, HTTPException, status
from common.models_schema import SpamAnalysisRequest, SpamAnalysisResponse
from fastapi_engine.services.ml_models import spam_engine
from common.logger import setup_logger

router = APIRouter(prefix="/api/spam", tags=["Email Spam NLP Engine"])
logger = setup_logger("SpamRoute")

@router.post("/predict", response_model=SpamAnalysisResponse, status_code=status.HTTP_200_OK)
async def predict_spam(request: SpamAnalysisRequest):
    """
    NLP and Machine Learning pipeline that analyzes email bodies for spam indicators,
    calculates classification probabilities, and identifies phishing/urgency triggers.
    """
    try:
        result = spam_engine.analyze(request.email_text)
        try:
            from common.cloud_db import cloud_db
            cloud_db.record_ai_telemetry(
                module="spam_detector",
                request_data={"text_snippet": request.email_text[:80]},
                response_data={"is_spam": result.get("is_spam"), "spam_probability": result.get("spam_probability")},
                latency_ms=result.get("inference_time_ms", 1.0)
            )
        except Exception:
            pass
        return SpamAnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Error during spam analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spam classification failure: {str(e)}"
        )
