import os
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

router = APIRouter()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.8-flash"


class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str


@router.get("/test")
def test():
    return {
        "message": "LegalEase backend is working"
    }


@router.post("/generate")
def generate_document(request: DocumentRequest):

    prompt = f"""
Create a professional legal document draft.

Document Type:
{request.document_type}

Parties Involved:
{request.parties}

Effective Date:
{request.effective_date}

Terms and Conditions:
{request.terms}

Write a clear, structured legal document using the information provided.

Do not invent important facts that were not provided.

Include:
- Document title
- Parties
- Effective date
- Definitions where appropriate
- Clear numbered clauses
- Terms and conditions
- Termination provisions where relevant
- Signatures section

Add this notice at the end:

"AI-generated draft. Review with a qualified legal professional before use."
"""

    try:

        response = None

        # Retry temporary Gemini 503 errors
        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt
                )

                break

            except Exception as e:

                if "503" in str(e) and attempt < 2:

                    time.sleep(3)

                else:

                    raise

        if response is None:
            raise Exception("Gemini did not return a response.")

        return {
            "document": response.text
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )