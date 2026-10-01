import React, { useState } from 'react';
import { UserRole, Language, AppTheme } from '../../types';
import { 
  Cpu, 
  RefreshCw, 
  BarChart2, 
  Trophy, 
  Target, 
  Sliders, 
  Terminal,
  ShieldAlert,
  CheckCircle2,
  Database,
  Lock,
  ArrowRight
} from 'lucide-react';
import { playHoloClick, playCrystallizeSound } from '../../utils/audioSynth';
import { EDATab } from './AIEngine/EDATab';
import { CrossValidationTab } from './AIEngine/CrossValidationTab';
import { CohortProjectionsTab } from './AIEngine/CohortProjectionsTab';
import { HyperparamsStatsTab } from './AIEngine/HyperparamsStatsTab';
import { TelemetryLogsTab } from './AIEngine/TelemetryLogsTab';
import { t } from '../../utils/i18n';

interface AIEngineViewProps {
  role: UserRole;
  isDatasetLoaded: boolean;
  onNavigateToDatasets: () => void;
  onRetrainTriggered?: () => void;
  loadedDatasetName?: string | null;
  language?: Language;
  theme?: AppTheme;
}

type TabKey = 'eda' | 'cv' | 'cohorts' | 'hyperparams' | 'telemetry';

export const AIEngineView: React.FC<AIEngineViewProps> = ({ 
  role, 
  isDatasetLoaded,
  onNavigateToDatasets,
  onRetrainTriggered,
  loadedDatasetName,
  language = 'es',
  theme = 'dark',
}) => {
  const [activeTab, setActiveTab] = useState<TabKey>('eda');
  const [isRetraining, setIsRetraining] = useState<boolean>(false);
  const [retrainFeedback, setRetrainFeedback] = useState<string | null>(null);

  const isLight = theme === 'light';

  // 1. BLOQUEO ESTRICTO: Si no hay dataset cargado, mostrar pantalla informativa bloqueada
  if (!isDatasetLoaded) {
    return (
      <div className={`w-full h-full pt-20 pb-12 px-4 sm:px-6 overflow-y-auto flex items-center justify-center transition-colors duration-200 ${
        isLight ? 'bg-slate-100 text-slate-800' : 'bg-[#04060a] text-slate-200'
      }`}>
        <div className={`max-w-lg w-full p-8 sm:p-12 rounded-3xl border-2 border-dashed backdrop-blur-xl text-center flex flex-col items-center justify-center space-y-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200 ${
          isLight ? 'border-slate-300 bg-white/90 shadow-slate-300/40' : 'border-slate-800 bg-slate-950/70'
        }`}>
          
          {/* Icono grande de una base de datos con un candado */}
          <div className="relative">
            <div className={`w-24 h-24 rounded-3xl border flex items-center justify-center shadow-inner ${
              isLight ? 'bg-slate-50 border-slate-300 text-slate-500' : 'bg-slate-900/90 border-slate-700/80 text-slate-400'
            }`}>
              <Database className="w-12 h-12 stroke-[1.5]" />
            </div>
            <div className="absolute -bottom-2 -right-2 w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/80 flex items-center justify-center text-amber-500 shadow-lg backdrop-blur-md">
              <Lock className="w-4 h-4" />
            </div>
          </div>

          {/* Texto explicativo */}
          <div className="space-y-2 max-w-md">
            <h2 className={`text-xl sm:text-2xl font-display font-bold ${
              isLight ? 'text-slate-900' : 'text-slate-100'
            }`}>
              {t('aiEngineInactiveTitle', language)}
            </h2>
            <p className={`text-sm font-mono leading-relaxed ${
              isLight ? 'text-slate-600' : 'text-slate-400'
            }`}>
              {t('aiEngineInactiveDesc', language)}
            </p>
            <p className={`text-xs font-mono leading-relaxed ${
              isLight ? 'text-slate-500' : 'text-slate-500'
            }`}>
              {t('aiEngineInactiveDetail', language)}
            </p>
          </div>

          {/* Botón primario que cambie la vista activa hacia la pestaña de Datasets */}
          <button
            onClick={() => {
              playHoloClick(1000);
              onNavigateToDatasets();
            }}
            className={`px-6 py-3 rounded-xl font-mono-hud text-xs font-bold flex items-center gap-2.5 transition-all shadow-xl hover:scale-105 active:scale-95 cursor-pointer ${
              isLight 
                ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20' 
                : 'bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-slate-950 shadow-cyan-500/20 glow-cyan'
            }`}
          >
            <Database className="w-4 h-4" />
            <span>{t('goToDatasets', language)}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  const canRetrain = role === 'ADMIN';

  const handleRetrain = () => {
    if (!canRetrain) {
      playHoloClick(400);
      setRetrainFeedback(t('adminRequiredRetrain', language));
      setTimeout(() => setRetrainFeedback(null), 3500);
      return;
    }

    if (isRetraining) return;

    setIsRetraining(true);
    playHoloClick(1200);
    if (onRetrainTriggered) {
      onRetrainTriggered();
    }

    setTimeout(() => {
      setIsRetraining(false);
      playCrystallizeSound();
      setRetrainFeedback(t('retrainSuccess', language));
      setTimeout(() => setRetrainFeedback(null), 5000);
    }, 2800);
  };

  const tabs = [
    { id: 'eda' as TabKey, label: t('tabEDA', language), icon: BarChart2 },
    { id: 'cv' as TabKey, label: t('tabCV', language), icon: Trophy },
    { id: 'cohorts' as TabKey, label: t('tabCohorts', language), icon: Target },
    { id: 'hyperparams' as TabKey, label: t('tabHyperparams', language), icon: Sliders },
    { id: 'telemetry' as TabKey, label: t('tabTelemetry', language), icon: Terminal },
  ];

  return (
    <div className={`w-full h-full pt-20 pb-12 px-4 sm:px-6 overflow-y-auto transition-colors duration-200 ${
      isLight ? 'bg-slate-100 text-slate-800' : 'bg-[#04060a] text-slate-200'
    }`}>
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Banner informativo de dataset activo */}
        {loadedDatasetName && (
          <div className={`p-3 rounded-xl border flex items-center justify-between text-xs font-mono ${
            isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950/40 border-cyan-500/30 text-cyan-300'
          }`}>
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-cyan-500" />
              <span>{t('activeDatasetInMemory', language)}: <strong className={isLight ? 'text-slate-900' : 'text-white'}>{loadedDatasetName}</strong></span>
            </div>
            <button
              onClick={() => {
                playHoloClick(900);
                onNavigateToDatasets();
              }}
              className={`text-[11px] underline cursor-pointer ${
                isLight ? 'text-slate-600 hover:text-sky-700' : 'text-slate-400 hover:text-cyan-300'
              }`}
            >
              {t('changeDatasetInRepo', language)}
            </button>
          </div>
        )}

        {/* 1. CABECERA DEL MÓDULO (HEADER ESTRICTO) */}
        <header className={`border rounded-2xl p-5 sm:p-6 shadow-xl relative overflow-hidden ${
          isLight ? 'bg-white border-slate-300 text-slate-800 shadow-slate-200/50' : 'bg-slate-900 border-slate-800/90 text-slate-200'
        }`}>
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 relative z-10">
            
            {/* Lado Izquierdo: Icono + Título + Subtítulo */}
            <div className="space-y-1.5 max-w-3xl">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/10">
                  <Cpu className="w-5 h-5 text-cyan-400" />
                </div>
                <h1 className={`text-xl sm:text-2xl font-bold tracking-tight ${
                  isLight ? 'text-slate-900' : 'text-white'
                }`}>
                  {t('aiEngineTitle', language)}
                </h1>
              </div>
              
              <p className={`text-xs sm:text-sm font-mono-hud leading-relaxed ${
                isLight ? 'text-slate-600' : 'text-slate-400'
              }`}>
                {t('aiEngineSubtitle', language)}
              </p>
            </div>

            {/* Lado Derecho: Acciones (Badge Neón + Botón Primario) */}
            <div className="flex flex-wrap items-center gap-3 self-start lg:self-center">
              <div className={`px-3.5 py-1.5 rounded-full border font-mono text-xs font-semibold shadow-sm ${
                isLight 
                  ? 'bg-sky-50 border-sky-300 text-sky-800' 
                  : 'bg-cyan-950/80 border-cyan-400 text-cyan-300 glow-cyan'
              }`}>
                XGBoost + SHAP Explainability
              </div>

              <button
                onClick={handleRetrain}
                disabled={isRetraining}
                title={canRetrain ? 'Reentrenar pesos en GPU' : 'Requiere rol ADMIN'}
                className={`px-4 sm:px-5 py-2.5 rounded-xl font-mono-hud text-xs font-bold flex items-center gap-2 transition-all cursor-pointer shadow-xl ${
                  isRetraining
                    ? 'bg-cyan-400/60 text-slate-950 cursor-wait'
                    : isLight
                      ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20 hover:scale-[1.02] active:scale-[0.98]'
                      : 'bg-cyan-400 hover:bg-cyan-300 text-slate-950 shadow-cyan-400/25 hover:shadow-cyan-400/40 hover:scale-[1.02] active:scale-[0.98]'
                }`}
              >
                <RefreshCw className={`w-4 h-4 ${isLight ? 'text-white' : 'text-slate-950'} ${isRetraining ? 'animate-spin' : ''}`} />
                <span>{isRetraining ? t('retraining', language) : t('retrainModel', language)}</span>
              </button>
            </div>
          </div>

          {/* Feedback banner for retraining */}
          {retrainFeedback && (
            <div className={`mt-4 p-3 rounded-xl border text-xs font-mono flex items-center justify-between animate-in fade-in slide-in-from-top-1 ${
              isLight ? 'bg-sky-50 border-sky-300 text-sky-900' : 'bg-cyan-950/40 border-cyan-500/40 text-cyan-200'
            }`}>
              <div className="flex items-center gap-2">
                {canRetrain ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                ) : (
                  <ShieldAlert className="w-4 h-4 text-amber-500 shrink-0" />
                )}
                <span>{retrainFeedback}</span>
              </div>
              <button
                onClick={() => setRetrainFeedback(null)}
                className={`cursor-pointer ml-2 ${isLight ? 'text-slate-500 hover:text-slate-900' : 'text-slate-400 hover:text-slate-200'}`}
              >
                ✕
              </button>
            </div>
          )}
        </header>

        {/* 2. NAVEGACIÓN POR PESTAÑAS (SUBMÓDULOS) */}
        <nav className={`flex items-center gap-1.5 sm:gap-2 border-b pb-3 overflow-x-auto no-scrollbar ${
          isLight ? 'border-slate-300' : 'border-slate-800/90'
        }`}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  playHoloClick(800);
                  setActiveTab(tab.id);
                }}
                className={`px-3.5 sm:px-4 py-2 rounded-xl text-xs font-mono-hud flex items-center gap-2 whitespace-nowrap transition-all cursor-pointer ${
                  isActive
                    ? isLight
                      ? 'bg-sky-600 text-white font-bold shadow-md'
                      : 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-400 shadow-md shadow-cyan-500/10 glow-cyan'
                    : isLight
                      ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60 border border-transparent'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? (isLight ? 'text-white' : 'text-cyan-400') : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* 3. CONTENIDO DE LAS PESTAÑAS */}
        <main className="min-h-[500px]">
          {activeTab === 'eda' && <EDATab language={language} theme={theme} />}
          {activeTab === 'cv' && <CrossValidationTab language={language} theme={theme} />}
          {activeTab === 'cohorts' && <CohortProjectionsTab language={language} theme={theme} />}
          {activeTab === 'hyperparams' && <HyperparamsStatsTab language={language} theme={theme} />}
          {activeTab === 'telemetry' && <TelemetryLogsTab language={language} theme={theme} />}
        </main>

      </div>
    </div>
  );
};
