/*
  # Main Bunyan AI Database Schema

  1. New Tables
    - `users` - User accounts and profiles
    - `sessions` - Processing sessions for lectures
    - `flashcards` - Generated flashcard content
    - `visual_content` - Generated visual materials
    - `user_preferences` - Personalization settings
    - `analytics_events` - User interaction tracking
    - `cloud_files` - Cloud storage file references

  2. Security
    - Enable RLS on all tables
    - Add policies for user data access
    - Secure API key storage

  3. Indexes
    - Performance optimization for queries
    - Full-text search capabilities
*/

-- Users table for authentication and profiles
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  username text UNIQUE NOT NULL,
  display_name text NOT NULL,
  bio text DEFAULT '',
  avatar_url text,
  language text DEFAULT 'ar',
  dark_mode boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  is_verified boolean DEFAULT false,
  subscription_tier text DEFAULT 'free'
);

-- Processing sessions table
CREATE TABLE IF NOT EXISTS sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  title text NOT NULL,
  description text,
  audio_file_url text,
  transcript text,
  summary text,
  status text DEFAULT 'idle',
  progress integer DEFAULT 0,
  source_type text DEFAULT 'upload', -- 'upload', 'youtube', 'cloud'
  source_url text,
  language text DEFAULT 'ar',
  difficulty text DEFAULT 'medium',
  card_count integer DEFAULT 20,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  completed_at timestamptz
);

-- Flashcards table
CREATE TABLE IF NOT EXISTS flashcards (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES sessions(id) ON DELETE CASCADE,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  front text NOT NULL,
  back text,
  type text DEFAULT 'basic', -- 'basic', 'cloze', 'multiple-choice'
  difficulty text DEFAULT 'medium',
  tags text[] DEFAULT '{}',
  visual_content_id uuid,
  audio_segment_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  last_reviewed timestamptz,
  review_count integer DEFAULT 0,
  success_rate real DEFAULT 0.0,
  next_review timestamptz
);

-- Visual content table
CREATE TABLE IF NOT EXISTS visual_content (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid REFERENCES sessions(id) ON DELETE CASCADE,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  content_type text NOT NULL, -- 'diagram', 'table', 'mindmap', 'chart'
  title text NOT NULL,
  data jsonb NOT NULL,
  image_base64 text,
  html_content text,
  metadata jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  preferred_modes text[] DEFAULT '{"basic_educational"}',
  preferred_styles text[] DEFAULT '{"definition_based"}',
  difficulty_preference text DEFAULT 'medium',
  study_time_preference integer DEFAULT 30,
  learning_goals text[] DEFAULT '{}',
  weak_areas text[] DEFAULT '{}',
  strong_areas text[] DEFAULT '{}',
  performance_history jsonb DEFAULT '[]',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Analytics events table
CREATE TABLE IF NOT EXISTS analytics_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  session_id uuid REFERENCES sessions(id) ON DELETE SET NULL,
  event_type text NOT NULL,
  event_data jsonb DEFAULT '{}',
  timestamp timestamptz DEFAULT now(),
  ip_address inet,
  user_agent text
);

-- Cloud files table
CREATE TABLE IF NOT EXISTS cloud_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  provider text NOT NULL, -- 'google_drive', 'onedrive'
  file_id text NOT NULL,
  file_name text NOT NULL,
  file_size bigint,
  mime_type text,
  download_url text,
  parent_folder text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(provider, file_id, user_id)
);

-- Community shared decks table
CREATE TABLE IF NOT EXISTS shared_decks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id uuid REFERENCES users(id) ON DELETE CASCADE,
  title text NOT NULL,
  description text,
  subject text NOT NULL,
  difficulty text NOT NULL,
  card_count integer NOT NULL,
  visibility text DEFAULT 'public',
  tags text[] DEFAULT '{}',
  language text DEFAULT 'ar',
  deck_data jsonb NOT NULL,
  download_count integer DEFAULT 0,
  rating_average real DEFAULT 0.0,
  rating_count integer DEFAULT 0,
  is_featured boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Deck ratings table
CREATE TABLE IF NOT EXISTS deck_ratings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  deck_id uuid REFERENCES shared_decks(id) ON DELETE CASCADE,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  rating integer NOT NULL CHECK (rating >= 1 AND rating <= 5),
  review_text text,
  created_at timestamptz DEFAULT now(),
  UNIQUE(deck_id, user_id)
);

-- Deck comments table
CREATE TABLE IF NOT EXISTS deck_comments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  deck_id uuid REFERENCES shared_decks(id) ON DELETE CASCADE,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  content text NOT NULL,
  parent_comment_id uuid REFERENCES deck_comments(id) ON DELETE CASCADE,
  likes integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Deck downloads table
CREATE TABLE IF NOT EXISTS deck_downloads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  deck_id uuid REFERENCES shared_decks(id) ON DELETE CASCADE,
  user_id uuid REFERENCES users(id) ON DELETE CASCADE,
  downloaded_at timestamptz DEFAULT now()
);

-- User follows table
CREATE TABLE IF NOT EXISTS user_follows (
  follower_id uuid REFERENCES users(id) ON DELETE CASCADE,
  following_id uuid REFERENCES users(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (follower_id, following_id)
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE visual_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_decks ENABLE ROW LEVEL SECURITY;
ALTER TABLE deck_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE deck_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE deck_downloads ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_follows ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users
CREATE POLICY "Users can read own profile"
  ON users
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON users
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = id);

-- RLS Policies for sessions
CREATE POLICY "Users can read own sessions"
  ON sessions
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own sessions"
  ON sessions
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions"
  ON sessions
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for flashcards
CREATE POLICY "Users can read own flashcards"
  ON flashcards
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own flashcards"
  ON flashcards
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own flashcards"
  ON flashcards
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for visual content
CREATE POLICY "Users can read own visual content"
  ON visual_content
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own visual content"
  ON visual_content
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for shared decks (public read access)
CREATE POLICY "Anyone can read public shared decks"
  ON shared_decks
  FOR SELECT
  TO authenticated
  USING (visibility = 'public' OR auth.uid() = author_id);

CREATE POLICY "Users can create shared decks"
  ON shared_decks
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = author_id);

CREATE POLICY "Authors can update own shared decks"
  ON shared_decks
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = author_id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_flashcards_session_id ON flashcards(session_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_user_id ON flashcards(user_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_next_review ON flashcards(next_review);
CREATE INDEX IF NOT EXISTS idx_visual_content_session_id ON visual_content(session_id);
CREATE INDEX IF NOT EXISTS idx_shared_decks_subject ON shared_decks(subject);
CREATE INDEX IF NOT EXISTS idx_shared_decks_difficulty ON shared_decks(difficulty);
CREATE INDEX IF NOT EXISTS idx_shared_decks_rating ON shared_decks(rating_average);
CREATE INDEX IF NOT EXISTS idx_shared_decks_downloads ON shared_decks(download_count);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_timestamp ON analytics_events(timestamp);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_sessions_title_search ON sessions USING gin(to_tsvector('arabic', title));
CREATE INDEX IF NOT EXISTS idx_flashcards_content_search ON flashcards USING gin(to_tsvector('arabic', front || ' ' || COALESCE(back, '')));
CREATE INDEX IF NOT EXISTS idx_shared_decks_search ON shared_decks USING gin(to_tsvector('arabic', title || ' ' || COALESCE(description, '')));