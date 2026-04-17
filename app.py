import streamlit as st
import pdfplumber
import json
import requests
import pandas as pd
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- UI / UX SETUP (Custom CSS for Dark Theme & Animations) ---
st.set_page_config(page_title="AI Job Matcher", page_icon="🎯", layout="centered", initial_sidebar_state="collapsed")

custom_css = """
<style>
    /* Force Dark Theme elements */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* Hero Section */
    .hero { text-align: center; padding: 2rem 0; }
    .hero h1 { font-size: 3rem; font-weight: 800; background: -webkit-linear-gradient(#4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero p { font-size: 1.2rem; color: #A0AEC0; }
    
    /* Job Cards with smooth hover transition */
    .job-card {
        background-color: #1A202C;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .job-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
        border-color: #4facfe;
    }
    .job-title { font-size: 1.4rem; font-weight: 700; color: #E2E8F0; margin-bottom: 5px; }
    .job-company { font-size: 1rem; color: #A0AEC0; margin-bottom: 15px; }
    .match-badge { background-color: #2b6cb0; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.9rem; font-weight: bold; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- SECURE API SETUP ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    RAPID_API_KEY = st.secrets["RAPIDAPI_KEY"]
except:
    st.warning("⚠️ API Keys missing. App will not function until keys are added to Streamlit Secrets.")
    st.stop()

# --- BACKEND LOGIC ---
@st.cache_resource(show_spinner=False)
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

def extract_text(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def extract_skills(text):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Analyze this resume. Return strictly a JSON object.
    {{
        "role": "Ideal job title",
        "skills": ["Top 5 technical skills"]
    }}
    Resume: {text[:2500]}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def get_live_jobs(query, location, job_type=""):
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
    search_query = f"{query} {job_type} jobs in {location}"
    params = {"query": search_query, "num_pages": "1"}
    try:
        req = requests.get(url, headers=headers, params=params)
        return req.json().get('data', [])
    except:
        return []

# --- FRONTEND SECTIONS ---

# 1. Hero Section
st.markdown("""
<div class="hero">
    <h1>Next-Gen Job Matcher</h1>
    <p>Upload your resume. Let AI analyze your skills and find your perfect role.</p>
</div>
""", unsafe_allow_html=True)

# 2. Input & Upload Section
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    uploaded_file = st.file_uploader("Drop your CV/Resume here (PDF)", type="pdf")
with col2:
    city = st.text_input("Preferred Location", "Lahore, Pakistan")
with col3:
    job_type = st.selectbox("Job Type", ["Full-time", "Remote", "Internship", "Contract"])

# 3. Submission Workflow
if uploaded_file and st.button("Find My Matches 🚀", use_container_width=True):
    with st.status("🧠 Processing your profile...", expanded=True) as status:
        st.write("Extracting resume data...")
        cv_text = extract_text(uploaded_file)
        
        st.write("Analyzing skills via Groq...")
        profile = extract_skills(cv_text)
        
        st.write(f"Hunting for {profile['role']} roles in {city}...")
        jobs = get_live_jobs(profile['role'], city, job_type)
        
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    # 4. Results Section (Card Layout)
    if jobs:
        st.markdown(f"### 🔥 Top {profile['role']} Opportunities for You")
        user_vec = model.encode([f"{profile['role']} {', '.join(profile['skills'])}"])
        
        # Calculate scores
        for job in jobs:
            job_desc = f"{job.get('job_title')} {job.get('job_description', '')}"
            job_vec = model.encode([job_desc])
            job['match_score'] = int(cosine_similarity(user_vec, job_vec)[0][0] * 100)
            
        # Sort and display
        jobs = sorted(jobs, key=lambda x: x['match_score'], reverse=True)
        
        for job in jobs[:10]: # Show top 10
            title = job.get('job_title', 'Unknown Title')
            company = job.get('employer_name', 'Unknown Company')
            loc = job.get('job_city', city)
            link = job.get('job_apply_link', '#')
            score = job['match_score']
            
            card_html = f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div class="job-title">{title}</div>
                        <div class="job-company">🏢 {company} | 📍 {loc}</div>
                    </div>
                    <div class="match-badge">{score}% Match</div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            # Streamlit buttons must be outside pure HTML for functionality
            st.link_button("Apply Now", link)
            
    else:
        st.error(f"No jobs found for '{profile['role']}' in {city}. Try modifying your filters.")