"""
Community Sharing Platform
Enables users to share, discover, and collaborate on flashcard decks
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

class DeckVisibility(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"
    FRIENDS_ONLY = "friends_only"

class ContentRating(Enum):
    EXCELLENT = 5
    GOOD = 4
    AVERAGE = 3
    POOR = 2
    VERY_POOR = 1

@dataclass
class SharedDeck:
    deck_id: str
    title: str
    description: str
    author_id: str
    author_name: str
    subject: str
    difficulty: str
    card_count: int
    visibility: DeckVisibility
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    download_count: int
    rating_average: float
    rating_count: int
    is_featured: bool = False
    language: str = "en"

@dataclass
class DeckComment:
    comment_id: str
    deck_id: str
    user_id: str
    username: str
    content: str
    created_at: datetime
    parent_comment_id: Optional[str] = None
    likes: int = 0

@dataclass
class UserProfile:
    user_id: str
    username: str
    email: str
    display_name: str
    bio: str
    avatar_url: Optional[str]
    created_at: datetime
    total_decks: int
    total_downloads: int
    reputation_score: int
    is_verified: bool = False

class CommunityDatabase:
    """Database manager for community features"""
    
    def __init__(self, db_path: str = "community.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize community database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                bio TEXT DEFAULT '',
                avatar_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_decks INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0,
                reputation_score INTEGER DEFAULT 0,
                is_verified BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Shared decks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_decks (
                deck_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                author_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                card_count INTEGER NOT NULL,
                visibility TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                download_count INTEGER DEFAULT 0,
                rating_average REAL DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT FALSE,
                language TEXT DEFAULT 'en',
                deck_data TEXT NOT NULL,
                FOREIGN KEY (author_id) REFERENCES users (user_id)
            )
        ''')
        
        
        # Deck ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deck_ratings (
                rating_id TEXT PRIMARY KEY,
                deck_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                review_text TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES shared_decks (deck_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(deck_id, user_id)
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deck_comments (
                comment_id TEXT PRIMARY KEY,
                deck_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                parent_comment_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                FOREIGN KEY (deck_id) REFERENCES shared_decks (deck_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (parent_comment_id) REFERENCES deck_comments (comment_id)
            )
        ''')
        
        # User follows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_follows (
                follower_id TEXT NOT NULL,
                following_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (follower_id, following_id),
                FOREIGN KEY (follower_id) REFERENCES users (user_id),
                FOREIGN KEY (following_id) REFERENCES users (user_id)
            )
        ''')
        
        # Deck downloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deck_downloads (
                download_id TEXT PRIMARY KEY,
                deck_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES shared_decks (deck_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decks_subject ON shared_decks (subject)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decks_difficulty ON shared_decks (difficulty)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decks_rating ON shared_decks (rating_average)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_decks_downloads ON shared_decks (download_count)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_deck ON deck_comments (deck_id)')
        
        conn.commit()
        conn.close()

class CommunityManager:
    """Main community platform manager"""
    
    def __init__(self, db_path: str = "community.db"):
        self.db = CommunityDatabase(db_path)
    
    def create_user_profile(self, username: str, email: str, display_name: str, 
                          bio: str = "") -> Optional[UserProfile]:
        """Create a new user profile"""
        user_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, email, display_name, bio)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, email, display_name, bio))
            
            conn.commit()
            
            return UserProfile(
                user_id=user_id,
                username=username,
                email=email,
                display_name=display_name,
                bio=bio,
                avatar_url=None,
                created_at=datetime.now(),
                total_decks=0,
                total_downloads=0,
                reputation_score=0
            )
            
        except sqlite3.IntegrityError as e:
            print(f"Error creating user profile: {e}")
            return None
        finally:
            conn.close()
    
    def share_deck(self, author_id: str, title: str, description: str, 
                  flashcards: List[Dict[str, Any]], subject: str, difficulty: str,
                  visibility: DeckVisibility = DeckVisibility.PUBLIC,
                  tags: List[str] = None, language: str = "en") -> Optional[str]:
        """Share a flashcard deck with the community"""
        
        deck_id = str(uuid.uuid4())
        tags = tags or []
        
        # Prepare deck data
        deck_data = {
            'flashcards': flashcards,
            'metadata': {
                'created_with': 'Bunyan AI',
                'version': '1.0',
                'card_count': len(flashcards)
            }
        }
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO shared_decks 
                (deck_id, title, description, author_id, subject, difficulty, 
                 card_count, visibility, tags, language, deck_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deck_id, title, description, author_id, subject, difficulty,
                len(flashcards), visibility.value, json.dumps(tags), 
                language, json.dumps(deck_data)
            ))
            
            # Update user's total decks count
            cursor.execute('''
                UPDATE users SET total_decks = total_decks + 1 WHERE user_id = ?
            ''', (author_id,))
            
            conn.commit()
            return deck_id
            
        except Exception as e:
            print(f"Error sharing deck: {e}")
            return None
        finally:
            conn.close()
    
    def search_decks(self, query: str = "", subject: str = "", difficulty: str = "",
                    language: str = "", tags: List[str] = None, 
                    sort_by: str = "rating", limit: int = 20) -> List[SharedDeck]:
        """Search for shared decks"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Build query
        where_conditions = ["visibility = 'public'"]
        params = []
        
        if query:
            where_conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        if subject:
            where_conditions.append("subject = ?")
            params.append(subject)
        
        if difficulty:
            where_conditions.append("difficulty = ?")
            params.append(difficulty)
        
        if language:
            where_conditions.append("language = ?")
            params.append(language)
        
        if tags:
            for tag in tags:
                where_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
        
        # Sort options
        sort_options = {
            "rating": "rating_average DESC, rating_count DESC",
            "downloads": "download_count DESC",
            "newest": "created_at DESC",
            "title": "title ASC"
        }
        order_by = sort_options.get(sort_by, "rating_average DESC")
        
        query_sql = f'''
            SELECT d.*, u.username as author_name
            FROM shared_decks d
            JOIN users u ON d.author_id = u.user_id
            WHERE {" AND ".join(where_conditions)}
            ORDER BY {order_by}
            LIMIT ?
        '''
        params.append(limit)
        
        try:
            cursor.execute(query_sql, params)
            results = cursor.fetchall()
            
            decks = []
            for row in results:
                deck = SharedDeck(
                    deck_id=row[0],
                    title=row[1],
                    description=row[2] or "",
                    author_id=row[3],
                    author_name=row[-1],  # From JOIN
                    subject=row[4],
                    difficulty=row[5],
                    card_count=row[6],
                    visibility=DeckVisibility(row[7]),
                    tags=json.loads(row[8]),
                    created_at=datetime.fromisoformat(row[9]),
                    updated_at=datetime.fromisoformat(row[10]),
                    download_count=row[11],
                    rating_average=row[12],
                    rating_count=row[13],
                    is_featured=bool(row[14]),
                    language=row[15]
                )
                decks.append(deck)
            
            return decks
            
        except Exception as e:
            print(f"Error searching decks: {e}")
            return []
        finally:
            conn.close()
    
    def download_deck(self, deck_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Download a shared deck"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Get deck data
            cursor.execute('''
                SELECT deck_data, author_id FROM shared_decks WHERE deck_id = ?
            ''', (deck_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            deck_data, author_id = result
            
            # Record download
            download_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO deck_downloads (download_id, deck_id, user_id)
                VALUES (?, ?, ?)
            ''', (download_id, deck_id, user_id))
            
            # Update download count
            cursor.execute('''
                UPDATE shared_decks SET download_count = download_count + 1 
                WHERE deck_id = ?
            ''', (deck_id,))
            
            # Update author's total downloads
            cursor.execute('''
                UPDATE users SET total_downloads = total_downloads + 1 
                WHERE user_id = ?
            ''', (author_id,))
            
            conn.commit()
            
            return json.loads(deck_data)
            
        except Exception as e:
            print(f"Error downloading deck: {e}")
            return None
        finally:
            conn.close()
    
    def rate_deck(self, deck_id: str, user_id: str, rating: int, 
                 review_text: str = "") -> bool:
        """Rate a shared deck"""
        
        if not (1 <= rating <= 5):
            return False
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            rating_id = str(uuid.uuid4())
            
            # Insert or update rating
            cursor.execute('''
                INSERT OR REPLACE INTO deck_ratings 
                (rating_id, deck_id, user_id, rating, review_text)
                VALUES (?, ?, ?, ?, ?)
            ''', (rating_id, deck_id, user_id, rating, review_text))
            
            # Recalculate deck rating average
            cursor.execute('''
                SELECT AVG(rating), COUNT(rating) FROM deck_ratings WHERE deck_id = ?
            ''', (deck_id,))
            
            avg_rating, rating_count = cursor.fetchone()
            
            cursor.execute('''
                UPDATE shared_decks 
                SET rating_average = ?, rating_count = ?
                WHERE deck_id = ?
            ''', (avg_rating, rating_count, deck_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error rating deck: {e}")
            return False
        finally:
            conn.close()
    
    def add_comment(self, deck_id: str, user_id: str, content: str,
                   parent_comment_id: str = None) -> Optional[str]:
        """Add a comment to a deck"""
        
        comment_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO deck_comments 
                (comment_id, deck_id, user_id, content, parent_comment_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (comment_id, deck_id, user_id, content, parent_comment_id))
            
            conn.commit()
            return comment_id
            
        except Exception as e:
            print(f"Error adding comment: {e}")
            return None
        finally:
            conn.close()
    
    def get_deck_comments(self, deck_id: str) -> List[DeckComment]:
        """Get comments for a deck"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT c.*, u.username
                FROM deck_comments c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.deck_id = ?
                ORDER BY c.created_at ASC
            ''', (deck_id,))
            
            comments = []
            for row in cursor.fetchall():
                comment = DeckComment(
                    comment_id=row[0],
                    deck_id=row[1],
                    user_id=row[2],
                    username=row[-1],  # From JOIN
                    content=row[3],
                    created_at=datetime.fromisoformat(row[5]),
                    parent_comment_id=row[4],
                    likes=row[6]
                )
                comments.append(comment)
            
            return comments
            
        except Exception as e:
            print(f"Error getting comments: {e}")
            return []
        finally:
            conn.close()
    
    def fork_deck(self, original_deck_id: str, user_id: str, 
                 new_title: str = None, modifications: Dict[str, Any] = None) -> Optional[str]:
        """Fork (copy and customize) an existing deck"""
        
        # Download original deck
        original_deck = self.download_deck(original_deck_id, user_id)
        if not original_deck:
            return None
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Get original deck info
            cursor.execute('''
                SELECT title, description, subject, difficulty, tags, language
                FROM shared_decks WHERE deck_id = ?
            ''', (original_deck_id,))
            
            original_info = cursor.fetchone()
            if not original_info:
                return None
            
            # Prepare new deck data
            flashcards = original_deck['flashcards'].copy()
            
            # Apply modifications if provided
            if modifications:
                if 'card_modifications' in modifications:
                    for card_id, changes in modifications['card_modifications'].items():
                        for card in flashcards:
                            if card.get('id') == card_id:
                                card.update(changes)
                
                if 'new_cards' in modifications:
                    flashcards.extend(modifications['new_cards'])
                
                if 'removed_cards' in modifications:
                    removed_ids = set(modifications['removed_cards'])
                    flashcards = [card for card in flashcards 
                                if card.get('id') not in removed_ids]
            
            # Create forked deck
            fork_title = new_title or f"Fork of {original_info[0]}"
            
            forked_deck_id = self.share_deck(
                author_id=user_id,
                title=fork_title,
                description=f"Forked from: {original_info[1] or original_info[0]}",
                flashcards=flashcards,
                subject=original_info[2],
                difficulty=original_info[3],
                tags=json.loads(original_info[4]),
                language=original_info[5]
            )
            
            return forked_deck_id
            
        except Exception as e:
            print(f"Error forking deck: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_decks(self, user_id: str, include_private: bool = False) -> List[SharedDeck]:
        """Get all decks created by a user"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            where_clause = "author_id = ?"
            params = [user_id]
            
            if not include_private:
                where_clause += " AND visibility != 'private'"
            
            cursor.execute(f'''
                SELECT d.*, u.username as author_name
                FROM shared_decks d
                JOIN users u ON d.author_id = u.user_id
                WHERE {where_clause}
                ORDER BY d.created_at DESC
            ''', params)
            
            decks = []
            for row in cursor.fetchall():
                deck = SharedDeck(
                    deck_id=row[0],
                    title=row[1],
                    description=row[2] or "",
                    author_id=row[3],
                    author_name=row[-1],
                    subject=row[4],
                    difficulty=row[5],
                    card_count=row[6],
                    visibility=DeckVisibility(row[7]),
                    tags=json.loads(row[8]),
                    created_at=datetime.fromisoformat(row[9]),
                    updated_at=datetime.fromisoformat(row[10]),
                    download_count=row[11],
                    rating_average=row[12],
                    rating_count=row[13],
                    is_featured=bool(row[14]),
                    language=row[15]
                )
                decks.append(deck)
            
            return decks
            
        except Exception as e:
            print(f"Error getting user decks: {e}")
            return []
        finally:
            conn.close()
    
    def get_trending_decks(self, time_period: str = "week", limit: int = 10) -> List[SharedDeck]:
        """Get trending decks based on recent activity"""
        
        # Calculate date threshold
        if time_period == "day":
            threshold = datetime.now() - timedelta(days=1)
        elif time_period == "week":
            threshold = datetime.now() - timedelta(weeks=1)
        elif time_period == "month":
            threshold = datetime.now() - timedelta(days=30)
        else:
            threshold = datetime.now() - timedelta(weeks=1)
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT d.*, u.username as author_name,
                       COUNT(dl.download_id) as recent_downloads
                FROM shared_decks d
                JOIN users u ON d.author_id = u.user_id
                LEFT JOIN deck_downloads dl ON d.deck_id = dl.deck_id 
                    AND dl.downloaded_at > ?
                WHERE d.visibility = 'public'
                GROUP BY d.deck_id
                ORDER BY recent_downloads DESC, d.rating_average DESC
                LIMIT ?
            ''', (threshold.isoformat(), limit))
            
            decks = []
            for row in cursor.fetchall():
                deck = SharedDeck(
                    deck_id=row[0],
                    title=row[1],
                    description=row[2] or "",
                    author_id=row[3],
                    author_name=row[-2],  # Second to last due to recent_downloads
                    subject=row[4],
                    difficulty=row[5],
                    card_count=row[6],
                    visibility=DeckVisibility(row[7]),
                    tags=json.loads(row[8]),
                    created_at=datetime.fromisoformat(row[9]),
                    updated_at=datetime.fromisoformat(row[10]),
                    download_count=row[11],
                    rating_average=row[12],
                    rating_count=row[13],
                    is_featured=bool(row[14]),
                    language=row[15]
                )
                decks.append(deck)
            
            return decks
            
        except Exception as e:
            print(f"Error getting trending decks: {e}")
            return []
        finally:
            conn.close()

class CommunityModerationSystem:
    """Content moderation and quality control system"""
    
    def __init__(self, community_manager: CommunityManager):
        self.community_manager = community_manager
        self.inappropriate_keywords = [
            'spam', 'scam', 'fake', 'inappropriate', 'offensive'
        ]
    
    def moderate_deck_content(self, title: str, description: str, 
                            flashcards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Moderate deck content for quality and appropriateness"""
        
        issues = []
        warnings = []
        
        # Check title and description
        if len(title.strip()) < 3:
            issues.append("Title is too short")
        
        if any(keyword in title.lower() for keyword in self.inappropriate_keywords):
            issues.append("Title contains inappropriate content")
        
        if len(description.strip()) < 10:
            warnings.append("Description is very short - consider adding more details")
        
        # Check flashcards quality
        if len(flashcards) < 5:
            warnings.append("Deck has very few cards - consider adding more content")
        
        empty_cards = sum(1 for card in flashcards 
                         if not card.get('front', '').strip() or not card.get('back', '').strip())
        
        if empty_cards > 0:
            issues.append(f"{empty_cards} cards have empty content")
        
        # Check for duplicate cards
        card_fronts = [card.get('front', '').strip().lower() for card in flashcards]
        duplicates = len(card_fronts) - len(set(card_fronts))
        
        if duplicates > 0:
            warnings.append(f"{duplicates} duplicate cards detected")
        
        # Determine approval status
        if issues:
            status = "rejected"
        elif warnings:
            status = "approved_with_warnings"
        else:
            status = "approved"
        
        return {
            'status': status,
            'issues': issues,
            'warnings': warnings,
            'quality_score': self._calculate_quality_score(title, description, flashcards)
        }
    
    def _calculate_quality_score(self, title: str, description: str, 
                               flashcards: List[Dict[str, Any]]) -> float:
        """Calculate quality score for a deck"""
        score = 0.0
        max_score = 100.0
        
        # Title quality (20 points)
        if len(title.strip()) >= 10:
            score += 20
        elif len(title.strip()) >= 5:
            score += 10
        
        # Description quality (20 points)
        if len(description.strip()) >= 100:
            score += 20
        elif len(description.strip()) >= 50:
            score += 15
        elif len(description.strip()) >= 20:
            score += 10
        
        # Card count (20 points)
        card_count = len(flashcards)
        if card_count >= 20:
            score += 20
        elif card_count >= 10:
            score += 15
        elif card_count >= 5:
            score += 10
        
        # Card content quality (40 points)
        if flashcards:
            total_content_length = 0
            valid_cards = 0
            
            for card in flashcards:
                front = card.get('front', '').strip()
                back = card.get('back', '').strip()
                
                if front and back:
                    valid_cards += 1
                    total_content_length += len(front) + len(back)
            
            # Valid card ratio (20 points)
            valid_ratio = valid_cards / len(flashcards)
            score += valid_ratio * 20
            
            # Average content length (20 points)
            if valid_cards > 0:
                avg_length = total_content_length / valid_cards
                if avg_length >= 100:
                    score += 20
                elif avg_length >= 50:
                    score += 15
                elif avg_length >= 25:
                    score += 10
        
        return min(score, max_score)