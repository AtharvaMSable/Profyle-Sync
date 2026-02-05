"""
Setup and installation script for Smart Resume Analyzer
Run this after configuring your .env file
"""

import subprocess
import sys
import os
from pathlib import Path

def print_step(step_num, message):
    """Print formatted step message."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {message}")
    print('='*60)

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n→ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    print(f"\nPython version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    
    print("✅ Python version is adequate")
    return True

def check_env_file():
    """Check if .env file exists and is configured."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("\n❌ .env file not found!")
        print("\nPlease follow these steps:")
        print("1. Copy .env.example to .env")
        print("2. Update SUPABASE_URL and SUPABASE_KEY")
        print("3. Run this script again")
        return False
    
    # Read .env and check for placeholders
    with open(env_path, 'r') as f:
        content = f.read()
    
    if 'your_supabase_project_url_here' in content or 'your_supabase_anon_key_here' in content:
        print("\n⚠️  .env file exists but not configured!")
        print("\nPlease update your .env file with:")
        print("- SUPABASE_URL (from Supabase dashboard)")
        print("- SUPABASE_KEY (anon/public key)")
        return False
    
    print("✅ .env file found and configured")
    return True

def main():
    """Main setup process."""
    print("="*60)
    print("  Smart Resume Analyzer - Setup Script")
    print("="*60)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Check .env file
    print_step(2, "Checking Configuration")
    if not check_env_file():
        print("\n⚠️  Please configure your .env file first!")
        print("See UPGRADE_GUIDE.md for instructions.")
        sys.exit(1)
    
    # Step 3: Install Python packages
    print_step(3, "Installing Python Packages")
    
    packages_to_install = [
        ("pip install -r requirements.txt", "Installing all requirements"),
    ]
    
    for command, description in packages_to_install:
        if not run_command(command, description):
            print("\n⚠️  Some packages failed to install.")
            print("You may need to install them manually.")
    
    # Step 4: Download spaCy model
    print_step(4, "Downloading spaCy Model")
    run_command(
        "python -m spacy download en_core_web_sm",
        "Downloading en_core_web_sm model"
    )
    
    # Step 5: Download NLTK data
    print_step(5, "Downloading NLTK Data")
    run_command(
        'python -c "import nltk; nltk.download(\'stopwords\')"',
        "Downloading NLTK stopwords"
    )
    
    # Step 6: Create necessary directories
    print_step(6, "Creating Directories")
    directories = ['categorized_resumes', 'temp']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Final message
    print("\n" + "="*60)
    print("  ✅ SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("\n1. Ensure Supabase database is setup:")
    print("   - Go to Supabase SQL Editor")
    print("   - Run: database/supabase_setup.sql")
    
    print("\n2. Start the application:")
    print("   streamlit run app_upgraded.py")
    
    print("\n3. Access the app in your browser:")
    print("   http://localhost:8501")
    
    print("\n📚 Documentation:")
    print("   - README.md - Full documentation")
    print("   - UPGRADE_GUIDE.md - Setup guide")
    
    print("\n" + "="*60)
    print("Happy analyzing! 🎉")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
