import random
import string
import hmac
import hashlib
import time
import base64
from fastapi import APIRouter, HTTPException, status
from common.config import CAPTCHA_SALT
from common.models_schema import CaptchaGenerateResponse, CaptchaVerifyRequest, CaptchaVerifyResponse
from common.logger import setup_logger

router = APIRouter(prefix="/api/captcha", tags=["Dynamic CAPTCHA Security"])
logger = setup_logger("CaptchaRoute")

# Characters excluding visually ambiguous glyphs (O, 0, I, l, 1)
CHAR_SET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
CAPTCHA_EXPIRATION_SECONDS = 300  # 5 minutes

def _generate_captcha_token(solution: str, timestamp: int) -> str:
    """Creates a cryptographic HMAC signature containing solution and expiration timestamp."""
    message = f"{solution.upper()}:{timestamp}:{CAPTCHA_SALT}".encode()
    signature = hmac.new(CAPTCHA_SALT.encode(), message, hashlib.sha256).hexdigest()
    payload = f"{timestamp}:{signature}"
    return base64.urlsafe_b64encode(payload.encode()).decode()

def _verify_captcha_token(token: str, user_solution: str) -> bool:
    """Verifies HMAC signature, timestamp expiration, and user solution match."""
    try:
        raw_payload = base64.urlsafe_b64decode(token.encode()).decode()
        parts = raw_payload.split(":")
        if len(parts) != 2:
            return False
            
        timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        now = int(time.time())
        
        # Expiration check
        if now - timestamp > CAPTCHA_EXPIRATION_SECONDS or timestamp > now + 60:
            logger.warning("CAPTCHA verification failed: Token expired.")
            return False
            
        # Recompute signature
        expected_sig = hmac.new(
            CAPTCHA_SALT.encode(),
            f"{user_solution.strip().upper()}:{timestamp}:{CAPTCHA_SALT}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_sig)
    except Exception as e:
        logger.error(f"Error during token verification: {e}")
        return False

def _generate_svg_captcha(text: str) -> str:
    """Procedurally renders an anti-OCR distorted SVG CAPTCHA."""
    width = 240
    height = 80
    
    # Random vibrant colors
    colors = ["#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#34d399", "#fbbf24"]
    
    # Generate noise lines
    noise_lines = []
    for _ in range(6):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        stroke_color = random.choice(colors)
        stroke_width = random.uniform(1.2, 2.5)
        noise_lines.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="{stroke_width}" opacity="0.55" />'
        )
        
    # Generate noise dots
    noise_dots = []
    for _ in range(40):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        r = random.uniform(1.0, 2.2)
        dot_color = random.choice(colors)
        noise_dots.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{dot_color}" opacity="0.4" />'
        )
        
    # Render characters with random rotation, offsets, and fonts
    char_elements = []
    start_x = 22
    for i, char in enumerate(text):
        char_x = start_x + (i * 34) + random.randint(-3, 3)
        char_y = 52 + random.randint(-4, 4)
        rot_angle = random.randint(-22, 22)
        char_color = random.choice(colors)
        
        char_elements.append(
            f'<text x="{char_x}" y="{char_y}" font-family="Arial, sans-serif" font-size="34" '
            f'font-weight="bold" fill="{char_color}" '
            f'transform="rotate({rot_angle} {char_x} {char_y})" '
            f'filter="drop-shadow(0 0 4px rgba(0,0,0,0.5))">{char}</text>'
        )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background: #0f172a; border-radius: 8px; border: 1px solid #334155; user-select: none;">
        <rect width="100%" height="100%" fill="#0a0f1d" rx="8"/>
        {"".join(noise_dots)}
        {"".join(noise_lines)}
        {"".join(char_elements)}
    </svg>"""
    
    return svg_content

@router.get("/generate", response_model=CaptchaGenerateResponse, status_code=status.HTTP_200_OK)
async def generate_captcha():
    """Generates a secure procedural CAPTCHA image (SVG) and cryptographic challenge token."""
    try:
        captcha_text = "".join(random.choices(CHAR_SET, k=6))
        timestamp = int(time.time())
        token = _generate_captcha_token(captcha_text, timestamp)
        svg_image = _generate_svg_captcha(captcha_text)
        
        return CaptchaGenerateResponse(
            captcha_token=token,
            captcha_svg=svg_image,
            expires_in_seconds=CAPTCHA_EXPIRATION_SECONDS
        )
    except Exception as e:
        logger.error(f"Error generating CAPTCHA: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CAPTCHA generation failed: {str(e)}"
        )

@router.post("/verify", response_model=CaptchaVerifyResponse, status_code=status.HTTP_200_OK)
async def verify_captcha(request: CaptchaVerifyRequest):
    """Cryptographically verifies the user-entered CAPTCHA response."""
    is_valid = _verify_captcha_token(request.captcha_token, request.user_solution)
    
    if is_valid:
        return CaptchaVerifyResponse(
            valid=True,
            message="CAPTCHA challenge successfully validated. Bot protection cleared."
        )
    else:
        return CaptchaVerifyResponse(
            valid=False,
            message="Invalid or expired CAPTCHA code. Please request a new verification challenge."
        )
