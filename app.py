"""
Smart Resume Analyzer - Main Application
Enhanced with Supabase integration and modular architecture
"""

import os
import pandas as pd
import streamlit as st
import nltk
from nltk.corpus import stopwords
import time
import datetime
import spacy
import random
from streamlit_tags import st_tags
import plotly.express as px

# Import configurations and services
from config.settings import (
    APP_NAME, CATEGORY_MAPPING, ENABLE_SUMMARIZATION,
    ENABLE_COURSE_RECOMMENDATIONS, ENABLE_NER_EXTRACTION, validate_config
)
from database.db_manager import get_db_manager
from services.ml_service import get_ml_service
from services.skill_extraction import SkillExtractor
from services.text_processing import clean_text_general
from utils.file_handlers import read_pdf, read_docx, get_file_extension, save_uploaded_file
from utils.ui_helpers import display_skills_as_badges, display_metric_card, display_course_recommendations

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title=APP_NAME,
    page_icon="📄",
    initial_sidebar_state="expanded"
)

# --- Load Courses (Optional) ---
courses_available = False
ds_course, web_course, android_course, ios_course, uiux_course = [], [], [], [], []
try:
    from Courses import ds_course, web_course, android_course, ios_course, uiux_course
    courses_available = True
except ImportError:
    st.sidebar.warning("Courses.py not found. Course recommendations disabled.")

# --- Initialize NLTK Data ---
@st.cache_resource
def download_nltk_data():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

download_nltk_data()

# --- Load spaCy Model ---
@st.cache_resource
def load_spacy_model(model_name="en_core_web_sm"):
    try:
        nlp = spacy.load(model_name)
        return nlp, True, None
    except OSError:
        return None, False, f"spaCy model '{model_name}' not found. Run: python -m spacy download {model_name}"
    except Exception as e:
        return None, False, f"Error loading spaCy model: {e}"

nlp, spacy_loaded, spacy_error = load_spacy_model()

# --- Load Summarization Pipeline ---
summarizer_pipeline = None
summarizer_enabled = False

if ENABLE_SUMMARIZATION:
    @st.cache_resource
    def load_summarizer():
        try:
            from transformers import pipeline
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6", truncation=True)
            return summarizer, True, None
        except Exception as e:
            return None, False, f"Error loading summarization: {e}"
    
    summarizer_pipeline, summarizer_enabled, summarizer_error = load_summarizer()
    if not summarizer_enabled:
        st.sidebar.warning("Summarization disabled")

# --- Initialize Services ---
db_manager = get_db_manager()
ml_service = get_ml_service()
skill_extractor = SkillExtractor(nlp if spacy_loaded else None)

# Initialize categories in database
if db_manager.is_connected:
    db_manager.initialize_categories()

# --- Sidebar Status ---
st.sidebar.title("🎯 System Status")

# Validate configuration
config_valid, config_msg = validate_config()
if config_valid:
    st.sidebar.success("✅ Configuration Valid")
else:
    st.sidebar.error(f"❌ {config_msg}")
    st.error(f"Configuration Error: {config_msg}")
    st.info("Please update your .env file with Supabase credentials. See README.md for instructions.")

if db_manager.is_connected:
    st.sidebar.success("✅ Database Connected")
else:
    st.sidebar.error("❌ Database Disconnected")

if ml_service.is_loaded():
    st.sidebar.success("✅ ML Models Loaded")
else:
    st.sidebar.error("❌ ML Models Not Loaded")

if spacy_loaded:
    st.sidebar.success("✅ spaCy NER Loaded")
else:
    st.sidebar.warning("⚠️ spaCy NER Disabled")

if summarizer_enabled:
    st.sidebar.success("✅ Summarization Enabled")
else:
    st.sidebar.info("ℹ️ Summarization Disabled")

# --- Session State Initialization ---
if 'categorization_results' not in st.session_state:
    st.session_state.categorization_results = None
if 'uploaded_file_details' not in st.session_state:
    st.session_state.uploaded_file_details = {}
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False
if 'analysis_output' not in st.session_state:
    st.session_state.analysis_output = None

# --- Navigation ---
st.sidebar.title("📌 Navigation")
app_mode = st.sidebar.selectbox(
    "Choose Mode:",
    ["🏠 Home", "👤 User Analysis", " Admin Panel"]
)

