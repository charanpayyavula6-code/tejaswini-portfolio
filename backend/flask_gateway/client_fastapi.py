import time
import httpx
from typing import Dict, Any, Optional
from common.config import FASTAPI_BASE_URL
from common.logger import setup_logger

logger = setup_logger("FastAPIClient")

class FastAPIMicroserviceClient:
    """
    Resilient HTTP client for orchestrating synchronous & asynchronous
    calls from Flask API Gateway to FastAPI compute engine.
    """
    
    def __init__(self, base_url: str = FASTAPI_BASE_URL, timeout: float = 6.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
    def _make_request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 2
    ) -> Dict[str, Any]:
        """Executes HTTP request with automatic retry logic and structured error normalization."""
        url = f"{self.base_url}{path}"
        last_error = None
        
        for attempt in range(1, retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(
                        method=method,
                        url=url,
                        json=json_data,
                        params=params
                    )
                    
                    if response.is_success:
                        return response.json()
                    else:
                        error_detail = response.text
                        try:
                            error_detail = response.json().get("detail", error_detail)
                        except Exception:
                            pass
                        logger.warning(
                            f"FastAPI microservice returned HTTP {response.status_code} for {method} {path}: {error_detail}"
                        )
                        return {
                            "error": True,
                            "status_code": response.status_code,
                            "detail": error_detail
                        }
            except httpx.ConnectError as e:
                last_error = f"Cannot connect to FastAPI compute engine at {self.base_url}. Service may be starting up."
                logger.warning(f"Connection attempt {attempt}/{retries} failed: {last_error}")
            except httpx.TimeoutException as e:
                last_error = f"Request to FastAPI compute engine timed out after {self.timeout}s."
                logger.warning(f"Timeout attempt {attempt}/{retries}: {last_error}")
            except Exception as e:
                last_error = f"Unexpected error during microservice communication: {str(e)}"
                logger.error(last_error, exc_info=True)
                
            time.sleep(0.15 * attempt)
            
        return {
            "error": True,
            "status_code": 503,
            "detail": last_error or "FastAPI Microservice unavailable"
        }

    # =========================================================================
    # Subsystem Client Methods
    # =========================================================================
    def check_health(self) -> Dict[str, Any]:
        """Queries FastAPI /health endpoint."""
        return self._make_request("GET", "/health")
        
    def analyze_spam(self, email_text: str) -> Dict[str, Any]:
        """Requests NLP Spam classification on email text."""
        return self._make_request("POST", "/api/spam/predict", json_data={"email_text": email_text})
        
    def verify_face_attendance(
        self,
        student_id: str,
        student_name: str,
        image_base64: Optional[str] = None,
        device_id: Optional[str] = "CAM-GATE-01"
    ) -> Dict[str, Any]:
        """Requests facial landmark extraction and biometric verification."""
        return self._make_request(
            "POST",
            "/api/face/verify-attendance",
            json_data={
                "student_id": student_id,
                "student_name": student_name,
                "image_base64": image_base64,
                "device_id": device_id
            }
        )
        
    def generate_captcha(self) -> Dict[str, Any]:
        """Requests dynamically rendered SVG CAPTCHA with challenge token."""
        return self._make_request("GET", "/api/captcha/generate")
        
    def verify_captcha(self, captcha_token: str, user_solution: str) -> Dict[str, Any]:
        """Validates CAPTCHA cryptographic challenge."""
        return self._make_request(
            "POST",
            "/api/captcha/verify",
            json_data={
                "captcha_token": captcha_token,
                "user_solution": user_solution
            }
        )
        
    def predict_diabetes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts diabetes risk metrics from clinical parameters."""
        return self._make_request("POST", "/api/disease/predict-diabetes", json_data=data)
        
    def predict_heart_disease(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts cardiovascular disease risk metrics."""
        return self._make_request("POST", "/api/disease/predict-heart", json_data=data)
        
    def query_assistant(self, query: str) -> Dict[str, Any]:
        """Queries the portfolio AI knowledge assistant."""
        return self._make_request("POST", "/api/assistant/chat", json_data={"query": query})

fastapi_client = FastAPIMicroserviceClient()
