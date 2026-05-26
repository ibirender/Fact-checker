import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import json
import re
import os
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fact Tracker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: #000000 !important;
    color: #d4d4d8;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #000000 !important;
    min-height: 100vh;
}

[data-testid="stHeader"] { background: transparent !important; }

/* ── Hide bottom-right Streamlit toolbar & deploy button ── */
[data-testid="stToolbar"],
.stDeployButton,
#MainMenu,
footer,
[data-testid="stStatusWidget"],
[data-testid="manage-app-button"],
.viewerBadge_container__r5tak,
.viewerBadge_link__qRIco,
.st-emotion-cache-h4xjwg,          /* deploy badge wrapper */
.st-emotion-cache-czk5ss,
[class*="deployButton"],
[class*="viewerBadge"],
div[data-testid="stDecoration"],
div[class*="StatusWidget"],
section[data-testid="stSidebar"] ~ div > div:last-child,
.st-emotion-cache-1dp5vir,
iframe[title="streamlit_analytics"],
#bui3,
.stApp > header + div > div:last-child > div:last-child > div:last-child > div:last-child {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* Nuke the entire fixed footer region */
.st-emotion-cache-10trblm,
.st-emotion-cache-15zrgzn,
.reportview-container .main footer,
footer { visibility: hidden !important; display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: #1c1c1c; border-radius: 2px; }

/* ── Hero ── */
.hero-section {
    text-align: center;
    padding: 4rem 1rem 3rem;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse 60% 50% at 50% -10%, rgba(99,102,241,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 20% 80%, rgba(16,185,129,0.06) 0%, transparent 60%);
    pointer-events: none;
}

.main-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(4rem, 10vw, 8rem);
    letter-spacing: 6px;
    color: #f4f4f5;
    line-height: 0.95;
    margin-bottom: 1rem;
    position: relative;
}

.main-title span {
    background: linear-gradient(135deg, #6366f1 0%, #06b6d4 50%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #27272a;
    letter-spacing: 5px;
    text-transform: uppercase;
    margin-bottom: 0;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #18181b 30%, #18181b 70%, transparent);
    margin: 0 0 2.5rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #3f3f46;
    text-transform: uppercase;
    letter-spacing: 4px;
    margin-bottom: 0.85rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #0d0d0d;
}

/* ── Stat boxes ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #0d0d0d;
    border: 1px solid #0d0d0d;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 2rem;
}

.stat-box {
    background: #030303;
    padding: 1.4rem 1rem;
    text-align: center;
}

.stat-number {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: 2px;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.stat-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: #3f3f46;
    text-transform: uppercase;
    letter-spacing: 3px;
}

/* ── Claim cards ── */
.card {
    background: #030303;
    border-radius: 10px;
    padding: 1.4rem 1.6rem 1.4rem 1.5rem;
    margin-bottom: 0.75rem;
    position: relative;
    overflow: hidden;
    border: 1px solid #111111;
    transition: border-color 0.2s ease;
}

.card:hover { border-color: #1c1c1e; }

.card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 3px;
    border-radius: 10px 0 0 10px;
}

.card-verified::after   { background: #10b981; }
.card-inaccurate::after { background: #f59e0b; }
.card-false::after      { background: #ef4444; }

.card-verified   { border-color: #0d1f18; }
.card-inaccurate { border-color: #1f1a0d; }
.card-false      { border-color: #1f0d0d; }

/* Subtle top glow per status */
.card-verified::before   { content: ''; position: absolute; top:0;left:0;right:0; height:1px; background: linear-gradient(90deg, #10b981 0%, transparent 50%); }
.card-inaccurate::before { content: ''; position: absolute; top:0;left:0;right:0; height:1px; background: linear-gradient(90deg, #f59e0b 0%, transparent 50%); }
.card-false::before      { content: ''; position: absolute; top:0;left:0;right:0; height:1px; background: linear-gradient(90deg, #ef4444 0%, transparent 50%); }

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 0.2rem 0.75rem;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.badge-verified   { background: rgba(16,185,129,0.07);  color: #10b981; border: 1px solid rgba(16,185,129,0.15); }
.badge-inaccurate { background: rgba(245,158,11,0.07);  color: #f59e0b; border: 1px solid rgba(245,158,11,0.15); }
.badge-false      { background: rgba(239,68,68,0.07);   color: #ef4444; border: 1px solid rgba(239,68,68,0.15); }

.claim-text {
    font-size: 0.92rem;
    font-weight: 500;
    color: #a1a1aa;
    margin-bottom: 0.65rem;
    line-height: 1.6;
    padding-left: 0.4rem;
    border-left: 1px solid #18181b;
}

.explanation {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #3f3f46;
    line-height: 1.8;
    padding-left: 0.4rem;
}

/* ── Group headers ── */
.group-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 1.5rem 0 0.8rem;
    padding: 0.4rem 0;
}
.group-false      { color: #ef4444; border-bottom: 1px solid #1f0d0d; }
.group-inaccurate { color: #f59e0b; border-bottom: 1px solid #1f1a0d; }
.group-verified   { color: #10b981; border-bottom: 1px solid #0d1f18; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #030303 !important;
    border: 1px dashed #1c1c1e !important;
    border-radius: 10px !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #3f3f46 !important;
}
[data-testid="stFileUploader"] * {
    color: #3f3f46 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── Button ── */
div.stButton > button {
    width: 100%;
    background: #0a0a0a;
    color: #71717a;
    border: 1px solid #1c1c1e;
    padding: 0.9rem 2rem;
    border-radius: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.25s ease;
}

div.stButton > button:hover {
    background: #0f0f0f;
    border-color: #6366f1;
    color: #a5b4fc;
    box-shadow: 0 0 20px rgba(99,102,241,0.1), inset 0 0 20px rgba(99,102,241,0.03);
}

div.stButton > button:active {
    transform: scale(0.99);
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #030303 !important;
    border: 1px solid #1c1c1e !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] > div {
    border-top-color: #6366f1 !important;
}

/* ── Footer ── */
.footer-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #18181b;
    text-align: center;
    padding: 3rem 0 2rem;
    letter-spacing: 6px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    data = uploaded_file.read()
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def analyze_claims(text: str, api_key: str) -> list:
    """Groq or xAI API fact-checking with robust error handling"""
    prompt = f"""You are an expert fact-checker AI. Analyze the following document text and:

1. Extract ALL specific, verifiable claims — focus on:
   - Statistics and numbers (e.g., "X% of users", "revenue of $Y billion")
   - Dates and timelines
   - Named entities with attributed facts
   - Technical/scientific claims
   - Financial figures

2. For EACH claim, verify it using your knowledge and flag if it seems outdated or potentially false.

3. Classify each claim as:
   - "Verified" — claim is accurate and matches known data
   - "Inaccurate" — claim is outdated or partially wrong
   - "False" — claim is clearly incorrect or fabricated

Return a JSON array of objects. Each object must have EXACTLY these keys:
- "claim": the exact claim from the document (string)
- "status": one of "Verified", "Inaccurate", or "False" (string)
- "explanation": brief explanation of your verdict, including the correct fact if wrong (string)

Extract at least 5 claims. Return ONLY valid JSON. No markdown, no preamble.

Example response:
[
  {{"claim": "Example claim", "status": "Verified", "explanation": "This is correct because..."}}
]

Document text:
\"\"\"
{text[:6000]}
\"\"\"
"""

    try:
        if api_key.startswith("xai-"):
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "grok-3",
                "messages": [
                    {"role": "system", "content": "You are a fact-checking AI. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            res_json = response.json()
            raw = res_json["choices"][0]["message"]["content"].strip()
        else:
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a fact-checking AI. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content.strip()

        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"```$", "", raw)
        raw = re.sub(r"^```\s*", "", raw)

        parsed = json.loads(raw)

        if isinstance(parsed, dict):
            if "claims" in parsed:
                claims_data = parsed["claims"]
            elif "results" in parsed:
                claims_data = parsed["results"]
            else:
                claims_data = []
                for value in parsed.values():
                    if isinstance(value, list):
                        claims_data = value
                        break
        elif isinstance(parsed, list):
            claims_data = parsed
        else:
            claims_data = []

        validated = []
        for claim in claims_data:
            if isinstance(claim, dict) and all(k in claim for k in ["claim", "status", "explanation"]):
                validated.append(claim)

        return validated

    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return []


# ── API Key ───────────────────────────────────────────────────────────────────

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("""
        ⚠️ **API Key Missing**

        Please add your Groq API key to Streamlit Secrets:
        1. Go to your app settings on Streamlit Cloud
        2. Add secret: `GROQ_API_KEY` = `your_key_here`

        *For local development: set environment variable `GROQ_API_KEY`*
        """)
        st.stop()


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-section">
    <div class="main-title">FACT<span>TRACKER</span></div>
    <div class="subtitle">── Automated Claim Verification Engine ──</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">01 &nbsp;/&nbsp; Upload Document</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop a PDF to fact-check",
    type=["pdf"],
    label_visibility="collapsed",
)

if uploaded_file:
    st.success(f"✓ &nbsp; {uploaded_file.name}")

st.markdown("<br>", unsafe_allow_html=True)
run = st.button("ANALYZE & FACT-CHECK →")

if run:
    if not uploaded_file:
        st.error("⚠ Please upload a PDF document first.")
    else:
        with st.spinner("Extracting text from PDF..."):
            doc_text = extract_text_from_pdf(uploaded_file)

        if len(doc_text.strip()) < 50:
            st.error("⚠ Could not extract readable text. Try a text-based PDF.")
        else:
            with st.spinner("Running claim analysis..."):
                claims = analyze_claims(doc_text, api_key)

            if claims and len(claims) > 0:
                verified   = [c for c in claims if c.get("status") == "Verified"]
                inaccurate = [c for c in claims if c.get("status") == "Inaccurate"]
                false_     = [c for c in claims if c.get("status") == "False"]

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">02 &nbsp;/&nbsp; Summary</div>', unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#52525b">{len(claims)}</div>
                        <div class="stat-label">Total Claims</div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#10b981">{len(verified)}</div>
                        <div class="stat-label">Verified</div>
                    </div>""", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#f59e0b">{len(inaccurate)}</div>
                        <div class="stat-label">Inaccurate</div>
                    </div>""", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#ef4444">{len(false_)}</div>
                        <div class="stat-label">False</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">03 &nbsp;/&nbsp; Detailed Results</div>', unsafe_allow_html=True)

                for status_key, css_key, heading, dot in [
                    ("False",      "false",      "FALSE CLAIMS",      "●"),
                    ("Inaccurate", "inaccurate", "INACCURATE CLAIMS",  "●"),
                    ("Verified",   "verified",   "VERIFIED CLAIMS",   "●"),
                ]:
                    group = [c for c in claims if c.get("status") == status_key]
                    if group:
                        st.markdown(f'<div class="group-header group-{css_key}">{dot}&nbsp; {heading} &nbsp;<span style="opacity:0.4">({len(group)})</span></div>', unsafe_allow_html=True)
                        for item in group:
                            st.markdown(f"""
<div class="card card-{css_key}">
    <span class="badge badge-{css_key}">{status_key}</span>
    <div class="claim-text">"{item.get('claim', 'N/A')}"</div>
    <div class="explanation">→ &nbsp;{item.get('explanation', 'No explanation')}</div>
</div>""", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.warning("⚠ No valid claims were extracted. Please try a different PDF.")

st.markdown('<div class="footer-text">FACT &nbsp;·&nbsp; TRACKER &nbsp;·&nbsp; ENGINE</div>', unsafe_allow_html=True)