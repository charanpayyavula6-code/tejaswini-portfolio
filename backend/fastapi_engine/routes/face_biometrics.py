from fastapi import APIRouter, HTTPException, status
from common.models_schema import FaceVerificationRequest, AttendanceRecordResponse
from fastapi_engine.services.vision_engine import vision_engine
from common.logger import setup_logger

router = APIRouter(prefix="/api/face", tags=["Face Recognition & Biometrics"])
logger = setup_logger("FaceBiometricsRoute")

@router.post("/verify-attendance", response_model=AttendanceRecordResponse, status_code=status.HTTP_200_OK)
async def verify_face_attendance(request: FaceVerificationRequest):
    """
    Simulates OpenCV & Deep Learning face detection, extracts 8D biometric embeddings,
    validates anti-spoof liveness, and matches against registered student profiles.
    """
    try:
        result = vision_engine.verify_face_attendance(
            student_id=request.student_id,
            student_name=request.student_name,
            image_base64=request.image_base64,
            device_id=request.device_id or "CAM-GATE-01"
        )
        if result.get("verified"):
            try:
                from common.cloud_db import cloud_db
                cloud_db.record_attendance(
                    student_id=result["student_id"],
                    student_name=result["student_name"],
                    confidence=result["confidence_score"],
                    status=result["status"],
                    device_id=request.device_id or "CAM-GATE-01"
                )
            except Exception as db_err:
                logger.warning(f"Cloud DB attendance log skipped: {db_err}")
        return AttendanceRecordResponse(**result)
    except Exception as e:
        logger.error(f"Error during face biometric verification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Biometric processing failure: {str(e)}"
        )
