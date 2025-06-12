import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface Flashcard {
  id: string;
  front: string;
  back: string;
  type: 'basic' | 'cloze' | 'multiple-choice';
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
  created: Date;
}

interface ProcessingSession {
  id: string;
  title: string;
  audioFile: File | null;
  transcript: string;
  summary: string;
  flashcards: Flashcard[];
  status: 'idle' | 'transcribing' | 'summarizing' | 'generating' | 'completed' | 'error';
  progress: number;
  created: Date;
}

interface AppState {
  currentSession: ProcessingSession | null;
  sessions: ProcessingSession[];
  darkMode: boolean;
  language: 'en' | 'ar';
  settings: {
    difficulty: 'easy' | 'medium' | 'hard';
    cardCount: number;
    includeAudio: boolean;
    exportFormat: 'csv' | 'apkg';
  };
}

type AppAction = 
  | { type: 'SET_CURRENT_SESSION'; payload: ProcessingSession }
  | { type: 'UPDATE_SESSION_STATUS'; payload: { status: ProcessingSession['status']; progress: number } }
  | { type: 'UPDATE_TRANSCRIPT'; payload: string }
  | { type: 'UPDATE_SUMMARY'; payload: string }
  | { type: 'UPDATE_FLASHCARDS'; payload: Flashcard[] }
  | { type: 'TOGGLE_DARK_MODE' }
  | { type: 'SET_LANGUAGE'; payload: 'en' | 'ar' }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<AppState['settings']> }
  | { type: 'ADD_SESSION'; payload: ProcessingSession }
  | { type: 'DELETE_SESSION'; payload: string };

const initialState: AppState = {
  currentSession: null,
  sessions: [],
  darkMode: false,
  language: 'ar', // Default to Arabic
  settings: {
    difficulty: 'medium',
    cardCount: 20,
    includeAudio: false,
    exportFormat: 'csv'
  }
};

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_CURRENT_SESSION':
      return { ...state, currentSession: action.payload };
    case 'UPDATE_SESSION_STATUS':
      if (!state.currentSession) return state;
      return {
        ...state,
        currentSession: {
          ...state.currentSession,
          status: action.payload.status,
          progress: action.payload.progress
        }
      };
    case 'UPDATE_TRANSCRIPT':
      if (!state.currentSession) return state;
      return {
        ...state,
        currentSession: {
          ...state.currentSession,
          transcript: action.payload
        }
      };
    case 'UPDATE_SUMMARY':
      if (!state.currentSession) return state;
      return {
        ...state,
        currentSession: {
          ...state.currentSession,
          summary: action.payload
        }
      };
    case 'UPDATE_FLASHCARDS':
      if (!state.currentSession) return state;
      return {
        ...state,
        currentSession: {
          ...state.currentSession,
          flashcards: action.payload
        }
      };
    case 'TOGGLE_DARK_MODE':
      return { ...state, darkMode: !state.darkMode };
    case 'SET_LANGUAGE':
      return { ...state, language: action.payload };
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      };
    case 'ADD_SESSION':
      return {
        ...state,
        sessions: [action.payload, ...state.sessions]
      };
    case 'DELETE_SESSION':
      return {
        ...state,
        sessions: state.sessions.filter(s => s.id !== action.payload)
      };
    default:
      return state;
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      <div className={state.darkMode ? 'dark' : ''} dir={state.language === 'ar' ? 'rtl' : 'ltr'}>
        {children}
      </div>
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}