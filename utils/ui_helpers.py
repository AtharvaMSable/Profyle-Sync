"""UI helper functions for Streamlit."""
import base64
import streamlit as st
import pandas as pd
from typing import List, Tuple
import random


def show_pdf_inline(file_path: str):
    """Display PDF file inline in Streamlit."""
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Could not find PDF: {file_path}")
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")


def get_table_download_link(df: pd.DataFrame, filename: str, link_text: str) -> str:
    """Generate download link for dataframe as CSV."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href


def display_course_recommendations(course_list: List[Tuple[str, str]], num_recommendations: int = 4) -> List[str]:
    """
    Display course recommendations in Streamlit.
    
    Args:
        course_list: List of (course_name, course_link) tuples
        num_recommendations: Number of courses to display
        
    Returns:
        List of displayed course names
    """
    if not course_list:
        return []
    
    displayed_courses = []
    
    try:
        # Shuffle for variety
        shuffled_courses = course_list.copy()
        random.shuffle(shuffled_courses)
        
        st.markdown("### 📚 Recommended Courses")
        
        for i, (c_name, c_link) in enumerate(shuffled_courses[:num_recommendations], 1):
            st.markdown(f"{i}. [{c_name}]({c_link})")
            displayed_courses.append(c_name)
    
    except Exception as e:
        st.warning(f"Error displaying course recommendations: {e}")
    
    return displayed_courses


def display_metric_card(title: str, value: str, icon: str = "📊"):
    """Display a metric card with custom styling."""
    st.markdown(f"""
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin: 0.5rem 0;">
            <h4 style="margin: 0; color: #262730;">{icon} {title}</h4>
            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0; color: #0068c9;">{value}</p>
        </div>
    """, unsafe_allow_html=True)


def create_skill_badge(skill: str, color: str = "#0068c9") -> str:
    """Create HTML for a skill badge."""
    return f'<span style="background-color: {color}; color: white; padding: 0.2rem 0.6rem; border-radius: 1rem; margin: 0.2rem; display: inline-block; font-size: 0.85rem;">{skill}</span>'


def display_skills_as_badges(skills: List[str], color: str = "#0068c9"):
    """Display skills as styled badges."""
    if not skills:
        st.info("No skills found")
        return
    
    badges_html = "".join([create_skill_badge(skill, color) for skill in skills])
    st.markdown(f'<div style="line-height: 2.5;">{badges_html}</div>', unsafe_allow_html=True)
