import React, { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { 
  Upload as UploadIcon, 
  FileAudio, 
  AlertCircle, 
  CheckCircle,
  Settings,
  Play,
  Pause
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../contexts/AppContext';
import { useTranslation } from '../utils/translations';

const Upload: React.FC = () => {
  const { state, dispatch } = useApp();
  const { t } = useTranslation(state.language);
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [sessionTitle, setSessionTitle] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setSessionTitle(file.name.replace(/\.[^/.]+$/, ''));
      toast.success(state.language === 'ar' ? 'تم رفع الملف الصوتي بنجاح!' : 'Audio file uploaded successfully!');
    }
  }, [state.language]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.aac', '.flac']
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const handleStartProcessing = () => {
    if (!selectedFile || !sessionTitle.trim()) {
      toast.error(state.language === 'ar' ? 'يرجى اختيار ملف وإدخال عنوان الجلسة' : 'Please select a file and enter a session title');
      return;
    }

    const newSession = {
      id: crypto.randomUUID(),
      title: sessionTitle.trim(),
      audioFile: selectedFile,
      transcript: '',
      summary: '',
      flashcards: [],
      status: 'idle' as const,
      progress: 0,
      created: new Date()
    };

    dispatch({ type: 'SET_CURRENT_SESSION', payload: newSession });
    dispatch({ type: 'ADD_SESSION', payload: newSession });
    navigate('/processing');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`text-center ${state.language === 'ar' ? 'text-right' : ''}`}
      >
        <h1 className={`text-3xl font-bold text-slate-900 dark:text-white mb-4 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
          {t('uploadYourLecture')}
        </h1>
        <p className={`text-lg text-slate-600 dark:text-slate-300 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
          {t('uploadSubtitle')}
        </p>
      </motion.div>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-8"
      >
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
            isDragActive
              ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/10'
              : selectedFile
              ? 'border-green-400 bg-green-50 dark:bg-green-900/10'
              : 'border-slate-300 dark:border-slate-600 hover:border-blue-400 hover:bg-slate-50 dark:hover:bg-slate-700'
          }`}
        >
          <input {...getInputProps()} />
          
          {selectedFile ? (
            <div className="space-y-4">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
              <div>
                <h3 className={`text-xl font-semibold text-slate-900 dark:text-white ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                  {t('fileReady')}
                </h3>
                <p className={`text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                  {selectedFile.name}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-500">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
          ) : isDragActive ? (
            <div className="space-y-4">
              <UploadIcon className="w-16 h-16 text-blue-500 mx-auto animate-bounce" />
              <div>
                <h3 className={`text-xl font-semibold text-slate-900 dark:text-white ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                  {t('dropFileHere')}
                </h3>
                <p className={`text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                  {t('releaseToUpload')}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <FileAudio className="w-16 h-16 text-slate-400 mx-auto" />
              <div>
                <h3 className={`text-xl font-semibold text-slate-900 dark:text-white ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                  {t('uploadAudioFile')}
                </h3>
                <p className={`text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                  {t('dragAndDrop')}
                </p>
                <p className={`text-sm text-slate-500 dark:text-slate-500 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
                  {t('supportedFormats')}
                </p>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Session Configuration */}
      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
        >
          <div className={`flex items-center mb-6 ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
            <Settings className={`w-5 h-5 text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'ml-2' : 'mr-2'}`} />
            <h2 className={`text-lg font-semibold text-slate-900 dark:text-white ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('sessionConfiguration')}
            </h2>
          </div>

          <div className="space-y-6">
            {/* Session Title */}
            <div>
              <label className={`block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                {t('sessionTitle')}
              </label>
              <input
                type="text"
                value={sessionTitle}
                onChange={(e) => setSessionTitle(e.target.value)}
                className={`w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent ${state.language === 'ar' ? 'text-right font-arabic' : ''}`}
                placeholder={t('sessionTitlePlaceholder')}
                dir={state.language === 'ar' ? 'rtl' : 'ltr'}
              />
            </div>

            {/* Processing Settings */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className={`block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                  {t('difficultyLevel')}
                </label>
                <select
                  value={state.settings.difficulty}
                  onChange={(e) => dispatch({ 
                    type: 'UPDATE_SETTINGS', 
                    payload: { difficulty: e.target.value as 'easy' | 'medium' | 'hard' }
                  })}
                  className={`w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 ${state.language === 'ar' ? 'text-right font-arabic' : ''}`}
                  dir={state.language === 'ar' ? 'rtl' : 'ltr'}
                >
                  <option value="easy">{t('easy')}</option>
                  <option value="medium">{t('medium')}</option>
                  <option value="hard">{t('hard')}</option>
                </select>
              </div>

              <div>
                <label className={`block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                  {t('numberOfCards')}
                </label>
                <select
                  value={state.settings.cardCount}
                  onChange={(e) => dispatch({ 
                    type: 'UPDATE_SETTINGS', 
                    payload: { cardCount: parseInt(e.target.value) }
                  })}
                  className={`w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 ${state.language === 'ar' ? 'text-right font-arabic' : ''}`}
                  dir={state.language === 'ar' ? 'rtl' : 'ltr'}
                >
                  <option value={10}>10 {t('cards')}</option>
                  <option value={20}>20 {t('cards')}</option>
                  <option value={30}>30 {t('cards')}</option>
                  <option value={50}>50 {t('cards')}</option>
                </select>
              </div>

              <div>
                <label className={`block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                  {t('exportFormat')}
                </label>
                <select
                  value={state.settings.exportFormat}
                  onChange={(e) => dispatch({ 
                    type: 'UPDATE_SETTINGS', 
                    payload: { exportFormat: e.target.value as 'csv' | 'apkg' }
                  })}
                  className={`w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 ${state.language === 'ar' ? 'text-right font-arabic' : ''}`}
                  dir={state.language === 'ar' ? 'rtl' : 'ltr'}
                >
                  <option value="csv">{t('csvAnkiImport')}</option>
                  <option value="apkg">{t('apkgAnkiDeck')}</option>
                </select>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Action Buttons */}
      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className={`flex justify-center space-x-4 ${state.language === 'ar' ? 'space-x-reverse' : ''}`}
        >
          <button
            onClick={() => {
              setSelectedFile(null);
              setSessionTitle('');
            }}
            className={`px-6 py-3 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors ${state.language === 'ar' ? 'font-arabic' : ''}`}
          >
            {t('clearFile')}
          </button>
          <button
            onClick={handleStartProcessing}
            disabled={!sessionTitle.trim()}
            className={`px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center ${state.language === 'ar' ? 'flex-row-reverse font-arabic' : ''}`}
          >
            <Play className={`w-5 h-5 ${state.language === 'ar' ? 'ml-2' : 'mr-2'}`} />
            {t('startProcessing')}
          </button>
        </motion.div>
      )}

      {/* Tips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-xl p-6"
      >
        <div className={`flex items-start ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
          <AlertCircle className={`w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0 ${state.language === 'ar' ? 'ml-3' : 'mr-3'}`} />
          <div className={state.language === 'ar' ? 'text-right' : ''}>
            <h3 className={`font-semibold text-blue-900 dark:text-blue-300 mb-2 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              {t('tipsForBestResults')}
            </h3>
            <ul className={`text-sm text-blue-800 dark:text-blue-300 space-y-1 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
              <li>{t('tip1')}</li>
              <li>{t('tip2')}</li>
              <li>{t('tip3')}</li>
              <li>{t('tip4')}</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Upload;