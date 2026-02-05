-- Supabase Database Setup Script
-- Run this in your Supabase SQL Editor

-- 1. Create Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert predefined categories
INSERT INTO categories (id, category_name) VALUES
    (0, 'Advocate'),
    (1, 'Arts'),
    (2, 'Automation Testing'),
    (3, 'Blockchain'),
    (4, 'Business Analyst'),
    (5, 'Civil Engineer'),
    (6, 'Data Science'),
    (7, 'Database'),
    (8, 'DevOps Engineer'),
    (9, 'DotNet Developer'),
    (10, 'ETL Developer'),
    (11, 'Electrical Engineering'),
    (12, 'HR'),
    (13, 'Hadoop'),
    (14, 'Health and fitness'),
    (15, 'Java Developer'),
    (16, 'Mechanical Engineer'),
    (17, 'Network Security Engineer'),
    (18, 'Operations Manager'),
    (19, 'PMO'),
    (20, 'Python Developer'),
    (21, 'SAP Developer'),
    (22, 'Sales'),
    (23, 'Testing'),
    (24, 'Web Designing')
ON CONFLICT (id) DO NOTHING;

-- 2. Create Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    file_hash VARCHAR(64),
    original_text TEXT,
    cleaned_text TEXT,
    file_path VARCHAR(500)
);

-- Create index for faster searches
CREATE INDEX IF NOT EXISTS idx_resumes_filename ON resumes(filename);
CREATE INDEX IF NOT EXISTS idx_resumes_upload_timestamp ON resumes(upload_timestamp DESC);

-- 3. Create Resume Analysis Table
CREATE TABLE IF NOT EXISTS resume_analysis (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),
    confidence_score DECIMAL(5,2),
    analysis_timestamp TIMESTAMP DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_resume_analysis_resume_id ON resume_analysis(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_analysis_category_id ON resume_analysis(category_id);

-- 4. Create Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(skill_name);

-- 5. Create Resume-Skills Junction Table
CREATE TABLE IF NOT EXISTS resume_skills (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    extraction_method VARCHAR(20) DEFAULT 'rule_based',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(resume_id, skill_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_resume_skills_resume_id ON resume_skills(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_skills_skill_id ON resume_skills(skill_id);

-- 6. Create Job Descriptions Table
CREATE TABLE IF NOT EXISTS job_descriptions (
    id SERIAL PRIMARY KEY,
    jd_text TEXT NOT NULL,
    required_skills TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Create Resume-JD Matches Table
CREATE TABLE IF NOT EXISTS resume_jd_matches (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    jd_id INTEGER REFERENCES job_descriptions(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2),
    matching_skills TEXT[],
    missing_skills TEXT[],
    match_timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_matches_resume_id ON resume_jd_matches(resume_id);
CREATE INDEX IF NOT EXISTS idx_matches_jd_id ON resume_jd_matches(jd_id);
CREATE INDEX IF NOT EXISTS idx_matches_score ON resume_jd_matches(match_score DESC);

-- 8. Create Users Table (for future multi-user support)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9. Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_jd_matches ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now - customize based on your needs)
CREATE POLICY "Allow all operations" ON resumes FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON resume_analysis FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON resume_skills FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON job_descriptions FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON resume_jd_matches FOR ALL USING (true);

-- 10. Create Views for Common Queries
CREATE OR REPLACE VIEW resume_details AS
SELECT 
    r.id,
    r.filename,
    r.upload_timestamp,
    c.category_name,
    ra.confidence_score,
    COUNT(DISTINCT rs.skill_id) as skill_count
FROM resumes r
LEFT JOIN resume_analysis ra ON r.id = ra.resume_id
LEFT JOIN categories c ON ra.category_id = c.id
LEFT JOIN resume_skills rs ON r.id = rs.resume_id
GROUP BY r.id, r.filename, r.upload_timestamp, c.category_name, ra.confidence_score;

-- View for category statistics
CREATE OR REPLACE VIEW category_statistics AS
SELECT 
    c.category_name,
    COUNT(ra.id) as resume_count
FROM categories c
LEFT JOIN resume_analysis ra ON c.id = ra.category_id
GROUP BY c.id, c.category_name
ORDER BY resume_count DESC;

-- Success message
SELECT 'Database setup completed successfully! 🎉' as message;
