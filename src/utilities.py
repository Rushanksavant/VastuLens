from pydantic import BaseModel, Field
from typing import List, Literal, Optional

ZoneType = Literal["NW", "N", "NE", "W", "CENTER", "E", "SW", "S", "SE"]

class InteractiveMarker(BaseModel):
    id: str = Field(..., description="Unique string identifier, e.g., 'door_1', 'stove_1', 'commode_1'")
    label: Literal[
        "MAIN_ENTRANCE", "BALCONY_DOOR", "COOKING_STOVE", 
        "TOILET_COMMODE", "BED_HEADBOARD", "POOJA_MANDIR", 
        "WATER_SINK", "WASHING_MACHINE"
    ]
    x_percent: float = Field(..., description="Horizontal spatial position (0-100% from top-left of floor plan).")
    y_percent: float = Field(..., description="Vertical spatial position (0-100% from top-left of floor plan).")
    zone: ZoneType
    notes: Optional[str] = Field(None, description="Brief justification for this marker's detected location.")

class RoomDetails(BaseModel):
    room_name: str
    room_type: Literal[
        "KITCHEN", "MASTER_BEDROOM", "GUEST_BEDROOM", 
        "BATHROOM_TOILET", "LIVING_ROOM", "BALCONY", 
        "DINING_ROOM", "HALLWAY", "POOJA_ROOM"
    ]
    primary_zone: ZoneType
    secondary_zones: List[ZoneType] = []

class ComplexFloorPlanExtraction(BaseModel):
    suggested_markers: List[InteractiveMarker] = Field(
        ..., 
        description="List of initial proposed spatial markers for doors, key fixtures, and elements for user review."
    )
    rooms: List[RoomDetails] = Field(..., description="List of detected room regions.")
    brahmasthan_status: Literal["CLEAR", "OBSTRUCTED_BY_WALL", "OBSTRUCTED_BY_TOILET", "OBSTRUCTED_BY_STAIRS"] = Field(
        ...,
        description="Physical status of the central grid zone (CENTER)."
    )


COMPLEX_VASTU_PROMPT = """
Analyze the floor plan image overlaid with a 3x3 red Vastu grid.

SPATIAL & FIXTURE EXTRACTION INSTRUCTIONS:
1. **MARKER COORDINATES (0-100%)**:
   - Calculate normalized percentage coordinates (x_percent, y_percent) from top-left (0,0) to bottom-right (100,100).
   - Identify external doors, stove hobs, toilet commodes, bed headboards, water sinks, and washing machines.

2. **ENTRANCE vs BALCONY DISAMBIGUATION**:
   - Do NOT mark balcony or patio exits as MAIN_ENTRANCE.
   - Label patio/balcony slider doors as `BALCONY_DOOR`.
   - Label main entryway doors (leading into hallways, foyers, or entrance corridors) as `MAIN_ENTRANCE`. If ambiguous or cropped out, omit or label as secondary exit.

3. **BRAHMASTHAN (CENTER ZONE)**:
   - Return 'CLEAR' if the central grid area is open walking/living space, even if printed text/room names overlay it.
   - Return an obstructed status ONLY if solid structural walls, staircases, or enclosed toilets lie inside the center block.

4. **ROOM BOUNDARIES**:
   - Extract major rooms and their corresponding 3x3 zones.
"""