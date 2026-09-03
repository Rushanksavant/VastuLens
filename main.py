import base64
import io
import os
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.grid_lens import overlay_vastu_grid
from src.detector import analyze_floor_plan
from src.engine import VastuAuditor
from src.utilities import InteractiveMarker, ComplexFloorPlanExtraction, ZoneType

app = FastAPI(title="Vastu Vision AI API")

# Serve static frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


class AuditRequest(BaseModel):
    extraction_data: dict
    confirmed_markers: List[InteractiveMarker]


@app.post("/api/analyze")
async def analyze_layout(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    raw_bytes = await file.read()
    
    # 1. Overlay 3x3 Vastu Grid
    grid_buffer = overlay_vastu_grid(raw_bytes)
    
    # 2. Convert grid image buffer to Base64 data URL for instant frontend rendering
    grid_b64 = base64.b64encode(grid_buffer.getvalue()).decode("utf-8")
    image_data_url = f"data:image/jpeg;base64,{grid_b64}"

    # 3. Call Gemini Vision detector
    try:
        extraction = analyze_floor_plan(grid_buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "image_url": image_data_url,
        "extraction_data": extraction.model_dump()
    }


@app.post("/api/audit")
async def run_audit(payload: AuditRequest):
    try:
        extraction = ComplexFloorPlanExtraction(**payload.extraction_data)
        auditor = VastuAuditor()
        result = auditor.run_audit(extraction, payload.confirmed_markers)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)