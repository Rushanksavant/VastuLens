import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import complex schema and prompt from utilities
from src.utilities import ComplexFloorPlanExtraction, COMPLEX_VASTU_PROMPT

load_dotenv()

def analyze_floor_plan(image_path: str) -> ComplexFloorPlanExtraction:
    client = genai.Client()
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",  # Standard vision model for structured Pydantic extraction
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

# if __name__ == "__main__":
#     # Ensure this matches the output path from grid_lens.py
#     result = analyze_floor_plan("src/outputs/plan1_grid_improved.jpg")
#     print(result.model_dump_json(indent=2))