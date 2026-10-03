import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { 
  CV_PRESET_RESULTS, 
  CVMockResult 
} from '../../../data/aiEngineMockData';
import { 
  Trophy, 
  Play, 
  RefreshCw, 
  GitBranch, 
  ShieldCheck, 
  CheckCircle2, 
  Sliders, 
  Activity, 
  Cpu, 
  Zap,
  Info,
  RotateCcw,
  Sparkles,
  Check
} from 'lucide-react';
import { playHoloClick, playCrystallizeSound } from '../../../utils/audioSynth';
import { runCrossValidationApi, fetchActiveMLModelApi, deployMLModelApi } from '../../../services/api';
import { Language, AppTheme } from '../../../types';
import { t } from '../../../utils/i18n';
import { ExplainabilityCard } from '../../Common/ExplainabilityCard';

interface CrossValidationTabProps {
  language?: Language;
  theme?: AppTheme;
}

export const CrossValidationTab: React.FC<CrossValidationTabProps> = ({
  language = 'es',
  theme = 'dark',
}) => {
  const [selectedAlgoKey, setSelectedAlgoKey] = useState<string>('xgboost');
  const [nFolds, setNFolds] = useState<number>(5);
  const [strategy, setStrategy] = useState<string>('K-Fold Estratificado');
  const [hasRunCV, setHasRunCV] = useState<boolean>(true);
  const [isGeneratingCV, setIsGeneratingCV] = useState<boolean>(false);
  const [currentResult, setCurrentResult] = useState<CVMockResult>(CV_PRESET_RESULTS.xgboost);
  const [activeDeployedModel, setActiveDeployedModel] = useState<any | null>(null);
  const [isDeploying, setIsDeploying] = useState<boolean>(false);
  const [deployFeedback, setDeployFeedback] = useState<string | null>(null);

  const isLight = theme === 'light';

  // Live Synchronize Champion Model from Streamlit / FastAPI Backend
  useEffect(() => {
    let isMounted = true;
    const syncActiveModel = async () => {
      const active = await fetchActiveMLModelApi();
      if (active && isMounted) {
        setActiveDeployedModel(active);
      }
    };
    syncActiveModel();
    const interval = setInterval(syncActiveModel, 3500);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleDeployCurrentAlgo = async () => {
    setIsDeploying(true);
    playHoloClick(1100);
    try {
      const res = await deployMLModelApi(selectedAlgoKey, 'Front Principal 3D');
      if (res) {
        setActiveDeployedModel(res);
        playCrystallizeSound();
        setDeployFeedback(
          language === 'en'
            ? `Champion Model updated to "${res.name}". Synchronized across Streamlit and 3D Twin.`
            : `Modelo Campeón actualizado a "${res.name}". Sincronizado en Streamlit y Gemelo 3D.`
        );
      }
    } catch (e) {
      // ignore
    } finally {
      setIsDeploying(false);
      setTimeout(() => setDeployFeedback(null), 6000);
    }
  };

  const handleRunCV = async () => {
    setIsGeneratingCV(true);
    playHoloClick(950);
    try {
      const res = await runCrossValidationApi(nFolds, selectedAlgoKey);
      setCurrentResult({
        ...res,
        kFolds: nFolds,
        strategy,
      });
      setHasRunCV(true);
      playCrystallizeSound();
    } catch (e) {
      setHasRunCV(true);
    } finally {
      setIsGeneratingCV(false);
    }
  };

  const handleResetCV = () => {
    playHoloClick(700);
    setHasRunCV(false);
  };

  const algos = [
    { key: 'xgboost', name: 'XGBoost v3.4 (SOTA)', badge: 'Recomendado' },
    { key: 'lightgbm', name: 'LightGBM v4.1', badge: 'Baja Latencia' },
    { key: 'random_forest', name: 'Random Forest 500T', badge: 'Alta Robustez' },
    { key: 'neural_net', name: 'MLP Deep Neural Net', badge: 'No Lineal' },
  ];

  const summary = currentResult?.summary || {
    meanF1: 91.2,
    stdF1: 0.44,
    meanRocAuc: 94.8,
    stdRocAuc: 0.25,
  };
  const meanRocAuc = summary.meanRocAuc ?? 94.8;
  const stdRocAuc = summary.stdRocAuc ?? 0.25;
  const meanF1 = summary.meanF1 ?? 91.2;
  const accTest = currentResult?.metricsTrainVsTest?.find((m: any) => m.metric === 'Accuracy')?.Test ?? 92.6;
  const logLossVal = 0.108;

  const cm = currentResult?.confusionMatrix || {
    tp: 48250,
    fp: 4680,
    fn: 3950,
    tn: 48520,
    tpPct: 92.4,
    fpPct: 8.8,
    fnPct: 7.6,
    tnPct: 91.2,
  };
  const totalCM = ((cm.tp ?? 0) + (cm.tn ?? 0) + (cm.fp ?? 0) + (cm.fn ?? 0)) || 1;
  const cmAccuracy = ((((cm.tp ?? 0) + (cm.tn ?? 0)) / totalCM) * 100).toFixed(1);

  const rocCurveData = (currentResult as any)?.rocCurve || [
    { fpr: 0.00, tpr: 0.00, random: 0.00 },
    { fpr: 0.02, tpr: 0.48, random: 0.02 },
    { fpr: 0.05, tpr: 0.72, random: 0.05 },
    { fpr: 0.10, tpr: 0.86, random: 0.10 },
    { fpr: 0.18, tpr: 0.93, random: 0.18 },
    { fpr: 0.30, tpr: 0.96, random: 0.30 },
    { fpr: 0.50, tpr: 0.98, random: 0.50 },
    { fpr: 1.00, tpr: 1.00, random: 1.00 },
  ];

  const featureImportance = (currentResult as any)?.featureImportance || [
    { feature: 'Aporte a Seguridad Social', importance: 28.5 },
    { feature: 'Ingreso Neto Diario (USD)', importance: 22.1 },
    { feature: 'Nivel Educativo (Años)', importance: 18.4 },
    { feature: 'Tamaño de la Empresa', importance: 14.2 },
    { feature: 'Uso de Medios Digitales (QR)', importance: 10.8 },
    { feature: 'Sector de Actividad', importance: 6.0 },
  ];

  const modelLabel = currentResult?.algorithm || 'XGBoost SOTA';

  return (
    <div className="space-y-6 animate-in fade-in duration-300">

      {/* 0. BANNER DEL MODELO CAMPEÓN ACTIVO SINCRONIZADO */}
      <div className={`p-4 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-lg ${
        isLight 
          ? 'bg-gradient-to-r from-emerald-50 via-teal-50 to-sky-50 border-emerald-300 text-slate-800' 
          : 'bg-gradient-to-r from-emerald-950/50 via-slate-900 to-cyan-950/40 border-emerald-500/40 text-slate-100'
      }`}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-400 flex items-center justify-center text-emerald-400 shrink-0">
            <Trophy className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                {language === 'en' ? 'Live Champion in Production' : 'Modelo Campeón en Producción'}
              </span>
              <span className="text-xs font-mono text-slate-400">
                {activeDeployedModel?.deployedBy ? `• ${activeDeployedModel.deployedBy}` : '• Sincronizado con Streamlit'}
              </span>
            </div>
            <h3 className="text-sm md:text-base font-display font-bold text-emerald-400 mt-0.5">
              {activeDeployedModel?.name || 'XGBoost Gradient Boosted Trees v3.4'}
            </h3>
            <p className="text-[11px] font-mono text-slate-400">
              {language === 'en' 
                ? 'Governing 3D Agent formalization transitions, Monte Carlo shocks & policy response dynamics.'
                : 'Gobierna las probabilidades de formalización en el Gemelo 3D, choques Monte Carlo y dinámicas de política.'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-stretch md:self-auto justify-end">
          <button
            onClick={handleDeployCurrentAlgo}
            disabled={isDeploying}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold flex items-center gap-2 transition-all cursor-pointer shadow-md ${
              isLight
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20'
                : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-emerald-500/20'
            }`}
          >
            {isDeploying ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>
              {language === 'en' ? 'Deploy Inspected Model' : 'Desplegar Modelo Inspeccionado'}
            </span>
          </button>
        </div>
      </div>

      {deployFeedback && (
        <div className="p-3 rounded-xl bg-emerald-500/20 border border-emerald-500 text-emerald-300 text-xs font-mono flex items-center gap-2 animate-in fade-in">
          <Check className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{deployFeedback}</span>
        </div>
      )}

      {/* 1. TOP CONTROL BAR / CONFIGURACIÓN DE CORRIDA */}
      <div className={`hud-glass p-5 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
        isLight ? 'border-slate-300 shadow-sm' : 'border-cyan-500/25'
      }`}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono-hud text-cyan-600 dark:text-cyan-400 font-bold uppercase tracking-wider">
              {t('cvTitle', language)}
            </span>
            <span className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
              isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950 border-cyan-500/30 text-cyan-300'
            }`}>
              {language === 'en' ? 'Benchmarking Suite' : 'Matriz Comparativa'}
            </span>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-amber-500/20 border border-amber-400 text-amber-500 font-bold">
              Demostración
            </span>
          </div>
          <p className={`text-xs ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
            {t('cvSubtitle', language)}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Selector de Algoritmo */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className={isLight ? 'text-slate-600' : 'text-slate-400'}>{t('modelSelected', language)}:</span>
            <select
              value={selectedAlgoKey}
              onChange={(e) => {
                setSelectedAlgoKey(e.target.value);
                setCurrentResult(CV_PRESET_RESULTS[e.target.value] || CV_PRESET_RESULTS.xgboost);
              }}
              className={`px-3 py-1.5 rounded-xl border text-xs font-mono cursor-pointer outline-none ${
                isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900 border-slate-700 text-cyan-300'
              }`}
            >
              {algos.map((a) => (
                <option key={a.key} value={a.key}>
                  {a.name} ({a.badge})
                </option>
              ))}
            </select>
          </div>

          {/* Selector de Folds */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className={isLight ? 'text-slate-600' : 'text-slate-400'}>{t('foldsCount', language)}:</span>
            <select
              value={nFolds}
              onChange={(e) => setNFolds(Number(e.target.value))}
              className={`px-3 py-1.5 rounded-xl border text-xs font-mono cursor-pointer outline-none ${
                isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900 border-slate-700 text-cyan-300'
              }`}
            >
              <option value={3}>3 Folds</option>
              <option value={5}>5 Folds (Standard)</option>
              <option value={10}>10 Folds (Full)</option>
            </select>
          </div>

          {/* Botón Ejecutar */}
          <button
            onClick={handleRunCV}
            disabled={isGeneratingCV}
            className={`px-5 py-2.5 rounded-xl font-mono-hud text-xs font-bold flex items-center gap-2 transition-all cursor-pointer shadow-lg ${
              isGeneratingCV
                ? 'bg-cyan-500/50 text-slate-950 cursor-not-allowed opacity-90'
                : isLight
                  ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20'
                  : 'bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-slate-950 shadow-cyan-500/20 glow-cyan'
            }`}
          >
            {isGeneratingCV ? (
              <>
                <RefreshCw className={`w-4 h-4 animate-spin ${isLight ? 'text-white' : 'text-slate-950'}`} />
                <span>{language === 'en' ? 'Validating...' : 'Validando...'}</span>
              </>
            ) : (
              <>
                <Play className={`w-4 h-4 fill-current ${isLight ? 'text-white' : 'text-slate-950'}`} />
                <span>{t('runCV', language)}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* 2. ESTADO INICIAL (VISTA VACÍA) */}
      {!hasRunCV && !isGeneratingCV && (
        <div className={`p-16 rounded-2xl border-2 border-dashed text-center flex flex-col items-center justify-center space-y-4 my-2 ${
          isLight ? 'border-slate-300 bg-white/60 text-slate-700' : 'border-slate-700/80 bg-slate-950/40 text-slate-300'
        }`}>
          <div className={`w-16 h-16 rounded-2xl border flex items-center justify-center shadow-inner ${
            isLight ? 'bg-slate-100 border-slate-300 text-slate-400' : 'bg-slate-900/80 border-slate-800 text-slate-500'
          }`}>
            <Trophy className="w-8 h-8 stroke-[1.5]" />
          </div>
          <div className="space-y-1 max-w-md">
            <p className={`text-sm font-mono font-semibold ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
              {t('cvEmptyPrompt', language)}
            </p>
            <p className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
              {t('cvEmptyDetail', language)}
            </p>
          </div>
        </div>
      )}

      {/* 3. SIMULACIÓN DE CARGA */}
      {isGeneratingCV && (
        <div className={`hud-glass p-12 rounded-2xl border text-center flex flex-col items-center justify-center space-y-6 my-2 animate-in fade-in duration-200 ${
          isLight ? 'border-slate-300' : 'border-cyan-500/30'
        }`}>
          <div className="relative flex items-center justify-center">
            <div className={`w-16 h-16 rounded-full border-4 animate-spin ${
              isLight ? 'border-sky-200 border-t-sky-600' : 'border-cyan-500/20 border-t-cyan-400'
            }`} />
            <Cpu className="w-6 h-6 text-cyan-500 absolute animate-pulse" />
          </div>

          <div className="space-y-1">
            <h4 className={`text-sm font-display font-bold ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
              {t('cvProcessingTitle', language)}
            </h4>
            <p className={`text-xs font-mono ${isLight ? 'text-sky-700' : 'text-cyan-400/80'}`}>
              {t('cvProcessingDetail', language)}
            </p>
          </div>
        </div>
      )}

      {/* 4. DESPLIEGUE DE RESULTADOS */}
      {hasRunCV && !isGeneratingCV && (
        <>
          {/* Header de Resultados */}
          <div className={`flex items-center justify-between pb-1 border-b ${
            isLight ? 'border-slate-300' : 'border-slate-800/80'
          }`}>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-xs font-mono text-emerald-500 font-bold uppercase tracking-wider">
                {t('cvResultsAvailable', language)}
              </span>
            </div>
            <button
              onClick={handleResetCV}
              className={`px-3 py-1.5 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer shadow-sm ${
                isLight 
                  ? 'bg-white hover:bg-slate-50 border-slate-300 text-slate-700 hover:text-rose-600 hover:border-rose-300' 
                  : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300 hover:text-rose-300 hover:border-rose-500/40'
              }`}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>{t('cleanReset', language)}</span>
            </button>
          </div>

          {/* 1. 4 METRIC CARDS */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('metricRocAuc', language)}</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{(meanRocAuc / 100).toFixed(3)}</span>
                <span className="text-xs text-emerald-500 font-mono font-bold">±{(stdRocAuc / 100).toFixed(3)}</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {nFolds} Folds {strategy}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('metricF1', language)}</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{meanF1.toFixed(1)}%</span>
                <span className="text-xs text-cyan-600 dark:text-cyan-400 font-mono">Weighted</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? 'Class balance metric' : 'Balanceo de clases formal/informal'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('metricAccuracy', language)}</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{accTest.toFixed(1)}%</span>
                <span className="text-xs text-emerald-500 font-mono">OK</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? 'Global test set accuracy' : 'Precisión global en conjunto de prueba'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('metricLogLoss', language)}</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{logLossVal.toFixed(3)}</span>
                <span className="text-xs text-emerald-500 font-mono">{language === 'en' ? 'Low error' : 'Bajo error'}</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? 'Cross-entropy loss function' : 'Pérdida por entropía cruzada'}
              </p>
            </div>
          </div>

          {/* 2. ROC CURVE & CONFUSION MATRIX */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* ROC Curve Chart */}
            <div className="lg:col-span-8 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
              <div>
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('rocCurveTitle', language)}
                </h3>
                <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('rocCurveSubtitle', language)}
                </p>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={rocCurveData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} />
                    <XAxis dataKey="fpr" type="number" domain={[0, 1]} stroke="#64748b" tick={{ fontSize: 10 }} label={{ value: 'FPR (1 - Specificity)', position: 'insideBottom', offset: -5, fontSize: 10, fill: '#64748b' }} />
                    <YAxis dataKey="tpr" type="number" domain={[0, 1]} stroke="#64748b" tick={{ fontSize: 10 }} label={{ value: 'TPR (Sensitivity)', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#64748b' }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(8, 12, 20, 0.95)', 
                        borderColor: isLight ? '#cbd5e1' : '#00f0ff', 
                        borderRadius: '12px',
                        fontSize: '11px',
                        color: isLight ? '#0f172a' : '#f8fafc'
                      }} 
                    />
                    <Line type="monotone" dataKey="tpr" stroke="#00f0ff" strokeWidth={2.5} dot={false} name={modelLabel} />
                    <Line type="monotone" dataKey="random" stroke="#64748b" strokeDasharray="4 4" dot={false} name="Random Guess (0.50)" />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Chart Explainability: ROC-AUC Discrimination Curve' : 'Explicabilidad: Curva ROC y Capacidad de Discriminación'}
                variableOrMetric="AUC = 0.948 (Excelente)"
                whatItIs={language === 'en'
                  ? 'Receiver Operating Characteristic (ROC) curve displaying true positive rate (sensitivity) vs false positive rate (1 - specificity) across all classification thresholds.'
                  : 'Curva de Característica Operativa del Receptor (ROC) que enfrenta la tasa de verdaderos positivos (sensibilidad) contra la tasa de falsos positivos en todos los umbrales posibles.'}
                howToRead={language === 'en'
                  ? 'The area under the curve (AUC = 0.948) indicates a 94.8% probability that the model ranks a randomly chosen formal worker higher than an informal one.'
                  : 'El área bajo la curva (AUC = 0.948) certifica que el clasificador distingue con un 94.8% de precisión matemática entre un contrato formal e informal.'}
                policyImpact={language === 'en'
                  ? 'Ensures subsidy programs only target agents genuinely on the threshold of formalization, avoiding fiscal leakage.'
                  : 'Garantiza que la focalización de subsidios beneficie a microempresas con capacidad real de transición, evitando fugas de recursos públicos.'}
                benchmarksOrAlerts="AUC > 0.90: Rendimiento Sobresaliente | AUC < 0.70: Rendimiento Deficiente"
              />
            </div>

            {/* Confusion Matrix */}
            <div className="lg:col-span-4 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4 flex flex-col justify-between">
              <div>
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('confusionMatrixTitle', language)}
                </h3>
                <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('confusionMatrixSubtitle', language)}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 font-mono text-xs text-center my-2">
                <div className={`p-4 rounded-xl border ${
                  isLight ? 'bg-sky-50 border-sky-300 text-sky-900' : 'bg-cyan-950/60 border-cyan-500/40 text-cyan-200'
                }`}>
                  <span className={`text-[10px] block ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>TP (Formal)</span>
                  <span className="text-2xl font-bold">{(cm.tp ?? 0).toLocaleString()}</span>
                  <span className="text-[10px] text-emerald-500 block">{((cm.tp ?? 0) / 1000).toFixed(1)}k Hit</span>
                </div>

                <div className={`p-4 rounded-xl border ${
                  isLight ? 'bg-rose-50 border-rose-200 text-rose-800' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
                }`}>
                  <span className={`text-[10px] block ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>FP (Informal→Form)</span>
                  <span className="text-2xl font-bold">{(cm.fp ?? 0).toLocaleString()}</span>
                  <span className="text-[10px] text-rose-500 block">Error Tipo I</span>
                </div>

                <div className={`p-4 rounded-xl border ${
                  isLight ? 'bg-rose-50 border-rose-200 text-rose-800' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
                }`}>
                  <span className={`text-[10px] block ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>FN (Form→Informal)</span>
                  <span className="text-2xl font-bold">{(cm.fn ?? 0).toLocaleString()}</span>
                  <span className="text-[10px] text-rose-500 block">Error Tipo II</span>
                </div>

                <div className={`p-4 rounded-xl border ${
                  isLight ? 'bg-sky-50 border-sky-300 text-sky-900' : 'bg-cyan-950/60 border-cyan-500/40 text-cyan-200'
                }`}>
                  <span className={`text-[10px] block ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>TN (Informal)</span>
                  <span className="text-2xl font-bold">{(cm.tn ?? 0).toLocaleString()}</span>
                  <span className="text-[10px] text-emerald-500 block">{((cm.tn ?? 0) / 1000).toFixed(1)}k Hit</span>
                </div>
              </div>

              <div className={`p-2.5 rounded-xl border flex items-center justify-between text-[11px] font-mono ${
                isLight ? 'bg-slate-50 border-slate-200 text-slate-700' : 'bg-slate-900/50 border-slate-800 text-slate-300'
              }`}>
                <span>{t('metricAccuracy', language)}:</span>
                <span className="font-bold text-emerald-500">
                  {cmAccuracy}%
                </span>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Matrix Explainability: Classification Errors & Trade-offs' : 'Explicabilidad: Matriz de Confusión y Errores Tipo I/II'}
                variableOrMetric="Matriz de Clasificación 2x2"
                whatItIs={language === 'en'
                  ? 'Contingency table breaking down exact counts of True Positives, False Positives (Type I Error), False Negatives (Type II Error), and True Negatives.'
                  : 'Tabla de contingencia 2x2 que desglosa los aciertos (TP, TN) y los errores de predicción (Falsos Positivos y Falsos Negativos).'}
                howToRead={language === 'en'
                  ? 'A low False Positive rate prevents paying subsidies to agents that would have formalized anyway (deadweight loss).'
                  : 'Minimizar los falsos positivos (Error Tipo I) previene el pago de subsidios a unidades que se formalizarían de forma autónoma (peso muerto).'}
                policyImpact={language === 'en'
                  ? 'Balances administrative costs against the social benefit of inclusive registration.'
                  : 'Permite sintonizar la política de inclusión laboral equilibrando el costo fiscal con el impacto social.'}
              />
            </div>
          </div>

          {/* 3. FEATURE IMPORTANCE (SHAP VALUES) */}
          <div className="hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
            <div>
              <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                {t('featureImportanceTitle', language)}
              </h3>
              <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {t('featureImportanceSubtitle', language)}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
              {featureImportance.map((feat: any) => (
                <div key={feat.feature} className={`p-3 rounded-xl border space-y-1.5 ${
                  isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-900/40 border-slate-800'
                }`}>
                  <div className="flex justify-between font-semibold">
                    <span className={isLight ? 'text-slate-800' : 'text-slate-200'}>{feat.feature}</span>
                    <span className="text-cyan-600 dark:text-cyan-400">{feat.importance}%</span>
                  </div>
                  <div className={`w-full h-1.5 rounded-full overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-800'}`}>
                    <div
                      className="bg-gradient-to-r from-cyan-400 to-indigo-500 h-full rounded-full"
                      style={{ width: `${(feat.importance ?? 10) * 3.2}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <ExplainabilityCard
              language={language}
              theme={theme}
              title={language === 'en' ? 'Feature Importance Explainability: TreeSHAP Attribution' : 'Explicabilidad: Importancia de Características (TreeSHAP)'}
              variableOrMetric="Importancia Relativa (%)"
              whatItIs={language === 'en'
                ? 'Global feature importance derived from TreeSHAP values quantifying how strongly each variable influences model decisions.'
                : 'Importancia global de variables calculada mediante valores TreeSHAP, midiendo el peso de cada palanca en la formalización.'}
                howToRead={language === 'en'
                ? 'Longer bars highlight policy levers with maximum direct impact on labor formalization.'
                : 'Las barras más largas señalan las variables que mayor tracción tienen para formalizar trabajadores de bajos ingresos.'}
              policyImpact={language === 'en'
                ? 'Directs government funding towards social security contribution waivers and certified training programs.'
                : 'Focaliza el gasto público en subsidiar aportes a seguridad social y programas de cualificación dual con retorno comprobado.'}
              formulaOrMethod="TreeSHAP: Explicación aditiva de Shapley basada en árboles de decisión"
            />
          </div>


        </>
      )}

    </div>
  );
};
