from src.utilities import ComplexFloorPlanExtraction
from dataclasses import dataclass, field
from typing import Literal, Optional
from enum import Enum


class Severity(str, Enum):
    PASS = "PASS"
    MINOR_DEFECT = "MINOR_DEFECT"
    MAJOR_DEFECT = "MAJOR_DEFECT"
    CRITICAL_DEFECT = "CRITICAL_DEFECT"


@dataclass
class AuditFinding:
    element: str
    zone: str
    severity: Severity
    penalty: int
    description: str
    remedy: Optional[str] = None
    category: str = "General"


# ---------------------------------------------------------------------------
# Rule definitions — each rule is self-contained with full metadata
# ---------------------------------------------------------------------------

ENTRANCE_RULE = {
    "category": "Main Entrance",
    "weight": 30,
    "ideal": {
        "zones": ["NE", "N", "E"],
        "description": "Ideal zones — invites positive energy flow.",
    },
    "acceptable": {
        "zones": ["NW"],
        "penalty": 10,
        "description": "Acceptable but not ideal — energy flow slightly restricted.",
        "remedy": "Place a Vastu pyramid near the entrance threshold to amplify positive energy.",
    },
    "prohibited": {
        "SW": {
            "penalty": 30,
            "description": "Severe defect — SW entrance invites stagnant energy.",
            "remedy": "Install a Vastu lead helix/pyramid at entrance threshold; paint door dark red.",
        },
        "SE": {
            "penalty": 20,
            "description": "Major defect — SE entrance creates fire-energy imbalance.",
            "remedy": "Paint door frame light red/cream; place a copper helix near the door.",
        },
        "S": {
            "penalty": 25,
            "description": "Major defect — South entrance blocks prosperity energy.",
            "remedy": "Place a Vastu yantra above the door; use a green door mat.",
        },
        "W": {
            "penalty": 15,
            "description": "Minor defect — West entrance slows positive energy.",
            "remedy": "Ensure doorway is well-lit; place a metal wind chime outside.",
        },
    },
}

BRAHMASTHAN_RULE = {
    "category": "Brahmasthan",
    "weight": 20,
    "description": "The CENTER zone must remain open — it is the energy nucleus of the home.",
    "obstructions": {
        "OBSTRUCTED_BY_TOILET": {
            "penalty": 20,
            "severity": Severity.CRITICAL_DEFECT,
            "remedy": "Major Vastu defect: place raw sea salt in a brass bowl inside the toilet; keep door always closed.",
        },
        "OBSTRUCTED_BY_WALL": {
            "penalty": 15,
            "severity": Severity.MAJOR_DEFECT,
            "remedy": "Avoid placing heavy furniture or load-bearing structures in the CENTER zone.",
        },
        "OBSTRUCTED_BY_STAIRS": {
            "penalty": 15,
            "severity": Severity.MAJOR_DEFECT,
            "remedy": "Place a Vastu pyramid under the staircase; keep area clean and well-lit.",
        },
    },
}

