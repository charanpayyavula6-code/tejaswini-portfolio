from fastapi import APIRouter, HTTPException, status
from common.models_schema import (
    DiabetesPredictionRequest,
    HeartDiseasePredictionRequest,
    DiseaseRiskResponse
)
from fastapi_engine.services.ml_models import disease_predictor
from common.logger import setup_logger

router = APIRouter(prefix="/api/disease", tags=["Clinical Disease Prediction"])
logger = setup_logger("DiseaseRoute")

@router.post("/predict-diabetes", response_model=DiseaseRiskResponse, status_code=status.HTTP_200_OK)
async def predict_diabetes(request: DiabetesPredictionRequest):
    """
    Evaluates clinical diabetes indicators (fasting glucose, BMI, blood pressure, insulin, pedigree)
    and returns stratified risk classification with health recommendations.
    """
    try:
        result = disease_predictor.predict_diabetes(
            glucose=request.glucose,
            blood_pressure=request.blood_pressure,
            bmi=request.bmi,
            age=request.age,
            insulin=request.insulin,
            pregnancies=request.pregnancies,
            skin_thickness=request.skin_thickness,
            pedigree=request.diabetes_pedigree
        )
        try:
            from common.cloud_db import cloud_db
            cloud_db.record_ai_telemetry(
                module="disease_prediction_diabetes",
                request_data={"glucose": request.glucose, "bmi": request.bmi, "age": request.age},
                response_data={"risk_level": result.get("risk_level"), "probability": result.get("risk_probability")},
                latency_ms=1.5
            )
        except Exception:
            pass
        return DiseaseRiskResponse(**result)
    except Exception as e:
        logger.error(f"Error during diabetes prediction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diabetes risk evaluation failure: {str(e)}"
        )

@router.post("/predict-heart", response_model=DiseaseRiskResponse, status_code=status.HTTP_200_OK)
async def predict_heart_disease(request: HeartDiseasePredictionRequest):
    """
    Evaluates cardiovascular indicators (chest pain class, resting BP, serum cholesterol, max heart rate, ST depression)
    to output myocardial ischemia risk assessment and clinical recommendations.
    """
    try:
        result = disease_predictor.predict_heart_disease(
            age=request.age,
            sex=request.sex,
            chest_pain_type=request.chest_pain_type,
            resting_bp=request.resting_bp,
            cholesterol=request.cholesterol,
            max_heart_rate=request.max_heart_rate,
            st_depression=request.st_depression,
            exercise_angina=request.exercise_induced_angina
        )
        try:
            from common.cloud_db import cloud_db
            cloud_db.record_ai_telemetry(
                module="disease_prediction_heart",
                request_data={"age": request.age, "resting_bp": request.resting_bp, "cholesterol": request.cholesterol},
                response_data={"risk_level": result.get("risk_level"), "probability": result.get("risk_probability")},
                latency_ms=1.5
            )
        except Exception:
            pass
        return DiseaseRiskResponse(**result)
    except Exception as e:
        logger.error(f"Error during cardiovascular prediction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Heart disease risk evaluation failure: {str(e)}"
        )

