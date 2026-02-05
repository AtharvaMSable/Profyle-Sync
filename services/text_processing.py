"""Text processing and cleaning utilities."""
import re
from typing import List
from nltk.corpus import stopwords


def clean_text_general(txt: str) -> str:
    """General text cleaning function."""
    txt = str(txt).lower()
    txt = re.sub('http\S+\s', ' ', txt)
    txt = re.sub('rt|cc', ' ', txt)
    txt = re.sub('#\S+', '', txt)
    txt = re.sub('@\S+', '  ', txt)
    txt = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', txt)
    txt = re.sub(r'[^\x00-\x7f]', ' ', txt)
    txt = re.sub('\s+', ' ', txt)
    return txt.strip()


def clean_resume_for_categorization(txt: str, remove_stopwords: bool = False) -> str:
    """
    Clean resume text specifically for ML categorization.
    This should match the preprocessing used during model training.
    """
    clean_text = re.sub('http\S+\s', ' ', txt)
    clean_text = re.sub('RT|cc', ' ', clean_text)
    clean_text = re.sub('#\S+\s', ' ', clean_text)
    clean_text = re.sub('@\S+', '  ', clean_text)
    clean_text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', clean_text)
    clean_text = re.sub(r'[^\x00-\x7f]', ' ', clean_text)
    clean_text = re.sub('\s+', ' ', clean_text)
    
    if remove_stopwords:
        stop_words = set(stopwords.words('english'))
        clean_text = ' '.join(word for word in clean_text.split() if word.lower() not in stop_words)
    
    return clean_text.lower()


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    return re.findall(phone_pattern, text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)
