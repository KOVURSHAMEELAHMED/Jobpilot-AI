# 📁 backend/job_matcher_ai.py
"""
OFF-CAMPUS AI JOB MATCHER
AI-powered job matching using NLP and ML
"""

import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import re

class OffCampusJobMatcher:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.skill_database = self.load_skill_database()
        
    def load_skill_database(self):
        """Load comprehensive skill database"""
        return {
            'programming': ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'TypeScript'],
            'web_dev': ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Node.js', 'Express'],
            'data_science': ['Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'SQL'],
            'devops': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'CI/CD'],
            'automation': ['Selenium', 'Playwright', 'Cypress', 'Test Automation'],
            'soft_skills': ['Communication', 'Teamwork', 'Problem Solving', 'Leadership']
        }
    
    def calculate_job_match_score(self, resume_text, job_description):
        """Calculate match score between resume and job"""
        # Text similarity
        text_similarity = self.calculate_text_similarity(resume_text, job_description)
        
        # Skill matching
        skill_match = self.calculate_skill_match(resume_text, job_description)
        
        # Experience level matching
        experience_match = self.match_experience_level(resume_text, job_description)
        
        # Weighted score
        final_score = (text_similarity * 0.4) + (skill_match * 0.4) + (experience_match * 0.2)
        
        return {
            'overall_score': round(final_score * 100, 2),
            'text_similarity': round(text_similarity * 100, 2),
            'skill_match': round(skill_match * 100, 2),
            'experience_match': round(experience_match * 100, 2),
            'matched_skills': self.extract_matched_skills(resume_text, job_description),
            'missing_skills': self.extract_missing_skills(resume_text, job_description)
        }
    
    def calculate_text_similarity(self, text1, text2):
        """Calculate cosine similarity between texts"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except:
            return 0.0
    
    def extract_matched_skills(self, resume_text, job_description):
        """Extract skills that match between resume and job"""
        resume_skills = self.extract_skills_from_text(resume_text)
        job_skills = self.extract_skills_from_text(job_description)
        
        matched = []
        for skill in resume_skills:
            if any(job_skill.lower() == skill.lower() for job_skill in job_skills):
                matched.append(skill)
        
        return matched
    
    def extract_skills_from_text(self, text):
        """Extract technical skills from text"""
        found_skills = []
        text_lower = text.lower()
        
        for category, skills in self.skill_database.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
        
        # Also find skills using NLP
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG" or ent.label_ == "PRODUCT":
                # Check if it's a known tech skill
                if any(skill.lower() in ent.text.lower() for skill in 
                       self.skill_database['programming'] + 
                       self.skill_database['web_dev'] +
                       self.skill_database['data_science']):
                    found_skills.append(ent.text)
        
        return list(set(found_skills))