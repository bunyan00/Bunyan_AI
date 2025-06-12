import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Upload, 
  Brain, 
  History, 
  Zap, 
  Users, 
  TrendingUp,
  Clock,
  FileAudio
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { useTranslation } from '../utils/translations';

const Dashboard: React.FC = () => {
  const { state } = useApp();
  const { t } = useTranslation(state.language);

  const stats = [
    {
      name: t('totalSessions'),
      value: state.sessions.length,
      icon: FileAudio,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/20'
    },
    {
      name: t('flashcardsCreated'),
      value: state.sessions.reduce((acc, session) => acc + session.flashcards.length, 0),
      icon: Brain,
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-100 dark:bg-emerald-900/20'
    },
    {
      name: t('hoursProcessed'),
      value: Math.round(state.sessions.length * 1.5), // Simulated
      icon: Clock,
      color: 'text-orange-600 dark:text-orange-400',
      bg: 'bg-orange-100 dark:bg-orange-900/20'
    },
    {
      name: t('learningEfficiency'),
      value: '94%',
      icon: TrendingUp,
      color: 'text-purple-600 dark:text-purple-400',
      bg: 'bg-purple-100 dark:bg-purple-900/20'
    }
  ];

  const quickActions = [
    {
      name: t('uploadNewLecture'),
      description: t('uploadDescription'),
      href: '/upload',
      icon: Upload,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-50 dark:bg-blue-900/10'
    },
    {
      name: t('reviewFlashcards'),
      description: t('reviewDescription'),
      href: '/flashcards',
      icon: Brain,
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-50 dark:bg-emerald-900/10'
    },
    {
      name: t('viewHistory'),
      description: t('historyDescription'),
      href: '/history',
      icon: History,
      color: 'text-orange-600 dark:text-orange-400',
      bg: 'bg-orange-50 dark:bg-orange-900/10'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`text-4xl font-bold text-slate-900 dark:text-white mb-4 ${state.language === 'ar' ? 'font-arabic' : ''}`}
        >
          {t('welcomeTitle')}
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto ${state.language === 'ar' ? 'font-arabic' : ''}`}
        >
          {t('welcomeSubtitle')}
        </motion.p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700"
            >
              <div className={`flex items-center ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
                <div className={`p-3 rounded-lg ${stat.bg}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className={state.language === 'ar' ? 'mr-4 text-right' : 'ml-4'}>
                  <p className={`text-sm font-medium text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                    {stat.name}
                  </p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          return (
            <motion.div
              key={action.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
            >
              <Link
                to={action.href}
                className={`block p-6 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 ${action.bg} hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-all duration-200 group`}
              >
                <div className={`flex items-center mb-4 ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
                  <div className="p-2 rounded-lg bg-white dark:bg-slate-800 shadow-sm">
                    <Icon className={`w-6 h-6 ${action.color}`} />
                  </div>
                </div>
                <h3 className={`text-lg font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                  {action.name}
                </h3>
                <p className={`text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                  {action.description}
                </p>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {/* Recent Activity */}
      {state.sessions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
        >
          <h2 className={`text-xl font-semibold text-slate-900 dark:text-white mb-4 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
            {t('recentSessions')}
          </h2>
          <div className="space-y-3">
            {state.sessions.slice(0, 3).map((session) => (
              <div key={session.id} className={`flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
                <div className={state.language === 'ar' ? 'text-right' : ''}>
                  <h3 className={`font-medium text-slate-900 dark:text-white ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                    {session.title}
                  </h3>
                  <p className={`text-sm text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                    {session.flashcards.length} {t('cards')} • {new Date(session.created).toLocaleDateString(state.language === 'ar' ? 'ar-SA' : 'en-US')}
                  </p>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${state.language === 'ar' ? 'font-arabic' : ''} ${
                  session.status === 'completed' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                }`}>
                  {session.status === 'completed' ? t('completed') : t('processing')}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Features Showcase */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white"
      >
        <div className={`flex items-center mb-6 ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
          <Zap className="w-8 h-8 mr-3" />
          <h2 className={`text-2xl font-bold ${state.language === 'ar' ? 'font-arabic' : ''}`}>
            {t('aiPoweredLearning')}
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className={`text-center ${state.language === 'ar' ? 'text-right' : ''}`}>
            <div className="bg-white/10 rounded-lg p-4 mb-3">
              <FileAudio className="w-8 h-8 mx-auto" />
            </div>
            <h3 className={`font-semibold mb-2 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('smartTranscription')}
            </h3>
            <p className={`text-blue-100 text-sm ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('transcriptionDescription')}
            </p>
          </div>
          <div className={`text-center ${state.language === 'ar' ? 'text-right' : ''}`}>
            <div className="bg-white/10 rounded-lg p-4 mb-3">
              <Brain className="w-8 h-8 mx-auto" />
            </div>
            <h3 className={`font-semibold mb-2 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('intelligentCards')}
            </h3>
            <p className={`text-blue-100 text-sm ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('cardsDescription')}
            </p>
          </div>
          <div className={`text-center ${state.language === 'ar' ? 'text-right' : ''}`}>
            <div className="bg-white/10 rounded-lg p-4 mb-3">
              <Users className="w-8 h-8 mx-auto" />
            </div>
            <h3 className={`font-semibold mb-2 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('ankiIntegration')}
            </h3>
            <p className={`text-blue-100 text-sm ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('integrationDescription')}
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;