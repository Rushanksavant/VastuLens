from typing import List, Optional
from pydantic import BaseModel
from enum import Enum


class Severity(str, Enum):
    PASS = "PASS"
    MINOR_DEFECT = "MINOR_DEFECT"
    MAJOR_DEFECT = "MAJOR_DEFECT"
    CRITICAL_DEFECT = "CRITICAL_DEFECT"


class AuditFinding(BaseModel):
    element: str
    zone: str
    severity: Severity
    penalty: int
    category: str
    description: str
    remedy: Optional[str] = None


class AuditResult(BaseModel):
    score: int
    total_penalty: int
    findings: List[AuditFinding]


class VastuAuditor:
    def run_audit(self, extraction, confirmed_markers: List) -> AuditResult:
        findings: List[AuditFinding] = []
        total_penalty = 0

        # 1. Brahmasthan Check
        b_status = getattr(extraction, "brahmasthan_status", "CLEAR")
        if b_status != "CLEAR":
            p = 25 if b_status == "OBSTRUCTED_BY_TOILET" else 15
            sev = Severity.CRITICAL_DEFECT if b_status == "OBSTRUCTED_BY_TOILET" else Severity.MAJOR_DEFECT
            findings.append(AuditFinding(
                element="Brahmasthan (Center)",
                zone="CENTER",
                severity=sev,
                penalty=p,
                category="Structural Integrity",
                description=f"Central Brahmasthan is {b_status.lower().replace('_', ' ')}. Must remain open and unencumbered.",
                remedy="Remove heavy structures/partitions or use copper pyramid chips if walls are non-removable."
            ))
            total_penalty += p
        else:
            findings.append(AuditFinding(
                element="Brahmasthan (Center)",
                zone="CENTER",
                severity=Severity.PASS,
                penalty=0,
                category="Structural Integrity",
                description="Central space is clear and open.",
                remedy=None
            ))

        # 2. Evaluate All 8 Marker Elements
        for marker in confirmed_markers:
            lbl = marker.label if hasattr(marker, 'label') else marker.get('label')
            zone = marker.zone if hasattr(marker, 'zone') else marker.get('zone')
            marker_id = marker.id if hasattr(marker, 'id') else marker.get('id')

            # MAIN ENTRANCE
            if lbl == "MAIN_ENTRANCE":
                if zone in ["NE", "N", "E"]:
                    findings.append(AuditFinding(element=f"Main Entrance ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Energy Inflow", description="Highly auspicious entrance orientation bringing prosperity."))
                elif zone in ["NW", "SE"]:
                    p = 10
                    findings.append(AuditFinding(element=f"Main Entrance ({marker_id})", zone=zone, severity=Severity.MINOR_DEFECT, penalty=p, category="Energy Inflow", description=f"Entrance in {zone} is secondary/moderately acceptable.", remedy="Place Brass Helix or Vastu Pyramids on the doorframe."))
                    total_penalty += p
                else: # SW, S, W
                    p = 20
                    findings.append(AuditFinding(element=f"Main Entrance ({marker_id})", zone=zone, severity=Severity.CRITICAL_DEFECT, penalty=p, category="Energy Inflow", description=f"Entrance in {zone} causes financial drain and instability.", remedy="Install Rahu/Yantra threshold, Lead helix, or double yellow/white strip lines."))
                    total_penalty += p

            # POOJA MANDIR
            elif lbl == "POOJA_MANDIR":
                if zone in ["NE", "N", "E"]:
                    findings.append(AuditFinding(element=f"Pooja Mandir ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Spiritual Energy", description="Pooja room is perfectly aligned in the divine Ishanya (NE) quadrant."))
                elif zone in ["CENTER", "NW"]:
                    p = 5
                    findings.append(AuditFinding(element=f"Pooja Mandir ({marker_id})", zone=zone, severity=Severity.MINOR_DEFECT, penalty=p, category="Spiritual Energy", description=f"Pooja Mandir in {zone} is acceptable if kept well-lit and clutter-free.", remedy="Ensure warm illumination and light colors."))
                    total_penalty += p
                else: # SW, S, SE, W
                    p = 15
                    findings.append(AuditFinding(element=f"Pooja Mandir ({marker_id})", zone=zone, severity=Severity.MAJOR_DEFECT, penalty=p, category="Spiritual Energy", description=f"Pooja Mandir in {zone} clashes with elemental zones (Fire/Earth).", remedy="Place idol on a raised wooden platform and keep copper water vessel nearby."))
                    total_penalty += p

            # COOKING STOVE
            elif lbl == "COOKING_STOVE":
                if zone == "SE":
                    findings.append(AuditFinding(element=f"Cooking Stove ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Fire Element", description="Kitchen stove positioned in ideal Agneya (SE) fire zone."))
                elif zone in ["NW", "E"]:
                    p = 10
                    findings.append(AuditFinding(element=f"Cooking Stove ({marker_id})", zone=zone, severity=Severity.MINOR_DEFECT, penalty=p, category="Fire Element", description=f"Stove in {zone} is acceptable secondary placement.", remedy="Ensure cook faces East while cooking."))
                    total_penalty += p
                else: # NE, SW, S, W, N, CENTER
                    p = 20
                    findings.append(AuditFinding(element=f"Cooking Stove ({marker_id})", zone=zone, severity=Severity.CRITICAL_DEFECT, penalty=p, category="Fire Element", description=f"Stove in {zone} causes severe Fire vs Water/Earth element conflict.", remedy="Place a green fluorite slab or yellow jasper gemstone plate under the cooktop base."))
                    total_penalty += p

            # TOILET COMMODE
            elif lbl == "TOILET_COMMODE":
                if zone in ["NW", "W", "S"]:
                    findings.append(AuditFinding(element=f"Toilet Commode ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Waste Disposal", description="Commode placed in proper negative energy disposal zone."))
                elif zone in ["SE", "E"]:
                    p = 12
                    findings.append(AuditFinding(element=f"Toilet Commode ({marker_id})", zone=zone, severity=Severity.MAJOR_DEFECT, penalty=p, category="Waste Disposal", description=f"Toilet in {zone} drains positive financial/growth energy.", remedy="Keep lid closed, add sea salt bowl, use copper metal tape around commode base."))
                    total_penalty += p
                else: # NE, SW, CENTER
                    p = 25
                    findings.append(AuditFinding(element=f"Toilet Commode ({marker_id})", zone=zone, severity=Severity.CRITICAL_DEFECT, penalty=p, category="Waste Disposal", description=f"Toilet in {zone} is a critical Vastu Dosh severely impacting health.", remedy="Install zinc/lead metal boundary strips in floor tiles around toilet base."))
                    total_penalty += p

            # BED HEADBOARD
            elif lbl == "BED_HEADBOARD":
                if zone in ["SW", "S", "W"]:
                    findings.append(AuditFinding(element=f"Bed Headboard ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Stability & Rest", description="Bed placed in ideal stability and grounding quadrant."))
                elif zone in ["NW", "E"]:
                    p = 8
                    findings.append(AuditFinding(element=f"Bed Headboard ({marker_id})", zone=zone, severity=Severity.MINOR_DEFECT, penalty=p, category="Stability & Rest", description=f"Bed in {zone} is acceptable for guest/children bedrooms.", remedy="Ensure head points South or East while sleeping."))
                    total_penalty += p
                else: # NE, SE
                    p = 15
                    findings.append(AuditFinding(element=f"Bed Headboard ({marker_id})", zone=zone, severity=Severity.MAJOR_DEFECT, penalty=p, category="Stability & Rest", description=f"Bed in {zone} causes restless sleep and high stress.", remedy="Use solid wooden headboard, avoid metal frames, and shift headboard to South wall."))
                    total_penalty += p

            # WATER SINK
            elif lbl == "WATER_SINK":
                if zone in ["NE", "N", "E"]:
                    findings.append(AuditFinding(element=f"Water Sink ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Water Element", description="Sink aligned with natural water element flow."))
                elif zone == "NW":
                    p = 5
                    findings.append(AuditFinding(element=f"Water Sink ({marker_id})", zone=zone, severity=Severity.MINOR_DEFECT, penalty=p, category="Water Element", description="Water sink in NW is moderately acceptable.", remedy="Keep sink clean and ensure zero pipe leakage."))
                    total_penalty += p
                else: # SE, SW, S, W
                    p = 12
                    findings.append(AuditFinding(element=f"Water Sink ({marker_id})", zone=zone, severity=Severity.MAJOR_DEFECT, penalty=p, category="Water Element", description=f"Sink in {zone} creates Fire-Water conflict (SE) or loss of stability (SW).", remedy="Place wooden partition or small green indoor plant between sink and stove."))
                    total_penalty += p

            # WASHING MACHINE
            elif lbl == "WASHING_MACHINE":
                if zone in ["NW", "SE"]:
                    findings.append(AuditFinding(element=f"Washing Machine ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Utility", description="Washing machine placed in proper utility/movement zone."))
                elif zone in ["W", "S", "E"]:
                    p = 5
                    findings.append(AuditFinding(element=f"Washing Machine ({marker_id})", zone=zone, severity=Severity.MINOR_DEFECT, penalty=p, category="Utility", description=f"Washing machine in {zone} is secondary placement.", remedy="Avoid running washing cycles during late evening/night hours."))
                    total_penalty += p
                else: # NE, SW, CENTER
                    p = 12
                    findings.append(AuditFinding(element=f"Washing Machine ({marker_id})", zone=zone, severity=Severity.MAJOR_DEFECT, penalty=p, category="Utility", description=f"Washing machine in {zone} churns and drains positive energy.", remedy="Keep machine covered with light green cloth when not in use."))
                    total_penalty += p

            # BALCONY DOOR
            elif lbl == "BALCONY_DOOR":
                if zone in ["NE", "N", "E"]:
                    findings.append(AuditFinding(element=f"Balcony Door ({marker_id})", zone=zone, severity=Severity.PASS, penalty=0, category="Light & Ventilation", description="Balcony door admits vital solar and magnetic energy."))
                elif zone in ["NW", "SE"]:
                    p = 5
                    findings.append(AuditFinding(element=f"Balcony Door ({marker_id})", zone=zone, severity=Severity.MINOR_DEFECT, penalty=p, category="Light & Ventilation", description=f"Balcony door in {zone} is acceptable.", remedy="Use translucent light curtains."))
                    total_penalty += p
                else: # SW, S, W
                    p = 12
                    findings.append(AuditFinding(element=f"Balcony Door ({marker_id})", zone=zone, severity=Severity.MAJOR_DEFECT, penalty=p, category="Light & Ventilation", description=f"Balcony in {zone} creates heavy energy leakage.", remedy="Use heavy dark curtains and keep door closed after sunset."))
                    total_penalty += p

        final_score = max(0, 100 - total_penalty)
        return AuditResult(
            score=final_score,
            total_penalty=total_penalty,
            findings=findings
        )