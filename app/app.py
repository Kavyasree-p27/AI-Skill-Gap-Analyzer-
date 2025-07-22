import streamlit as st
import json
import pandas as pd
import re
import spacy
import pdfplumber
import pickle

# ---------- Session State Initialization ----------
if "resume_processed" not in st.session_state:
    st.session_state.resume_processed = False
if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
if "use_auto" not in st.session_state:
    st.session_state.use_auto = False
if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

# ---------- Load Data Functions ----------
@st.cache_data
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

@st.cache_data
def load_courses(csv_path):
    df = pd.read_csv(csv_path)
    df['skills_covered'] = df['skills_covered'].apply(lambda x: [s.strip().lower() for s in x.split(',')])
    return df

# ---------- NLP Skill Extraction ----------
@st.cache_resource
def load_spacy_model():
    import subprocess
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")


def extract_skills_from_text(text, known_skills):
    nlp = load_spacy_model()
    doc = nlp(text.lower())
    extracted = set()

    for token in doc:
        if token.text in known_skills:
            extracted.add(token.text)

    for skill in known_skills:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text.lower()):
            extracted.add(skill.lower())

    return list(extracted)

# ---------- Model Loading ----------
def load_job_classifier():
    with open('models/job_classifier.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('models/tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

# ---------- Skill Gap Logic ----------
def find_missing_skills(candidate_skills, job_skills):
    return [skill for skill in job_skills if skill.lower() not in [s.lower() for s in candidate_skills]]

def recommend_courses(missing_skills, courses_df):
    recommended = set()
    for skill in missing_skills:
        for _, row in courses_df.iterrows():
            if skill.lower() in row['skills_covered']:
                recommended.add(row['course_name'])
    return list(recommended)

def predict_job_role(skills, model, vectorizer):
    skill_text = ", ".join(skills)
    skill_vector = vectorizer.transform([skill_text])
    prediction = model.predict(skill_vector)[0]
    return prediction

def compute_placement_score(candidate_skills, job_skills):
    match_count = sum(1 for skill in job_skills if skill.lower() in [s.lower() for s in candidate_skills])
    total = len(job_skills)
    if total == 0:
        return 0, 0
    score = (match_count / total) * 100
    return round(score, 2), match_count

# ---------- Load All Data ----------
resumes_data = load_json('data/sample_resumes.json')
jobs = load_json('data/job_descriptions.json')
courses = load_courses('data/excelr_courses.csv')
job_titles = [j['job_title'] for j in jobs]

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Skill Gap Analyzer", layout="centered")
st.title("AI-Powered Skill Gap Analyzer for ExcelR Learners")

# Step 1: Upload or Paste Resume
st.subheader("\U0001F4C4 Upload Resume (PDF) or Paste Text")

uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
resume_text = ""

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
        resume_text = "\n".join(pages)
    st.success("Resume text extracted from PDF!")
    st.text_area("Extracted Resume Text:", resume_text, height=250, key="pdf_text")
else:
    resume_text = st.text_area("Paste Resume Text Below:", height=250, placeholder="Paste your resume or skills summary here...", key="typed_text")

# Step 2: Process Resume
if st.button("✅ Done"):
    if not resume_text.strip():
        st.warning("⚠️ Please upload a resume or paste text before clicking Done.")
    else:
        known_skills = set(skill for course in courses['skills_covered'] for skill in course)
        extracted_skills = extract_skills_from_text(resume_text, known_skills)
        st.session_state.extracted_skills = extracted_skills
        st.session_state.resume_processed = True
        st.session_state.analysis_ready = False
        st.session_state.selected_job = None

# Step 3: Job Role Selection
if st.session_state.resume_processed:
    st.subheader("🎯 Choose Job Role")
    use_auto = st.checkbox("🔍 Auto-detect best-fit role from resume", key="auto_detect_checkbox")
    st.session_state.use_auto = use_auto
    options = ["--Select--"] + job_titles

    default_index = 0

    if use_auto and st.session_state.extracted_skills:
        model, vectorizer = load_job_classifier()
        auto_job = predict_job_role(st.session_state.extracted_skills, model, vectorizer)
        st.success(f"🧠 Suggested Role: {auto_job}")

        if auto_job in job_titles:
            st.session_state.selected_job = auto_job
            default_index = options.index(auto_job)
        else:
            st.session_state.selected_job = None
    elif st.session_state.selected_job in job_titles:
        default_index = options.index(st.session_state.selected_job)

    selected_job = st.selectbox("Select or confirm the Target Job Role", options, index=default_index, key="job_select")

    if selected_job != "--Select--":
        st.session_state.selected_job = selected_job

    if st.session_state.selected_job and st.session_state.selected_job != "--Select--":
        if use_auto:
            st.session_state.analysis_ready = True

# Step 4: Display Extracted Skills
if st.session_state.resume_processed:
    st.subheader("🔍 Extracted Skills:")
    st.write(", ".join(st.session_state.extracted_skills) if st.session_state.extracted_skills else "No skills found.")

# Step 5: Show Analysis After Proceed
if st.session_state.analysis_ready and st.session_state.selected_job != "--Select--":
    job = next((j for j in jobs if j['job_title'] == st.session_state.selected_job), None)

    if job is None:
        st.error(f"❌ Could not find job: {st.session_state.selected_job}")
    else:
        required_skills = job['required_skills']
        missing_skills = find_missing_skills(st.session_state.extracted_skills, required_skills)

        st.subheader("❗ Missing Skills:")
        if missing_skills:
            st.write(", ".join(missing_skills))
            recommended = recommend_courses(missing_skills, courses)

            st.subheader("📘 Recommended ExcelR Courses:")
            if recommended:
                for course in recommended:
                    st.success(course)
            else:
                st.info("No matching courses found.")
        else:
            st.success("🎉 No missing skills! You're fully qualified for this job.")

        # Compute placement score for selected role
    score, matched = compute_placement_score(
        st.session_state.extracted_skills,
        job['required_skills']
    )

    # Show placement readiness score
    st.subheader("📊 Placement Readiness Score")
    st.write(f"✅ You matched **{matched} / {len(job['required_skills'])}** required skills.")
    st.write(f"🎯 Match Percentage: **{score}%**")

    # Interpretation
    if score >= 75:
        st.success("You are highly suitable for this role. Ready for placement!")
    elif score >= 50:
        st.warning("You are somewhat suitable. Some upskilling is recommended.")
    else:
        st.error("You need more training before applying for this role.")

    # Show other suitable roles regardless of threshold
    st.subheader("💼 Other Suitable Roles:")
    found_any = False

    for alt_job in jobs:
        if alt_job['job_title'] != st.session_state.selected_job:
            alt_score, _ = compute_placement_score(
                st.session_state.extracted_skills,
                alt_job['required_skills']
            )
            if alt_score >= 30:  # show anything above 30% match
                found_any = True
                st.info(f"👉 **{alt_job['job_title']}** → {alt_score:.2f}% match")

    if not found_any:
        st.info("No other roles found with ≥30% match. Please consider upskilling.")


