import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// Database types
export interface User {
  id: string
  email: string
  username: string
  display_name: string
  bio?: string
  avatar_url?: string
  language: 'en' | 'ar'
  dark_mode: boolean
  created_at: string
  updated_at: string
  is_verified: boolean
  subscription_tier: 'free' | 'premium' | 'enterprise'
}

export interface Session {
  id: string
  user_id: string
  title: string
  description?: string
  audio_file_url?: string
  transcript?: string
  summary?: string
  status: 'idle' | 'transcribing' | 'summarizing' | 'generating' | 'completed' | 'error'
  progress: number
  source_type: 'upload' | 'youtube' | 'cloud'
  source_url?: string
  language: 'en' | 'ar'
  difficulty: 'easy' | 'medium' | 'hard'
  card_count: number
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface Flashcard {
  id: string
  session_id: string
  user_id: string
  front: string
  back?: string
  type: 'basic' | 'cloze' | 'multiple-choice'
  difficulty: 'easy' | 'medium' | 'hard'
  tags: string[]
  visual_content_id?: string
  audio_segment_url?: string
  created_at: string
  updated_at: string
  last_reviewed?: string
  review_count: number
  success_rate: number
  next_review?: string
}

export interface VisualContent {
  id: string
  session_id: string
  user_id: string
  content_type: 'diagram' | 'table' | 'mindmap' | 'chart'
  title: string
  data: any
  image_base64?: string
  html_content?: string
  metadata: any
  created_at: string
}

export interface SharedDeck {
  id: string
  author_id: string
  title: string
  description?: string
  subject: string
  difficulty: string
  card_count: number
  visibility: 'public' | 'private' | 'unlisted' | 'friends_only'
  tags: string[]
  language: 'en' | 'ar'
  deck_data: any
  download_count: number
  rating_average: number
  rating_count: number
  is_featured: boolean
  created_at: string
  updated_at: string
}

// Auth helpers
export const getCurrentUser = async () => {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

export const signInWithEmail = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  })
  return { data, error }
}

export const signUpWithEmail = async (email: string, password: string, metadata: any = {}) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: metadata
    }
  })
  return { data, error }
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}

// Database helpers
export const createSession = async (sessionData: Partial<Session>) => {
  const { data, error } = await supabase
    .from('sessions')
    .insert(sessionData)
    .select()
    .single()
  
  return { data, error }
}

export const updateSession = async (id: string, updates: Partial<Session>) => {
  const { data, error } = await supabase
    .from('sessions')
    .update(updates)
    .eq('id', id)
    .select()
    .single()
  
  return { data, error }
}

export const getUserSessions = async (userId: string) => {
  const { data, error } = await supabase
    .from('sessions')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
  
  return { data, error }
}

export const createFlashcards = async (flashcards: Partial<Flashcard>[]) => {
  const { data, error } = await supabase
    .from('flashcards')
    .insert(flashcards)
    .select()
  
  return { data, error }
}

export const getSessionFlashcards = async (sessionId: string) => {
  const { data, error } = await supabase
    .from('flashcards')
    .select('*')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: true })
  
  return { data, error }
}

export const createVisualContent = async (visualData: Partial<VisualContent>) => {
  const { data, error } = await supabase
    .from('visual_content')
    .insert(visualData)
    .select()
    .single()
  
  return { data, error }
}

export const getSessionVisualContent = async (sessionId: string) => {
  const { data, error } = await supabase
    .from('visual_content')
    .select('*')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: true })
  
  return { data, error }
}

// Community features
export const getPublicDecks = async (filters: any = {}) => {
  let query = supabase
    .from('shared_decks')
    .select(`
      *,
      users!shared_decks_author_id_fkey(username, display_name)
    `)
    .eq('visibility', 'public')
  
  if (filters.subject) {
    query = query.eq('subject', filters.subject)
  }
  
  if (filters.difficulty) {
    query = query.eq('difficulty', filters.difficulty)
  }
  
  if (filters.language) {
    query = query.eq('language', filters.language)
  }
  
  const { data, error } = await query
    .order('rating_average', { ascending: false })
    .limit(filters.limit || 20)
  
  return { data, error }
}

export const shareDecks = async (deckData: Partial<SharedDeck>) => {
  const { data, error } = await supabase
    .from('shared_decks')
    .insert(deckData)
    .select()
    .single()
  
  return { data, error }
}

export const downloadDeck = async (deckId: string, userId: string) => {
  // Record download
  await supabase
    .from('deck_downloads')
    .insert({ deck_id: deckId, user_id: userId })
  
  // Increment download count
  await supabase
    .from('shared_decks')
    .update({ download_count: supabase.sql`download_count + 1` })
    .eq('id', deckId)
  
  // Get deck data
  const { data, error } = await supabase
    .from('shared_decks')
    .select('deck_data')
    .eq('id', deckId)
    .single()
  
  return { data, error }
}

// Analytics
export const trackEvent = async (eventType: string, eventData: any = {}) => {
  const user = await getCurrentUser()
  if (!user) return
  
  const { error } = await supabase
    .from('analytics_events')
    .insert({
      user_id: user.id,
      event_type: eventType,
      event_data: eventData
    })
  
  return { error }
}

export const getUserAnalytics = async (userId: string, timeRange: string = '30d') => {
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - (timeRange === '7d' ? 7 : 30))
  
  const { data, error } = await supabase
    .from('analytics_events')
    .select('*')
    .eq('user_id', userId)
    .gte('timestamp', startDate.toISOString())
    .order('timestamp', { ascending: false })
  
  return { data, error }
}