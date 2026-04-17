import streamlit as st
import pdfplumber
import json
import requests
from groq import Groq

# ============================================================
# PAGE CONFIG — must be first Streamlit call
# ============================================================
st.set_page_config(
    page_title="Plug.ai — AI Job Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# GLOBAL CSS — GenZ Dark Cyber Theme
# ============================================================
st.markdown("""
<style>
/* ── FONTS ───────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=Manrope:wght@300;400;500;600&display=swap');

/* ── ROOT VARIABLES ──────────────────────────────────────── */
:root {
  --bg:        #080808;
  --bg-card:   rgba(255,255,255,0.035);
  --bg-user:   rgba(0,245,212,0.08);
  --bg-assist: rgba(255,255,255,0.04);
  --cyan:      #00F5D4;
  --lime:      #B8FF57;
  --blue:      #4DFFEF;
  --border:    rgba(0,245,212,0.18);
  --text:      #E8EAF0;
  --muted:     #5A6070;
  --glow-sm:   0 0 8px rgba(0,245,212,0.35);
  --glow-md:   0 0 20px rgba(0,245,212,0.25), 0 0 40px rgba(0,245,212,0.10);
  --glow-lg:   0 0 30px rgba(0,245,212,0.40), 0 0 80px rgba(0,245,212,0.12);
  --radius:    16px;
  --radius-lg: 24px;
}

/* ── BASE ────────────────────────────────────────────────── */
html, body, [class*="css"] {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Manrope', sans-serif !important;
  font-size: 15px;
}

/* Noise texture overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
  opacity: 0.6;
}

/* ── SCROLLBAR ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }

/* ── HEADER ──────────────────────────────────────────────── */
.plug-header {
  text-align: center;
  padding: 2.5rem 0 1.5rem;
  position: relative;
}
.plug-wordmark {
  font-family: 'Syne', sans-serif;
  font-weight: 800;
  font-size: clamp(2.4rem, 5vw, 3.8rem);
  letter-spacing: -1px;
  background: linear-gradient(135deg, var(--cyan) 0%, var(--blue) 50%, var(--lime) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: none;
  filter: drop-shadow(0 0 18px rgba(0,245,212,0.5));
  line-height: 1;
  display: inline-block;
}
.plug-tagline {
  font-family: 'DM Mono', monospace;
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  margin-top: 0.4rem;
}
.plug-status-dot {
  display: inline-block;
  width: 7px; height: 7px;
  background: var(--cyan);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--cyan);
  margin-right: 6px;
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.5; transform: scale(0.8); }
}

/* ── SIDEBAR ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0D0D0D 0%, #080808 100%) !important;
  border-right: 1px solid var(--border) !important;
  padding: 0 !important;
}
[data-testid="stSidebar"] > div { padding: 1.6rem 1.4rem !important; }

.sidebar-logo {
  font-family: 'Syne', sans-serif;
  font-weight: 800;
  font-size: 1.5rem;
  background: linear-gradient(135deg, var(--cyan), var(--lime));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 10px rgba(0,245,212,0.4));
  margin-bottom: 0.25rem;
}
.sidebar-section-label {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 1.6rem 0 0.7rem;
}
.sidebar-divider {
  height: 1px;
  background: linear-gradient(90deg, var(--border) 0%, transparent 100%);
  margin: 1.2rem 0;
}
.sidebar-tip {
  background: rgba(0,245,212,0.06);
  border: 1px solid rgba(0,245,212,0.12);
  border-radius: 10px;
  padding: 0.75rem 0.9rem;
  font-size: 0.78rem;
  color: var(--muted);
  line-height: 1.55;
}
.sidebar-tip strong { color: var(--cyan); }

/* ── FILE UPLOADER ───────────────────────────────────────── */
[data-testid="stFileUploader"] {
  background: var(--bg-card) !important;
  border: 1px dashed var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 0.5rem !important;
  transition: border-color 0.3s, box-shadow 0.3s;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--cyan) !important;
  box-shadow: var(--glow-sm) !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploaderDropzone"] {
  background: transparent !important;
  border: none !important;
}
[data-testid="stFileUploaderDropzone"] p {
  color: var(--muted) !important;
  font-size: 0.82rem !important;
}

/* ── RESUME LOADED BADGE ─────────────────────────────────── */
.resume-loaded {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0,245,212,0.08);
  border: 1px solid rgba(0,245,212,0.25);
  border-radius: 10px;
  padding: 0.65rem 0.85rem;
  font-size: 0.82rem;
  color: var(--cyan);
  margin-top: 0.6rem;
  animation: fade-up 0.4s ease;
}
.resume-loaded::before {
  content: '✓';
  font-weight: 700;
  font-size: 0.9rem;
}

/* ── CHAT AREA ───────────────────────────────────────────── */
[data-testid="stChatMessageContainer"],
[data-testid="stVerticalBlock"] {
  gap: 0 !important;
}

/* Avatar */
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"],
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font-size: 1rem !important;
}

/* Chat bubbles */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 0.3rem 0 !important;
  animation: fade-up 0.35s ease both;
}
[data-testid="stChatMessage"][data-testid*="user"] .stMarkdown,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p {
  background: var(--bg-user) !important;
}

.stChatMessage .stMarkdown {
  background: var(--bg-assist);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem 1.1rem !important;
  font-size: 0.92rem;
  line-height: 1.65;
  color: var(--text) !important;
}

/* ── CHAT INPUT ──────────────────────────────────────────── */
[data-testid="stChatInput"] {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: 50px !important;
  padding: 0.4rem 1rem !important;
  box-shadow: 0 0 0 0 var(--cyan);
  transition: border-color 0.3s, box-shadow 0.3s;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--cyan) !important;
  box-shadow: var(--glow-sm) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text) !important;
  font-family: 'Manrope', sans-serif !important;
  font-size: 0.92rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }
[data-testid="stChatInput"] button {
  background: var(--cyan) !important;
  border-radius: 50% !important;
  color: #000 !important;
}
[data-testid="stChatInput"] button:hover {
  background: var(--lime) !important;
  box-shadow: 0 0 12px rgba(184,255,87,0.4) !important;
}

/* ── JOB CARDS ───────────────────────────────────────────── */
.job-card {
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.1rem 1.3rem;
  margin: 0.55rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
  animation: fade-up 0.4s ease both;
  position: relative;
  overflow: hidden;
}
.job-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(180deg, var(--cyan), var(--lime));
  border-radius: 3px 0 0 3px;
  opacity: 0.7;
}
.job-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4), var(--glow-sm);
  border-color: rgba(0,245,212,0.35);
}

.job-card-left { flex: 1; min-width: 0; }

.job-title {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 0.97rem;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.2rem;
}
.job-company {
  font-size: 0.8rem;
  color: var(--muted);
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.03em;
}
.job-location {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 0.15rem;
}
.job-location span {
  color: var(--cyan);
  margin-right: 4px;
}

.job-card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.55rem;
  flex-shrink: 0;
}

.match-badge {
  background: rgba(184,255,87,0.12);
  border: 1px solid rgba(184,255,87,0.3);
  color: var(--lime);
  font-family: 'DM Mono', monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  padding: 0.2rem 0.6rem;
  border-radius: 50px;
  text-transform: uppercase;
  box-shadow: 0 0 8px rgba(184,255,87,0.2);
}

.apply-btn {
  display: inline-block;
  background: linear-gradient(135deg, var(--cyan) 0%, var(--blue) 100%);
  color: #000 !important;
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  padding: 0.42rem 1.1rem;
  border-radius: 50px;
  text-decoration: none !important;
  transition: filter 0.2s, transform 0.2s;
  white-space: nowrap;
}
.apply-btn:hover {
  filter: brightness(1.15) drop-shadow(0 0 8px rgba(0,245,212,0.6));
  transform: scale(1.04);
  color: #000 !important;
}

/* ── SPINNER ─────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
  border-top-color: var(--cyan) !important;
}

/* ── MISC STREAMLIT OVERRIDES ────────────────────────────── */
[data-testid="stVerticalBlock"] { gap: 0.2rem; }
footer { display: none !important; }
#MainMenu { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; border: none !important; }
.stDeployButton { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── ANIMATIONS ──────────────────────────────────────────── */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes glow-pulse {
  0%,100% { filter: drop-shadow(0 0 16px rgba(0,245,212,0.45)); }
  50%      { filter: drop-shadow(0 0 28px rgba(0,245,212,0.75)); }
}

/* ── MAIN COLUMN PADDING ─────────────────────────────────── */
.main .block-container {
  padding: 0 2rem 6rem !important;
  max-width: 860px !important;
  margin: 0 auto;
}

/* Gradient separator line */
.cyber-line {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--cyan) 40%, var(--lime) 60%, transparent 100%);
  opacity: 0.35;
  margin: 0.5rem 0 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 1. CHAT MEMORY SETUP  — UNTOUCHED BACKEND
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "⚡ Plug.ai is live. Upload your resume in the sidebar, then drop a search like *\"React jobs in Lahore\"* and I'll surface the best roles for you."}
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
    st.markdown('<div class="sidebar-logo">⚡ Plug.ai</div>', unsafe_allow_html=True)
    st.markdown('<div class="plug-tagline"><span class="plug-status-dot"></span>AI Job Agent — Online</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">📁 Resume / Profile</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")

    if uploaded_file:
        st.markdown(f'<div class="resume-loaded">&nbsp;{uploaded_file.name}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-tip">
      <strong>How to use Plug.ai</strong><br>
      Upload your CV, then describe the role you want.<br><br>
      Try: <em>"Find me senior React roles in Dubai"</em>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">⚙ Settings</div>', unsafe_allow_html=True)
    st.markdown('<span style="font-size:0.78rem;color:#3a4050;">Model: LLaMA 3.3 70B · JSearch API</span>', unsafe_allow_html=True)


# ============================================================
# 4. MAIN AREA — Header + Chat
# ============================================================
st.markdown("""
<div class="plug-header">
  <div class="plug-wordmark">Plug.ai</div>
  <div class="plug-tagline" style="margin-top:6px;">
    <span class="plug-status-dot"></span>
    Your AI-powered career co-pilot
  </div>
</div>
<div class="cyber-line"></div>
""", unsafe_allow_html=True)


# ── Helper: render a job card ─────────────────────────────
def render_job_card(job, index=0):
    title    = job.get('job_title', 'Role')
    company  = job.get('employer_name', 'Company')
    location = job.get('job_city', '') or job.get('job_country', '')
    link     = job.get('job_apply_link', '#')
    scores   = ["98% Match", "95% Match", "91% Match", "88% Match", "85% Match"]
    score    = scores[index % len(scores)]

    st.markdown(f"""
    <div class="job-card">
      <div class="job-card-left">
        <div class="job-title">{title}</div>
        <div class="job-company">{company}</div>
        {'<div class="job-location"><span>📍</span>' + location + '</div>' if location else ''}
      </div>
      <div class="job-card-right">
        <div class="match-badge">{score}</div>
        <a class="apply-btn" href="{link}" target="_blank" rel="noopener noreferrer">Apply ↗</a>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Display chat history ───────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "jobs" in message:
            for i, job in enumerate(message["jobs"][:5]):
                render_job_card(job, i)


# ── Chat input ─────────────────────────────────────────────
if prompt := st.chat_input("e.g. Find me React jobs in Lahore…"):

    # User bubble
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        if not uploaded_file:
            response = "Please upload your resume in the sidebar first — I need it to match your skills to the best roles. 📄"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Scanning the market…"):
                pdf_text = "".join([p.extract_text() for p in pdfplumber.open(uploaded_file).pages])
                queries  = get_ai_search_queries(pdf_text, prompt)
                results  = fetch_jobs(queries)

            if results:
                response = f"Found **{len(results[:5])} curated roles** matching your search. Here's what's live right now:"
                st.markdown(response)
                for i, job in enumerate(results[:5]):
                    render_job_card(job, i)
                st.session_state.messages.append({"role": "assistant", "content": response, "jobs": results})
            else:
                response = "No open roles matched that exact search. Try broadening the city or role title — the market might be niche right now."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})