# --- Course Recommendation Function ---
def recommend_courses(category_name: str, num_recommendations: int = 4):
    """Recommend courses based on category."""
    if not courses_available:
        return []
    
    category_course_map = {
        'Data Science': ds_course,
        'Web Designing': web_course,
        'Android Development': android_course,
        'IOS Development': ios_course,
        'UI-UX Development': uiux_course,
        'Java Developer': web_course,
        'Python Developer': ds_course,
    }
    
    course_list = category_course_map.get(category_name, [])
    if not course_list:
        return []
    
    # Shuffle for variety
    shuffled = course_list.copy()
    random.shuffle(shuffled)
    
    return shuffled[:num_recommendations]

# ===================================
# HOME PAGE
# ===================================
if app_mode == '🏠 Home':
    st.title(f"📄 {APP_NAME}")
    st.markdown("### Intelligent Resume Analysis Powered by AI")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🤖 ML Categorization")
        st.write("Automatically categorize resumes into 25+ professional categories using machine learning.")
    
    with col2:
        st.markdown("### 🔍 Skill Extraction")
        st.write("Extract skills using rule-based and NER methods for comprehensive analysis.")
    
    with col3:
        st.markdown("### 📊 JD Matching")
        st.write("Calculate compatibility scores between resumes and job descriptions.")
    
    st.markdown("---")
    
    st.markdown("### 🚀 Get Started")
    st.markdown("""
    1. **👤 User Analysis**: Upload resumes for categorization and analysis
    2. **🔑 Admin Panel**: View analytics and manage data
    
    Select a mode from the sidebar to begin!
    """)
    
    st.markdown("---")
    st.info("💡 Tip: Make sure to configure your .env file with Supabase credentials. See README.md for instructions.")

