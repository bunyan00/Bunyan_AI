import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  FileAudio, 
  MessageSquare, 
  BookOpen, 
  Brain, 
  CheckCircle,
  Loader2,
  AlertTriangle
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { useTranslation } from '../utils/translations';

const Processing: React.FC = () => {
  const { state, dispatch } = useApp();
  const { t } = useTranslation(state.language);
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { 
      id: 'transcribing', 
      name: t('transcribingAudio'), 
      icon: FileAudio,
      description: t('transcribingDescription')
    },
    { 
      id: 'summarizing', 
      name: t('analyzingContent'), 
      icon: MessageSquare,
      description: t('analyzingDescription')
    },
    { 
      id: 'generating', 
      name: t('generatingCards'), 
      icon: Brain,
      description: t('generatingDescription')
    },
    { 
      id: 'completed', 
      name: t('processingComplete'), 
      icon: CheckCircle,
      description: t('processingCompleteDescription')
    }
  ];

  // Simulate processing stages
  useEffect(() => {
    if (!state.currentSession) {
      navigate('/upload');
      return;
    }

    const simulateProcessing = async () => {
      const stages = ['transcribing', 'summarizing', 'generating', 'completed'];
      
      for (let i = 0; i < stages.length; i++) {
        const stage = stages[i];
        setCurrentStep(i);
        
        dispatch({ 
          type: 'UPDATE_SESSION_STATUS', 
          payload: { 
            status: stage as any, 
            progress: ((i + 1) / stages.length) * 100 
          }
        });

        // Simulate different processing times
        const delay = stage === 'transcribing' ? 3000 : stage === 'generating' ? 4000 : 2000;
        await new Promise(resolve => setTimeout(resolve, delay));

        // Update content based on stage
        if (stage === 'transcribing') {
          dispatch({ 
            type: 'UPDATE_TRANSCRIPT', 
            payload: generateMockTranscript(state.language)
          });
        } else if (stage === 'summarizing') {
          dispatch({ 
            type: 'UPDATE_SUMMARY', 
            payload: generateMockSummary(state.language)
          });
        } else if (stage === 'generating') {
          dispatch({ 
            type: 'UPDATE_FLASHCARDS', 
            payload: generateMockFlashcards(state.language)
          });
        }
      }

      // Navigate to flashcards after completion
      setTimeout(() => {
        navigate('/flashcards');
      }, 1500);
    };

    simulateProcessing();
  }, [state.currentSession, dispatch, navigate, state.language]);

  const generateMockTranscript = (language: 'en' | 'ar') => {
    if (language === 'ar') {
      return `مرحباً بكم في محاضرة اليوم حول أساسيات التعلم الآلي.

التعلم الآلي هو فرع من فروع الذكاء الاصطناعي يركز على الخوارزميات والنماذج الإحصائية التي تستخدمها أنظمة الحاسوب لأداء المهام دون تعليمات صريحة. بدلاً من ذلك، تعتمد على الأنماط والاستنتاج من البيانات.

هناك ثلاثة أنواع رئيسية من التعلم الآلي: التعلم المُشرف عليه، والتعلم غير المُشرف عليه، والتعلم المعزز. يستخدم التعلم المُشرف عليه بيانات التدريب المُصنفة لتعلم دالة تربط بين المدخلات والمخرجات. تشمل الأمثلة الشائعة مشاكل التصنيف والانحدار.

يعمل التعلم غير المُشرف عليه مع البيانات غير المُصنفة لاكتشاف الأنماط أو الهياكل المخفية. يشمل هذا خوارزميات التجميع مثل K-means وتقنيات تقليل الأبعاد مثل تحليل المكونات الرئيسية.

التعلم المعزز يتعلق بتدريب الوكلاء لاتخاذ سلاسل من القرارات من خلال مكافأة الأعمال الجيدة ومعاقبة السيئة. هذا النهج كان ناجحاً بشكل خاص في ألعاب الحاسوب والروبوتات.

مفتاح النجاح في التعلم الآلي هو وجود بيانات عالية الجودة، واختيار الخوارزمية المناسبة لمشكلتك، وتقييم أداء نموذجك بشكل صحيح باستخدام تقنيات مثل التحقق المتقاطع.`;
    }
    
    return `Welcome to today's lecture on Machine Learning Fundamentals. 

Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models that computer systems use to perform tasks without explicit instructions. Instead, they rely on patterns and inference from data.

There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled training data to learn a mapping function from inputs to outputs. Common examples include classification and regression problems.

Unsupervised learning works with unlabeled data to discover hidden patterns or structures. This includes clustering algorithms like K-means and dimensionality reduction techniques like Principal Component Analysis.

Reinforcement learning is about training agents to make sequences of decisions by rewarding good actions and penalizing bad ones. This approach has been particularly successful in game playing and robotics.

The key to successful machine learning is having quality data, choosing the right algorithm for your problem, and properly evaluating your model's performance using techniques like cross-validation.`;
  };

  const generateMockSummary = (language: 'en' | 'ar') => {
    if (language === 'ar') {
      return `## أساسيات التعلم الآلي

### المفاهيم الأساسية:
- **التعريف**: التعلم الآلي هو فرع من الذكاء الاصطناعي يركز على الخوارزميات التي تتعلم من البيانات دون برمجة صريحة
- **المبدأ الأساسي**: الأنظمة تتعلم الأنماط وتستنتج من البيانات بدلاً من اتباع تعليمات مبرمجة مسبقاً

### الأنواع الثلاثة الرئيسية:
1. **التعلم المُشرف عليه**
   - يستخدم بيانات تدريب مُصنفة
   - يربط المدخلات بالمخرجات
   - أمثلة: التصنيف، الانحدار

2. **التعلم غير المُشرف عليه**
   - يعمل مع بيانات غير مُصنفة
   - يكتشف الأنماط المخفية
   - أمثلة: تجميع K-means، تحليل المكونات الرئيسية

3. **التعلم المعزز**
   - يدرب الوكلاء من خلال المكافآت/العقوبات
   - يتخذ قرارات متسلسلة
   - التطبيقات: ذكاء الألعاب، الروبوتات

### عوامل النجاح:
- بيانات عالية الجودة
- اختيار الخوارزمية المناسبة
- تقييم النموذج الصحيح (التحقق المتقاطع)`;
    }
    
    return `## Machine Learning Fundamentals

### Key Concepts:
- **Definition**: ML is a subset of AI focusing on algorithms that learn from data without explicit programming
- **Core Principle**: Systems learn patterns and make inferences from data rather than following pre-programmed instructions

### Three Main Types:
1. **Supervised Learning**
   - Uses labeled training data
   - Maps inputs to outputs
   - Examples: Classification, Regression

2. **Unsupervised Learning**
   - Works with unlabeled data
   - Discovers hidden patterns
   - Examples: K-means clustering, PCA

3. **Reinforcement Learning**
   - Trains agents through rewards/penalties
   - Makes sequential decisions
   - Applications: Game AI, Robotics

### Success Factors:
- Quality data
- Appropriate algorithm selection
- Proper model evaluation (cross-validation)`;
  };

  const generateMockFlashcards = (language: 'en' | 'ar') => {
    if (language === 'ar') {
      return [
        {
          id: '1',
          front: 'ما هو التعلم الآلي؟',
          back: 'فرع من فروع الذكاء الاصطناعي يركز على الخوارزميات والنماذج الإحصائية التي تمكن أنظمة الحاسوب من أداء المهام دون تعليمات صريحة، معتمدة بدلاً من ذلك على الأنماط والاستنتاج من البيانات.',
          type: 'basic' as const,
          difficulty: 'medium' as const,
          tags: ['تعريف', 'ذكاء اصطناعي', 'أساسيات'],
          created: new Date()
        },
        {
          id: '2',
          front: 'ما هي الأنواع الثلاثة الرئيسية للتعلم الآلي؟',
          back: '1. التعلم المُشرف عليه (يستخدم بيانات مُصنفة)\n2. التعلم غير المُشرف عليه (يجد أنماط في بيانات غير مُصنفة)\n3. التعلم المعزز (يتعلم من خلال المكافآت والعقوبات)',
          type: 'basic' as const,
          difficulty: 'medium' as const,
          tags: ['أنواع', 'تصنيف'],
          created: new Date()
        },
        {
          id: '3',
          front: '{{c1::التعلم المُشرف عليه}} يستخدم بيانات التدريب المُصنفة لتعلم دالة تربط بين المدخلات والمخرجات.',
          back: '',
          type: 'cloze' as const,
          difficulty: 'easy' as const,
          tags: ['تعلم مُشرف عليه', 'تعريف'],
          created: new Date()
        },
        {
          id: '4',
          front: 'أي نوع من التعلم الآلي هو الأفضل لاكتشاف الأنماط المخفية في البيانات غير المُصنفة؟',
          back: 'التعلم غير المُشرف عليه - يعمل مع البيانات غير المُصنفة لاكتشاف الأنماط أو الهياكل المخفية، باستخدام تقنيات مثل التجميع وتقليل الأبعاد.',
          type: 'basic' as const,
          difficulty: 'medium' as const,
          tags: ['تعلم غير مُشرف عليه'],
          created: new Date()
        },
        {
          id: '5',
          front: 'ما هي عوامل النجاح الرئيسية لمشاريع التعلم الآلي؟',
          back: '1. بيانات عالية الجودة\n2. اختيار الخوارزمية المناسبة لمشكلتك\n3. تقييم النموذج بشكل صحيح باستخدام تقنيات مثل التحقق المتقاطع',
          type: 'basic' as const,
          difficulty: 'hard' as const,
          tags: ['أفضل الممارسات', 'تقييم'],
          created: new Date()
        }
      ];
    }
    
    return [
      {
        id: '1',
        front: 'What is Machine Learning?',
        back: 'A subset of artificial intelligence that focuses on algorithms and statistical models that enable computer systems to perform tasks without explicit instructions, relying instead on patterns and inference from data.',
        type: 'basic' as const,
        difficulty: 'medium' as const,
        tags: ['definition', 'AI', 'fundamentals'],
        created: new Date()
      },
      {
        id: '2',
        front: 'What are the three main types of machine learning?',
        back: '1. Supervised Learning (uses labeled data)\n2. Unsupervised Learning (finds patterns in unlabeled data)\n3. Reinforcement Learning (learns through rewards and penalties)',
        type: 'basic' as const,
        difficulty: 'medium' as const,
        tags: ['types', 'classification'],
        created: new Date()
      },
      {
        id: '3',
        front: '{{c1::Supervised learning}} uses labeled training data to learn a mapping function from inputs to outputs.',
        back: '',
        type: 'cloze' as const,
        difficulty: 'easy' as const,
        tags: ['supervised learning', 'definition'],
        created: new Date()
      },
      {
        id: '4',
        front: 'Which ML type is best for discovering hidden patterns in unlabeled data?',
        back: 'Unsupervised Learning - it works with unlabeled data to discover hidden patterns or structures, using techniques like clustering and dimensionality reduction.',
        type: 'basic' as const,
        difficulty: 'medium' as const,
        tags: ['unsupervised learning'],
        created: new Date()
      },
      {
        id: '5',
        front: 'What are the key success factors for machine learning projects?',
        back: '1. Quality data\n2. Choosing the right algorithm for your problem\n3. Proper model evaluation using techniques like cross-validation',
        type: 'basic' as const,
        difficulty: 'hard' as const,
        tags: ['best practices', 'evaluation'],
        created: new Date()
      }
    ];
  };

  if (!state.currentSession) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className={`text-center ${state.language === 'ar' ? 'text-right' : ''}`}>
          <AlertTriangle className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <h2 className={`text-xl font-semibold text-slate-900 dark:text-white mb-2 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
            {state.language === 'ar' ? 'لم يتم العثور على جلسة' : 'No Session Found'}
          </h2>
          <p className={`text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
            {state.language === 'ar' ? 'يرجى رفع ملف لبدء المعالجة.' : 'Please upload a file to start processing.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`text-center ${state.language === 'ar' ? 'text-right' : ''}`}
      >
        <h1 className={`text-3xl font-bold text-slate-900 dark:text-white mb-4 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
          {t('processingYourLecture')}
        </h1>
        <p className={`text-lg text-slate-600 dark:text-slate-300 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
          {state.currentSession.title}
        </p>
      </motion.div>

      {/* Progress Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
      >
        <div className={`flex items-center justify-between mb-4 ${state.language === 'ar' ? 'flex-row-reverse' : ''}`}>
          <span className={`text-sm font-medium text-slate-700 dark:text-slate-300 ${state.language === 'ar' ? 'font-arabic' : ''}`}>
            {t('progress')}
          </span>
          <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
            {Math.round(state.currentSession.progress)}%
          </span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${state.currentSession.progress}%` }}
            className={`bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-500 ${state.language === 'ar' ? 'bg-gradient-to-l' : ''}`}
          />
        </div>
      </motion.div>

      {/* Processing Steps */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
      >
        <div className="space-y-6">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            const isUpcoming = index > currentStep;

            return (
              <div
                key={step.id}
                className={`flex items-start p-4 rounded-lg transition-all duration-300 ${
                  state.language === 'ar' ? 'flex-row-reverse text-right' : ''
                } ${
                  isActive
                    ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                    : isCompleted
                    ? 'bg-green-50 dark:bg-green-900/20'
                    : 'bg-slate-50 dark:bg-slate-700'
                }`}
              >
                <div className={`p-2 rounded-lg ${state.language === 'ar' ? 'ml-4' : 'mr-4'} ${
                  isActive
                    ? 'bg-blue-100 dark:bg-blue-900/40'
                    : isCompleted
                    ? 'bg-green-100 dark:bg-green-900/40'
                    : 'bg-slate-200 dark:bg-slate-600'
                }`}>
                  {isActive ? (
                    <Loader2 className={`w-5 h-5 animate-spin ${
                      isActive
                        ? 'text-blue-600 dark:text-blue-400'
                        : 'text-slate-400'
                    }`} />
                  ) : (
                    <Icon className={`w-5 h-5 ${
                      isActive
                        ? 'text-blue-600 dark:text-blue-400'
                        : isCompleted
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-slate-400'
                    }`} />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className={`font-semibold ${state.language === 'ar' ? 'font-arabic' : ''} ${
                    isActive
                      ? 'text-blue-900 dark:text-blue-100'
                      : isCompleted
                      ? 'text-green-900 dark:text-green-100'
                      : 'text-slate-600 dark:text-slate-400'
                  }`}>
                    {step.name}
                  </h3>
                  <p className={`text-sm mt-1 ${state.language === 'ar' ? 'font-arabic' : ''} ${
                    isActive
                      ? 'text-blue-700 dark:text-blue-300'
                      : isCompleted
                      ? 'text-green-700 dark:text-green-300'
                      : 'text-slate-500 dark:text-slate-500'
                  }`}>
                    {step.description}
                  </p>
                </div>
                {isCompleted && (
                  <CheckCircle className={`w-5 h-5 text-green-600 dark:text-green-400 ${state.language === 'ar' ? 'mr-4' : 'ml-4'}`} />
                )}
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Live Preview */}
      {state.currentSession.transcript && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6"
        >
          <h2 className={`text-lg font-semibold text-slate-900 dark:text-white mb-4 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
            {t('livePreview')}
          </h2>
          <div className="space-y-4">
            {state.currentSession.transcript && (
              <div>
                <h3 className={`font-medium text-slate-700 dark:text-slate-300 mb-2 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                  {t('transcriptPreview')}
                </h3>
                <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-4 max-h-32 overflow-y-auto">
                  <p className={`text-sm text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`} dir={state.language === 'ar' ? 'rtl' : 'ltr'}>
                    {state.currentSession.transcript.substring(0, 200)}
                    {state.currentSession.transcript.length > 200 && '...'}
                  </p>
                </div>
              </div>
            )}
            {state.currentSession.flashcards.length > 0 && (
              <div>
                <h3 className={`font-medium text-slate-700 dark:text-slate-300 mb-2 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                  {t('generatedCards')}: {state.currentSession.flashcards.length}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {state.currentSession.flashcards.slice(0, 2).map((card) => (
                    <div key={card.id} className="bg-slate-50 dark:bg-slate-700 rounded-lg p-3">
                      <p className={`text-sm font-medium text-slate-900 dark:text-white mb-1 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`} dir={state.language === 'ar' ? 'rtl' : 'ltr'}>
                        {card.front.substring(0, 50)}
                        {card.front.length > 50 && '...'}
                      </p>
                      <p className={`text-xs text-slate-600 dark:text-slate-400 ${state.language === 'ar' ? 'font-arabic text-right' : ''}`}>
                        {card.type} • {card.difficulty}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Processing;