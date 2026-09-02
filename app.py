import streamlit as st
import os
from dotenv import load_dotenv

from src.grid_lens import overlay_vastu_grid
from src.detector import analyze_floor_plan
from src.engine import VastuAuditor

load_dotenv()
st.set_page_config(page_title="VastuMatrix", page_icon="🏗️", layout="wide")

st.title("🏗️ VastuLens — Deterministic Spatial Audit Engine")
st.caption("Multimodal Vision Extraction + Programmatic Rule Scoring")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please set it in your environment or Streamlit secrets.")
    st.stop()

uploaded_file = st.file_uploader("Upload Architectural Floor Plan", type=["jpg", "jpeg", "png"])

if uploaded_file:
    os.makedirs("outputs", exist_ok=True)
    input_path = os.path.join("outputs", uploaded_file.name)
    grid_output_path = os.path.join("outputs", f"grid_{uploaded_file.name}")

    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Spatial Grid Overlay")
        overlay_vastu_grid(input_path, grid_output_path)
        st.image(grid_output_path, use_container_width=True)

    with col2:
        st.subheader("2. Audit Execution")
        if st.button("Run Spatial Compliance Audit", type="primary"):
            with st.spinner("Extracting spatial vectors via Gemini Vision & running audit engine..."):
                extraction = analyze_floor_plan(grid_output_path)
                auditor = VastuAuditor()
                score, audit_log = auditor.audit(extraction)

                st.metric(label="Overall Vastu Compliance Score", value=f"{score:.1f} / 100")
                st.progress(score / 100)

                st.write("### Audit Findings & Recommendations")
                for item in audit_log:
                    severity = item.get("severity", "INFO")
                    element = item.get("element")
                    zone = item.get("zone", item.get("status", "N/A"))
                    remedy = item.get("remedy")

                    if severity == "PASS":
                        st.success(f"✅ **{element}** ({zone}) — Compliant")
                    elif severity in ["CRITICAL_DEFECT", "MAJOR_DEFECT"]:
                        st.error(f"❌ **{element}** ({zone}) — {severity}")
                        if remedy:
                            st.info(f"💡 **Remedy:** {remedy}")
                    else:
                        st.warning(f"⚠️ **{element}** ({zone}) — {severity}")
                        if remedy:
                            st.info(f"💡 **Remedy:** {remedy}")