# ===================================
# USER ANALYSIS MODE
# ===================================
elif app_mode == '👤 User Analysis':
    st.title("👤 Resume Analysis")
    st.markdown("Upload and analyze resumes with AI-powered insights")
    st.markdown("---")
    
    # --- Section 1: Upload & Categorize ---
    st.header("1️⃣ Upload & Categorize Resumes")
    
    uploaded_files = st.file_uploader(
        "Choose PDF or DOCX files",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="user_file_uploader"
    )
    
    if st.button("📁 Categorize Resumes", key="categorize_btn"):
        # Clear previous results
        st.session_state.categorization_results = None
        st.session_state.uploaded_file_details = {}
        st.session_state.analyze_clicked = False
        st.session_state.analysis_output = None
        
        if not uploaded_files:
            st.error("Please upload at least one file")
            st.stop()
        
        if not ml_service.is_loaded():
            st.error("ML models not loaded. Cannot categorize resumes.")
            st.stop()
        
        if not db_manager.is_connected:
            st.error("Database not connected. Cannot process resumes.")
            st.stop()
        
        categorization_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            file_name = uploaded_file.name
            file_ext = get_file_extension(file_name)
            
            status_text.text(f"Processing {file_name}...")
            
            try:
                # Save temp file
                temp_path = os.path.join(".", f"temp_{file_name}")
                uploaded_file.seek(0)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Extract text
                text = ""
                if file_ext == '.pdf':
                    text = read_pdf(temp_path)
                elif file_ext == '.docx':
                    uploaded_file.seek(0)
                    text = read_docx(uploaded_file)
                
                if text:
                    # Predict category
                    category_name, category_id, confidence = ml_service.predict_category(text)
                    
                    # Store in session state
                    st.session_state.uploaded_file_details[file_name] = {
                        'text': text,
                        'category': category_name,
                        'category_id': category_id,
                        'confidence': confidence
                    }
                    
                    # Add to results
                    categorization_data.append({
                        'Filename': file_name,
                        'Predicted Category': category_name,
                        'Confidence': f"{confidence:.2f}%" if confidence > 0 else "N/A"
                    })
                    
                    # Save to database
                    resume_data = {
                        'filename': file_name,
                        'original_text': text,
                        'file_path': None  # No local path in cloud deployment
                    }
                    resume_record = db_manager.insert_resume(resume_data)
                    
                    if resume_record and category_id is not None:
                        analysis_data = {
                            'resume_id': resume_record['id'],
                            'category_id': category_id,
                            'confidence_score': float(confidence) if confidence else 0.0
                        }
                        db_manager.insert_analysis(analysis_data)
                
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            except Exception as e:
                st.error(f"Error processing {file_name}: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("✅ Categorization complete!")
        
        if categorization_data:
            st.session_state.categorization_results = pd.DataFrame(categorization_data)
            st.rerun()
        else:
            st.warning("No resumes were successfully processed.")
    
    # --- Display Categorization Results ---
    if st.session_state.get('categorization_results') is not None:
        st.markdown("---")
        st.subheader("📊 Categorization Results")
        st.dataframe(st.session_state['categorization_results'], use_container_width=True)
        
        csv = st.session_state['categorization_results'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name='categorization_results.csv',
            mime='text/csv'
        )
    
    # --- Section 2: Detailed Analysis ---
    st.markdown("---")
    st.header("2️⃣ Detailed Resume Analysis")
    
    if st.session_state.get('uploaded_file_details'):
        available_files = list(st.session_state['uploaded_file_details'].keys())
        
        selected_file = st.selectbox(
            "Select Resume for Analysis:",
            available_files,
            key="selected_resume"
        )
        
        job_description = st.text_area(
            "Paste Job Description:",
            height=200,
            key="job_description"
        )
        
        if st.button("🔍 Analyze Resume", key="analyze_btn"):
            if not selected_file or not job_description:
                st.error("Please select a resume and provide a job description")
                st.stop()
            
            resume_details = st.session_state['uploaded_file_details'].get(selected_file)
            
            if not resume_details:
                st.error("Resume details not found")
                st.stop()
            
            with st.spinner("Analyzing... This may take a moment."):
                resume_text = resume_details['text']
                predicted_category = resume_details.get('category', 'N/A')
                confidence = resume_details.get('confidence', 0)
                
                # Extract skills from resume
                resume_skills = skill_extractor.extract_combined(resume_text)
                
                # Extract skills from JD
                jd_skills = skill_extractor.extract_rule_based(job_description)
                
                # Match skills
                match_result = skill_extractor.match_with_jd(resume_skills, jd_skills)
                
                # Course recommendations
                recommended_courses = []
                if courses_available and predicted_category not in ["Unknown", "Prediction Error"]:
                    recommended_courses = recommend_courses(predicted_category, 4)
                
                # Summarization
                resume_summary = "Summarization not available"
                jd_summary = "Summarization not available"
                
                if summarizer_enabled and summarizer_pipeline:
                    try:
                        resume_clean = clean_text_general(resume_text)[:1024]
                        resume_summary = summarizer_pipeline(
                            resume_clean,
                            max_length=130,
                            min_length=30,
                            do_sample=False
                        )[0]['summary_text']
                    except Exception as e:
                        resume_summary = f"Error: {e}"
                    
                    try:
                        jd_clean = clean_text_general(job_description)[:1024]
                        jd_summary = summarizer_pipeline(
                            jd_clean,
                            max_length=130,
                            min_length=30,
                            do_sample=False
                        )[0]['summary_text']
                    except Exception as e:
                        jd_summary = f"Error: {e}"
                
                # Store results
                st.session_state.analysis_output = {
                    'selected_file': selected_file,
                    'job_description': job_description,
                    'predicted_category': predicted_category,
                    'confidence': confidence,
                    'resume_skills': resume_skills,
                    'jd_skills': jd_skills,
                    'match_result': match_result,
                    'recommended_courses': recommended_courses,
                    'resume_summary': resume_summary,
                    'jd_summary': jd_summary
                }
                st.session_state.analyze_clicked = True
                
                # Save to database
                if db_manager.is_connected:
                    # Find resume ID
                    resumes = db_manager.search_resumes(selected_file)
                    if resumes:
                        resume_id = resumes[0]['id']
                        
                        # Save skills
                        db_manager.insert_resume_skills(
                            resume_id,
                            resume_skills,
                            'combined'
                        )
                        
                        # Save JD and match
                        jd_data = {
                            'jd_text': job_description,
                            'required_skills': jd_skills
                        }
                        jd_record = db_manager.client.table('job_descriptions').insert(jd_data).execute()
                        
                        if jd_record.data:
                            jd_id = jd_record.data[0]['id']
                            
                            match_data = {
                                'resume_id': resume_id,
                                'jd_id': jd_id,
                                'match_score': match_result['score'],
                                'matching_skills': match_result['matching_skills'],
                                'missing_skills': match_result['missing_skills']
                            }
                            db_manager.insert_jd_match(match_data)
                
                st.rerun()
    
    # --- Display Analysis Results ---
    if st.session_state.get('analyze_clicked') and st.session_state.get('analysis_output'):
        results = st.session_state.analysis_output
        
        st.markdown("---")
        st.subheader(f"📄 Analysis Results: {results['selected_file']}")
        
        # Category and confidence
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"**Predicted Category:** {results['predicted_category']}")
        with col2:
            if results.get('confidence', 0) > 0:
                st.metric("Confidence", f"{results['confidence']:.2f}%")
        
        # Summarization
        if summarizer_enabled:
            st.markdown("---")
            st.markdown("### 🤖 AI-Generated Summaries")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Resume Summary:**")
                st.success(results['resume_summary'])
            with col2:
                st.markdown("**Job Description Summary:**")
                st.info(results['jd_summary'])
        
        # Skills and Score
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 Extracted Skills")
            if results['resume_skills']:
                display_skills_as_badges(results['resume_skills'])
            else:
                st.info("No skills identified")
        
        with col2:
            st.markdown("### 📊 Match Score")
            match_result = results['match_result']
            st.metric("Skill Match", f"{match_result['score']:.1f}%")
            st.progress(int(match_result['score']) / 100)
            st.caption(f"{match_result['matched_count']} of {match_result['total_jd_skills']} skills matched")
        
        # Matching and Missing Skills
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Matching Skills")
            matching = match_result['matching_skills']
            if matching:
                display_skills_as_badges(matching, "#28a745")
            else:
                st.info("No matching skills found")
        
        with col2:
            st.markdown("### ⚠️ Missing Skills")
            missing = match_result['missing_skills']
            if missing:
                display_skills_as_badges(missing, "#dc3545")
            else:
                st.success("All JD skills present!")
        
        # Course Recommendations
        if results.get('recommended_courses'):
            st.markdown("---")
            st.markdown("### 📚 Recommended Courses")
            for i, (name, link) in enumerate(results['recommended_courses'], 1):
                st.markdown(f"{i}. [{name}]({link})")
    
    else:
        st.info("👆 Upload and categorize resumes first, then analyze them against job descriptions.")

