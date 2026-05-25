import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import json
import re
import os
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactGuard AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e8f0;
    font-family: 'Syne', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 20%, #1a0a2e 0%, #0a0a0f 50%),
                radial-gradient(ellipse at 80% 80%, #0a1a2e 0%, transparent 50%);
    min-height: 100vh;
}

[data-testid="stHeader"] { background: transparent !important; }

.main-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    letter-spacing: -2px;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #6b7280;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}

.hero-section {
    text-align: center;
    padding: 3rem 1rem 2rem;
    border-bottom: 1px solid rgba(167, 139, 250, 0.15);
    margin-bottom: 2.5rem;
}

.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.card-verified::before  { background: linear-gradient(90deg, #34d399, #059669); }
.card-inaccurate::before { background: linear-gradient(90deg, #fbbf24, #d97706); }
.card-false::before      { background: linear-gradient(90deg, #f87171, #dc2626); }

.badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}

.badge-verified   { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-inaccurate { background: rgba(251,191,36,0.15);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.badge-false      { background: rgba(248,113,113,0.15); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }

.claim-text {
    font-size: 1rem;
    font-weight: 600;
    color: #e8e8f0;
    margin-bottom: 0.5rem;
    line-height: 1.5;
}

.explanation {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #9ca3af;
    line-height: 1.6;
}

.stat-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}

.stat-number {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.5rem;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.stat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    padding: 0.85rem 2rem;
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(124, 58, 237, 0.6);
}

.footer-text {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #374151;
    text-align: center;
    padding: 2rem 0 1rem;
    letter-spacing: 1px;
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
            # xAI (Grok) API Integration
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
            # Default Groq API Integration
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
        
        # Clean markdown
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"```$", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        
        # Parse JSON
        data = json.loads(raw)
        
        # Handle different response formats
        if isinstance(data, dict):
            if "claims" in data:
                claims_data = data["claims"]
            elif "results" in data:
                claims_data = data["results"]
            else:
                claims_data = []
                for value in data.values():
                    if isinstance(value, list):
                        claims_data = value
                        break
        elif isinstance(data, list):
            claims_data = data
        else:
            claims_data = []
        
        # Validate each claim
        validated = []
        for claim in claims_data:
            if isinstance(claim, dict) and all(k in claim for k in ["claim", "status", "explanation"]):
                validated.append(claim)
        
        return validated
        
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return []


# ── UI ────────────────────────────────────────────────────────────────────────

# ✅ FIX: API key automatically read from secrets (user ko nahi mangni)
try:
    # Try to get API key from Streamlit secrets (production)
    api_key = st.secrets["GROQ_API_KEY"]
except:
    # Fallback for local development (optional)
    api_key = os.environ.get("GROQ_API_KEY", "")
    
    # If still no key, show setup instructions (not ask user)
    if not api_key:
        st.error("""
        ⚠️ **API Key Missing**
        
        Please add your Groq API key to Streamlit Secrets:
        1. Go to your app settings on Streamlit Cloud
        2. Add secret: `GROQ_API_KEY` = `your_key_here`
        
        *For local development: set environment variable `GROQ_API_KEY`*
        """)
        st.stop()

st.markdown("""
<div class="hero-section">
    <div class="main-title">FactGuard AI</div>
    <div class="subtitle">✦ Automated Claim Verification Engine ✦</div>
</div>
""", unsafe_allow_html=True)

# ❌ Removed API key input field - ab user se nahi mangega

st.markdown('<div class="section-label">📄 Upload Document</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop a PDF to fact-check",
    type=["pdf"],
)

if uploaded_file:
    st.success(f"✅ Loaded: **{uploaded_file.name}**")

st.markdown("<br>", unsafe_allow_html=True)
run = st.button("🔍 ANALYZE & FACT-CHECK")

if run:
    if not uploaded_file:
        st.error("⚠️ Please upload a PDF document first.")
    else:
        with st.spinner("Extracting text from PDF..."):
            doc_text = extract_text_from_pdf(uploaded_file)

        if len(doc_text.strip()) < 50:
            st.error("⚠️ Could not extract readable text. Try a text-based PDF.")
        else:
            with st.spinner("🤖 Groq AI is analyzing claims..."):
                claims = analyze_claims(doc_text, api_key)

            if claims and len(claims) > 0:
                verified   = [c for c in claims if c.get("status") == "Verified"]
                inaccurate = [c for c in claims if c.get("status") == "Inaccurate"]
                false_     = [c for c in claims if c.get("status") == "False"]

                st.markdown('<div class="section-label">📊 Summary</div>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#e8e8f0">{len(claims)}</div>
                        <div class="stat-label">Total Claims</div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#34d399">{len(verified)}</div>
                        <div class="stat-label">Verified</div>
                    </div>""", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#fbbf24">{len(inaccurate)}</div>
                        <div class="stat-label">Inaccurate</div>
                    </div>""", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""<div class="stat-box">
                        <div class="stat-number" style="color:#f87171">{len(false_)}</div>
                        <div class="stat-label">False</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">🔎 Detailed Results</div>', unsafe_allow_html=True)

                for status_key, css_key, heading in [
                    ("False", "false", "🚨 FALSE CLAIMS"),
                    ("Inaccurate", "inaccurate", "⚠️ INACCURATE CLAIMS"),
                    ("Verified", "verified", "✅ VERIFIED CLAIMS"),
                ]:
                    group = [c for c in claims if c.get("status") == status_key]
                    if group:
                        st.markdown(f"**{heading}** ({len(group)})")
                        for item in group:
                            st.markdown(f"""
<div class="card card-{css_key}">
    <span class="badge badge-{css_key}">{status_key}</span>
    <div class="claim-text">"{item.get('claim', 'N/A')}"</div>
    <div class="explanation">→ {item.get('explanation', 'No explanation')}</div>
</div>""", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No valid claims were extracted from the document. Please try a different PDF or check the content format.")

st.markdown('<div class="footer-text">FACTGUARD AI · POWERED BY GROQ · BUILT FOR COG CULTURE ASSESSMENT</div>', unsafe_allow_html=True)