FIXTURE_RULES = {
    "COOKING_STOVE": {
        "category": "Kitchen",
        "weight": 15,
        "element": "Fire",
        "ideal": {
            "zones": ["SE"],
            "description": "SE is the fire zone — ideal for cooking stove.",
        },
        "acceptable": {
            "zones": ["NW"],
            "penalty": 8,
            "description": "NW is acceptable — slight fire-air energy mismatch.",
            "remedy": "Place a small red light near the stove to strengthen fire energy.",
        },
        "prohibited": {
            "NE": {
                "penalty": 15,
                "description": "Fire-water conflict — NE is the water zone.",
                "remedy": "Place a yellow marble slab beneath the stove to neutralize fire-water conflict.",
            },
            "SW": {
                "penalty": 12,
                "description": "SW stove causes earth-fire imbalance.",
                "remedy": "Place a copper plate beneath the stove; face East while cooking.",
            },
            "CENTER": {
                "penalty": 15,
                "description": "Stove in Brahmasthan disrupts central energy.",
                "remedy": "Relocate stove; use a Vastu copper strip to define energy zones.",
            },
            "N": {
                "penalty": 10,
                "description": "North is the water zone — fire here causes conflict.",
                "remedy": "Place a green plant between stove and northern wall.",
            },
        },
    },
    "TOILET_COMMODE": {
        "category": "Bathroom",
        "weight": 15,
        "element": "Water/Waste",
        "ideal": {
            "zones": ["NW", "W", "S"],
            "description": "NW/W/S are acceptable zones for waste water disposal.",
        },
        "acceptable": {
            "zones": [],
            "penalty": 0,
            "description": "",
            "remedy": "",
        },
        "prohibited": {
            "NE": {
                "penalty": 15,
                "description": "Critical defect — NE toilet contaminates the sacred water-prayer zone.",
                "remedy": "Major Vastu Defect: place raw sea salt in a brass bowl inside toilet; keep door closed at all times.",
            },
            "CENTER": {
                "penalty": 15,
                "description": "Toilet in Brahmasthan — most severe Vastu defect.",
                "remedy": "Keep door closed; place Vastu pyramids on all four walls inside; use sea salt remedy.",
            },
            "SE": {
                "penalty": 10,
                "description": "SE toilet creates fire-water conflict.",
                "remedy": "Paint toilet walls light blue; place a copper helix inside.",
            },
            "E": {
                "penalty": 10,
                "description": "East toilet blocks morning solar energy.",
                "remedy": "Keep toilet door closed; place a green plant outside the toilet door.",
            },
        },
    },
    "BED_HEADBOARD": {
        "category": "Bedroom",
        "weight": 10,
        "element": "Earth",
        "ideal": {
            "zones": ["S", "SW", "W"],
            "description": "Head facing South/SW promotes restful sleep per Vastu.",
        },
        "acceptable": {
            "zones": ["E"],
            "penalty": 5,
            "description": "East is acceptable — promotes early rising but lighter sleep.",
            "remedy": "Use warm-toned bedding to balance solar energy from the East.",
        },
        "prohibited": {
            "N": {
                "penalty": 10,
                "description": "Head pointing North creates magnetic field conflict — disrupts sleep.",
                "remedy": "Rotate bed so headboard faces South or West.",
            },
            "NE": {
                "penalty": 8,
                "description": "NE headboard causes restlessness and disturbed sleep.",
                "remedy": "Rotate bed; place a Vastu crystal ball in the NE corner of the bedroom.",
            },
        },
    },
    "WASHING_MACHINE": {
        "category": "Utility",
        "weight": 5,
        "element": "Water",
        "ideal": {
            "zones": ["NW", "W"],
            "description": "NW/W zones are ideal for water-based appliances.",
        },
        "acceptable": {
            "zones": ["SE"],
            "penalty": 3,
            "description": "SE is acceptable with mitigation.",
            "remedy": "Place a blue mat beneath the washing machine.",
        },
        "prohibited": {
            "NE": {
                "penalty": 5,
                "description": "NE washing machine disturbs the sacred northeast water energy.",
                "remedy": "Relocate or place copper coins beneath the machine.",
            },
            "SW": {
                "penalty": 5,
                "description": "SW washing machine causes earth-water imbalance.",
                "remedy": "Place a yellow mat beneath the machine; keep area dry.",
            },
        },
    },
}

ROOM_ZONE_RULES = {
    "KITCHEN": {
        "ideal": ["SE"],
        "acceptable": ["NW"],
        "prohibited": ["NE", "SW", "CENTER"],
        "weight": 8,
    },
    "MASTER_BEDROOM": {
        "ideal": ["SW", "S", "W"],
        "acceptable": ["NW", "SE"],
        "prohibited": ["NE", "CENTER"],
        "weight": 8,
    },
    "BATHROOM_TOILET": {
        "ideal": ["NW", "W", "S"],
        "acceptable": ["SE"],
        "prohibited": ["NE", "CENTER", "E"],
        "weight": 6,
    },
    "LIVING_ROOM": {
        "ideal": ["N", "NE", "E"],
        "acceptable": ["NW", "SE"],
        "prohibited": ["SW"],
        "weight": 5,
    },
    "GUEST_BEDROOM": {
        "ideal": ["NW", "N", "E"],
        "acceptable": ["SE", "W"],
        "prohibited": ["SW", "CENTER"],
        "weight": 5,
    },
    "DINING_ROOM": {
        "ideal": ["W", "E"],
        "acceptable": ["N", "S"],
        "prohibited": ["CENTER"],
        "weight": 4,
    },
}

