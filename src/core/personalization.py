"""
Flashcard Style Personalization System
Provides different study modes and personalized learning experiences
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import random
from datetime import datetime, timedelta

class StudyMode(Enum):
    BASIC_EDUCATIONAL = "basic_educational"
    EXAM_PREP = "exam_prep"
    CHALLENGE = "challenge"
    FAST_REVIEW = "fast_review"
    SPACED_REPETITION = "spaced_repetition"

class CardStyle(Enum):
    DEFINITION_BASED = "definition_based"
    MULTIPLE_CHOICE = "multiple_choice"
    CLOZE_DELETION = "cloze_deletion"
    REVERSE_QUESTIONING = "reverse_questioning"
    SCENARIO_BASED = "scenario_based"

@dataclass
class StudySession:
    session_id: str
    user_id: str
    mode: StudyMode
    cards: List[Dict[str, Any]]
    current_card_index: int
    start_time: datetime
    responses: List[Dict[str, Any]]
    settings: Dict[str, Any]

@dataclass
class PersonalizationProfile:
    user_id: str
    preferred_modes: List[StudyMode]
    preferred_styles: List[CardStyle]
    difficulty_preference: str
    study_time_preference: int  # minutes
    performance_history: List[Dict[str, Any]]
    learning_goals: List[str]
    weak_areas: List[str]

class FlashcardPersonalizer:
    """Handles personalization of flashcard presentation and study modes"""
    
    def __init__(self):
        self.user_profiles = {}
        self.mode_configurations = self._initialize_mode_configurations()
    
    def _initialize_mode_configurations(self) -> Dict[StudyMode, Dict[str, Any]]:
        """Initialize configuration for different study modes"""
        return {
            StudyMode.BASIC_EDUCATIONAL: {
                "time_per_card": 30,  # seconds
                "show_hints": True,
                "allow_retries": True,
                "feedback_detail": "comprehensive",
                "card_styles": [CardStyle.DEFINITION_BASED, CardStyle.CLOZE_DELETION],
                "ui_theme": "clean_minimal"
            },
            StudyMode.EXAM_PREP: {
                "time_per_card": 20,
                "show_hints": False,
                "allow_retries": False,
                "feedback_detail": "immediate",
                "card_styles": [CardStyle.MULTIPLE_CHOICE, CardStyle.SCENARIO_BASED],
                "ui_theme": "exam_focused",
                "include_timer": True,
                "track_accuracy": True
            },
            StudyMode.CHALLENGE: {
                "time_per_card": 15,
                "show_hints": False,
                "allow_retries": False,
                "feedback_detail": "minimal",
                "card_styles": [CardStyle.REVERSE_QUESTIONING, CardStyle.CLOZE_DELETION],
                "ui_theme": "gamified",
                "scoring_system": True,
                "difficulty_progression": True
            },
            StudyMode.FAST_REVIEW: {
                "time_per_card": 10,
                "show_hints": False,
                "allow_retries": False,
                "feedback_detail": "none",
                "card_styles": [CardStyle.DEFINITION_BASED],
                "ui_theme": "minimalist",
                "auto_advance": True
            },
            StudyMode.SPACED_REPETITION: {
                "time_per_card": 25,
                "show_hints": True,
                "allow_retries": True,
                "feedback_detail": "adaptive",
                "card_styles": [CardStyle.DEFINITION_BASED, CardStyle.CLOZE_DELETION],
                "ui_theme": "spaced_rep",
                "algorithm": "sm2",
                "track_intervals": True
            }
        }
    
    def create_personalized_session(self, user_id: str, cards: List[Dict[str, Any]], 
                                  mode: StudyMode = None) -> StudySession:
        """Create a personalized study session"""
        
        # Get user profile or create default
        profile = self.get_user_profile(user_id)
        
        # Determine study mode
        if not mode:
            mode = profile.preferred_modes[0] if profile.preferred_modes else StudyMode.BASIC_EDUCATIONAL
        
        # Personalize cards based on mode and profile
        personalized_cards = self._personalize_cards(cards, mode, profile)
        
        # Create session
        session = StudySession(
            session_id=f"session_{user_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            mode=mode,
            cards=personalized_cards,
            current_card_index=0,
            start_time=datetime.now(),
            responses=[],
            settings=self.mode_configurations[mode].copy()
        )
        
        return session
    
    def _personalize_cards(self, cards: List[Dict[str, Any]], 
                          mode: StudyMode, 
                          profile: PersonalizationProfile) -> List[Dict[str, Any]]:
        """Personalize cards based on mode and user profile"""
        
        personalized_cards = []
        mode_config = self.mode_configurations[mode]
        
        for card in cards:
            personalized_card = card.copy()
            
            # Apply style transformations based on mode
            if mode == StudyMode.EXAM_PREP:
                personalized_card = self._convert_to_multiple_choice(personalized_card)
            elif mode == StudyMode.CHALLENGE:
                personalized_card = self._convert_to_reverse_questioning(personalized_card)
            elif mode == StudyMode.FAST_REVIEW:
                personalized_card = self._simplify_for_fast_review(personalized_card)
            
            # Add mode-specific metadata
            personalized_card['mode_settings'] = {
                'time_limit': mode_config.get('time_per_card', 30),
                'show_hints': mode_config.get('show_hints', True),
                'allow_retries': mode_config.get('allow_retries', True),
                'feedback_detail': mode_config.get('feedback_detail', 'comprehensive')
            }
            
            # Add difficulty adjustment based on user performance
            if profile.weak_areas and any(area in card.get('tags', []) for area in profile.weak_areas):
                personalized_card['adjusted_difficulty'] = 'easier'
                personalized_card['mode_settings']['time_limit'] += 10
                personalized_card['mode_settings']['show_hints'] = True
            
            personalized_cards.append(personalized_card)
        
        # Reorder cards based on mode strategy
        if mode == StudyMode.SPACED_REPETITION:
            personalized_cards = self._apply_spaced_repetition_order(personalized_cards, profile)
        elif mode == StudyMode.CHALLENGE:
            personalized_cards = self._apply_difficulty_progression(personalized_cards)
        
        return personalized_cards
    
    def _convert_to_multiple_choice(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """Convert card to multiple choice format"""
        if card.get('type') == 'multiple_choice':
            return card
        
        # Generate distractors (in production, use AI to generate better distractors)
        correct_answer = card.get('back', '')
        distractors = [
            "Alternative answer 1",
            "Alternative answer 2", 
            "Alternative answer 3"
        ]
        
        choices = [correct_answer] + distractors
        random.shuffle(choices)
        
        card['type'] = 'multiple_choice'
        card['choices'] = choices
        card['correct_answer'] = correct_answer
        
        return card
    
    def _convert_to_reverse_questioning(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """Convert card to reverse questioning format"""
        # Swap front and back for reverse questioning
        original_front = card.get('front', '')
        original_back = card.get('back', '')
        
        card['front'] = f"What question would have this answer: {original_back}"
        card['back'] = original_front
        card['type'] = 'reverse_questioning'
        
        return card
    
    def _simplify_for_fast_review(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify card for fast review mode"""
        # Truncate long content
        if len(card.get('front', '')) > 100:
            card['front'] = card['front'][:97] + "..."
        
        if len(card.get('back', '')) > 150:
            card['back'] = card['back'][:147] + "..."
        
        # Remove complex formatting
        card['simplified'] = True
        
        return card
    
    def _apply_spaced_repetition_order(self, cards: List[Dict[str, Any]], 
                                     profile: PersonalizationProfile) -> List[Dict[str, Any]]:
        """Apply spaced repetition algorithm to card ordering"""
        # Simple implementation - in production, use proper SM-2 algorithm
        
        # Prioritize cards that haven't been seen recently
        now = datetime.now()
        
        for card in cards:
            last_reviewed = card.get('last_reviewed')
            if last_reviewed:
                days_since_review = (now - datetime.fromisoformat(last_reviewed)).days
                card['priority'] = days_since_review
            else:
                card['priority'] = 999  # New cards get high priority
        
        # Sort by priority (highest first)
        cards.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return cards
    
    def _apply_difficulty_progression(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply difficulty progression for challenge mode"""
        # Sort cards by difficulty (easy to hard)
        difficulty_order = {'easy': 1, 'medium': 2, 'hard': 3}
        
        cards.sort(key=lambda x: difficulty_order.get(x.get('difficulty', 'medium'), 2))
        
        return cards
    
    def get_user_profile(self, user_id: str) -> PersonalizationProfile:
        """Get or create user personalization profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = PersonalizationProfile(
                user_id=user_id,
                preferred_modes=[StudyMode.BASIC_EDUCATIONAL],
                preferred_styles=[CardStyle.DEFINITION_BASED],
                difficulty_preference="medium",
                study_time_preference=30,
                performance_history=[],
                learning_goals=[],
                weak_areas=[]
            )
        
        return self.user_profiles[user_id]
    
    def update_user_profile(self, user_id: str, session_data: Dict[str, Any]):
        """Update user profile based on session performance"""
        profile = self.get_user_profile(user_id)
        
        # Analyze session performance
        total_cards = len(session_data.get('responses', []))
        correct_responses = sum(1 for r in session_data.get('responses', []) 
                              if r.get('correct', False))
        accuracy = correct_responses / total_cards if total_cards > 0 else 0
        
        # Update performance history
        performance_entry = {
            'date': datetime.now().isoformat(),
            'mode': session_data.get('mode'),
            'accuracy': accuracy,
            'total_cards': total_cards,
            'study_time': session_data.get('study_time', 0)
        }
        profile.performance_history.append(performance_entry)
        
        # Identify weak areas
        weak_topics = []
        for response in session_data.get('responses', []):
            if not response.get('correct', False):
                card_tags = response.get('card', {}).get('tags', [])
                weak_topics.extend(card_tags)
        
        # Update weak areas (keep most frequent)
        from collections import Counter
        weak_area_counts = Counter(weak_topics)
        profile.weak_areas = [topic for topic, count in weak_area_counts.most_common(5)]
        
        # Adjust preferences based on performance
        if accuracy > 0.8:  # High performance
            if session_data.get('mode') not in profile.preferred_modes:
                profile.preferred_modes.append(StudyMode(session_data.get('mode')))
        
        # Keep only recent performance history (last 30 entries)
        profile.performance_history = profile.performance_history[-30:]

class UIThemeManager:
    """Manages different UI themes for different study modes"""
    
    def __init__(self):
        self.themes = {
            "clean_minimal": {
                "colors": {
                    "primary": "#2563eb",
                    "background": "#ffffff",
                    "text": "#1f2937",
                    "accent": "#10b981"
                },
                "fonts": {
                    "primary": "Inter, sans-serif",
                    "size": "16px"
                },
                "layout": {
                    "card_padding": "2rem",
                    "border_radius": "12px",
                    "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                }
            },
            "exam_focused": {
                "colors": {
                    "primary": "#dc2626",
                    "background": "#fef2f2",
                    "text": "#1f2937",
                    "accent": "#f59e0b"
                },
                "fonts": {
                    "primary": "system-ui, sans-serif",
                    "size": "18px"
                },
                "layout": {
                    "card_padding": "1.5rem",
                    "border_radius": "8px",
                    "shadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
                },
                "features": {
                    "timer_visible": True,
                    "progress_bar": True
                }
            },
            "gamified": {
                "colors": {
                    "primary": "#7c3aed",
                    "background": "#faf5ff",
                    "text": "#1f2937",
                    "accent": "#06b6d4"
                },
                "fonts": {
                    "primary": "Poppins, sans-serif",
                    "size": "16px"
                },
                "layout": {
                    "card_padding": "2rem",
                    "border_radius": "16px",
                    "shadow": "0 8px 25px -5px rgba(0, 0, 0, 0.1)"
                },
                "features": {
                    "score_display": True,
                    "streak_counter": True,
                    "animations": True
                }
            },
            "minimalist": {
                "colors": {
                    "primary": "#374151",
                    "background": "#f9fafb",
                    "text": "#111827",
                    "accent": "#6b7280"
                },
                "fonts": {
                    "primary": "system-ui, sans-serif",
                    "size": "14px"
                },
                "layout": {
                    "card_padding": "1rem",
                    "border_radius": "4px",
                    "shadow": "none"
                },
                "features": {
                    "minimal_ui": True,
                    "auto_advance": True
                }
            }
        }
    
    def get_theme_config(self, theme_name: str) -> Dict[str, Any]:
        """Get theme configuration"""
        return self.themes.get(theme_name, self.themes["clean_minimal"])
    
    def generate_css(self, theme_name: str) -> str:
        """Generate CSS for a specific theme"""
        theme = self.get_theme_config(theme_name)
        
        css = f"""
        .flashcard-container {{
            background-color: {theme['colors']['background']};
            color: {theme['colors']['text']};
            font-family: {theme['fonts']['primary']};
            font-size: {theme['fonts']['size']};
        }}
        
        .flashcard {{
            padding: {theme['layout']['card_padding']};
            border-radius: {theme['layout']['border_radius']};
            box-shadow: {theme['layout']['shadow']};
            background-color: white;
        }}
        
        .primary-button {{
            background-color: {theme['colors']['primary']};
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: {theme['layout']['border_radius']};
            font-family: {theme['fonts']['primary']};
        }}
        
        .accent-element {{
            color: {theme['colors']['accent']};
        }}
        """
        
        # Add theme-specific features
        if theme.get('features', {}).get('timer_visible'):
            css += """
            .timer-display {
                position: fixed;
                top: 1rem;
                right: 1rem;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 4px;
            }
            """
        
        if theme.get('features', {}).get('score_display'):
            css += """
            .score-display {
                position: fixed;
                top: 1rem;
                left: 1rem;
                background: linear-gradient(45deg, #7c3aed, #06b6d4);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-weight: bold;
            }
            """
        
        return css