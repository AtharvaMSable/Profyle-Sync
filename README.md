# 🎯 Smart Resume Analyzer - Deep Learning Edition

An intelligent resume analysis system powered by Machine Learning, NLP, and Deep Learning for automated resume categorization, skill extraction, and job description matching.

## ✨ Features

- **🤖 ML-Based Resume Categorization**: Automatically categorize resumes into 25+ professional categories
- **🔍 Intelligent Skill Extraction**: Extract skills using both rule-based and NER (Named Entity Recognition) methods
- **📊 Resume vs Job Description Matching**: Calculate compatibility scores between resumes and job descriptions
- **💡 Smart Course Recommendations**: Suggest relevant courses based on predicted categories
- **📝 AI-Powered Summarization**: Generate concise summaries using transformer models
- **☁️ Cloud Database**: Supabase (PostgreSQL) for reliable data storage
- **📈 Analytics Dashboard**: View statistics and insights
- **🎨 Modern UI**: Clean, responsive Streamlit interface

## 🏗️ Architecture

```
project/
├── config/                 # Configuration and settings
│   ├── __init__.py
│   └── settings.py        # Environment variables and app config
├── database/              # Database layer
│   ├── __init__.py
│   ├── db_manager.py      # Supabase connection and queries
│   └── supabase_setup.sql # Database schema
├── services/              # Business logic
│   ├── __init__.py
│   ├── ml_service.py      # ML categorization service
│   ├── skill_extraction.py # Skill extraction service
│   └── text_processing.py  # Text cleaning utilities
├── utils/                 # Helper utilities
│   ├── __init__.py
│   ├── file_handlers.py   # File processing
│   └── ui_helpers.py      # UI components
├── app.py              # Main Streamlit application
├── Courses.py            # Course recommendations data
├── skills.py             # Skills database
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create from .env.example)
└── .env.example          # Example environment configuration
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Supabase account (free tier works great!)

### 2. Setup Supabase Database

1. **Create a Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Sign up / Log in
   - Click "New Project"
   - Choose organization, project name, database password, and region
   - Wait for setup to complete (~2 minutes)

2. **Get Your Credentials**:
   - Go to Project Settings → API
   - Copy your `Project URL` (SUPABASE_URL)
   - Copy your `anon/public` key (SUPABASE_KEY)

3. **Run Database Setup Script**:
   - In Supabase dashboard, go to SQL Editor
   - Click "New Query"
   - Copy content from `database/supabase_setup.sql`
   - Paste and click "Run"
   - You should see "Database setup completed successfully! 🎉"

### 3. Install Dependencies

```bash
# Clone/download the project
cd "\Project"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK data (will auto-download on first run)
python -c "import nltk; nltk.download('stopwords')"
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
copy .env.example .env

# Edit .env file and add your Supabase credentials:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key-here
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📋 Usage Guide

### User Analysis Mode

1. **Upload Resumes**:
   - Click "Choose PDF or DOCX files"
   - Select one or multiple resume files
   - Click "📁 Categorize Resumes"

2. **View Categorization Results**:
   - See predicted categories for each resume
   - Download results as CSV

3. **Detailed Analysis**:
   - Select a resume from the dropdown
   - Paste a job description
   - Click "🔍 Analyze Resume vs. Job Description"
   - View:
     - Match score
     - Extracted skills
     - Matching skills
     - Missing skills
     - Course recommendations
     - AI summary (if enabled)

### Admin Panel

- View all processed resumes
- Filter by category
- Search resumes
- View analytics and statistics
- Export data

## 🔧 Configuration

### Environment Variables (.env)

```env
# Supabase (Required)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# App Settings
APP_NAME=Smart Resume Analyzer
ENVIRONMENT=development

# Model Paths
TFIDF_MODEL_PATH=tfidf.pkl
ML_MODEL_PATH=model.pkl
SPACY_MODEL=en_core_web_sm

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,docx
OUTPUT_DIRECTORY=categorized_resumes

# Features
ENABLE_SUMMARIZATION=true
ENABLE_COURSE_RECOMMENDATIONS=true
ENABLE_NER_EXTRACTION=true
```

## 📊 Database Schema

### Main Tables:

- **resumes**: Store uploaded resume files and extracted text
- **categories**: 25 predefined job categories
- **resume_analysis**: ML prediction results and confidence scores
- **skills**: Master list of skills
- **resume_skills**: Junction table for resume-skill relationships
- **job_descriptions**: Store job postings
- **resume_jd_matches**: Store matching results with scores

## 🎓 Categories Supported

1. Advocate
2. Arts
3. Automation Testing
4. Blockchain
5. Business Analyst
6. Civil Engineer
7. Data Science
8. Database
9. DevOps Engineer
10. DotNet Developer
11. ETL Developer
12. Electrical Engineering
13. HR
14. Hadoop
15. Health and Fitness
16. Java Developer
17. Mechanical Engineer
18. Network Security Engineer
19. Operations Manager
20. PMO
21. Python Developer
22. SAP Developer
23. Sales
24. Testing
25. Web Designing

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Database**: Supabase (PostgreSQL)
- **ML/AI**:
  - Scikit-learn (TF-IDF, Classification)
  - spaCy (NER)
  - Transformers (Summarization)
  - NLTK (Text Processing)
- **Document Processing**: pypdf, python-docx
- **Data Analysis**: Pandas, NumPy
- **Visualization**: Plotly

## 🔒 Security Best Practices

1. **Never commit .env file** to version control
2. **Use Row Level Security (RLS)** in Supabase for production
3. **Validate file uploads** (size, type)
4. **Sanitize user inputs**
5. **Use environment variables** for all secrets
6. **Enable Supabase authentication** for multi-user scenarios

## 📈 Future Enhancements

- [ ] User authentication and authorization
- [ ] Resume template generation
- [ ] Batch processing improvements
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] API endpoints
- [ ] Mobile responsiveness
- [ ] Multi-language support
- [ ] ATS score calculation
- [ ] Interview preparation suggestions

## 🐛 Troubleshooting

### Database Connection Issues
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Check Supabase project status
- Ensure database setup SQL was run successfully

### Model Loading Errors
- Ensure `tfidf.pkl` and `model.pkl` are in project directory
- Check file permissions

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

 

---

 
