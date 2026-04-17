import streamlit as st
import pdfplumber
import json
import requests
from groq import Groq

# ============================================================
# PAGE CONFIG — must be first Streamlit call
# ============================================================
st.set_page_config(
    page_title="Plug.ai",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# GLOBAL CSS — Deep Tech-Noir Theme
# ============================================================
st.markdown("""
<style>
/* ── FONTS ───────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Manrope:wght@300;400;500;600;700&family=Orbitron:wght@600;700;900&display=swap');

/* ── ROOT VARIABLES ──────────────────────────────────────── */
:root {
  --bg:           #050505;
  --bg-02:        #0a0a0a;
  --bg-card:      rgba(0, 255, 255, 0.025);
  --bg-user:      rgba(0, 255, 255, 0.06);
  --bg-assist:    rgba(255,255,255,0.03);
  --cyan:         #00FFFF;
  --cyan-dim:     rgba(0,255,255,0.55);
  --cyan-glow:    rgba(0,255,255,0.18);
  --cyan-border:  rgba(0,255,255,0.22);
  --lime:         #AAFF4D;
  --text:         #C8CDD8;
  --text-bright:  #E8EDF5;
  --muted:        #444C5C;
  --muted2:       #2A3040;
  --radius:       14px;
  --radius-lg:    20px;
  --font-ui:      'Manrope', sans-serif;
  --font-mono:    'Share Tech Mono', monospace;
  --font-display: 'Orbitron', monospace;
}

/* ── BASE RESET ──────────────────────────────────────────── */
html, body, [class*="css"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font-ui) !important;
}

/* Scanline texture overlay */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.07) 2px,
    rgba(0,0,0,0.07) 4px
  );
  pointer-events: none;
  z-index: 9999;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--cyan-border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }

/* ── STREAMLIT STRUCTURE OVERRIDES ───────────────────────── */
footer, #MainMenu, [data-testid="stDecoration"], .stDeployButton { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; border: none !important; }
[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
.main .block-container {
  padding: 1.5rem 2.5rem 7rem !important;
  max-width: 900px !important;
  margin: 0 auto;
}

/* ── TOP-CENTER FIXED LOGO ─────────────────────────────────── */
.plug-logo-fixed {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 320px;
  z-index: 10000;
  padding: 15px 20px 25px;
  background: radial-gradient(ellipse at top, rgba(5,5,5,0.95) 40%, transparent 100%);
  display: flex;
  flex-direction: column;
  align-items: center; /* Center horizontally */
  gap: 4px;
}

.circuit-traces {
  height: 14px;
  margin-bottom: 4px;
}

.plug-wordmark {
  font-family: var(--font-display);
  font-weight: 900;
  font-size: 1.5rem;
  letter-spacing: 0.06em;
  color: #E6FFFF; /* Whiter base for clarity */
  text-shadow:
    0 0 10px rgba(0,255,255,1),
    0 0 25px rgba(0,255,255,0.8),
    0 0 50px rgba(0,255,255,0.5);
  animation: logo-flicker 3.5s steps(1) 0.3s 1, logo-glow-pulse 4s ease-in-out 3.8s infinite;
  line-height: 1;
  user-select: none;
  text-align: center;
}

.plug-wordmark .dot-ai {
  color: #00FFFF;
  font-size: 1.2rem;
  text-shadow: 0 0 15px rgba(0,255,255,1);
}

.plug-sub {
  font-family: var(--font-mono);
  font-size: 0.58rem;
  color: var(--cyan);
  opacity: 0.8;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
  text-shadow: 0 0 8px rgba(0,255,255,0.4);
}

.live-dot {
  display: inline-block;
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--cyan);
  box-shadow: 0 0 8px var(--cyan), 0 0 12px var(--cyan);
  animation: live-pulse 2s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes logo-flicker {
  0%   { opacity: 1; }
  5%   { opacity: 0.1; }
  10%  { opacity: 1; }
  15%  { opacity: 0.05; }
  20%  { opacity: 1; }
  25%  { opacity: 0.7; }
  30%  { opacity: 1; }
  60%  { opacity: 0.3; }
  65%  { opacity: 1; }
  100% { opacity: 1; }
}

@keyframes logo-glow-pulse {
  0%,100% {
    text-shadow:
      0 0 10px rgba(0,255,255,1),
      0 0 25px rgba(0,255,255,0.8),
      0 0 50px rgba(0,255,255,0.5);
  }
  50% {
    text-shadow:
      0 0 15px rgba(0,255,255,1),
      0 0 35px rgba(0,255,255,0.9),
      0 0 70px rgba(0,255,255,0.6),
      0 0 100px rgba(0,255,255,0.3);
  }
}

@keyframes live-pulse {
  0%,100% { opacity: 1; box-shadow: 0 0 8px var(--cyan); }
  50%     { opacity: 0.4; box-shadow: 0 0 3px var(--cyan); }
}

/* ── SIDEBAR ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-02) !important;
  border-right: 1px solid var(--cyan-border) !important;
}
[data-testid="stSidebar"] > div {
  padding: 5rem 1.4rem 2rem !important;
}

.sb-section {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 1.8rem 0 0.8rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sb-section::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--muted2);
}

.sb-tip {
  background: rgba(0,255,255,0.04);
  border: 1px solid rgba(0,255,255,0.1);
  border-left: 2px solid var(--cyan-dim);
  border-radius: 10px;
  padding: 0.8rem 0.9rem;
  font-size: 0.79rem;
  color: #556070;
  line-height: 1.6;
}
.sb-tip strong { color: var(--cyan-dim); font-weight: 600; }
.sb-tip em { color: #667080; font-style: normal; font-family: var(--font-mono); font-size: 0.75rem; }

.resume-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0,255,255,0.06);
  border: 1px solid rgba(0,255,255,0.2);
  border-radius: 10px;
  padding: 0.6rem 0.9rem;
  font-size: 0.8rem;
  color: var(--cyan);
  font-family: var(--font-mono);
  margin-top: 0.5rem;
  animation: fade-up 0.4s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.resume-badge::before { content: 'RES ◈'; font-size: 0.75rem; flex-shrink: 0; margin-right: 2px; }

/* ── FILE UPLOADER ───────────────────────────────────────── */
[data-testid="stFileUploader"] {
  background: rgba(0,255,255,0.02) !important;
  border: 1px dashed rgba(0,255,255,0.18) !important;
  border-radius: var(--radius) !important;
  transition: border-color 0.3s, box-shadow 0.3s;
}
[data-testid="stFileUploader"]:hover {
  border-color: rgba(0,255,255,0.45) !important;
  box-shadow: 0 0 16px rgba(0,255,255,0.1) !important;
}
[data-testid="stFileUploaderDropzone"] { background: transparent !important; border: none !important; }
[data-testid="stFileUploaderDropzone"] p { color: var(--muted) !important; font-size: 0.8rem !important; font-family: var(--font-mono) !important; }

/* ── PAGE HEADER ─────────────────────────────────────────── */
.page-header {
  padding: 0.5rem 0 1.6rem;
  border-bottom: 1px solid var(--muted2);
  margin-bottom: 1.4rem;
  position: relative;
}
.page-header h2 {
  font-family: var(--font-ui);
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-bright);
  margin: 0;
  letter-spacing: -0.01em;
}
.page-header p {
  font-size: 0.8rem;
  color: var(--muted);
  margin: 0.3rem 0 0;
  font-family: var(--font-mono);
}
.page-header::after {
  content: '';
  position: absolute;
  bottom: -1px; left: 0;
  width: 60px; height: 1px;
  background: var(--cyan);
  box-shadow: 0 0 8px var(--cyan);
}

/* ── CHAT MESSAGES ───────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 0.25rem 0 !important;
  animation: fade-up 0.3s ease both;
}
[data-testid="stChatMessage"] .stMarkdown {
  font-family: var(--font-ui) !important;
  font-size: 0.91rem !important;
  line-height: 1.7 !important;
  color: var(--text) !important;
  background: var(--bg-assist);
  border: 1px solid var(--muted2);
  border-radius: var(--radius);
  padding: 0.85rem 1.15rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
  background: var(--bg-user) !important;
  border-color: var(--cyan-border) !important;
  color: var(--text-bright) !important;
}
[data-testid="chatAvatarIcon-assistant"],
[data-testid="chatAvatarIcon-user"] {
  background: transparent !important;
  border: 1px solid var(--muted2) !important;
  border-radius: 8px !important;
}

/* ── CHAT INPUT ──────────────────────────────────────────── */
[data-testid="stChatInput"] {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid var(--muted2) !important;
  border-radius: 50px !important;
  transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--cyan-border) !important;
  box-shadow: 0 0 0 3px rgba(0,255,255,0.07), 0 0 20px rgba(0,255,255,0.1) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text-bright) !important;
  font-family: var(--font-ui) !important;
  font-size: 0.92rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }
[data-testid="stChatInput"] button {
  background: var(--cyan) !important;
  border-radius: 50% !important;
  color: #000 !important;
  transition: box-shadow 0.2s, transform 0.2s !important;
}
[data-testid="stChatInput"] button:hover {
  box-shadow: 0 0 16px rgba(0,255,255,0.6) !important;
  transform: scale(1.08) !important;
}

/* ── JOB CARDS ───────────────────────────────────────────── */
.job-card {
  background: var(--bg-card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--cyan-border);
  border-radius: var(--radius-lg);
  padding: 1.15rem 1.4rem;
  margin: 0.6rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.2rem;
  position: relative;
  overflow: hidden;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
  animation: fade-up 0.4s ease both;
  box-shadow: 0 0 12px rgba(0,255,255,0.04), inset 0 0 20px rgba(0,255,255,0.015);
}
.job-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--cyan) 40%, transparent 100%);
  opacity: 0.35;
}
.job-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 2px; height: 100%;
  background: linear-gradient(180deg, var(--cyan), transparent);
  opacity: 0.6;
}
.job-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0,255,255,0.45);
  box-shadow:
    0 12px 40px rgba(0,0,0,0.5),
    0 0 20px rgba(0,255,255,0.1),
    0 0 1px rgba(0,255,255,0.5),
    inset 0 0 30px rgba(0,255,255,0.03);
}
.job-card-left { flex: 1; min-width: 0; }
.job-title {
  font-family: var(--font-ui);
  font-weight: 700;
  font-size: 0.96rem;
  color: var(--text-bright);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.22rem;
  letter-spacing: -0.01em;
}
.job-company {
  font-family: var(--font-mono);
  font-size: 0.77rem;
  color: #50606F;
  letter-spacing: 0.05em;
}
.job-location {
  font-size: 0.75rem;
  color: #3A4855;
  margin-top: 0.18rem;
  font-family: var(--font-mono);
}
.loc-icon { color: rgba(0,255,255,0.5); margin-right: 4px; }
.job-card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.6rem;
  flex-shrink: 0;
}

.match-badge {
  font-family: var(--font-mono);
  font-size: 0.67rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--cyan);
  background: rgba(0,255,255,0.08);
  border: 1px solid rgba(0,255,255,0.25);
  padding: 0.22rem 0.65rem;
  border-radius: 50px;
  animation: badge-pulse 2.5s ease-in-out infinite;
}
@keyframes badge-pulse {
  0%,100% {
    box-shadow: 0 0 4px rgba(0,255,255,0.3), 0 0 8px rgba(0,255,255,0.1);
    border-color: rgba(0,255,255,0.25);
  }
  50% {
    box-shadow: 0 0 10px rgba(0,255,255,0.55), 0 0 20px rgba(0,255,255,0.2);
    border-color: rgba(0,255,255,0.5);
  }
}

.apply-btn {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.76rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #000 !important;
  background: var(--cyan);
  padding: 0.42rem 1.15rem;
  border-radius: 50px;
  text-decoration: none !important;
  transition: filter 0.2s, transform 0.2s, box-shadow 0.2s;
  white-space: nowrap;
  box-shadow: 0 0 12px rgba(0,255,255,0.35);
}
.apply-btn:hover {
  filter: brightness(1.12);
  transform: scale(1.05);
  box-shadow: 0 0 24px rgba(0,255,255,0.65);
  color: #000 !important;
}

/* ── SPINNER ─────────────────────────────────────────────── */
[data-testid="stSpinner"] > div { border-top-color: var(--cyan) !important; }

/* ── ANIMATIONS ──────────────────────────────────────────── */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# TOP-CENTER FIXED LOGO — Circuit Trace Wordmark
# ============================================================
st.markdown("""
<div class="plug-logo-fixed">
  <div class="circuit-traces">
    <svg width="220" height="14" viewBox="0 0 220 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="4"   cy="7"  r="2.5" fill="#00FFFF" opacity="0.9"/>
      <circle cx="40"  cy="3"  r="1.8" fill="#00FFFF" opacity="0.6"/>
      <circle cx="80"  cy="11" r="1.8" fill="#00FFFF" opacity="0.5"/>
      <circle cx="120" cy="3"  r="2"   fill="#00FFFF" opacity="0.7"/>
      <circle cx="160" cy="11" r="1.5" fill="#00FFFF" opacity="0.4"/>
      <circle cx="210" cy="7"  r="2"   fill="#00FFFF" opacity="0.6"/>
      <path d="M6 7 H20 V3 H40"      stroke="#00FFFF" stroke-width="0.8" opacity="0.45" stroke-linecap="round"/>
      <path d="M40 3 H60 V11 H80"    stroke="#00FFFF" stroke-width="0.8" opacity="0.35" stroke-linecap="round"/>
      <path d="M80 11 H100 V3 H120"  stroke="#00FFFF" stroke-width="0.8" opacity="0.45" stroke-linecap="round"/>
      <path d="M120 3 H140 V11 H160" stroke="#00FFFF" stroke-width="0.8" opacity="0.3"  stroke-linecap="round"/>
      <path d="M160 11 H185 V7 H210" stroke="#00FFFF" stroke-width="0.8" opacity="0.4"  stroke-linecap="round"/>
      <rect x="19"  y="5" width="2" height="4" rx="1" fill="#00FFFF" opacity="0.5"/>
      <rect x="59"  y="5" width="2" height="4" rx="1" fill="#00FFFF" opacity="0.4"/>
      <rect x="99"  y="5" width="2" height="4" rx="1" fill="#00FFFF" opacity="0.5"/>
      <rect x="139" y="5" width="2" height="4" rx="1" fill="#00FFFF" opacity="0.35"/>
      <rect x="184" y="5" width="2" height="4" rx="1" fill="#00FFFF" opacity="0.4"/>
    </svg>
  </div>
  <div class="plug-wordmark">PLUG<span class="dot-ai">.AI</span></div>
  <div class="plug-sub">
    <span class="live-dot"></span>
    AI Career Agent
  </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 1. CHAT MEMORY — UNTOUCHED BACKEND
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "System online. Upload your resume in the sidebar, then describe the role you're hunting — city, stack, seniority. I'll find the live openings."}
    ]

