from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from api.auth import get_current_user
from dotenv import load_dotenv
import os
import requests
import io
from PIL import Image
import pytesseract

load_dotenv()
router = APIRouter(prefix="/utils", tags=["utils"])

# OCR endpoint (requires tesseract installed on host)
@router.post("/ocr")
async def ocr_receipt(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read image: {str(e)}")

    # Try to use pytesseract; if not installed/configured, instruct user
    try:
        text = pytesseract.image_to_string(image)
    except Exception as e:
        # return helpful message to user if pytesseract/tesseract not available
        raise HTTPException(status_code=500, detail="OCR not available on server. Install Tesseract and pytesseract. Error: " + str(e))

    # Very simple parse heuristics: you can extend with regexes to capture amount, date, vendor
    # Here we return raw text plus placeholder parsed fields
    parsed = {
        "raw_text": text,
        "amount": None,
        "date": None,
        "possible_descriptions": text.splitlines()[:8]
    }
    return parsed

# Currency conversion proxy
@router.get("/convert")
def convert_currency(amount: float, from_currency: str, to_currency: str):
    """
    Uses EXCHANGE_API_URL from env. Example provider: exchangerate-api or others.
    This function expects a URL like 'https://api.exchangerate-api.com/v4/latest'
    which expects base appended: /{BASE}
    """
    EXCHANGE_API_URL = os.getenv("EXCHANGE_API_URL", "")
    API_KEY = os.getenv("EXCHANGE_API_KEY", "")
    if not EXCHANGE_API_URL:
        raise HTTPException(status_code=500, detail="Exchange API URL not configured in .env")

    # Some APIs expect base appended, some need query param; adapt as needed.
    url = f"{EXCHANGE_API_URL}/{from_currency}"
    headers = {}
    params = {}
    if API_KEY:
        # for providers using header auth
        headers["apikey"] = API_KEY
        # or use params['access_key'] = API_KEY depending on provider
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # try to find rates in common formats
        rates = data.get("rates") or data.get("conversion_rates") or {}
        if to_currency not in rates:
            raise HTTPException(status_code=400, detail=f"Target currency {to_currency} not found in rates")
        rate = rates[to_currency]
        converted = float(amount) * float(rate)
        return {"amount": amount, "from": from_currency, "to": to_currency, "rate": rate, "converted": converted}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Currency conversion failed: {str(e)}")