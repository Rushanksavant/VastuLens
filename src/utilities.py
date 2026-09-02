from pydantic import BaseModel, Field
from typing import List, Literal, Optional

ZoneType = Literal["NW", "N", "NE", "W", "CENTER", "E", "SW", "S", "SE"]

class SubFixture(BaseModel):
    name: Literal[
        "MAIN_ENTRANCE_DOOR", 
        "COOKING_STOVE", 
        "TOILET_COMMODE", 
        "BED_HEADBOARD", 
        "WATER_SINK", 
        "WASHING_MACHINE"
    ]
    zone: ZoneType
    orientation_facing: Optional[Literal["NORTH", "SOUTH", "EAST", "WEST"]] = None

class RoomDetails(BaseModel):
    room_name: str
    room_type: Literal[
        "KITCHEN", "MASTER_BEDROOM", "GUEST_BEDROOM", 
        "BATHROOM_TOILET", "LIVING_ROOM", "BALCONY", 
        "DINING_ROOM", "HALLWAY"
    ]
    primary_zone: ZoneType
    secondary_zones: List[ZoneType] = []

class ComplexFloorPlanExtraction(BaseModel):
    entrance_reasoning: str = Field(
        ...,
        description=(
            "Step-by-step visual audit of doors: "
            "1. List all doors connected to spaces labeled BALCONY, PATIO, or TERRACE and explicitly mark them as DISQUALIFIED. "
            "2. Identify the true front door attached to a Hallway, Foyer, Corridor, or exterior entryway wall."
        )
    )
    main_entrance: Optional[SubFixture] = Field(
        None, 
        description=(
            "The primary front entrance door into the residence. "
            "MUST NOT be a door leading to a Balcony, Patio, Deck, or Terrace."
        )
    )
    rooms: List[RoomDetails]
    fixtures: List[SubFixture]
    brahmasthan_status: Literal["CLEAR", "OBSTRUCTED_BY_WALL", "OBSTRUCTED_BY_TOILET", "OBSTRUCTED_BY_STAIRS"] = Field(
        ...,
        description="Physical status of the CENTER grid block (Brahmasthan)."
    )


COMPLEX_VASTU_PROMPT = """
Analyze the floor plan overlaid with a red 3x3 grid. Perform a granular Vastu extraction using strict architectural entry identification:

1. **MAIN ENTRANCE DISQUALIFICATION RULES (STRICT)**:
   - **Step 1 — Identify Outdoor Exits**: Look at spaces labeled `BALCONY`, `PATIO`, `TERRACE`, or areas containing outdoor seating/plants. ANY door opening into these spaces (e.g., the left doors in Plan 1 or bottom doors in Plan 2) is a SECONDARY PATIO DOOR. Immediately DISQUALIFY it.
   - **Step 2 — Identify Front Entryway**: Locate the single entrance door that leads into the home's primary circulation space (e.g., the door on the right wall of the `Hallway` in Plan 1, or the perimeter entry vestibule).
   - **Step 3 — Fallback**: If no primary front entrance door is visible on the outer walls or if it is cropped out, set `main_entrance` to `null`. DO NOT default to a balcony or patio door.

2. **BRAHMASTHAN (CENTER ZONE)**:
   - Mark as 'CLEAR' if the central grid area is open living/hall space, even if text labels cross into it.
   - Mark as obstructed ONLY if solid walls, staircases, or enclosed bathrooms sit physically inside the center grid.

3. **ROOMS & FIXTURES**:
   - Locate stove hobs, toilet commodes, and bed headboards by their drawn graphics.

Extract strictly using the JSON schema provided. Populate `entrance_reasoning` first before setting `main_entrance`.
"""