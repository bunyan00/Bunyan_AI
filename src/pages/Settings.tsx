import React from 'react';
import { motion } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  Moon, 
  Sun, 
  Languages, 
  Brain,
  Download,
  Volume2,
  Zap,
  Shield,
  HelpCircle
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';

const Settings: React.FC = () => {
  const { state, dispatch } = useApp();

  const settingSections = [
    {
      title: 'Appearance',
      icon: Moon,
      settings: [
        {
          id: 'darkMode',
          label: 'Dark Mode',
          description: 'Switch between light and dark themes',
          type: 'toggle',
          value: state.darkMode,
          onChange: () => dispatch({ type: 'TOGGLE_DARK_MODE' })
        },
        {
          id: 'language',
          label: 'Language',
          description: 'Choose your preferred language',
          type: 'select',
          value: state.language,
          options: [
            { value: 'en', label: 'English' },
            { value: 'ar', label: 'العربية' }
          ],
          onChange: (value: string) => dispatch({ type: 'SET_LANGUAGE', payload: value as 'en' | 'ar' })
        }
      ]
    },
    {
      title: 'Processing',
      icon: Brain,
      settings: [
        {
          id: 'difficulty',
          label: 'Default Difficulty',
          description: 'Default difficulty level for generated flashcards',
          type: 'select',
          value: state.settings.difficulty,
          options: [
            { value: 'easy', label: 'Easy' },
            { value: 'medium', label: 'Medium' },
            { value: 'hard', label: 'Hard' }
          ],
          onChange: (value: string) => dispatch({ 
            type: 'UPDATE_SETTINGS', 
            payload: { difficulty: value as 'easy' | 'medium' | 'hard' }
          })
        },
        {
          id: 'cardCount',
          label: 'Cards per Session',
          description: 'Number of flashcards to generate per lecture',
          type: 'select',
          value: state.settings.cardCount,
          options: [
            { value: 10, label: '10 Cards' },
            { value: 20, label: '20 Cards' },
            { value: 30, label: '30 Cards' },
            { value: 50, label: '50 Cards' }
          ],
          onChange: (value: number) => dispatch({ 
            type: 'UPDATE_SETTINGS', 
            payload: { cardCount: value }
          })
        },
        {
          id: 'includeAudio',
          label: 'Include Audio Clips',
          description: 'Attach audio segments to flashcards (experimental)',
          type: 'toggle',
          value: state.settings.includeAudio,
          onChange: () => dispatch({ 
            type: 'UPDATE_SETTINGS', 
            payload: { includeAudio: !state.settings.includeAudio }
          })
        }
      ]
    },
    {
      title: 'Export',
      icon: Download,
      settings: [
        {
          id: 'exportFormat',
          label: 'Default Export Format',
          description: 'Preferred format for exporting flashcards',
          type: 'select',
          value: state.settings.exportFormat,
          options: [
            { value: 'csv', label: 'CSV (Anki Import)' },
            { value: 'apkg', label: 'APKG (Anki Deck)' }
          ],
          onChange: (value: string) => dispatch({ 
            type: 'UPDATE_SETTINGS', 
            payload: { exportFormat: value as 'csv' | 'apkg' }
          })
        }
      ]
    }
  ];

  const renderSetting = (setting: any) => {
    switch (setting.type) {
      case 'toggle':
        return (
          <button
            onClick={setting.onChange}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              setting.value 
                ? 'bg-blue-600' 
                : 'bg-slate-200 dark:bg-slate-700'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                setting.value ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        );
      
      case 'select':
        return (
          <select
            value={setting.value}
            onChange={(e) => setting.onChange(
              setting.id === 'cardCount' ? parseInt(e.target.value) : e.target.value
            )}
            className="px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {setting.options.map((option: any) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
          Settings
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-300">
          Customize your Bunyan AI experience
        </p>
      </motion.div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {settingSections.map((section, sectionIndex) => {
          const SectionIcon = section.icon;
          return (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: sectionIndex * 0.1 }}
              className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
            >
              <div className="flex items-center mb-6">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg mr-3">
                  <SectionIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                  {section.title}
                </h2>
              </div>

              <div className="space-y-6">
                {section.settings.map((setting, settingIndex) => (
                  <div key={setting.id} className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-base font-medium text-slate-900 dark:text-white">
                        {setting.label}
                      </h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {setting.description}
                      </p>
                    </div>
                    <div className="ml-4">
                      {renderSetting(setting)}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* About Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-8 text-white"
      >
        <div className="text-center">
          <Zap className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-4">Bunyan AI</h2>
          <p className="text-blue-100 mb-6">
            Transform your lectures into intelligent flashcards with the power of AI. 
            Enhance your learning through automated transcription, summarization, and 
            spaced repetition.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <Shield className="w-8 h-8 mx-auto mb-2 text-blue-200" />
              <h3 className="font-semibold mb-1">Privacy First</h3>
              <p className="text-blue-100 text-sm">
                Your data stays secure and private
              </p>
            </div>
            <div>
              <Brain className="w-8 h-8 mx-auto mb-2 text-blue-200" />
              <h3 className="font-semibold mb-1">AI-Powered</h3>
              <p className="text-blue-100 text-sm">
                Advanced models for accurate processing
              </p>
            </div>
            <div>
              <HelpCircle className="w-8 h-8 mx-auto mb-2 text-blue-200" />
              <h3 className="font-semibold mb-1">Support</h3>
              <p className="text-blue-100 text-sm">
                Get help when you need it
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Version Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="text-center text-sm text-slate-500 dark:text-slate-400"
      >
        <p>Bunyan AI v1.0.0 • Built with React & TypeScript</p>
        <p className="mt-1">© 2024 Bunyan AI. All rights reserved.</p>
      </motion.div>
    </div>
  );
};

export default Settings;