# ===================================
# ADMIN PANEL
# ===================================
elif app_mode == '🔑 Admin Panel':
    st.title("🔑 Admin Panel")
    st.markdown("View analytics and manage resume data")
    st.markdown("---")
    
    # Simple login
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False
    
    if not st.session_state['admin_logged_in']:
        username = st.text_input("Username", key="admin_user")
        password = st.text_input("Password", type='password', key="admin_pass")
        
        if st.button('Login', key="admin_login"):
            if username == 'admin' and password == 'admin123':
                st.session_state['admin_logged_in'] = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        st.stop()
    
    # Admin is logged in
    if not db_manager.is_connected:
        st.error("Database not connected. Cannot display data.")
        st.stop()
    
    st.markdown("---")
    
    # Statistics
    stats = db_manager.get_statistics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card(
            "Total Resumes",
            str(stats.get('total_resumes', 0)),
            "📄"
        )
    with col2:
        display_metric_card(
            "Categories",
            "25",
            "📂"
        )
    with col3:
        display_metric_card(
            "Database",
            "Supabase",
            "☁️"
        )
    
    # All resumes
    st.markdown("---")
    st.subheader("📋 All Resumes")
    
    resumes = db_manager.get_all_resumes(limit=100)
    
    if resumes:
        # Convert to DataFrame
        df_data = []
        for resume in resumes:
            analysis = resume.get('resume_analysis', [])
            if analysis:
                analysis = analysis[0]
                category = analysis.get('categories')
                if category:
                    category_name = category.get('category_name', 'N/A')
                else:
                    category_name = 'N/A'
                confidence = analysis.get('confidence_score', 0)
            else:
                category_name = 'N/A'
                confidence = 0
            
            df_data.append({
                'ID': resume['id'],
                'Filename': resume['filename'],
                'Category': category_name,
                'Confidence': f"{float(confidence):.2f}%" if confidence else 'N/A',
                'Upload Date': resume['upload_timestamp']
            })
        
        df_admin = pd.DataFrame(df_data)
        st.dataframe(df_admin, use_container_width=True)
        
        # Download button
        csv = df_admin.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data",
            data=csv,
            file_name='admin_resumes.csv',
            mime='text/csv'
        )
        
        # Visualizations
        st.markdown("---")
        st.subheader("📊 Category Distribution")
        
        category_counts = df_admin['Category'].value_counts()
        if not category_counts.empty:
            fig = px.pie(
                names=category_counts.index,
                values=category_counts.values,
                title='Resume Distribution by Category'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No resumes found in database")


