import io
import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

from src.utilities import ComplexFloorPlanExtraction, COMPLEX_VASTU_PROMPT

# Safely load environment variables
load_dotenv(override=True)

MAX_RETRIES = 3
RETRY_DELAY = 2

def analyze_floor_plan(image_buffer: io.BytesIO) -> ComplexFloorPlanExtraction:
    """
    Calls Gemini Vision to extract floor plan markers and Vastu topology.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing or empty in .env")

    # Explicitly pass api_key to bypass local system credential file search
    client = genai.Client(api_key=api_key)

    # Ensure binary bytes are extracted from the buffer
    if isinstance(image_buffer, io.BytesIO):
        image_buffer.seek(0)
        image_bytes = image_buffer.getvalue()
    elif isinstance(image_buffer, bytes):
        image_bytes = image_buffer
    else:
        raise TypeError(f"Expected io.BytesIO or bytes, got {type(image_buffer)}")

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    COMPLEX_VASTU_PROMPT
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ComplexFloorPlanExtraction,
                    temperature=0.0
                )
            )

            return ComplexFloorPlanExtraction.model_validate_json(response.text)

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    raise RuntimeError(f"Floor plan analysis failed after {MAX_RETRIES} attempts. Error: {last_error}")