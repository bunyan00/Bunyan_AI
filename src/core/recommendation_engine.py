"""
Smart Flashcard Recommendation Engine
Provides intelligent suggestions based on content analysis and user preferences
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningObjective(Enum):
    MEMORIZATION = "memorization"
    COMPREHENSION = "comprehension"
    APPLICATION = "application"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"

@dataclass
class FlashcardTemplate:
    id: str
    title: str
    content: str
    field: str
    difficulty: DifficultyLevel
    learning_objective: LearningObjective
    tags: List[str]
    usage_count: int
    rating: float
    embedding: Optional[np.ndarray] = None

@dataclass
class RecommendationResult:
    template: FlashcardTemplate
    similarity_score: float
    relevance_reason: str
    suggested_modifications: List[str]

class KnowledgeBaseManager:
    """Manages the pre-built knowledge base of flashcard templates"""
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._initialize_database()
        self._load_predefined_templates()
    
    def _initialize_database(self):
        """Initialize the knowledge base database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcard_templates (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                field TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                learning_objective TEXT NOT NULL,
                tags TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                embedding BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_interactions (
                user_id TEXT,
                template_id TEXT,
                interaction_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                feedback_score INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_predefined_templates(self):
        """Load predefined flashcard templates for various fields"""
        templates = [
            # Medicine Templates
            {
                "id": "med_001",
                "title": "Anatomy Structure",
                "content": "What is the function of {structure}? Location: {location}. Function: {function}.",
                "field": "medicine",
                "difficulty": "intermediate",
                "learning_objective": "comprehension",
                "tags": ["anatomy", "structure", "function"]
            },
            {
                "id": "med_002", 
                "title": "Drug Mechanism",
                "content": "Drug: {drug_name}. Mechanism: {mechanism}. Indication: {indication}. Side effects: {side_effects}.",
                "field": "medicine",
                "difficulty": "advanced",
                "learning_objective": "application",
                "tags": ["pharmacology", "drugs", "mechanism"]
            },
            
            # Engineering Templates
            {
                "id": "eng_001",
                "title": "Formula Application",
                "content": "Formula: {formula}. Used for: {application}. Variables: {variables}. Units: {units}.",
                "field": "engineering",
                "difficulty": "intermediate",
                "learning_objective": "application",
                "tags": ["formula", "calculation", "physics"]
            },
            {
                "id": "eng_002",
                "title": "System Design",
                "content": "System: {system_name}. Components: {components}. Function: {function}. Advantages: {advantages}.",
                "field": "engineering",
                "difficulty": "advanced",
                "learning_objective": "analysis",
                "tags": ["design", "systems", "components"]
            },
            
            # Computer Science Templates
            {
                "id": "cs_001",
                "title": "Algorithm Complexity",
                "content": "Algorithm: {algorithm}. Time Complexity: {time_complexity}. Space Complexity: {space_complexity}. Use Case: {use_case}.",
                "field": "computer_science",
                "difficulty": "advanced",
                "learning_objective": "analysis",
                "tags": ["algorithms", "complexity", "performance"]
            },
            {
                "id": "cs_002",
                "title": "Data Structure",
                "content": "Data Structure: {structure}. Operations: {operations}. Time Complexity: {complexity}. Best Use: {use_case}.",
                "field": "computer_science",
                "difficulty": "intermediate",
                "learning_objective": "comprehension",
                "tags": ["data_structures", "operations", "efficiency"]
            },
            
            # Business Templates
            {
                "id": "bus_001",
                "title": "Business Model",
                "content": "Model: {model_name}. Key Features: {features}. Advantages: {advantages}. Examples: {examples}.",
                "field": "business",
                "difficulty": "intermediate",
                "learning_objective": "comprehension",
                "tags": ["business_model", "strategy", "examples"]
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for template in templates:
            # Generate embedding
            embedding = self.sentence_model.encode(template["content"])
            
            cursor.execute('''
                INSERT OR REPLACE INTO flashcard_templates 
                (id, title, content, field, difficulty, learning_objective, tags, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template["id"],
                template["title"],
                template["content"],
                template["field"],
                template["difficulty"],
                template["learning_objective"],
                json.dumps(template["tags"]),
                embedding.tobytes()
            ))
        
        conn.commit()
        conn.close()

class SmartRecommendationEngine:
    """Advanced recommendation engine for flashcard suggestions"""
    
    def __init__(self, knowledge_base: KnowledgeBaseManager):
        self.knowledge_base = knowledge_base
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.field_classifier = self._train_field_classifier()
    
    def _train_field_classifier(self):
        """Train a classifier to detect academic fields"""
        # In production, this would use a more sophisticated model
        field_keywords = {
            "medicine": ["anatomy", "physiology", "disease", "treatment", "diagnosis", "patient", "medical"],
            "engineering": ["design", "system", "mechanical", "electrical", "civil", "formula", "calculation"],
            "computer_science": ["algorithm", "data", "programming", "software", "computer", "code", "system"],
            "business": ["market", "strategy", "management", "finance", "economics", "company", "profit"],
            "physics": ["force", "energy", "motion", "wave", "particle", "quantum", "relativity"],
            "chemistry": ["molecule", "reaction", "compound", "element", "bond", "solution", "acid"],
            "biology": ["cell", "organism", "evolution", "genetics", "ecosystem", "species", "DNA"]
        }
        return field_keywords
    
    def detect_field(self, content: str) -> str:
        """Detect the academic field of the content"""
        content_lower = content.lower()
        field_scores = {}
        
        for field, keywords in self.field_classifier.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            field_scores[field] = score
        
        # Return field with highest score, default to 'general'
        if max(field_scores.values()) > 0:
            return max(field_scores, key=field_scores.get)
        return "general"
    
    def get_recommendations(self, 
                          lecture_content: str, 
                          user_preferences: Dict[str, Any] = None,
                          max_recommendations: int = 5) -> List[RecommendationResult]:
        """Get smart flashcard recommendations based on lecture content"""
        
        # Detect field
        detected_field = self.detect_field(lecture_content)
        
        # Generate content embedding
        content_embedding = self.sentence_model.encode(lecture_content)
        
        # Get templates from knowledge base
        templates = self._get_templates_by_field(detected_field)
        
        # Calculate similarities and rank
        recommendations = []
        for template in templates:
            similarity = self._calculate_similarity(content_embedding, template.embedding)
            
            # Apply user preference filters
            if self._matches_user_preferences(template, user_preferences):
                relevance_reason = self._generate_relevance_reason(template, detected_field, similarity)
                modifications = self._suggest_modifications(template, lecture_content)
                
                recommendations.append(RecommendationResult(
                    template=template,
                    similarity_score=similarity,
                    relevance_reason=relevance_reason,
                    suggested_modifications=modifications
                ))
        
        # Sort by similarity and return top recommendations
        recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
        return recommendations[:max_recommendations]
    
    def _get_templates_by_field(self, field: str) -> List[FlashcardTemplate]:
        """Retrieve templates from the knowledge base by field"""
        conn = sqlite3.connect(self.knowledge_base.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, field, difficulty, learning_objective, tags, usage_count, rating, embedding
            FROM flashcard_templates 
            WHERE field = ? OR field = 'general'
            ORDER BY rating DESC, usage_count DESC
        ''', (field,))
        
        templates = []
        for row in cursor.fetchall():
            embedding = np.frombuffer(row[9], dtype=np.float32) if row[9] else None
            template = FlashcardTemplate(
                id=row[0],
                title=row[1],
                content=row[2],
                field=row[3],
                difficulty=DifficultyLevel(row[4]),
                learning_objective=LearningObjective(row[5]),
                tags=json.loads(row[6]),
                usage_count=row[7],
                rating=row[8],
                embedding=embedding
            )
            templates.append(template)
        
        conn.close()
        return templates
    
    def _calculate_similarity(self, content_embedding: np.ndarray, template_embedding: np.ndarray) -> float:
        """Calculate semantic similarity between content and template"""
        if template_embedding is None:
            return 0.0
        
        # Reshape for cosine similarity calculation
        content_embedding = content_embedding.reshape(1, -1)
        template_embedding = template_embedding.reshape(1, -1)
        
        similarity = cosine_similarity(content_embedding, template_embedding)[0][0]
        return float(similarity)
    
    def _matches_user_preferences(self, template: FlashcardTemplate, preferences: Dict[str, Any]) -> bool:
        """Check if template matches user preferences"""
        if not preferences:
            return True
        
        # Check difficulty preference
        if 'difficulty' in preferences:
            if template.difficulty.value not in preferences['difficulty']:
                return False
        
        # Check learning objective preference
        if 'learning_objective' in preferences:
            if template.learning_objective.value not in preferences['learning_objective']:
                return False
        
        # Check tag preferences
        if 'required_tags' in preferences:
            if not any(tag in template.tags for tag in preferences['required_tags']):
                return False
        
        return True
    
    def _generate_relevance_reason(self, template: FlashcardTemplate, field: str, similarity: float) -> str:
        """Generate explanation for why this template is relevant"""
        reasons = []
        
        if template.field == field:
            reasons.append(f"Matches detected field: {field}")
        
        if similarity > 0.7:
            reasons.append("High semantic similarity to content")
        elif similarity > 0.5:
            reasons.append("Moderate semantic similarity to content")
        
        if template.rating > 4.0:
            reasons.append("Highly rated by other users")
        
        if template.usage_count > 100:
            reasons.append("Frequently used template")
        
        return "; ".join(reasons) if reasons else "General template match"
    
    def _suggest_modifications(self, template: FlashcardTemplate, content: str) -> List[str]:
        """Suggest modifications to adapt template to specific content"""
        modifications = []
        
        # Analyze content for specific entities
        if "definition" in content.lower():
            modifications.append("Add definition-based questions")
        
        if any(word in content.lower() for word in ["process", "step", "procedure"]):
            modifications.append("Convert to process-based cloze deletions")
        
        if any(word in content.lower() for word in ["compare", "contrast", "difference"]):
            modifications.append("Create comparison-style questions")
        
        if template.difficulty == DifficultyLevel.ADVANCED and "basic" in content.lower():
            modifications.append("Simplify language for better understanding")
        
        return modifications

class PersonalizationEngine:
    """Handles user-specific personalization and learning analytics"""
    
    def __init__(self):
        self.user_profiles = {}
    
    def update_user_profile(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user profile based on interactions"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferred_difficulty': [],
                'preferred_fields': [],
                'learning_objectives': [],
                'performance_history': []
            }
        
        profile = self.user_profiles[user_id]
        
        # Update preferences based on positive interactions
        if interaction_data.get('feedback_score', 0) >= 4:
            if 'difficulty' in interaction_data:
                profile['preferred_difficulty'].append(interaction_data['difficulty'])
            if 'field' in interaction_data:
                profile['preferred_fields'].append(interaction_data['field'])
        
        # Track performance
        profile['performance_history'].append({
            'timestamp': interaction_data.get('timestamp'),
            'score': interaction_data.get('feedback_score', 0),
            'template_id': interaction_data.get('template_id')
        })
    
    def get_personalized_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get personalized preferences for a user"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        
        # Calculate most frequent preferences
        preferences = {}
        
        if profile['preferred_difficulty']:
            preferences['difficulty'] = list(set(profile['preferred_difficulty']))
        
        if profile['preferred_fields']:
            preferences['fields'] = list(set(profile['preferred_fields']))
        
        return preferences