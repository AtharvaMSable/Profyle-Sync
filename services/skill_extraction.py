"""Skill extraction service using rule-based and NER methods."""
import re
from typing import List, Set
from config.settings import SKILLS_DB


class SkillExtractor:
    """Extracts skills from resume text using multiple methods."""
    
    def __init__(self, nlp_model=None):
        """Initialize skill extractor with optional spaCy model."""
        self.nlp = nlp_model
        self.skills_db_lower = set([s.lower() for s in SKILLS_DB])
    
    def extract_rule_based(self, resume_text: str) -> List[str]:
        """
        Extract skills using rule-based pattern matching.
        
        Args:
            resume_text: The resume text to extract skills from
            
        Returns:
            List of extracted skills
        """
        processed_text = ' '.join(resume_text.lower().split())
        found_skills: Set[str] = set()
        
        for skill in self.skills_db_lower:
            skill_pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(skill_pattern, processed_text):
                # Find the original case skill name
                original_skill = next((s for s in SKILLS_DB if s.lower() == skill), skill)
                found_skills.add(original_skill)
        
        return sorted(list(found_skills))
    
    def extract_ner_based(self, resume_text: str) -> List[str]:
        """
        Extract skills using Named Entity Recognition (spaCy).
        
        Args:
            resume_text: The resume text to extract skills from
            
        Returns:
            List of extracted skills
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(resume_text)
        found_skills_ner: Set[str] = set()
        potential_skill_labels = {"ORG", "PRODUCT", "WORK_OF_ART", "LAW", "NORP"}
        
        for ent in doc.ents:
            ent_text_lower = ent.text.lower().strip()
            
            # Prioritize direct match with SKILLS_DB
            if ent_text_lower in self.skills_db_lower:
                original_skill = next((s for s in SKILLS_DB if s.lower() == ent_text_lower), ent_text_lower)
                found_skills_ner.add(original_skill)
            elif ent.label_ in potential_skill_labels:
                # Additional filtering for potential skills
                if 2 <= len(ent_text_lower) < 30 and not ent_text_lower.isdigit():
                    # Could add to found skills or flag for review
                    pass
        
        return sorted(list(found_skills_ner))
    
    def extract_combined(self, resume_text: str) -> List[str]:
        """
        Extract skills using both rule-based and NER methods.
        
        Args:
            resume_text: The resume text to extract skills from
            
        Returns:
            Combined list of extracted skills
        """
        rule_skills = self.extract_rule_based(resume_text)
        ner_skills = self.extract_ner_based(resume_text)
        
        # Combine and deduplicate
        combined = set(rule_skills) | set(ner_skills)
        return sorted(list(combined))
    
    def match_with_jd(self, resume_skills: List[str], jd_skills: List[str]) -> dict:
        """
        Match resume skills with job description skills.
        
        Args:
            resume_skills: List of skills from resume
            jd_skills: List of skills from job description
            
        Returns:
            Dictionary with matching, missing skills and score
        """
        resume_skills_set = set(s.lower() for s in resume_skills)
        jd_skills_set = set(s.lower() for s in jd_skills)
        
        matching_skills = resume_skills_set.intersection(jd_skills_set)
        missing_skills = jd_skills_set.difference(resume_skills_set)
        
        score = (len(matching_skills) / len(jd_skills_set)) * 100 if jd_skills_set else 0
        
        return {
            'score': round(score, 2),
            'matching_skills': sorted(list(matching_skills)),
            'missing_skills': sorted(list(missing_skills)),
            'total_jd_skills': len(jd_skills_set),
            'matched_count': len(matching_skills)
        }
