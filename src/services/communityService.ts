import { supabase, trackEvent, type SharedDeck } from '../lib/supabase'

interface CommunityFilters {
  subject?: string
  difficulty?: string
  language?: string
  search?: string
  tags?: string[]
  sortBy?: 'rating' | 'downloads' | 'newest' | 'title'
  limit?: number
}

interface DeckRating {
  rating: number
  review: string
}

interface DeckComment {
  content: string
  parentId?: string
}

class CommunityService {
  async getPublicDecks(filters: CommunityFilters = {}): Promise<SharedDeck[]> {
    try {
      await trackEvent('community_browse_started', { filters })
      
      let query = supabase
        .from('shared_decks')
        .select(`
          *,
          users!shared_decks_author_id_fkey(username, display_name, avatar_url)
        `)
        .eq('visibility', 'public')
      
      // Apply filters
      if (filters.subject) {
        query = query.eq('subject', filters.subject)
      }
      
      if (filters.difficulty) {
        query = query.eq('difficulty', filters.difficulty)
      }
      
      if (filters.language) {
        query = query.eq('language', filters.language)
      }
      
      if (filters.search) {
        query = query.or(`title.ilike.%${filters.search}%,description.ilike.%${filters.search}%`)
      }
      
      if (filters.tags && filters.tags.length > 0) {
        query = query.contains('tags', filters.tags)
      }
      
      // Apply sorting
      switch (filters.sortBy) {
        case 'downloads':
          query = query.order('download_count', { ascending: false })
          break
        case 'newest':
          query = query.order('created_at', { ascending: false })
          break
        case 'title':
          query = query.order('title', { ascending: true })
          break
        default:
          query = query.order('rating_average', { ascending: false })
      }
      
      const { data, error } = await query.limit(filters.limit || 20)
      
      if (error) throw error
      
      await trackEvent('community_browse_completed', { 
        resultCount: data?.length || 0,
        filters 
      })
      
      return data || []
    } catch (error) {
      await trackEvent('community_browse_failed', { error: error.message })
      return []
    }
  }

  async shareDeck(deckData: {
    title: string
    description: string
    subject: string
    difficulty: string
    visibility: string
    tags: string[]
    language: string
    flashcards: any[]
  }): Promise<string | null> {
    try {
      await trackEvent('deck_share_started', { 
        title: deckData.title,
        cardCount: deckData.flashcards.length 
      })
      
      const { data: user } = await supabase.auth.getUser()
      if (!user.user) throw new Error('User not authenticated')
      
      const { data, error } = await supabase
        .from('shared_decks')
        .insert({
          author_id: user.user.id,
          title: deckData.title,
          description: deckData.description,
          subject: deckData.subject,
          difficulty: deckData.difficulty,
          card_count: deckData.flashcards.length,
          visibility: deckData.visibility,
          tags: deckData.tags,
          language: deckData.language,
          deck_data: {
            flashcards: deckData.flashcards,
            metadata: {
              created_with: 'Bunyan AI',
              version: '1.0',
              shared_at: new Date().toISOString()
            }
          }
        })
        .select()
        .single()
      
      if (error) throw error
      
      await trackEvent('deck_share_completed', { 
        deckId: data.id,
        title: deckData.title 
      })
      
      return data.id
    } catch (error) {
      await trackEvent('deck_share_failed', { error: error.message })
      return null
    }
  }

  async downloadDeck(deckId: string): Promise<any | null> {
    try {
      await trackEvent('deck_download_started', { deckId })
      
      const { data: user } = await supabase.auth.getUser()
      if (!user.user) throw new Error('User not authenticated')
      
      // Record download
      await supabase
        .from('deck_downloads')
        .insert({
          deck_id: deckId,
          user_id: user.user.id
        })
      
      // Increment download count
      await supabase
        .from('shared_decks')
        .update({ 
          download_count: supabase.sql`download_count + 1` 
        })
        .eq('id', deckId)
      
      // Get deck data
      const { data, error } = await supabase
        .from('shared_decks')
        .select('deck_data, title, author_id')
        .eq('id', deckId)
        .single()
      
      if (error) throw error
      
      await trackEvent('deck_download_completed', { 
        deckId,
        title: data.title 
      })
      
      return data.deck_data
    } catch (error) {
      await trackEvent('deck_download_failed', { error: error.message })
      return null
    }
  }

  async rateDeck(deckId: string, rating: DeckRating): Promise<boolean> {
    try {
      await trackEvent('deck_rating_started', { deckId, rating: rating.rating })
      
      const { data: user } = await supabase.auth.getUser()
      if (!user.user) throw new Error('User not authenticated')
      
      // Insert or update rating
      const { error: ratingError } = await supabase
        .from('deck_ratings')
        .upsert({
          deck_id: deckId,
          user_id: user.user.id,
          rating: rating.rating,
          review_text: rating.review
        })
      
      if (ratingError) throw ratingError
      
      // Recalculate average rating
      const { data: ratings, error: ratingsError } = await supabase
        .from('deck_ratings')
        .select('rating')
        .eq('deck_id', deckId)
      
      if (ratingsError) throw ratingsError
      
      const avgRating = ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length
      
      // Update deck with new average
      await supabase
        .from('shared_decks')
        .update({
          rating_average: avgRating,
          rating_count: ratings.length
        })
        .eq('id', deckId)
      
      await trackEvent('deck_rating_completed', { 
        deckId,
        rating: rating.rating,
        newAverage: avgRating 
      })
      
      return true
    } catch (error) {
      await trackEvent('deck_rating_failed', { error: error.message })
      return false
    }
  }

