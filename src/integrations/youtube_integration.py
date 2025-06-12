"""
YouTube Integration Module
Extracts audio transcripts and generates flashcards from YouTube videos
"""

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests
from typing import Dict, List, Any, Optional
import tempfile
import os
from dataclasses import dataclass
import json

@dataclass
class YouTubeVideoInfo:
    video_id: str
    title: str
    description: str
    duration: int  # seconds
    channel: str
    upload_date: str
    view_count: int
    language: str

@dataclass
class TranscriptSegment:
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None

class YouTubeProcessor:
    """Processes YouTube videos for educational content extraction"""
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True
        }
    
    def extract_video_info(self, url: str) -> Optional[YouTubeVideoInfo]:
        """Extract basic information about a YouTube video"""
        try:
            video_id = self._extract_video_id(url)
            if not video_id:
                return None
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return YouTubeVideoInfo(
                    video_id=video_id,
                    title=info.get('title', ''),
                    description=info.get('description', ''),
                    duration=info.get('duration', 0),
                    channel=info.get('uploader', ''),
                    upload_date=info.get('upload_date', ''),
                    view_count=info.get('view_count', 0),
                    language=info.get('language', 'en')
                )
        except Exception as e:
            print(f"Error extracting video info: {e}")
            return None
    
    def get_transcript(self, url: str, language: str = 'en') -> List[TranscriptSegment]:
        """Get transcript from YouTube video"""
        try:
            video_id = self._extract_video_id(url)
            if not video_id:
                return []
            
            # Try to get transcript in specified language
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            except:
                # Fallback to any available language
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            segments = []
            for entry in transcript_list:
                segment = TranscriptSegment(
                    start_time=entry['start'],
                    end_time=entry['start'] + entry['duration'],
                    text=entry['text']
                )
                segments.append(segment)
            
            return segments
            
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return []
    
    def download_audio(self, url: str, output_dir: str = None) -> Optional[str]:
        """Download audio from YouTube video"""
        try:
            if not output_dir:
                output_dir = tempfile.gettempdir()
            
            video_id = self._extract_video_id(url)
            output_path = os.path.join(output_dir, f"{video_id}.mp3")
            
            ydl_opts = self.ydl_opts.copy()
            ydl_opts['outtmpl'] = output_path.replace('.mp3', '.%(ext)s')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            return output_path
            
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

