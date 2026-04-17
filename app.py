import streamlit as st
import pdfplumber
import json
import requests
from groq import Groq

# --- 1. CHAT MEMORY SETUP ---
# This keeps the conversation and job cards on screen
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Salam! I'm your AI Job Agent. Upload your resume, then tell me what city or role you're looking for!"}
    ]

# --- 2. THE ENGINE ---
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
        except: continue
    return found_jobs

# --- 3. THE UI (GEMINI STYLE) ---
st.set_page_config(page_title="AI Job Chat", layout="wide")

# Sidebar for Resume Upload (Keeps the main chat clean)
with st.sidebar:
    st.title("📁 Resume Lab")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        st.success("Resume Loaded!")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "jobs" in message:
            for job in message["jobs"][:5]: # Show top 5 per turn
                with st.container(border=True):
                    st.write(f"**{job['job_title']}** | {job['employer_name']}")
                    st.link_button("Apply", job['job_apply_link'])

# Chat Input (The Gemini Box)
if prompt := st.chat_input("e.g. Find me React jobs in Lahore..."):
    # 1. Add User message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Assistant Response
    with st.chat_message("assistant"):
        if not uploaded_file:
            response = "Please upload a resume in the sidebar first so I can match your skills!"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Searching the market..."):
                # Extract text from PDF
                pdf_text = "".join([p.extract_text() for p in pdfplumber.open(uploaded_file).pages])
                
                # Get queries -> Fetch Jobs
                queries = get_ai_search_queries(pdf_text, prompt)
                results = fetch_jobs(queries)
                
                if results:
                    response = f"I found some great matches for you in {prompt}:"
                    st.markdown(response)
                    # Displaying jobs immediately
                    for job in results[:5]:
                        with st.container(border=True):
                            st.write(f"**{job['job_title']}** | {job['employer_name']}")
                            st.link_button("Apply", job['job_apply_link'])
                    
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": response, "jobs": results})
                else:
                    response = "I couldn't find any open roles for that specific request. Try a broader city?"
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})