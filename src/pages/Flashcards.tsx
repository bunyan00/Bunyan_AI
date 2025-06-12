import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  RotateCcw, 
  Download, 
  Edit3, 
  Trash2, 
  Plus,
  ChevronLeft,
  ChevronRight,
  Eye,
  EyeOff,
  Filter,
  Search
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../contexts/AppContext';

const Flashcards: React.FC = () => {
  const { state } = useApp();
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [viewMode, setViewMode] = useState<'study' | 'grid'>('study');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');

  const flashcards = state.currentSession?.flashcards || [];

  const filteredCards = flashcards.filter(card => {
    const matchesSearch = card.front.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         card.back.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'all' || card.difficulty === selectedDifficulty;
    const matchesType = selectedType === 'all' || card.type === selectedType;
    
    return matchesSearch && matchesDifficulty && matchesType;
  });

  const currentCard = filteredCards[currentCardIndex];

  const nextCard = () => {
    setIsFlipped(false);
    setCurrentCardIndex((prev) => (prev + 1) % filteredCards.length);
  };

  const prevCard = () => {
    setIsFlipped(false);
    setCurrentCardIndex((prev) => (prev - 1 + filteredCards.length) % filteredCards.length);
  };

  const handleExport = (format: 'csv' | 'apkg') => {
    if (flashcards.length === 0) {
      toast.error('No flashcards to export');
      return;
    }

    if (format === 'csv') {
      const csvContent = [
        'Front,Back,Type,Difficulty,Tags',
        ...flashcards.map(card => 
          `"${card.front}","${card.back}","${card.type}","${card.difficulty}","${card.tags.join(';')}"`
        )
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${state.currentSession?.title || 'flashcards'}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      
      toast.success('CSV file downloaded!');
    } else {
      // APKG export would require more complex implementation
      toast.success('APKG export feature coming soon!');
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case 'medium': return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
      case 'hard': return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      default: return 'text-slate-600 bg-slate-100 dark:text-slate-400 dark:bg-slate-700';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'basic': return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20';
      case 'cloze': return 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/20';
      case 'multiple-choice': return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/20';
      default: return 'text-slate-600 bg-slate-100 dark:text-slate-400 dark:bg-slate-700';
    }
  };

  if (flashcards.length === 0) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <Brain className="w-16 h-16 text-slate-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
          No Flashcards Yet
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mb-8">
          Upload and process a lecture to generate flashcards
        </p>
        <a
          href="/upload"
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          Upload Lecture
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
            Flashcards
          </h1>
          <p className="text-slate-600 dark:text-slate-300 mt-1">
            {state.currentSession?.title} • {flashcards.length} cards
          </p>
        </div>

        <div className="flex items-center space-x-4 mt-4 sm:mt-0">
          {/* View Mode Toggle */}
          <div className="flex bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('study')}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                viewMode === 'study'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              Study
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                viewMode === 'grid'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              Grid
            </button>
          </div>

          {/* Export Buttons */}
          <button
            onClick={() => handleExport('csv')}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </button>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Search
            </label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                placeholder="Search cards..."
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Difficulty
            </label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Difficulties</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Type
            </label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              <option value="basic">Basic</option>
              <option value="cloze">Cloze</option>
              <option value="multiple-choice">Multiple Choice</option>
            </select>
          </div>

          <div className="flex items-end">
            <div className="text-sm text-slate-600 dark:text-slate-400">
              Showing {filteredCards.length} of {flashcards.length} cards
            </div>
          </div>
        </div>
      </motion.div>

      {viewMode === 'study' ? (
        /* Study Mode */
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          {/* Card Display */}
          <div className="relative">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden min-h-80">
              <AnimatePresence mode="wait">
                <motion.div
                  key={`${currentCardIndex}-${isFlipped}`}
                  initial={{ rotateY: 90, opacity: 0 }}
                  animate={{ rotateY: 0, opacity: 1 }}
                  exit={{ rotateY: -90, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  className="p-8 h-full flex flex-col justify-center"
                >
                  {currentCard && (
                    <>
                      <div className="flex justify-between items-start mb-6">
                        <div className="flex space-x-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(currentCard.difficulty)}`}>
                            {currentCard.difficulty}
                          </span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(currentCard.type)}`}>
                            {currentCard.type}
                          </span>
                        </div>
                        <div className="text-sm text-slate-500 dark:text-slate-400">
                          {currentCardIndex + 1} / {filteredCards.length}
                        </div>
                      </div>

                      <div className="flex-1 flex items-center justify-center text-center">
                        {!isFlipped ? (
                          <div>
                            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                              Question
                            </h2>
                            <p className="text-lg text-slate-700 dark:text-slate-300 leading-relaxed">
                              {currentCard.front}
                            </p>
                          </div>
                        ) : (
                          <div>
                            <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                              Answer
                            </h2>
                            <div className="text-lg text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                              {currentCard.back || 'This is a cloze deletion card.'}
                            </div>
                          </div>
                        )}
                      </div>

                      {currentCard.tags.length > 0 && (
                        <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
                          <div className="flex flex-wrap gap-2">
                            {currentCard.tags.map((tag, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Navigation Buttons */}
            <button
              onClick={prevCard}
              disabled={filteredCards.length <= 1}
              className="absolute left-4 top-1/2 transform -translate-y-1/2 p-2 bg-white dark:bg-slate-800 rounded-full shadow-lg border border-slate-200 dark:border-slate-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              <ChevronLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </button>

            <button
              onClick={nextCard}
              disabled={filteredCards.length <= 1}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 p-2 bg-white dark:bg-slate-800 rounded-full shadow-lg border border-slate-200 dark:border-slate-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              <ChevronRight className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            </button>
          </div>

          {/* Study Controls */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setIsFlipped(!isFlipped)}
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {isFlipped ? <EyeOff className="w-5 h-5 mr-2" /> : <Eye className="w-5 h-5 mr-2" />}
              {isFlipped ? 'Show Question' : 'Show Answer'}
            </button>

            <button
              onClick={() => {
                setIsFlipped(false);
                setCurrentCardIndex(0);
              }}
              className="flex items-center px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              <RotateCcw className="w-5 h-5 mr-2" />
              Reset
            </button>
          </div>
        </motion.div>
      ) : (
        /* Grid Mode */
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredCards.map((card, index) => (
            <motion.div
              key={card.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(card.difficulty)}`}>
                    {card.difficulty}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(card.type)}`}>
                    {card.type}
                  </span>
                </div>
                <div className="flex space-x-1">
                  <button className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button className="p-1 text-slate-400 hover:text-red-600 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <h3 className="font-medium text-slate-900 dark:text-white text-sm mb-1">
                    Question
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3">
                    {card.front}
                  </p>
                </div>

                {card.back && (
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-white text-sm mb-1">
                      Answer
                    </h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2">
                      {card.back}
                    </p>
                  </div>
                )}
              </div>

              {card.tags.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex flex-wrap gap-1">
                    {card.tags.slice(0, 3).map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        className="px-2 py-1 text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                    {card.tags.length > 3 && (
                      <span className="px-2 py-1 text-xs text-slate-500 dark:text-slate-500">
                        +{card.tags.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default Flashcards;