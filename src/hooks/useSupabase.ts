import { useEffect, useState } from 'react'
import { supabase, getCurrentUser, type User } from '../lib/supabase'
import { useApp } from '../contexts/AppContext'

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    getCurrentUser().then((user) => {
      setUser(user as User)
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (session?.user) {
          setUser(session.user as User)
        } else {
          setUser(null)
        }
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  return { user, loading }
}

export const useRealtime = (table: string, filter?: any) => {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Initial fetch
    let query = supabase.from(table).select('*')
    
    if (filter) {
      Object.entries(filter).forEach(([key, value]) => {
        query = query.eq(key, value)
      })
    }

    query.then(({ data, error }) => {
      if (!error && data) {
        setData(data)
      }
      setLoading(false)
    })

    // Set up realtime subscription
    const subscription = supabase
      .channel(`${table}_changes`)
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: table,
          filter: filter ? Object.entries(filter).map(([key, value]) => `${key}=eq.${value}`).join(',') : undefined
        }, 
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setData(prev => [...prev, payload.new])
          } else if (payload.eventType === 'UPDATE') {
            setData(prev => prev.map(item => 
              item.id === payload.new.id ? payload.new : item
            ))
          } else if (payload.eventType === 'DELETE') {
            setData(prev => prev.filter(item => item.id !== payload.old.id))
          }
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [table, JSON.stringify(filter)])

  return { data, loading }
}

export const useUserSessions = () => {
  const { user } = useAuth()
  const { data: sessions, loading } = useRealtime('sessions', user ? { user_id: user.id } : null)
  
  return { sessions, loading }
}

export const useSessionFlashcards = (sessionId: string) => {
  const { data: flashcards, loading } = useRealtime('flashcards', { session_id: sessionId })
  
  return { flashcards, loading }
}

export const usePublicDecks = (filters: any = {}) => {
  const [decks, setDecks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDecks = async () => {
      let query = supabase
        .from('shared_decks')
        .select(`
          *,
          users!shared_decks_author_id_fkey(username, display_name)
        `)
        .eq('visibility', 'public')

      if (filters.subject) query = query.eq('subject', filters.subject)
      if (filters.difficulty) query = query.eq('difficulty', filters.difficulty)
      if (filters.language) query = query.eq('language', filters.language)
      if (filters.search) {
        query = query.or(`title.ilike.%${filters.search}%,description.ilike.%${filters.search}%`)
      }

      const { data, error } = await query
        .order('rating_average', { ascending: false })
        .limit(filters.limit || 20)

      if (!error && data) {
        setDecks(data)
      }
      setLoading(false)
    }

    fetchDecks()
  }, [JSON.stringify(filters)])

  return { decks, loading }
}

export const useAnalytics = (timeRange: string = '30d') => {
  const { user } = useAuth()
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return

    const fetchAnalytics = async () => {
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - (timeRange === '7d' ? 7 : 30))

      const { data, error } = await supabase
        .from('analytics_events')
        .select('*')
        .eq('user_id', user.id)
        .gte('timestamp', startDate.toISOString())

      if (!error && data) {
        // Process analytics data
        const processedData = {
          totalEvents: data.length,
          eventsByType: data.reduce((acc, event) => {
            acc[event.event_type] = (acc[event.event_type] || 0) + 1
            return acc
          }, {}),
          dailyActivity: data.reduce((acc, event) => {
            const date = new Date(event.timestamp).toDateString()
            acc[date] = (acc[date] || 0) + 1
            return acc
          }, {}),
          rawData: data
        }
        setAnalytics(processedData)
      }
      setLoading(false)
    }

    fetchAnalytics()
  }, [user, timeRange])

  return { analytics, loading }
}