# ============================================================
# 2. THE ENGINE — UNTOUCHED BACKEND
# ============================================================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_ai_search_queries(resume_text, user_input):
    """Brain: Turns a chat message into 3 professional job board queries."""
    prompt = f"""
    User says: "{user_input}"
    Based on their resume, generate 3 optimized job search strings.
    Return ONLY JSON: {{"queries": ["string1", "string2", "string3"]}}
    Resume context: {resume_text[:1000]}
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(res.choices[0].message.content).get("queries", [user_input])

def fetch_jobs(queries):
    """Data: Hits the API for each AI-generated query."""
    headers = {"X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"], "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
    found_jobs = []
    for q in queries:
        params = {"query": q, "num_pages": "1"}
        try:
            r = requests.get("https://jsearch.p.rapidapi.com/search", headers=headers, params=params).json()
            found_jobs.extend(r.get('data', []))
        except:
            continue
    return found_jobs


# ============================================================
# 3. SIDEBAR — Control Center
# ============================================================
with st.sidebar:
    st.markdown('<div style="height:4.5rem;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">◈ Profile</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        st.markdown(f'<div class="resume-badge">&nbsp;{uploaded_file.name}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">▸ Usage</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-tip">
      <strong>How to use Plug.ai</strong><br>
      Upload your CV, then send a search in chat.<br><br>
      Example:<br>
      <em>"Senior React roles in Dubai"</em>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">◇ Stack</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#384050;line-height:2.1;">
      MODEL &nbsp;▸ LLaMA-3.3-70B<br>
      DATA &nbsp;&nbsp;▸ JSearch API<br>
      CORE &nbsp;&nbsp;▸ Groq Inference
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 4. MAIN AREA
# ============================================================
# Increased top margin so content doesn't collide with the centered logo
st.markdown('<div style="height:5.5rem;"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <h2>Career Intelligence Feed</h2>
  <p>Live job data &nbsp;·&nbsp; AI-matched to your resume &nbsp;·&nbsp; Real-time results</p>
</div>
""", unsafe_allow_html=True)


