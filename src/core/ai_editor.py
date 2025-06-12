"""
AI-Powered Interactive Flashcard Editor
Provides real-time AI suggestions and dynamic editing capabilities
"""

import openai
import google.generativeai as genai
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import re
import asyncio
from datetime import datetime

class SuggestionType(Enum):
    CLOZE_CONVERSION = "cloze_conversion"
    SIMPLIFICATION = "simplification"
    DIFFICULTY_ADJUSTMENT = "difficulty_adjustment"
    FORMAT_IMPROVEMENT = "format_improvement"
    CONTENT_ENHANCEMENT = "content_enhancement"
    GRAMMAR_CORRECTION = "grammar_correction"

@dataclass
class AISuggestion:
    type: SuggestionType
    original_text: str
    suggested_text: str
    confidence: float
    reasoning: str
    preview: str

@dataclass
class EditSession:
    session_id: str
    user_id: str
    card_id: str
    original_content: Dict[str, str]
    current_content: Dict[str, str]
    suggestions: List[AISuggestion]
    accepted_suggestions: List[str]
    rejected_suggestions: List[str]
    timestamp: datetime

class AIFlashcardEditor:
    """Advanced AI-powered flashcard editor with real-time suggestions"""
    
    def __init__(self, openai_api_key: str, gemini_api_key: str):
        openai.api_key = openai_api_key
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.active_sessions = {}
        
        # Suggestion templates
        self.suggestion_prompts = {
            SuggestionType.CLOZE_CONVERSION: """
            Convert this flashcard question into a cloze deletion format. 
            Identify the most important term or concept and replace it with {{c1::term}}.
            
            Original: {text}
            
            Provide the cloze version and explain why this term was chosen.
            """,
            
            SuggestionType.SIMPLIFICATION: """
            Simplify this flashcard content to make it more accessible while maintaining accuracy.
            Remove jargon, use simpler words, and make the explanation clearer.
            
            Original: {text}
            
            Provide simplified version and explain the changes made.
            """,
            
            SuggestionType.DIFFICULTY_ADJUSTMENT: """
            Adjust the difficulty of this flashcard to {target_level} level.
            {target_level} level should be appropriate for {context}.
            
            Original: {text}
            
            Provide adjusted version and explain the difficulty changes.
            """,
            
            SuggestionType.FORMAT_IMPROVEMENT: """
            Improve the formatting and structure of this flashcard for better learning.
            Consider using bullet points, clear sections, or better organization.
            
            Original: {text}
            
            Provide improved format and explain the structural changes.
            """,
            
            SuggestionType.CONTENT_ENHANCEMENT: """
            Enhance this flashcard by adding relevant context, examples, or mnemonics.
            Make it more memorable and comprehensive without making it too long.
            
            Original: {text}
            
            Provide enhanced version and explain the additions.
            """
        }
    
    def start_edit_session(self, user_id: str, card_content: Dict[str, str]) -> str:
        """Start a new editing session"""
        session_id = f"edit_{user_id}_{datetime.now().timestamp()}"
        
        session = EditSession(
            session_id=session_id,
            user_id=user_id,
            card_id=card_content.get('id', ''),
            original_content=card_content.copy(),
            current_content=card_content.copy(),
            suggestions=[],
            accepted_suggestions=[],
            rejected_suggestions=[],
            timestamp=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        return session_id
    
    async def get_real_time_suggestions(self, session_id: str, 
                                      field_changed: str, 
                                      new_value: str) -> List[AISuggestion]:
        """Get real-time AI suggestions as user types"""
        if session_id not in self.active_sessions:
            return []
        
        session = self.active_sessions[session_id]
        session.current_content[field_changed] = new_value
        
        suggestions = []
        
        # Generate different types of suggestions
        if len(new_value) > 20:  # Only suggest for substantial content
            # Cloze conversion suggestion
            if field_changed == 'front' and not '{{c1::' in new_value:
                cloze_suggestion = await self._generate_cloze_suggestion(new_value)
                if cloze_suggestion:
                    suggestions.append(cloze_suggestion)
            
            # Simplification suggestion
            if self._is_complex_text(new_value):
                simplification = await self._generate_simplification_suggestion(new_value)
                if simplification:
                    suggestions.append(simplification)
            
            # Format improvement suggestion
            if self._needs_formatting(new_value):
                format_suggestion = await self._generate_format_suggestion(new_value)
                if format_suggestion:
                    suggestions.append(format_suggestion)
        
        session.suggestions.extend(suggestions)
        return suggestions
    
    async def _generate_cloze_suggestion(self, text: str) -> Optional[AISuggestion]:
        """Generate cloze deletion suggestion"""
        try:
            prompt = self.suggestion_prompts[SuggestionType.CLOZE_CONVERSION].format(text=text)
            
            response = await self._call_openai_async(prompt)
            
            # Parse response to extract cloze version
            cloze_match = re.search(r'\{\{c1::(.*?)\}\}', response)
            if cloze_match:
                suggested_text = response.split('\n')[0]  # First line usually contains the suggestion
                
                return AISuggestion(
                    type=SuggestionType.CLOZE_CONVERSION,
                    original_text=text,
                    suggested_text=suggested_text,
                    confidence=0.8,
                    reasoning="Convert to cloze deletion for active recall",
                    preview=suggested_text[:100] + "..." if len(suggested_text) > 100 else suggested_text
                )
        except Exception as e:
            print(f"Error generating cloze suggestion: {e}")
        
        return None
    
    async def _generate_simplification_suggestion(self, text: str) -> Optional[AISuggestion]:
        """Generate text simplification suggestion"""
        try:
            prompt = self.suggestion_prompts[SuggestionType.SIMPLIFICATION].format(text=text)
            
            # Use Gemini for simplification
            response = self.gemini_model.generate_content(prompt)
            suggested_text = response.text.split('\n')[0]
            
            return AISuggestion(
                type=SuggestionType.SIMPLIFICATION,
                original_text=text,
                suggested_text=suggested_text,
                confidence=0.7,
                reasoning="Simplify complex language for better understanding",
                preview=suggested_text[:100] + "..." if len(suggested_text) > 100 else suggested_text
            )
        except Exception as e:
            print(f"Error generating simplification suggestion: {e}")
        
        return None
    
    async def _generate_format_suggestion(self, text: str) -> Optional[AISuggestion]:
        """Generate formatting improvement suggestion"""
        try:
            prompt = self.suggestion_prompts[SuggestionType.FORMAT_IMPROVEMENT].format(text=text)
            
            response = await self._call_openai_async(prompt)
            suggested_text = response.split('\n')[0]
            
            return AISuggestion(
                type=SuggestionType.FORMAT_IMPROVEMENT,
                original_text=text,
                suggested_text=suggested_text,
                confidence=0.6,
                reasoning="Improve formatting for better readability",
                preview=suggested_text[:100] + "..." if len(suggested_text) > 100 else suggested_text
            )
        except Exception as e:
            print(f"Error generating format suggestion: {e}")
        
        return None
    
    async def _call_openai_async(self, prompt: str) -> str:
        """Async call to OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert educational content editor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return ""
    
    def _is_complex_text(self, text: str) -> bool:
        """Check if text is complex and might benefit from simplification"""
        # Simple heuristics for complexity
        complex_indicators = [
            len(text.split()) > 20,  # Long sentences
            len([word for word in text.split() if len(word) > 8]) > 3,  # Many long words
            text.count(',') > 3,  # Many clauses
            any(word in text.lower() for word in ['however', 'nevertheless', 'furthermore', 'consequently'])
        ]
        return sum(complex_indicators) >= 2
    
    def _needs_formatting(self, text: str) -> bool:
        """Check if text would benefit from better formatting"""
        formatting_indicators = [
            len(text) > 100 and '\n' not in text,  # Long text without breaks
            text.count('.') > 2 and not any(marker in text for marker in ['•', '-', '1.', '2.']),  # Multiple points without bullets
            ':' in text and '\n' not in text  # Lists without proper formatting
        ]
        return any(formatting_indicators)
    
    def apply_suggestion(self, session_id: str, suggestion_id: str, accept: bool) -> bool:
        """Apply or reject a suggestion"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Find the suggestion
        suggestion = None
        for s in session.suggestions:
            if id(s) == int(suggestion_id):  # Simple ID matching
                suggestion = s
                break
        
        if not suggestion:
            return False
        
        if accept:
            # Apply the suggestion
            if suggestion.type == SuggestionType.CLOZE_CONVERSION:
                session.current_content['front'] = suggestion.suggested_text
            else:
                # Determine which field to update based on suggestion type
                field = 'front' if 'front' in session.current_content else 'back'
                session.current_content[field] = suggestion.suggested_text
            
            session.accepted_suggestions.append(suggestion_id)
        else:
            session.rejected_suggestions.append(suggestion_id)
        
        return True
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of editing session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return {
            'session_id': session.session_id,
            'current_content': session.current_content,
            'pending_suggestions': [
                {
                    'id': str(id(s)),
                    'type': s.type.value,
                    'preview': s.preview,
                    'confidence': s.confidence,
                    'reasoning': s.reasoning
                }
                for s in session.suggestions 
                if str(id(s)) not in session.accepted_suggestions + session.rejected_suggestions
            ],
            'changes_made': session.current_content != session.original_content
        }
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End editing session and return final content"""
        if session_id not in self.active_sessions:
            return {}
        
        session = self.active_sessions[session_id]
        final_content = session.current_content.copy()
        
        # Clean up
        del self.active_sessions[session_id]
        
        return {
            'final_content': final_content,
            'suggestions_accepted': len(session.accepted_suggestions),
            'suggestions_rejected': len(session.rejected_suggestions),
            'total_changes': len([k for k in final_content.keys() 
                                if final_content[k] != session.original_content.get(k, '')])
        }

class SmartContentEnhancer:
    """Enhances flashcard content with additional context and examples"""
    
    def __init__(self, ai_editor: AIFlashcardEditor):
        self.ai_editor = ai_editor
    
    async def enhance_with_examples(self, content: str, field: str) -> str:
        """Add relevant examples to flashcard content"""
        prompt = f"""
        Enhance this {field} flashcard content by adding 1-2 relevant, concrete examples.
        Keep the examples brief and directly related to the concept.
        
        Original content: {content}
        
        Provide enhanced version with examples integrated naturally.
        """
        
        try:
            response = await self.ai_editor._call_openai_async(prompt)
            return response
        except Exception as e:
            print(f"Error enhancing with examples: {e}")
            return content
    
    async def add_mnemonics(self, content: str) -> str:
        """Generate mnemonic devices for better memorization"""
        prompt = f"""
        Create a simple, memorable mnemonic device for this flashcard content.
        The mnemonic should be easy to remember and directly related to the concept.
        
        Content: {content}
        
        Provide the mnemonic and briefly explain how it helps remember the concept.
        """
        
        try:
            response = await self.ai_editor._call_openai_async(prompt)
            return response
        except Exception as e:
            print(f"Error generating mnemonic: {e}")
            return ""
    
    async def suggest_related_concepts(self, content: str) -> List[str]:
        """Suggest related concepts for additional study"""
        prompt = f"""
        Based on this flashcard content, suggest 3-5 related concepts that a student should also study.
        Provide only the concept names, one per line.
        
        Content: {content}
        """
        
        try:
            response = await self.ai_editor._call_openai_async(prompt)
            concepts = [line.strip() for line in response.split('\n') if line.strip()]
            return concepts[:5]  # Limit to 5 suggestions
        except Exception as e:
            print(f"Error suggesting related concepts: {e}")
            return []