  async addComment(deckId: string, comment: DeckComment): Promise<string | null> {
    try {
      await trackEvent('deck_comment_started', { deckId })
      
      const { data: user } = await supabase.auth.getUser()
      if (!user.user) throw new Error('User not authenticated')
      
      const { data, error } = await supabase
        .from('deck_comments')
        .insert({
          deck_id: deckId,
          user_id: user.user.id,
          content: comment.content,
          parent_comment_id: comment.parentId
        })
        .select()
        .single()
      
      if (error) throw error
      
      await trackEvent('deck_comment_completed', { 
        deckId,
        commentId: data.id 
      })
      
      return data.id
    } catch (error) {
      await trackEvent('deck_comment_failed', { error: error.message })
      return null
    }
  }

  async getDeckComments(deckId: string): Promise<any[]> {
    try {
      const { data, error } = await supabase
        .from('deck_comments')
        .select(`
          *,
          users!deck_comments_user_id_fkey(username, display_name, avatar_url)
        `)
        .eq('deck_id', deckId)
        .order('created_at', { ascending: true })
      
      if (error) throw error
      
      return data || []
    } catch (error) {
      console.error('Error fetching deck comments:', error)
      return []
    }
  }

  async forkDeck(originalDeckId: string, modifications: {
    title?: string
    description?: string
    cardModifications?: any
    newCards?: any[]
    removedCards?: string[]
  }): Promise<string | null> {
    try {
      await trackEvent('deck_fork_started', { originalDeckId })
      
      // Download original deck
      const originalDeck = await this.downloadDeck(originalDeckId)
      if (!originalDeck) throw new Error('Could not download original deck')
      
      // Get original deck info
      const { data: originalInfo, error: infoError } = await supabase
        .from('shared_decks')
        .select('title, description, subject, difficulty, tags, language')
        .eq('id', originalDeckId)
        .single()
      
      if (infoError) throw infoError
      
      // Apply modifications
      let flashcards = [...originalDeck.flashcards]
      
      if (modifications.cardModifications) {
        flashcards = flashcards.map(card => {
          const mod = modifications.cardModifications[card.id]
          return mod ? { ...card, ...mod } : card
        })
      }
      
      if (modifications.newCards) {
        flashcards.push(...modifications.newCards)
      }
      
      if (modifications.removedCards) {
        flashcards = flashcards.filter(card => 
          !modifications.removedCards.includes(card.id)
        )
      }
      
      // Create forked deck
      const forkedDeckId = await this.shareDeck({
        title: modifications.title || `Fork of ${originalInfo.title}`,
        description: modifications.description || `Forked from: ${originalInfo.description}`,
        subject: originalInfo.subject,
        difficulty: originalInfo.difficulty,
        visibility: 'public',
        tags: originalInfo.tags,
        language: originalInfo.language,
        flashcards
      })
      
      await trackEvent('deck_fork_completed', { 
        originalDeckId,
        forkedDeckId,
        cardCount: flashcards.length 
      })
      
      return forkedDeckId
    } catch (error) {
      await trackEvent('deck_fork_failed', { error: error.message })
      return null
    }
  }

  async getUserDecks(userId: string, includePrivate: boolean = false): Promise<SharedDeck[]> {
    try {
      let query = supabase
        .from('shared_decks')
        .select('*')
        .eq('author_id', userId)
      
      if (!includePrivate) {
        query = query.neq('visibility', 'private')
      }
      
      const { data, error } = await query.order('created_at', { ascending: false })
      
      if (error) throw error
      
      return data || []
    } catch (error) {
      console.error('Error fetching user decks:', error)
      return []
    }
  }

  async getTrendingDecks(timeRange: '24h' | '7d' | '30d' = '7d'): Promise<SharedDeck[]> {
    try {
      const now = new Date()
      const startDate = new Date()
      
      switch (timeRange) {
        case '24h':
          startDate.setDate(now.getDate() - 1)
          break
        case '7d':
          startDate.setDate(now.getDate() - 7)
          break
        case '30d':
          startDate.setDate(now.getDate() - 30)
          break
      }
      
      const { data, error } = await supabase
        .from('shared_decks')
        .select(`
          *,
          users!shared_decks_author_id_fkey(username, display_name, avatar_url),
          deck_downloads!inner(downloaded_at)
        `)
        .eq('visibility', 'public')
        .gte('deck_downloads.downloaded_at', startDate.toISOString())
        .order('download_count', { ascending: false })
        .limit(10)
      
      if (error) throw error
      
      return data || []
    } catch (error) {
      console.error('Error fetching trending decks:', error)
      return []
    }
  }

  async followUser(userId: string): Promise<boolean> {
    try {
      const { data: user } = await supabase.auth.getUser()
      if (!user.user) throw new Error('User not authenticated')
      
      const { error } = await supabase
        .from('user_follows')
        .insert({
          follower_id: user.user.id,
          following_id: userId
        })
      
      if (error) throw error
      
      await trackEvent('user_follow', { followedUserId: userId })
      
      return true
    } catch (error) {
      console.error('Error following user:', error)
      return false
    }
  }

  async unfollowUser(userId: string): Promise<boolean> {
    try {
      const { data: user } = await supabase.auth.getUser()
      if (!user.user) throw new Error('User not authenticated')
      
      const { error } = await supabase
        .from('user_follows')
        .delete()
        .eq('follower_id', user.user.id)
        .eq('following_id', userId)
      
      if (error) throw error
      
      await trackEvent('user_unfollow', { unfollowedUserId: userId })
      
      return true
    } catch (error) {
      console.error('Error unfollowing user:', error)
      return false
    }
  }
}

export const communityService = new CommunityService()