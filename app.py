import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(resume_text, job_description):
    prompt = f"""
    Hey Act Like a skilled or very experienced ATS (Application Tracking System)
    with a deep understanding of tech field, software engineering, data science,
    data analyst and big data engineer. Your task is to evaluate the resume based
    on the given job description. You must consider the job market is very competitive
    and you should provide best assistance for improving the resumes.

    Assign the percentage Matching based on JD and
    the missing keywords with high accuracy.

    resume: {resume_text}
    description: {job_description}

    I want the response in one single string having the structure:
    {{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
    """
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-001")
    response = model.generate_content([prompt])
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

st.set_page_config(page_title="Smart ATS", page_icon="📄", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #f0f4f8;
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        color: #222831;
        text-align: center;
    }
    p {
        text-align: center;
        color: #555;
    }
    .stButton > button {
        background-color: #2d6cdf;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #1b4fa2;
    }
    .report-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .tag {
        display: inline-block;
        background-color: #dbeafe;
        color: #1d4ed8;
        padding: 5px 10px;
        margin: 5px;
        border-radius: 8px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1> Smart ATS Resume Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p>Boost your resume by matching it to job descriptions using AI</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 Job Description")
    jd = st.text_area("Paste the Job Description", height=250)

with col2:
    st.markdown("### 📁 Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume in PDF format", type="pdf")

st.markdown("<hr>", unsafe_allow_html=True)
center_btn = st.columns(3)[1]
with center_btn:
    if st.button(" Analyze Resume"):
        if uploaded_file and jd:
            with st.spinner("Analyzing your resume... "):
                resume_text = input_pdf_text(uploaded_file)
                response = get_gemini_response(resume_text, jd)

                try:
                    parsed = json.loads(response.replace("```json", "").replace("```", "").strip())

                    match_percent = int(parsed["JD Match"].replace("%", "").strip())
                    missing_keywords = parsed["MissingKeywords"]
                    summary = parsed["Profile Summary"]

                    st.markdown("<div class='report-container'>", unsafe_allow_html=True)
                    st.markdown("### ✅ Match Percentage")
                    st.progress(match_percent / 100)
                    st.write(f"**{match_percent}% match** with the job description.")

                    st.markdown("### ❌ Missing Keywords")
                    if missing_keywords:
                        for keyword in missing_keywords:
                            st.markdown(f"<span class='tag'>{keyword}</span>", unsafe_allow_html=True)
                    else:
                        st.success("No missing keywords. Great job!")

                    st.markdown("###  Profile Summary")
                    st.info(summary)
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error("Couldn't parse the response properly. Please try again.")
                    st.code(response)

        else:
            st.warning("⚠️ Please provide both resume and job description.")