class YouTubeContentAnalyzer:
    """Analyzes YouTube content for educational value and structure"""
    
    def __init__(self):
        self.educational_keywords = [
            'lecture', 'tutorial', 'lesson', 'course', 'education', 'learning',
            'explanation', 'guide', 'how to', 'introduction', 'basics',
            'advanced', 'theory', 'practice', 'example', 'demonstration'
        ]
        
        self.subject_keywords = {
            'mathematics': ['math', 'algebra', 'calculus', 'geometry', 'statistics'],
            'science': ['physics', 'chemistry', 'biology', 'science', 'experiment'],
            'computer_science': ['programming', 'coding', 'algorithm', 'software', 'computer'],
            'history': ['history', 'historical', 'ancient', 'medieval', 'modern'],
            'language': ['language', 'grammar', 'vocabulary', 'pronunciation', 'literature']
        }
    
    def analyze_educational_content(self, video_info: YouTubeVideoInfo, 
                                  transcript: List[TranscriptSegment]) -> Dict[str, Any]:
        """Analyze if content is educational and extract key information"""
        
        # Combine title, description, and transcript for analysis
        full_text = f"{video_info.title} {video_info.description}"
        if transcript:
            full_text += " " + " ".join([seg.text for seg in transcript])
        
        full_text = full_text.lower()
        
        # Check educational indicators
        educational_score = sum(1 for keyword in self.educational_keywords 
                              if keyword in full_text)
        
        # Identify subject area
        subject_scores = {}
        for subject, keywords in self.subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            if score > 0:
                subject_scores[subject] = score
        
        primary_subject = max(subject_scores.keys(), key=subject_scores.get) if subject_scores else 'general'
        
        # Extract key topics from transcript
        key_topics = self._extract_key_topics(transcript)
        
        # Identify lecture structure
        structure = self._identify_lecture_structure(transcript)
        
        return {
            'is_educational': educational_score >= 2,
            'educational_score': educational_score,
            'primary_subject': primary_subject,
            'subject_confidence': subject_scores.get(primary_subject, 0),
            'key_topics': key_topics,
            'lecture_structure': structure,
            'estimated_difficulty': self._estimate_difficulty(full_text),
            'content_quality': self._assess_content_quality(video_info, transcript)
        }
    
    def _extract_key_topics(self, transcript: List[TranscriptSegment]) -> List[str]:
        """Extract key topics from transcript using simple keyword extraction"""
        if not transcript:
            return []
        
        # Combine all transcript text
        full_text = " ".join([seg.text for seg in transcript])
        
        # Simple topic extraction (in production, use more sophisticated NLP)
        # Look for repeated important terms
        words = re.findall(r'\b[A-Za-z]{4,}\b', full_text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Filter out common words and get top topics
        common_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'}
        
        filtered_topics = {word: freq for word, freq in word_freq.items() 
                          if word not in common_words and freq >= 3}
        
        # Return top 10 topics
        top_topics = sorted(filtered_topics.keys(), key=filtered_topics.get, reverse=True)
        return top_topics[:10]
    
    def _identify_lecture_structure(self, transcript: List[TranscriptSegment]) -> Dict[str, Any]:
        """Identify the structure of the lecture"""
        if not transcript:
            return {'has_structure': False}
        
        # Look for structural indicators
        structure_indicators = {
            'introduction': ['introduction', 'intro', 'begin', 'start', 'today we'],
            'main_points': ['first', 'second', 'third', 'next', 'then', 'now'],
            'examples': ['example', 'for instance', 'such as', 'like'],
            'conclusion': ['conclusion', 'summary', 'to summarize', 'in conclusion', 'finally']
        }
        
        full_text = " ".join([seg.text for seg in transcript]).lower()
        
        structure_found = {}
        for section, indicators in structure_indicators.items():
            count = sum(1 for indicator in indicators if indicator in full_text)
            structure_found[section] = count > 0
        
        # Identify potential chapter breaks (long pauses or topic shifts)
        chapters = []
        current_chapter_start = 0
        
        for i, segment in enumerate(transcript):
            # Simple heuristic: if there's a gap > 3 seconds, it might be a chapter break
            if i > 0 and segment.start_time - transcript[i-1].end_time > 3:
                chapters.append({
                    'start_time': current_chapter_start,
                    'end_time': transcript[i-1].end_time,
                    'title': f"Chapter {len(chapters) + 1}"
                })
                current_chapter_start = segment.start_time
        
        # Add final chapter
        if transcript:
            chapters.append({
                'start_time': current_chapter_start,
                'end_time': transcript[-1].end_time,
                'title': f"Chapter {len(chapters) + 1}"
            })
        
        return {
            'has_structure': any(structure_found.values()),
            'sections_found': structure_found,
            'estimated_chapters': len(chapters),
            'chapters': chapters[:5]  # Limit to first 5 chapters
        }
    
    def _estimate_difficulty(self, text: str) -> str:
        """Estimate content difficulty based on language complexity"""
        # Simple heuristics for difficulty estimation
        difficulty_indicators = {
            'beginner': ['basic', 'introduction', 'simple', 'easy', 'beginner'],
            'intermediate': ['intermediate', 'moderate', 'standard', 'typical'],
            'advanced': ['advanced', 'complex', 'sophisticated', 'expert', 'professional']
        }
        
        scores = {}
        for level, indicators in difficulty_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            scores[level] = score
        
        # Also consider vocabulary complexity
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length > 6 or scores.get('advanced', 0) > 0:
            return 'advanced'
        elif avg_word_length > 4.5 or scores.get('intermediate', 0) > 0:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _assess_content_quality(self, video_info: YouTubeVideoInfo, 
                               transcript: List[TranscriptSegment]) -> Dict[str, Any]:
        """Assess the quality of educational content"""
        quality_score = 0
        quality_factors = []
        
        # Check video metrics
        if video_info.view_count > 10000:
            quality_score += 1
            quality_factors.append("High view count")
        
        if video_info.duration > 300:  # More than 5 minutes
            quality_score += 1
            quality_factors.append("Substantial duration")
        
        # Check transcript quality
        if transcript:
            total_words = sum(len(seg.text.split()) for seg in transcript)
            if total_words > 500:
                quality_score += 1
                quality_factors.append("Comprehensive content")
            
            # Check for clear speech patterns
            avg_segment_length = total_words / len(transcript)
            if 3 <= avg_segment_length <= 15:  # Good pacing
                quality_score += 1
                quality_factors.append("Good pacing")
        
        # Check title quality
        if len(video_info.title.split()) >= 4:
            quality_score += 1
            quality_factors.append("Descriptive title")
        
        quality_rating = "high" if quality_score >= 4 else "medium" if quality_score >= 2 else "low"
        
        return {
            'quality_score': quality_score,
            'quality_rating': quality_rating,
            'quality_factors': quality_factors,
            'max_score': 5
        }

class YouTubeFlashcardGenerator:
    """Generates flashcards specifically from YouTube educational content"""
    
    def __init__(self, ai_processor):
        self.ai_processor = ai_processor
    
    def generate_from_youtube(self, url: str, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Complete pipeline: YouTube URL to flashcards"""
        
        # Initialize processors
        youtube_processor = YouTubeProcessor()
        content_analyzer = YouTubeContentAnalyzer()
        
        # Extract video information
        video_info = youtube_processor.extract_video_info(url)
        if not video_info:
            return {'error': 'Could not extract video information'}
        
        # Get transcript
        transcript = youtube_processor.get_transcript(url)
        if not transcript:
            return {'error': 'Could not extract transcript from video'}
        
        # Analyze content
        content_analysis = content_analyzer.analyze_educational_content(video_info, transcript)
        
        if not content_analysis['is_educational']:
            return {'error': 'Video does not appear to contain educational content'}
        
        # Prepare content for flashcard generation
        lecture_content = self._prepare_lecture_content(video_info, transcript, content_analysis)
        
        # Generate flashcards using AI
        flashcards = self.ai_processor.generate_flashcards(
            content=lecture_content,
            preferences=preferences or {},
            context={
                'source': 'youtube',
                'video_id': video_info.video_id,
                'subject': content_analysis['primary_subject'],
                'difficulty': content_analysis['estimated_difficulty']
            }
        )
        
        return {
            'video_info': video_info,
            'content_analysis': content_analysis,
            'flashcards': flashcards,
            'metadata': {
                'source_url': url,
                'generation_timestamp': datetime.now().isoformat(),
                'transcript_segments': len(transcript)
            }
        }
    
    def _prepare_lecture_content(self, video_info: YouTubeVideoInfo, 
                               transcript: List[TranscriptSegment],
                               analysis: Dict[str, Any]) -> str:
        """Prepare structured content for flashcard generation"""
        
        # Create structured content
        content_parts = []
        
        # Add title and description
        content_parts.append(f"Title: {video_info.title}")
        if video_info.description:
            content_parts.append(f"Description: {video_info.description[:500]}...")
        
        # Add subject and difficulty
        content_parts.append(f"Subject: {analysis['primary_subject']}")
        content_parts.append(f"Difficulty Level: {analysis['estimated_difficulty']}")
        
        # Add key topics
        if analysis['key_topics']:
            content_parts.append(f"Key Topics: {', '.join(analysis['key_topics'][:5])}")
        
        # Add transcript content in chunks
        content_parts.append("\nLecture Content:")
        
        # Group transcript into logical chunks (every 2-3 minutes)
        chunk_duration = 180  # 3 minutes
        current_chunk = []
        current_chunk_start = 0
        
        for segment in transcript:
            if segment.start_time - current_chunk_start > chunk_duration and current_chunk:
                # Add chunk to content
                chunk_text = " ".join([seg.text for seg in current_chunk])
                content_parts.append(f"\nSection {len(content_parts) - 6}: {chunk_text}")
                
                # Start new chunk
                current_chunk = [segment]
                current_chunk_start = segment.start_time
            else:
                current_chunk.append(segment)
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join([seg.text for seg in current_chunk])
            content_parts.append(f"\nSection {len(content_parts) - 6}: {chunk_text}")
        
        return "\n".join(content_parts)