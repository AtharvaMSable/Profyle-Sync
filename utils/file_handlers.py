"""File handling utilities for document processing."""
import os
from typing import Optional
from pypdf import PdfReader
from docx import Document
import streamlit as st


def read_pdf(file_path: str) -> str:
    """
    Extract text from PDF file.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        st.error(f"Error reading PDF {os.path.basename(file_path)}: {e}")
    
    if not text:
        st.warning(f"Could not extract text from {os.path.basename(file_path)}")
    
    return text


def read_docx(file) -> str:
    """
    Extract text from DOCX file.
    
    Args:
        file: File object or path
        
    Returns:
        Extracted text
    """
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        
        if not text:
            st.warning(f"Could not extract text from DOCX {getattr(file, 'name', 'document')}")
        
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""


def save_uploaded_file(uploaded_file, destination_path: str) -> bool:
    """
    Save an uploaded file to disk.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        destination_path: Path where file should be saved
        
    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        uploaded_file.seek(0)
        
        with open(destination_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return True
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str, allowed_extensions: list) -> bool:
    """Check if file extension is allowed."""
    ext = get_file_extension(filename)
    return ext.lstrip('.') in allowed_extensions or ext in allowed_extensions
