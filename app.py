import html
import io
import re
from collections import defaultdict
from urllib.parse import quote

import streamlit as st
from PIL import Image

from extractor import scan_medicines
from validator import triage

st.set_page_config(
    page_title="MedStrip - Medicine Packaging Reader & Scheduler",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="auto",
)


# ---------- helpers ----------
def safe(text) -> str:
    """Safely escapes text for safe injection inside HTML blocks."""
    if text is None:
        return ""
    return html.escape(str(text))


def inject_css():
    """Injects modern, trustworthy healthcare styling without fragile Streamlit class selectors."""
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Hero Banner */
    .med-hero {
        background: linear-gradient(135deg, #0F766E 0%, #115E59 100%);
        color: #FFFFFF;
        padding: 24px 22px;
        border-radius: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px -2px rgba(15, 118, 110, 0.2);
    }
    .med-hero-pill {
        display: inline-block;
        background: rgba(255, 255, 255, 0.16);
        color: #CCFBF1;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-bottom: 8px;
    }
    .med-hero h1 {
        font-size: 1.95rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }
    .med-hero-tagline {
        font-size: 0.95rem;
        color: #E6FFFA;
        margin: 0 0 16px 0;
        line-height: 1.45;
    }
    .med-hero-steps {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .hero-step {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.82rem;
        color: #F0FDFA;
    }
    .hero-step strong {
        color: #FFFFFF;
        font-weight: 600;
    }
    .hero-arrow {
        color: #99F6E4;
        font-size: 0.75rem;
        opacity: 0.8;
    }

    /* Medical Disclaimer Banner */
    .med-disclaimer {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        background-color: #FEF3C7;
        border-left: 4px solid #D97706;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .disclaimer-icon {
        font-size: 1.3rem;
        line-height: 1.2;
    }
    .disclaimer-body {
        font-size: 0.84rem;
        color: #78350F;
        line-height: 1.4;
    }

    /* Section Stage Headers */
    .stage-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 24px;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #E2E8F0;
    }
    .stage-badge {
        background: #0D9488;
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .stage-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }

    /* Medicine Cards Elements */
    .med-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid #F1F5F9;
    }
    .med-card-name {
        font-size: 1.12rem;
        font-weight: 700;
        color: #0F172A;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Status Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .status-pill-ok {
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    .status-pill-confirm {
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
    }
    .status-pill-retake {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }

    /* Chips */
    .chips-section {
        margin: 8px 0 10px 0;
    }
    .chips-label {
        font-size: 0.74rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
        display: block;
    }
    .med-chip {
        display: inline-block;
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
        border-radius: 9999px;
        padding: 3px 10px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-right: 5px;
        margin-bottom: 5px;
    }

    /* Reason Alerts & Muted Notes */
    .med-reason-alert {
        background-color: #FFFBEB;
        border-left: 3px solid #F59E0B;
        padding: 6px 10px;
        border-radius: 6px;
        color: #92400E;
        font-size: 0.82rem;
        margin: 4px 0 6px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .med-muted-note {
        color: #64748B;
        font-size: 0.8rem;
        font-style: italic;
        margin: 3px 0 6px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Retake alert box */
    .med-retake-box {
        background-color: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 4px solid #EF4444;
        border-radius: 8px;
        padding: 10px 12px;
        color: #991B1B;
        font-size: 0.85rem;
        margin: 6px 0 8px 0;
    }

    /* Duplicate Ingredient Alert Card (Most prominent) */
    .dup-alert-card {
        background: #FEF2F2;
        border: 2px solid #EF4444;
        border-radius: 12px;
        padding: 16px 18px;
        margin: 20px 0;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.16);
    }
    .dup-alert-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    .dup-alert-icon {
        font-size: 1.6rem;
        line-height: 1;
    }
    .dup-alert-title {
        color: #991B1B;
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .dup-alert-subtitle {
        color: #B91C1C;
        font-size: 0.82rem;
        margin: 2px 0 0 0;
    }
    .dup-item-box {
        background: #FFFFFF;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 10px 12px;
        margin-top: 8px;
    }
    .dup-item-head {
        color: #991B1B;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .dup-item-explanation {
        color: #374151;
        font-size: 0.82rem;
        margin-top: 3px;
        line-height: 1.4;
    }

    /* Timetable Card */
    .timetable-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px;
        margin: 14px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .timetable-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 10px;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 12px;
    }
    .timetable-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
    }
    .timetable-section {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .timetable-slot-name {
        font-size: 0.9rem;
        font-weight: 700;
        color: #1E293B;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }
    .timetable-med-row {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 7px 10px;
        margin-bottom: 6px;
        font-size: 0.86rem;
        color: #1E293B;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
    }
    .timetable-med-row:last-child {
        margin-bottom: 0;
    }
    .food-instruction-tag {
        font-size: 0.72rem;
        font-weight: 600;
        background: #E0F2FE;
        color: #0369A1;
        border-radius: 9999px;
        padding: 2px 8px;
        white-space: nowrap;
    }

    /* WhatsApp button customization */
    a[href*="wa.me"] {
        background-color: #25D366 !important;
        color: #FFFFFF !important;
        border: 1px solid #25D366 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(37, 211, 102, 0.25) !important;
    }
    a[href*="wa.me"]:hover {
        background-color: #1EBE5D !important;
        border-color: #1EBE5D !important;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.35) !important;
    }

    /* Friendly Empty States */
    .empty-state {
        background: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 24px 16px;
        text-align: center;
        color: #64748B;
        margin: 12px 0;
    }
    .empty-state-icon {
        font-size: 2rem;
        margin-bottom: 6px;
        display: block;
    }
    .empty-state-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 3px;
    }
    .empty-state-text {
        font-size: 0.82rem;
        max-width: 400px;
        margin: 0 auto;
        line-height: 1.4;
    }

    /* Footer */
    .med-footer {
        text-align: center;
        padding: 28px 10px 10px 10px;
        color: #94A3B8;
        font-size: 0.78rem;
        line-height: 1.5;
        border-top: 1px solid #E2E8F0;
        margin-top: 36px;
    }

    /* Responsive Design */
    
    /* Mobile devices (up to 640px) */
    @media (max-width: 640px) {
        .med-hero { padding: 20px 16px; }
        .med-hero h1 { font-size: 1.5rem; }
        .med-hero-tagline { font-size: 0.85rem; }
        .med-hero-steps { flex-direction: column; align-items: flex-start; gap: 6px; }
        .hero-arrow { display: none; }
        .hero-step { font-size: 0.78rem; }
        
        .med-disclaimer { flex-direction: column; gap: 8px; padding: 10px 12px; }
        .disclaimer-icon { font-size: 1.1rem; }
        .disclaimer-body { font-size: 0.78rem; }
        
        .stage-header { flex-wrap: wrap; margin-top: 20px; margin-bottom: 10px; }
        .stage-badge { font-size: 0.7rem; padding: 2px 6px; }
        .stage-title { font-size: 1rem; }
        
        .med-card-header { flex-direction: column; align-items: flex-start; gap: 6px; }
        .med-card-name { font-size: 1rem; }
        .status-pill { font-size: 0.7rem; padding: 2px 8px; }
        
        .chips-label { font-size: 0.7rem; }
        .med-chip { font-size: 0.72rem; padding: 2px 8px; margin-right: 4px; margin-bottom: 4px; }
        
        .med-reason-alert { font-size: 0.76rem; padding: 5px 8px; }
        .med-muted-note { font-size: 0.76rem; }
        
        .med-retake-box { font-size: 0.8rem; padding: 8px 10px; }
        
        .dup-alert-card { padding: 14px 16px; margin: 16px 0; }
        .dup-alert-icon { font-size: 1.4rem; }
        .dup-alert-title { font-size: 0.95rem; }
        .dup-alert-subtitle { font-size: 0.76rem; }
        .dup-item-box { padding: 8px 10px; }
        .dup-item-head { font-size: 0.82rem; }
        .dup-item-explanation { font-size: 0.76rem; }
        
        .timetable-card { padding: 14px; margin: 12px 0; }
        .timetable-header { flex-direction: column; align-items: flex-start; gap: 6px; }
        .timetable-title { font-size: 0.95rem; }
        .timetable-section { padding: 10px 12px; }
        .timetable-slot-name { font-size: 0.82rem; flex-direction: column; align-items: flex-start; gap: 4px; }
        .timetable-med-row { font-size: 0.8rem; padding: 6px 8px; flex-direction: column; align-items: flex-start; gap: 4px; }
        .food-instruction-tag { font-size: 0.68rem; padding: 1px 6px; }
        
        .empty-state { padding: 20px 12px; }
        .empty-state-icon { font-size: 1.6rem; }
        .empty-state-title { font-size: 0.85rem; }
        .empty-state-text { font-size: 0.76rem; }
        
        .med-footer { padding: 24px 8px 8px 8px; font-size: 0.72rem; }
    }
    
    /* Tablets (641px to 768px) */
    @media (min-width: 641px) and (max-width: 768px) {
        .med-hero h1 { font-size: 1.7rem; }
        .med-hero-tagline { font-size: 0.9rem; }
        .med-hero-steps { gap: 6px; }
        .hero-step { font-size: 0.8rem; }
        
        .stage-title { font-size: 1.05rem; }
        .med-card-name { font-size: 1.05rem; }
        
        .timetable-med-row { font-size: 0.82rem; }
    }
    
    /* Small laptops (769px to 1024px) */
    @media (min-width: 769px) and (max-width: 1024px) {
        .med-hero h1 { font-size: 1.8rem; }
        .timetable-card { padding: 16px; }
    }
    
    /* Large laptops and desktops (1025px and above) */
    @media (min-width: 1025px) {
        .med-hero { padding: 28px 24px; }
        .med-hero h1 { font-size: 2rem; }
        .timetable-card { padding: 20px; }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_stage_header(number: int, title: str):
    """Renders a clean, numbered section heading."""
    st.markdown(
        f"""
    <div class="stage-header">
        <span class="stage-badge">Stage {number}</span>
        <h3 class="stage-title">{safe(title)}</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )


def format_schedule_item(item_text: str) -> tuple[str, str]:
    """Extracts medicine name and food instruction for clean timetable display."""
    m = re.match(r"^(.*?)\s*\((.*?)\)$", item_text)
    if m:
        return safe(m.group(1)), safe(m.group(2))
    return safe(item_text), ""


# ---------- core logic (kept exactly as required) ----------
@st.cache_data(show_spinner=False, ttl=3600, max_entries=50)
def cached_scan(image_bytes: bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((1600, 1600))                 # smaller upload = faster, cheaper
    result = scan_medicines(img)
    if result is None:
        raise ValueError("Reply did not match schema")   # errors are not cached
    return result


def base_name(ingredient: str) -> str:
    s = ingredient.lower()
    s = re.sub(r"\d+(\.\d+)?\s*(mg|mcg|µg|g|ml|iu|%)", "", s)
    s = re.sub(r"\b(ip|bp|usp|anhydrous|hydrochloride|hcl)\b", "", s)
    s = re.sub(r"[^a-z ]", " ", s)
    return " ".join(s.split())


def find_duplicates(meds):
    seen = defaultdict(set)
    for m in meds:
        label = m.brand_name or m.generic_name
        for ing in m.active_ingredients:
            key = base_name(ing)
            if key:
                seen[key].add(label)
    return {k: sorted(v) for k, v in seen.items() if len(v) > 1}


def build_message(name, schedule, dups):
    lines = [f"MedStrip schedule for {name or 'you'}"]
    for slot, items in schedule.items():
        if items:
            lines.append(f"\n{slot}:")
            lines += [f"- {x}" for x in items]
    if dups:
        lines.append("\nWARNING - same ingredient in more than one medicine:")
        for ing, labels in dups.items():
            lines.append(f"- {ing.title()}: {', '.join(labels)}")
    lines.append("\nBased on printed pack text and the timings you entered. "
                 "Not medical advice - confirm with your doctor or pharmacist.")
    return "\n".join(lines)[:1500]


# ---------- inject design styling ----------
inject_css()

# ---------- sidebar: how it works, privacy, limitations ----------
with st.sidebar:
    st.markdown(
        """
    <div style="text-align: center; padding: 8px 0 14px 0;">
        <span style="font-size: 2.2rem;">💊</span>
        <h2 style="margin: 4px 0 0 0; color: #0F766E; font-size: 1.25rem; font-weight: 800;">MedStrip</h2>
        <span style="font-size: 0.78rem; color: #64748B;">Prescription Vision Assistant</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📋 How It Works")
    st.markdown(
        "1. **Snap:** Photograph your medicine strips or packaging.\n"
        "2. **Review:** AI extracts brand names, active ingredients, and detects ingredient overlaps.\n"
        "3. **Schedule:** Pick your morning, afternoon, or night timings.\n"
        "4. **Share:** Send to WhatsApp with one click or download as a text file."
    )

    st.markdown("---")
    st.markdown("### 📸 Tips for Best Scans")
    st.markdown(
        "- **Avoid glare:** Tilt metallic foil packs slightly away from direct flash.\n"
        "- **Keep it flat:** Smooth bent packaging so small text is readable.\n"
        "- **Focus on text:** Ensure brand name and active strength are in focus."
    )

    st.markdown("---")
    st.markdown("### 🔒 Privacy & Data Safety")
    st.info(
        "**Photos are processed in memory and never stored.** "
        "No images or personal medical data are kept on any disk or server."
    )

    st.markdown("### ⚠️ Honest Limitations")
    st.caption(
        "• AI vision can misread creased, blurry, or low-contrast packaging.\n\n"
        "• MedStrip only transcribes printed text; it is **not medical advice**.\n\n"
        "• Always follow your doctor's official prescription and consult a licensed pharmacist."
    )

# ---------- hero header ----------
st.markdown(
    """
<div class="med-hero">
    <div class="med-hero-pill">Health Vision AI</div>
    <h1>💊 MedStrip</h1>
    <div class="med-hero-tagline">
        Photograph your medicine strips or boxes. MedStrip reads printed pack text, checks for overlapping ingredients, and helps you organize a safe daily routine.
    </div>
    <div class="med-hero-steps">
        <div class="hero-step"><span>📸</span> <strong>1. Snap</strong> Packaging</div>
        <span class="hero-arrow">➔</span>
        <div class="hero-step"><span>🔍</span> <strong>2. Review</strong> Ingredients</div>
        <span class="hero-arrow">➔</span>
        <div class="hero-step"><span>⏰</span> <strong>3. Schedule</strong> & Share</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- medical disclaimer (clearly visible near the top) ----------
st.markdown(
    """
<div class="med-disclaimer">
    <div class="disclaimer-icon">🩺</div>
    <div class="disclaimer-body">
        <strong>Medical Notice:</strong> MedStrip only reads printed packaging text using computer vision. It is <strong>not medical advice</strong>. Always follow your doctor's written prescription and confirm your schedule with a qualified pharmacist.
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------- 1. details ----------
render_stage_header(1, "1. Your details")
col_name, col_phone = st.columns(2)
with col_name:
    name = st.text_input("Your name", placeholder="e.g. Alex Smith")
with col_phone:
    number = st.text_input("WhatsApp number with country code", placeholder="+919876543210")


# ---------- 2. upload and scan ----------
render_stage_header(2, "2. Upload photos")
files = st.file_uploader(
    "Medicine strips or boxes",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    help="Upload clear photos of medicine strips, foil blisters, or packaging boxes."
)

if files and st.button("Scan medicines", type="primary", use_container_width=True):
    found, failed = [], []
    with st.spinner("Reading your photos with Gemini Vision... Analyzing active ingredients & packaging..."):
        for f in files:
            try:
                res = cached_scan(f.getvalue())
            except Exception:
                failed.append(f.name)
                continue
            for med in res.medicines:
                found.append((med, triage(med, res.image_quality)))
    st.session_state["found"] = found
    st.session_state["failed"] = failed

for fname in st.session_state.get("failed", []):
    st.error(f"Couldn't scan {fname}. The service may be busy, so try again in a minute.")

found = st.session_state.get("found", [])


# ---------- 3. review and set timings ----------
if found:
    render_stage_header(3, "3. Review and set timings")
    schedule = {"Morning": [], "Afternoon": [], "Night": []}

    for i, (med, t) in enumerate(found):
        with st.container(border=True):
            # Status badge mapping
            status_map = {
                "ok": ("status-pill-ok", "✓ Looks good"),
                "confirm": ("status-pill-confirm", "⚠️ Please check"),
                "retake": ("status-pill-retake", "✕ Retake photo"),
            }
            status_cls, status_txt = status_map.get(t["status"], ("status-pill-confirm", "⚠️ Please check"))
            med_name_escaped = safe(t["name"] or "Unknown medicine")

            st.markdown(
                f"""
            <div class="med-card-header">
                <div class="med-card-name">💊 {med_name_escaped}</div>
                <span class="status-pill {status_cls}">{status_txt}</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

            if t["status"] == "retake":
                st.markdown(
                    """
                <div class="med-retake-box">
                    <strong>Couldn't read this one clearly.</strong> Please retake a sharper photo with better lighting and no glare.
                </div>
                """,
                    unsafe_allow_html=True,
                )
                for u in t["unreadable_parts"]:
                    st.markdown(f'<div class="med-muted-note">🔍 <span><em>Not readable:</em> {safe(u)}</span></div>', unsafe_allow_html=True)
                continue

            if med.active_ingredients:
                chips_html = "".join([f'<span class="med-chip">{safe(ing)}</span>' for ing in med.active_ingredients])
                st.markdown(
                    f"""
                <div class="chips-section">
                    <span class="chips-label">Active Ingredients</span>
                    {chips_html}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            for r in t["reasons"]:
                st.markdown(f'<div class="med-reason-alert">⚠️ <span>{safe(r)}</span></div>', unsafe_allow_html=True)

            for u in t["unreadable_parts"]:
                st.markdown(f'<div class="med-muted-note">🔍 <span><em>Not readable:</em> {safe(u)}</span></div>', unsafe_allow_html=True)

            confirmed = True
            if t["status"] == "confirm":
                confirmed = st.checkbox("I checked this against the pack", key=f"conf{i}")

            st.caption("Daily Timing & Meal Instructions:")
            c1, c2, c3 = st.columns(3)
            picks = {
                "Morning": c1.checkbox("🌅 Morning", key=f"m{i}"),
                "Afternoon": c2.checkbox("☀️ Afternoon", key=f"a{i}"),
                "Night": c3.checkbox("🌙 Night", key=f"n{i}")
            }
            food = st.selectbox("Take", ["after food", "before food", "anytime"], key=f"f{i}")

            if confirmed:
                for slot, picked in picks.items():
                    if picked:
                        schedule[slot].append(f"{t['name']} ({food})")

    # ---------- prominent duplicate-ingredient warning ----------
    usable = [m for m, t in found if t["status"] != "retake"]
    dups = find_duplicates(usable)
    if dups:
        dup_boxes = ""
        for ing, labels in dups.items():
            escaped_ing = safe(ing.title())
            escaped_labels = safe(", ".join(labels))
            dup_boxes += f"""
            <div class="dup-item-box">
                <div class="dup-item-head">⚠️ {escaped_ing} appears in: {escaped_labels}</div>
                <div class="dup-item-explanation">
                    Taking these together may accidentally double your dose. Ask a pharmacist or your doctor before combining them.
                </div>
            </div>
            """
        st.markdown(
            f"""
        <div class="dup-alert-card">
            <div class="dup-alert-header">
                <span class="dup-alert-icon">⚠️</span>
                <div>
                    <h3 class="dup-alert-title">POTENTIAL INGREDIENT OVERLAP DETECTED</h3>
                    <p class="dup-alert-subtitle">Two or more of your scanned medicines share the same active ingredient.</p>
                </div>
            </div>
            {dup_boxes}
        </div>
        """,
            unsafe_allow_html=True,
        )

    # ---------- 4. schedule and share ----------
    render_stage_header(4, "4. Your schedule")
    if any(schedule.values()):
        message = build_message(name, schedule, dups)

        # Render structured timetable card
        timetable_sections = ""
        slots_info = [
            ("Morning", "🌅 Morning", "Breakfast / Early Day"),
            ("Afternoon", "☀️ Afternoon", "Lunch / Midday"),
            ("Night", "🌙 Night", "Dinner / Bedtime"),
        ]

        for slot_key, slot_label, slot_desc in slots_info:
            items = schedule.get(slot_key, [])
            if items:
                items_html = ""
                for itm in items:
                    med_name, food_inst = format_schedule_item(itm)
                    tag_html = f'<span class="food-instruction-tag">{food_inst}</span>' if food_inst else ""
                    items_html += f"""
                    <div class="timetable-med-row">
                        <span>💊 <strong>{med_name}</strong></span>
                        {tag_html}
                    </div>
                    """
                timetable_sections += f"""
                <div class="timetable-section">
                    <div class="timetable-slot-name">{slot_label} <span style="font-weight:400; font-size:0.78rem; color:#64748B;">({slot_desc})</span></div>
                    {items_html}
                </div>
                """

        recipient_label = safe(name or "You")
        timetable_card_html = f"""
        <div class="timetable-card">
            <div class="timetable-header">
                <div class="timetable-title">📅 Daily Schedule for {recipient_label}</div>
            </div>
            {timetable_sections}
        </div>
        """
        st.html(timetable_card_html)


        with st.expander("📋 View message text summary"):
            st.text(message)

        col_wa, col_dl = st.columns(2)
        digits = re.sub(r"\D", "", number)       # wa.me wants digits only
        with col_wa:
            if 10 <= len(digits) <= 15:
                st.link_button(
                    "💬 Send to WhatsApp",
                    f"https://wa.me/{digits}?text={quote(message)}",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.info("Enter your WhatsApp number in Stage 1 (like +919876543210) to enable direct sending.")
        with col_dl:
            st.download_button(
                "📥 Download schedule",
                message,
                file_name="medstrip_schedule.txt",
                use_container_width=True
            )
    else:
        st.markdown(
            """
        <div class="empty-state">
            <span class="empty-state-icon">⏰</span>
            <div class="empty-state-title">Select your dosage timings above</div>
            <div class="empty-state-text">
                Tick at least one time slot (Morning 🌅, Afternoon ☀️, or Night 🌙) in <strong>Stage 3</strong> to assemble your daily schedule.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
else:
    # Friendly empty state when no medicines are uploaded/scanned yet
    st.markdown(
        """
    <div class="empty-state">
        <span class="empty-state-icon">📸</span>
        <div class="empty-state-title">No medicines scanned yet</div>
        <div class="empty-state-text">
            Upload photos of your packaging or strips in <strong>Stage 2</strong> above and tap <strong>Scan medicines</strong> to review ingredients and build your schedule.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ---------- footer ----------
st.markdown(
    """
<div class="med-footer">
    <strong>MedStrip</strong> • Intelligent Medicine Packaging Reader<br>
    Photos are processed in-memory and not stored. Always follow official prescriptions and professional medical guidance.
</div>
""",
    unsafe_allow_html=True,
)