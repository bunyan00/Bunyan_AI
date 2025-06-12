import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  History as HistoryIcon, 
  FileAudio, 
  Brain, 
  Clock, 
  Trash2,
  Download,
  Play,
  MoreVertical,
  Search,
  Calendar
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';

const History: React.FC = () => {
  const { state, dispatch } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'title' | 'cards'>('date');

  const filteredSessions = state.sessions
    .filter(session => 
      session.title.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.created).getTime() - new Date(a.created).getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        case 'cards':
          return b.flashcards.length - a.flashcards.length;
        default:
          return 0;
      }
    });

  const handleDeleteSession = (sessionId: string) => {
    if (window.confirm('Are you sure you want to delete this session?')) {
      dispatch({ type: 'DELETE_SESSION', payload: sessionId });
    }
  };

  const handleDownloadSession = (session: any) => {
    const csvContent = [
      'Front,Back,Type,Difficulty,Tags',
      ...session.flashcards.map((card: any) => 
        `"${card.front}","${card.back}","${card.type}","${card.difficulty}","${card.tags.join(';')}"`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${session.title}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case 'error':
        return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      default:
        return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  if (state.sessions.length === 0) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <HistoryIcon className="w-16 h-16 text-slate-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
          No Processing History
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mb-8">
          Your processed lectures will appear here
        </p>
        <a
          href="/upload"
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <FileAudio className="w-5 h-5 mr-2" />
          Upload First Lecture
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Processing History
          </h1>
          <p className="text-slate-600 dark:text-slate-300 mt-1">
            {state.sessions.length} sessions • {state.sessions.reduce((total, session) => total + session.flashcards.length, 0)} total cards
          </p>
        </div>
      </motion.div>

      {/* Filters and Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Search Sessions
            </label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                placeholder="Search by session title..."
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'title' | 'cards')}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="date">Date (Newest First)</option>
              <option value="title">Title (A-Z)</option>
              <option value="cards">Card Count</option>
            </select>
          </div>
        </div>
      </motion.div>

      {/* Sessions Grid */}
      <div className="space-y-4">
        {filteredSessions.map((session, index) => (
          <motion.div
            key={session.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-start space-x-4">
                  <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                    <FileAudio className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white truncate">
                        {session.title}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(session.status)}`}>
                        {session.status}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm text-slate-600 dark:text-slate-400">
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-2" />
                        {formatDate(session.created)}
                      </div>
                      <div className="flex items-center">
                        <Brain className="w-4 h-4 mr-2" />
                        {session.flashcards.length} flashcards
                      </div>
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-2" />
                        ~{Math.round(session.flashcards.length * 0.5)} min study time
                      </div>
                    </div>

                    {session.summary && (
                      <p className="mt-3 text-sm text-slate-600 dark:text-slate-400 line-clamp-2">
                        {session.summary.substring(0, 200)}...
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 ml-4">
                {session.status === 'completed' && (
                  <>
                    <button
                      onClick={() => {
                        dispatch({ type: 'SET_CURRENT_SESSION', payload: session });
                        window.location.href = '/flashcards';
                      }}
                      className="p-2 text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                      title="Study Cards"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDownloadSession(session)}
                      className="p-2 text-slate-600 dark:text-slate-400 hover:text-green-600 dark:hover:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                      title="Download CSV"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </>
                )}
                <button
                  onClick={() => handleDeleteSession(session.id)}
                  className="p-2 text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  title="Delete Session"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Progress Bar for incomplete sessions */}
            {session.status !== 'completed' && session.status !== 'error' && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-600 dark:text-slate-400">
                    Processing...
                  </span>
                  <span className="text-sm text-blue-600 dark:text-blue-400">
                    {session.progress}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${session.progress}%` }}
                  />
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {filteredSessions.length === 0 && searchTerm && (
        <div className="text-center py-12">
          <Search className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No sessions found
          </h3>
          <p className="text-slate-600 dark:text-slate-400">
            Try adjusting your search terms
          </p>
        </div>
      )}
    </div>
  );
};

export default History;