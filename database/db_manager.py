"""Supabase database manager and connection handler."""
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

from config.settings import SUPABASE_URL, SUPABASE_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseManager:
    """Manages Supabase database connections and operations."""
    
    _instance: Optional['SupabaseManager'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Singleton pattern to ensure single database connection."""
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Supabase client."""
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client."""
        try:
            if not SUPABASE_URL or not SUPABASE_KEY:
                logger.error("Supabase credentials not configured")
                return
            
            # Create client without proxy parameter for compatibility
            self._client = create_client(
                supabase_url=SUPABASE_URL,
                supabase_key=SUPABASE_KEY
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self._client = None
    
    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client."""
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._client is not None
    
    # Resume Operations
    def insert_resume(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Insert a new resume record."""
        if not self.is_connected:
            logger.error("Database not connected")
            return None
        
        try:
            result = self._client.table('resumes').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error inserting resume: {e}")
            return None
    
    def insert_analysis(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Insert a new analysis record."""
        if not self.is_connected:
            logger.error("Database not connected")
            return None
        
        try:
            result = self._client.table('resume_analysis').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error inserting analysis: {e}")
            return None
    
    def insert_resume_skills(self, resume_id: int, skills: List[str], method: str = 'rule_based') -> bool:
        """Insert skills for a resume."""
        if not self.is_connected:
            return False
        
        try:
            # First, ensure skills exist in skills table
            skill_ids = []
            for skill_name in skills:
                # Try to get or create skill
                skill_result = self._client.table('skills').select('id').eq('skill_name', skill_name).execute()
                
                if skill_result.data:
                    skill_ids.append(skill_result.data[0]['id'])
                else:
                    # Insert new skill
                    new_skill = self._client.table('skills').insert({'skill_name': skill_name}).execute()
                    if new_skill.data:
                        skill_ids.append(new_skill.data[0]['id'])
            
            # Insert resume-skill relationships
            for skill_id in skill_ids:
                self._client.table('resume_skills').insert({
                    'resume_id': resume_id,
                    'skill_id': skill_id,
                    'extraction_method': method
                }).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error inserting resume skills: {e}")
            return False
    
    def insert_jd_match(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Insert a job description match record."""
        if not self.is_connected:
            return None
        
        try:
            result = self._client.table('resume_jd_matches').insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error inserting JD match: {e}")
            return None
    
    # Query Operations
    def get_all_resumes(self, limit: int = 100) -> List[Dict]:
        """Get all resumes with their analysis."""
        if not self.is_connected:
            return []
        
        try:
            result = self._client.table('resumes').select(
                '*, resume_analysis(*, categories(category_name))'
            ).order('upload_timestamp', desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching resumes: {e}")
            return []
    
    def get_resume_by_id(self, resume_id: int) -> Optional[Dict]:
        """Get a single resume with full details."""
        if not self.is_connected:
            return None
        
        try:
            result = self._client.table('resumes').select(
                '*, resume_analysis(*, categories(category_name)), resume_skills(skills(skill_name), extraction_method)'
            ).eq('id', resume_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching resume: {e}")
            return None
    
    def get_resumes_by_category(self, category_name: str) -> List[Dict]:
        """Get all resumes for a specific category."""
        if not self.is_connected:
            return []
        
        try:
            result = self._client.table('resume_analysis').select(
                'resumes(*, resume_analysis(*)), categories!inner(category_name)'
            ).eq('categories.category_name', category_name).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching resumes by category: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics."""
        if not self.is_connected:
            return {}
        
        try:
            stats = {}
            
            # Total resumes
            total_resumes = self._client.table('resumes').select('id', count='exact').execute()
            stats['total_resumes'] = total_resumes.count if total_resumes else 0
            
            # Category distribution
            category_dist = self._client.table('resume_analysis').select(
                'category_id, categories(category_name)', count='exact'
            ).execute()
            stats['category_distribution'] = category_dist.data if category_dist.data else []
            
            # Recent activity (last 7 days)
            # This would require date filtering - simplified for now
            stats['recent_uploads'] = 0
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            return {}
    
    def search_resumes(self, query: str) -> List[Dict]:
        """Search resumes by filename or content."""
        if not self.is_connected:
            return []
        
        try:
            result = self._client.table('resumes').select(
                '*, resume_analysis(*, categories(category_name))'
            ).ilike('filename', f'%{query}%').execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error searching resumes: {e}")
            return []
    
    def initialize_categories(self) -> bool:
        """Initialize categories table with predefined categories."""
        if not self.is_connected:
            logger.error("Database not connected")
            return False
        
        try:
            from config.settings import CATEGORY_MAPPING
            
            # Check if categories exist
            existing = self._client.table('categories').select('id').execute()
            
            if existing.data and len(existing.data) > 0:
                logger.info(f"Categories already initialized ({len(existing.data)} categories found)")
                return True
            
            # Insert all categories from CATEGORY_MAPPING
            categories_data = [
                {'id': cat_id, 'category_name': cat_name}
                for cat_id, cat_name in CATEGORY_MAPPING.items()
            ]
            
            result = self._client.table('categories').insert(categories_data).execute()
            
            if result.data:
                logger.info(f"Successfully initialized {len(result.data)} categories")
                return True
            else:
                logger.warning("No categories were inserted")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing categories: {e}")
            return False


@st.cache_resource
def get_db_manager() -> SupabaseManager:
    """Get or create the database manager instance (cached)."""
    return SupabaseManager()
