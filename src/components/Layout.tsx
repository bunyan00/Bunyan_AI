import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Upload, 
  Brain, 
  History, 
  Settings, 
  Moon, 
  Sun,
  Languages,
  BookOpen
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { useTranslation } from '../utils/translations';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { state, dispatch } = useApp();
  const { t } = useTranslation(state.language);
  const location = useLocation();

  const navigation = [
    { name: t('dashboard'), href: '/', icon: Home },
    { name: t('upload'), href: '/upload', icon: Upload },
    { name: t('flashcards'), href: '/flashcards', icon: Brain },
    { name: t('history'), href: '/history', icon: History },
    { name: t('settings'), href: '/settings', icon: Settings },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex h-screen bg-white dark:bg-slate-900">
      {/* Sidebar */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700">
          {/* Logo */}
          <div className={`flex items-center flex-shrink-0 px-4 ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
            <BookOpen className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <span className={`text-xl font-bold text-slate-900 dark:text-white ${state.language === 'ar' ? 'mr-2 font-arabic' : 'ml-2'}`}>
              {state.language === 'ar' ? 'بنيان الذكي' : 'Bunyan AI'}
            </span>
          </div>

          {/* Navigation */}
          <div className="mt-8 flex-grow flex flex-col">
            <nav className="flex-1 px-2 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      state.language === 'ar' ? 'flex-row-reverse text-right' : ''
                    } ${
                      isActive(item.href)
                        ? 'bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
                    }`}
                  >
                    <Icon className={`h-5 w-5 flex-shrink-0 ${state.language === 'ar' ? 'ml-3' : 'mr-3'}`} />
                    <span className={state.language === 'ar' ? 'font-arabic' : ''}>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="bg-white dark:bg-slate-900 shadow border-b border-slate-200 dark:border-slate-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className={`flex items-center md:hidden ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
                <BookOpen className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                <span className={`text-xl font-bold text-slate-900 dark:text-white ${state.language === 'ar' ? 'mr-2 font-arabic' : 'ml-2'}`}>
                  {state.language === 'ar' ? 'بنيان الذكي' : 'Bunyan AI'}
                </span>
              </div>
              
              <div className="flex items-center space-x-4">
                {/* Language Toggle */}
                <button
                  onClick={() => dispatch({ 
                    type: 'SET_LANGUAGE', 
                    payload: state.language === 'en' ? 'ar' : 'en' 
                  })}
                  className="p-2 rounded-md text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  title={state.language === 'ar' ? 'تغيير اللغة' : 'Change Language'}
                >
                  <Languages className="w-5 h-5" />
                </button>

                {/* Dark Mode Toggle */}
                <button
                  onClick={() => dispatch({ type: 'TOGGLE_DARK_MODE' })}
                  className="p-2 rounded-md text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  title={state.language === 'ar' ? 'تبديل الوضع المظلم' : 'Toggle Dark Mode'}
                >
                  {state.darkMode ? (
                    <Sun className="w-5 h-5" />
                  ) : (
                    <Moon className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </div>

      {/* Mobile navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700">
        <div className="flex justify-around py-2">
          {navigation.slice(0, 4).map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex flex-col items-center p-2 text-xs ${
                  isActive(item.href)
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-slate-500 dark:text-slate-400'
                }`}
              >
                <Icon className="w-5 h-5 mb-1" />
                <span className={`${state.language === 'ar' ? 'font-arabic text-xs' : ''}`}>
                  {item.name}
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Layout;