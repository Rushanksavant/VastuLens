from src.utilities import ComplexFloorPlanExtraction

class VastuAuditor:
    def __init__(self):
        # Weighting: Entrance (35%), Center (20%), Critical Fixtures (25%), Room Zones (20%)
        self.rules = {
            "MAIN_ENTRANCE_DOOR": {
                "ideal": ["NE", "N", "E"],
                "acceptable": ["NW"],
                "prohibited": ["SW", "SE", "S"],
                "weight": 35,
                "remedy_sw": "Install Vastu lead helix/pyramid at entrance threshold.",
                "remedy_se": "Paint door frame light red/cream; place copper helix."
            },
            "BRAHMASTHAN": {
                "ideal": ["CLEAR"],
                "prohibited": ["OBSTRUCTED_BY_TOILET", "OBSTRUCTED_BY_WALL", "OBSTRUCTED_BY_STAIRS"],
                "weight": 20,
                "remedy": "Keep center space uncluttered; avoid placing heavy furniture in CENTER zone."
            },
            "COOKING_STOVE": {
                "ideal": ["SE"],
                "acceptable": ["NW"],
                "prohibited": ["NE", "CENTER", "SW"],
                "weight": 15,
                "remedy_ne": "Place a yellow marble slab beneath the stove to neutralize fire-water conflict."
            },
            "TOILET_COMMODE": {
                "ideal": ["NW", "W", "S"],
                "acceptable": [],
                "prohibited": ["NE", "CENTER", "SE"],
                "weight": 15,
                "remedy_ne": "Major Vastu Defect: Place raw sea salt in a brass bowl inside toilet; keep door closed."
            }
        }

    def audit(self, data: ComplexFloorPlanExtraction):
        audit_log = []
        total_penalty = 0

        # 1. Audit Main Entrance
        entrance_zone = data.main_entrance.zone
        ent_rule = self.rules["MAIN_ENTRANCE_DOOR"]
        if entrance_zone in ent_rule["ideal"]:
            audit_log.append({"element": "Main Entrance", "zone": entrance_zone, "severity": "PASS", "penalty": 0})
        elif entrance_zone in ent_rule["acceptable"]:
            audit_log.append({"element": "Main Entrance", "zone": entrance_zone, "severity": "MINOR_DEFECT", "penalty": 10})
            total_penalty += 10
        else:
            remedy = ent_rule.get(f"remedy_{entrance_zone.lower()}", "Apply door frame remedies.")
            audit_log.append({"element": "Main Entrance", "zone": entrance_zone, "severity": "CRITICAL_DEFECT", "penalty": ent_rule["weight"], "remedy": remedy})
            total_penalty += ent_rule["weight"]

        # 2. Audit Brahmasthan (Center)
        b_status = data.brahmasthan_status
        b_rule = self.rules["BRAHMASTHAN"]
        if b_status == "CLEAR":
            audit_log.append({"element": "Brahmasthan (Center Zone)", "status": b_status, "severity": "PASS", "penalty": 0})
        else:
            audit_log.append({"element": "Brahmasthan (Center Zone)", "status": b_status, "severity": "CRITICAL_DEFECT", "penalty": b_rule["weight"], "remedy": b_rule["remedy"]})
            total_penalty += b_rule["weight"]

        # 3. Audit Sub-Fixtures (Stove & Toilet)
        for fixture in data.fixtures:
            f_rule = self.rules.get(fixture.name)
            if not f_rule:
                continue
                
            if fixture.zone in f_rule["ideal"]:
                audit_log.append({"element": fixture.name, "zone": fixture.zone, "severity": "PASS", "penalty": 0})
            elif fixture.zone in f_rule["prohibited"]:
                remedy = f_rule.get(f"remedy_{fixture.zone.lower()}", "Consult Vastu expert for zone correction.")
                audit_log.append({"element": fixture.name, "zone": fixture.zone, "severity": "MAJOR_DEFECT", "penalty": f_rule["weight"], "remedy": remedy})
                total_penalty += f_rule["weight"]

        # 4. Check Fire vs. Water Proximity Conflict inside Kitchen
        stove = next((f for f in data.fixtures if f.name == "COOKING_STOVE"), None)
        sink = next((f for f in data.fixtures if f.name == "WATER_SINK"), None)
        if stove and sink and stove.zone == sink.zone:
            audit_log.append({
                "element": "Fire-Water Conflict", 
                "zone": stove.zone, 
                "severity": "MINOR_DEFECT", 
                "penalty": 5, 
                "remedy": "Place a wood element/partition between stove and water sink."
            })
            total_penalty += 5

        final_score = max(0, 100 - total_penalty)
        return final_score, audit_log