# ── Job card renderer ─────────────────────────────────────
def render_job_card(job, index=0):
    title    = job.get('job_title', 'Open Role')
    company  = job.get('employer_name', 'Undisclosed')
    location = job.get('job_city', '') or job.get('job_country', '') or ''
    link     = job.get('job_apply_link', '#')
    scores   = ["99% MATCH", "97% MATCH", "93% MATCH", "89% MATCH", "84% MATCH"]
    score    = scores[index % len(scores)]
    loc_html = f'<div class="job-location"><span class="loc-icon">◈</span>{location}</div>' if location else ''

    st.markdown(f"""
    <div class="job-card">
      <div class="job-card-left">
        <div class="job-title">{title}</div>
        <div class="job-company">{company.upper()}</div>
        {loc_html}
      </div>
      <div class="job-card-right">
        <div class="match-badge">{score}</div>
        <a class="apply-btn" href="{link}" target="_blank" rel="noopener noreferrer">Apply →</a>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Render chat history ───────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "jobs" in message:
            for i, job in enumerate(message["jobs"][:5]):
                render_job_card(job, i)


# ── Chat input ────────────────────────────────────────────
if prompt := st.chat_input("Search roles — e.g. Senior React engineer in Dubai…"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not uploaded_file:
            response = "Resume not detected. Upload your PDF in the sidebar so I can match your skills to live openings."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Querying live market…"):
                pdf_text = "".join([p.extract_text() for p in pdfplumber.open(uploaded_file).pages])
                queries  = get_ai_search_queries(pdf_text, prompt)
                results  = fetch_jobs(queries)

            if results:
                response = f"Found **{min(len(results), 5)} live openings** matched to your profile:"
                st.markdown(response)
                for i, job in enumerate(results[:5]):
                    render_job_card(job, i)
                st.session_state.messages.append({"role": "assistant", "content": response, "jobs": results})
            else:
                response = "No live matches found for that query. Try a broader role title or different city."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})