CONFLICT_RULES = [
    {
        "name": "Fire-Water Conflict",
        "fixtures": ("COOKING_STOVE", "WATER_SINK"),
        "condition": "same_zone",
        "penalty": 5,
        "severity": Severity.MINOR_DEFECT,
        "description": "Stove and sink in the same zone creates a fire-water energy conflict.",
        "remedy": "Place a wooden partition or potted plant between stove and sink.",
    },
    {
        "name": "Toilet-Kitchen Adjacency",
        "fixtures": ("TOILET_COMMODE", "COOKING_STOVE"),
        "condition": "same_zone",
        "penalty": 10,
        "severity": Severity.MAJOR_DEFECT,
        "description": "Toilet and kitchen in the same zone — severe hygiene and energy conflict.",
        "remedy": "Ensure solid wall separation; place sea salt bowls in both spaces.",
    },
]


# ---------------------------------------------------------------------------
# Audit Engine
# ---------------------------------------------------------------------------

class VastuAuditor:
    def __init__(self):
        self.entrance_rule = ENTRANCE_RULE
        self.brahmasthan_rule = BRAHMASTHAN_RULE
        self.fixture_rules = FIXTURE_RULES
        self.room_rules = ROOM_ZONE_RULES
        self.conflict_rules = CONFLICT_RULES

    def _audit_entrance(self, data: ComplexFloorPlanExtraction) -> list[AuditFinding]:
        findings = []
        
        # Guard against un-detected or ambiguous main entrance
        if not data.main_entrance:
            findings.append(AuditFinding(
                element="Main Entrance",
                zone="UNKNOWN",
                severity=Severity.MINOR_DEFECT,
                penalty=0,
                description="Main front entrance door could not be conclusively identified on the floor plan.",
                remedy="Ensure the floor plan clearly displays the primary entry door and foyer.",
                category=self.entrance_rule["category"],
            ))
            return findings

        zone = data.main_entrance.zone
        rule = self.entrance_rule

        if zone in rule["ideal"]["zones"]:
            findings.append(AuditFinding(
                element="Main Entrance", zone=zone,
                severity=Severity.PASS, penalty=0,
                description=rule["ideal"]["description"],
                category=rule["category"],
            ))
        elif zone in rule["acceptable"]["zones"]:
            acc = rule["acceptable"]
            findings.append(AuditFinding(
                element="Main Entrance", zone=zone,
                severity=Severity.MINOR_DEFECT, penalty=acc["penalty"],
                description=acc["description"], remedy=acc["remedy"],
                category=rule["category"],
            ))
        elif zone in rule["prohibited"]:
            proh = rule["prohibited"][zone]
            findings.append(AuditFinding(
                element="Main Entrance", zone=zone,
                severity=Severity.CRITICAL_DEFECT if proh["penalty"] >= 25 else Severity.MAJOR_DEFECT,
                penalty=proh["penalty"],
                description=proh["description"], remedy=proh["remedy"],
                category=rule["category"],
            ))

        return findings

    def _audit_brahmasthan(self, data: ComplexFloorPlanExtraction) -> list[AuditFinding]:
        findings = []
        status = data.brahmasthan_status
        rule = self.brahmasthan_rule

        if status == "CLEAR":
            findings.append(AuditFinding(
                element="Brahmasthan (Center Zone)", zone="CENTER",
                severity=Severity.PASS, penalty=0,
                description="Center zone is clear — energy nucleus unobstructed.",
                category=rule["category"],
            ))
        else:
            obs = rule["obstructions"].get(status, {})
            findings.append(AuditFinding(
                element="Brahmasthan (Center Zone)", zone="CENTER",
                severity=obs.get("severity", Severity.MAJOR_DEFECT),
                penalty=obs.get("penalty", 15),
                description=rule["description"],
                remedy=obs.get("remedy"),
                category=rule["category"],
            ))

        return findings

    def _audit_fixtures(self, data: ComplexFloorPlanExtraction) -> list[AuditFinding]:
        findings = []

        for fixture in data.fixtures:
            rule = self.fixture_rules.get(fixture.name)
            if not rule:
                continue

            zone = fixture.zone
            element_label = f"{fixture.name.replace('_', ' ').title()}"

            if zone in rule["ideal"]["zones"]:
                findings.append(AuditFinding(
                    element=element_label, zone=zone,
                    severity=Severity.PASS, penalty=0,
                    description=rule["ideal"]["description"],
                    category=rule["category"],
                ))
            elif zone in rule["acceptable"]["zones"]:
                acc = rule["acceptable"]
                findings.append(AuditFinding(
                    element=element_label, zone=zone,
                    severity=Severity.MINOR_DEFECT, penalty=acc["penalty"],
                    description=acc["description"], remedy=acc["remedy"],
                    category=rule["category"],
                ))
            elif zone in rule["prohibited"]:
                proh = rule["prohibited"][zone]
                findings.append(AuditFinding(
                    element=element_label, zone=zone,
                    severity=Severity.MAJOR_DEFECT if proh["penalty"] < 15 else Severity.CRITICAL_DEFECT,
                    penalty=proh["penalty"],
                    description=proh["description"], remedy=proh["remedy"],
                    category=rule["category"],
                ))

        return findings

    def _audit_room_zones(self, data: ComplexFloorPlanExtraction) -> list[AuditFinding]:
        findings = []

        for room in data.rooms:
            rule = self.room_rules.get(room.room_type)
            if not rule:
                continue

            zone = room.primary_zone
            label = f"{room.room_name} ({room.room_type.replace('_', ' ').title()})"

            if zone in rule["ideal"]:
                findings.append(AuditFinding(
                    element=label, zone=zone,
                    severity=Severity.PASS, penalty=0,
                    description=f"Ideal zone for {room.room_type.replace('_', ' ').lower()}.",
                    category="Room Zones",
                ))
            elif zone in rule["acceptable"]:
                findings.append(AuditFinding(
                    element=label, zone=zone,
                    severity=Severity.MINOR_DEFECT, penalty=3,
                    description=f"Acceptable but not ideal zone for {room.room_type.replace('_', ' ').lower()}.",
                    remedy="Enhance zone energy with appropriate color scheme and plants.",
                    category="Room Zones",
                ))
            elif zone in rule["prohibited"]:
                findings.append(AuditFinding(
                    element=label, zone=zone,
                    severity=Severity.MAJOR_DEFECT, penalty=rule["weight"],
                    description=f"Prohibited zone for {room.room_type.replace('_', ' ').lower()} — causes energy imbalance.",
                    remedy="Consult a Vastu expert for structural or symbolic remedies.",
                    category="Room Zones",
                ))

        return findings

    def _audit_conflicts(self, data: ComplexFloorPlanExtraction) -> list[AuditFinding]:
        findings = []
        fixture_map = {f.name: f for f in data.fixtures}

        for rule in self.conflict_rules:
            a_name, b_name = rule["fixtures"]
            a = fixture_map.get(a_name)
            b = fixture_map.get(b_name)

            if not a or not b:
                continue

            if rule["condition"] == "same_zone" and a.zone == b.zone:
                findings.append(AuditFinding(
                    element=rule["name"], zone=a.zone,
                    severity=rule["severity"], penalty=rule["penalty"],
                    description=rule["description"], remedy=rule["remedy"],
                    category="Element Conflicts",
                ))

        return findings

    def audit(self, data: ComplexFloorPlanExtraction):
        all_findings: list[AuditFinding] = []

        all_findings.extend(self._audit_entrance(data))
        all_findings.extend(self._audit_brahmasthan(data))
        all_findings.extend(self._audit_fixtures(data))
        all_findings.extend(self._audit_room_zones(data))
        all_findings.extend(self._audit_conflicts(data))

        total_penalty = sum(f.penalty for f in all_findings)
        final_score = max(0, 100 - total_penalty)

        # Build category summary
        categories = {}
        for f in all_findings:
            cat = f.category
            if cat not in categories:
                categories[cat] = {"pass": 0, "issues": 0, "penalty": 0}
            if f.severity == Severity.PASS:
                categories[cat]["pass"] += 1
            else:
                categories[cat]["issues"] += 1
                categories[cat]["penalty"] += f.penalty

        return final_score, all_findings, categories
