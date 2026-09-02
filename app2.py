import io
import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageOps

from src.grid_lens2 import overlay_vastu_grid
from src.detector2 import analyze_floor_plan
from src.engine2 import VastuAuditor, Severity

load_dotenv()

st.set_page_config(
    page_title="VastuLens",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styling & Restored Finding Card Palette ───────────────────────────────────
st.markdown("""
<style>
/* ── Score card ── */
.vm-score-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.vm-score-number {
    font-size: 2.75rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.04em;
    min-width: 3.5rem;
}
.vm-score-label {
    font-size: 0.75rem;
    color: #9ca3af;
    font-weight: 500;
    margin-top: 0.2rem;
}
.vm-score-verdict {
    font-size: 0.85rem;
    color: #374151;
    line-height: 1.6;
}
.vm-score-good { color: #16a34a; }
.vm-score-mid  { color: #d97706; }
.vm-score-bad  { color: #dc2626; }

/* ── Category pills ── */
.vm-cat-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0.75rem 0 1.25rem 0;
}
.vm-cat-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid;
    white-space: nowrap;
}
.pill-good { background: #f0fdf4; color: #15803d; border-color: #bbf7d0; }
.pill-warn { background: #fffbeb; color: #b45309; border-color: #fde68a; }
.pill-bad  { background: #fef2f2; color: #b91c1c; border-color: #fecaca; }

/* ── Finding cards (Restored Original Colors) ── */
.vm-finding {
    border-radius: 8px;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid;
}
.finding-pass     { background: #f0fdf4; border-color: #22c55e; }
.finding-minor    { background: #fffbeb; border-color: #f59e0b; }
.finding-major    { background: #fff7ed; border-color: #f97316; }
.finding-critical { background: #fef2f2; border-color: #ef4444; }

.finding-element { font-weight: 600; font-size: 0.85rem; color: #111827; }
.finding-zone {
    display: inline-block;
    background: #e5e7eb;
    color: #374151;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    margin-left: 0.35rem;
    vertical-align: middle;
    letter-spacing: 0.04em;
}
.finding-desc {
    font-size: 0.78rem;
    color: #4b5563;
    margin-top: 0.2rem;
    line-height: 1.5;
}
.finding-remedy {
    font-size: 0.75rem;
    color: #1d4ed8;
    margin-top: 0.3rem;
    padding-top: 0.3rem;
    border-top: 1px solid rgba(0,0,0,0.06);
    line-height: 1.5;
}

/* ── Section UI ── */
.vm-section-title {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
    margin: 0 0 0.6rem 0;
}
.vm-step {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    background: #111827;
    color: white;
    border-radius: 50%;
    font-size: 0.65rem;
    font-weight: 700;
    margin-right: 0.4rem;
    vertical-align: middle;
}
.vm-hint { font-size: 0.72rem; color: #9ca3af; margin-top: 0.4rem; line-height: 1.4; }

[data-testid="stHeader"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def score_color(score):
    return "vm-score-good" if score >= 75 else ("vm-score-mid" if score >= 50 else "vm-score-bad")

def score_verdict(score):
    if score >= 75:
        return "✦ Strong Vastu compliance. Minor refinements may further strengthen energy flow."
    elif score >= 50:
        return "◈ Moderate compliance — several defects detected. Remedies recommended."
    return "✗ Significant Vastu defects present. Immediate remedies advised."

def pill_class(penalty):
    return "pill-good" if penalty == 0 else ("pill-warn" if penalty <= 8 else "pill-bad")

def pill_icon(penalty):
    return "✓" if penalty == 0 else ("!" if penalty <= 8 else "✗")

def finding_card(item):
    css_map = {
        Severity.PASS: "finding-pass",
        Severity.MINOR_DEFECT: "finding-minor",
        Severity.MAJOR_DEFECT: "finding-major",
        Severity.CRITICAL_DEFECT: "finding-critical",
    }
    sev_labels = {
        Severity.MINOR_DEFECT: "Minor",
        Severity.MAJOR_DEFECT: "Major",
        Severity.CRITICAL_DEFECT: "Critical",
    }
    css = css_map.get(item.severity, "finding-minor")
    sev = sev_labels.get(item.severity, "")
    sev_html = f' <span style="font-size:0.68rem;font-weight:600;color:#9ca3af;">— {sev}</span>' if sev else ""
    remedy_html = (
        f'<div class="finding-remedy">💡 {item.remedy}</div>'
        if (item.remedy and item.severity != Severity.PASS) else ""
    )
    return f"""
    <div class="vm-finding {css}">
        <div class="finding-element">{item.element}{sev_html}<span class="finding-zone">{item.zone}</span></div>
        <div class="finding-desc">{item.description}</div>
        {remedy_html}
    </div>
    """

def load_sample_thumbnail(path: str, size=(400, 300)) -> Image.Image:
    """Forces all sample floor plans to render at an identical 4:3 aspect ratio."""
    img = Image.open(path).convert("RGB")
    return ImageOps.fit(img, size, Image.Resampling.LANCZOS)

def load_sample_as_buffer(path: str) -> io.BytesIO:
    with open(path, "rb") as f:
        buf = io.BytesIO(f.read())
    buf.seek(0)
    return buf

def uploaded_file_to_buffer(uploaded_file) -> io.BytesIO:
    buf = io.BytesIO(uploaded_file.read())
    buf.seek(0)
    return buf


# ── API Key Resolution ────────────────────────────────────────────────────────
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
else:
    st.error("Missing GEMINI_API_KEY. Set it in `.env` or Streamlit Cloud Secrets.")
    st.stop()


# ── Page Header ───────────────────────────────────────────────────────────────
st.title("🏗️ VastuLens")
st.caption("Upload a 2D floor plan — get a directional grid overlay and a scored Vastu compliance audit.")
st.divider()


# ── Session State ─────────────────────────────────────────────────────────────
if "active_image_buf" not in st.session_state:
    st.session_state.active_image_buf = None
if "active_image_name" not in st.session_state:
    st.session_state.active_image_name = None


# ── File Uploader ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your floor plan — JPG or PNG",
    type=["jpg", "jpeg", "png"],
    help="Upload a top-down 2D floor plan. North should face upward for accurate zone mapping."
)

if uploaded_file:
    st.session_state.active_image_buf = uploaded_file_to_buffer(uploaded_file)
    st.session_state.active_image_name = uploaded_file.name


# ── Sample Images (Equal Dimensions via PIL) ──────────────────────────────────
SAMPLES_DIR = "samples"
sample_files = []
if os.path.isdir(SAMPLES_DIR):
    sample_files = sorted([
        f for f in os.listdir(SAMPLES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])

if sample_files:
    st.markdown('<p class="vm-section-title">OR TRY A SAMPLE FLOOR PLAN</p>', unsafe_allow_html=True)

    visible = sample_files[:4]
    cols = st.columns(len(visible))

    for col, fname in zip(cols, visible):
        fpath = os.path.join(SAMPLES_DIR, fname)
        label = os.path.splitext(fname)[0].replace("_", " ").replace("-", " ").title()
        is_selected = st.session_state.active_image_name == fname

        with col:
            # Load uniform thumbnail
            thumb = load_sample_thumbnail(fpath)
            st.image(thumb, use_container_width=True)
            
            btn_label = f"✓ {label}" if is_selected else f"Use {label}"
            btn_type = "primary" if is_selected else "secondary"
            if st.button(btn_label, key=f"sample_{fname}", type=btn_type, use_container_width=True):
                st.session_state.active_image_buf = load_sample_as_buffer(fpath)
                st.session_state.active_image_name = fname
                st.rerun()


# ── Empty State ───────────────────────────────────────────────────────────────
if st.session_state.active_image_buf is None:
    st.info("👆 Upload a floor plan image above or select one of the sample plans to begin.")
    st.stop()

st.divider()

# ── Grid Overlay Engine Execution ─────────────────────────────────────────────
grid_buffer = overlay_vastu_grid(st.session_state.active_image_buf)


# ── Two-Column Layout: Audit (Left), Grid (Right) ──────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<p class="vm-section-title"><span class="vm-step">1</span>Run Audit</p>', unsafe_allow_html=True)

    if st.button("Run Vastu Compliance Audit", type="primary", use_container_width=True):

        with st.spinner("Reading floor plan with Gemini Vision…"):
            try:
                grid_buffer.seek(0)
                extraction = analyze_floor_plan(grid_buffer)
            except RuntimeError:
                st.error("Cannot process request at the moment, please try again later.")
                st.stop()

        with st.spinner("Scoring compliance…"):
            auditor = VastuAuditor()
            score, findings, categories = auditor.audit(extraction)

        # Score card
        st.markdown(f"""
        <div class="vm-score-card">
            <div>
                <div class="vm-score-number {score_color(score)}">{score:.0f}</div>
                <div class="vm-score-label">out of 100</div>
            </div>
            <div class="vm-score-verdict">{score_verdict(score)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Category pills
        pills = "".join(
            f'<span class="vm-cat-pill {pill_class(s["penalty"])}">'
            f'{pill_icon(s["penalty"])} {cat} {s["pass"]}/{s["pass"]+s["issues"]}</span>'
            for cat, s in categories.items()
        )
        st.markdown(f'<div class="vm-cat-row">{pills}</div>', unsafe_allow_html=True)

        # Findings grouped by category
        st.markdown('<p class="vm-section-title">Detailed Findings & Remedies</p>', unsafe_allow_html=True)

        grouped: dict[str, list] = {}
        for f in findings:
            grouped.setdefault(f.category, []).append(f)

        for category, items in grouped.items():
            issues = [i for i in items if i.severity != Severity.PASS]
            passes = [i for i in items if i.severity == Severity.PASS]
            label = f"{category} — {len(passes)} pass, {len(issues)} issue{'s' if len(issues) != 1 else ''}"
            with st.expander(label, expanded=(len(issues) > 0)):
                st.markdown("".join(finding_card(i) for i in items), unsafe_allow_html=True)

with right:
    st.markdown('<p class="vm-section-title"><span class="vm-step">2</span>Grid Overlay</p>', unsafe_allow_html=True)
    grid_buffer.seek(0)
    st.image(grid_buffer, use_container_width=True)
    st.markdown(
        '<p class="vm-hint">Red grid divides the plan into 9 directional zones. '
        'North is assumed to face upward.</p>',
        unsafe_allow_html=True
    )