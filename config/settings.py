"""Application settings and configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# App Configuration
APP_NAME = os.getenv("APP_NAME", "Smart Resume Analyzer")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Model Paths
TFIDF_MODEL_PATH = os.getenv("TFIDF_MODEL_PATH", "tfidf.pkl")
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "model.pkl")
SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")

# File Upload Settings
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx").split(",")
OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "categorized_resumes")

# Feature Flags
ENABLE_SUMMARIZATION = os.getenv("ENABLE_SUMMARIZATION", "true").lower() == "true"
ENABLE_COURSE_RECOMMENDATIONS = os.getenv("ENABLE_COURSE_RECOMMENDATIONS", "true").lower() == "true"
ENABLE_NER_EXTRACTION = os.getenv("ENABLE_NER_EXTRACTION", "true").lower() == "true"

# Category Mapping
CATEGORY_MAPPING = {
    15: "Java Developer", 23: "Testing", 8: "DevOps Engineer",
    20: "Python Developer", 24: "Web Designing", 12: "HR",
    13: "Hadoop", 3: "Blockchain", 10: "ETL Developer",
    18: "Operations Manager", 6: "Data Science", 22: "Sales",
    16: "Mechanical Engineer", 1: "Arts", 7: "Database",
    11: "Electrical Engineering", 14: "Health and fitness", 19: "PMO",
    4: "Business Analyst", 9: "DotNet Developer", 2: "Automation Testing",
    17: "Network Security Engineer", 21: "SAP Developer", 5: "Civil Engineer",
    0: "Advocate",
}

# Skills Database
SKILLS_DB = [
    'python', 'java', 'c++', 'c#', 'javascript', 'js', 'html', 'css', 'php', 'ruby', 'swift', 'kotlin',
    'sql', 'mysql', 'postgresql', 'sqlite', 'mongodb', 'cassandra', 'redis', 'oracle', 'sql server',
    'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'git',
    'linux', 'unix', 'windows', 'macos',
    'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'spring', 'ruby on rails', '.net',
    'pandas', 'numpy', 'scipy', 'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'pytorch', 'matplotlib', 'seaborn', 'plotly',
    'machine learning', 'deep learning', 'data science', 'data analysis', 'data visualization', 'nlp', 'natural language processing',
    'computer vision', 'big data', 'hadoop', 'spark', 'kafka', 'hive', 'hbase', 'spacy', 'nltk',
    'agile', 'scrum', 'jira', 'project management', 'product management',
    'communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking',
    'customer service', 'sales', 'marketing', 'seo', 'sem', 'content creation',
    'ui/ux', 'design', 'photoshop', 'illustrator', 'figma',
    'devops', 'automation testing', 'selenium', 'cybersecurity', 'network security',
    'sap', 'etl', 'power bi', 'tableau', 'excel', 'word', 'powerpoint',
    'blockchain', 'solidity', 'ethereum', 'hyperledger',
    'mechanical engineering', 'electrical engineering', 'civil engineering',
    'hr', 'recruitment', 'talent acquisition', 'employee relations',
    'health', 'fitness', 'nutrition',
    'advocate', 'legal', 'law',
    'jquery', 'bootstrap', 'd3.js', 'dc.js', 'logstash', 'kibana', 'r', 'sap hana',
    'rest', 'soap', 'api', 'microservices',
    'pmo', 'operations management', 'business analysis', 'dotnet'
]

def validate_config():
    """Validate required configuration."""
    if not SUPABASE_URL or SUPABASE_URL == "your_supabase_project_url_here":
        return False, "SUPABASE_URL not configured. Please update .env file."
    if not SUPABASE_KEY or SUPABASE_KEY == "your_supabase_anon_key_here":
        return False, "SUPABASE_KEY not configured. Please update .env file."
    return True, "Configuration valid."
