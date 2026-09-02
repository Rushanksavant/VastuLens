import io
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

from src.utilities import ComplexFloorPlanExtraction, COMPLEX_VASTU_PROMPT

load_dotenv()

MAX_RETRIES = 3
RETRY_DELAY = 2


def analyze_floor_plan(image_buffer: io.BytesIO) -> ComplexFloorPlanExtraction:
    """
    Accepts a BytesIO buffer of the grid-overlaid image.
    Nothing is read from or written to disk.
    """
    client = genai.Client()
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            image_buffer.seek(0)
            image_bytes = image_buffer.read()

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    COMPLEX_VASTU_PROMPT
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ComplexFloorPlanExtraction,
                    temperature=0.1
                )
            )

            return ComplexFloorPlanExtraction.model_validate_json(response.text)

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"Failed to process floor plan after {MAX_RETRIES} attempts. Last error: {last_error}"
    )