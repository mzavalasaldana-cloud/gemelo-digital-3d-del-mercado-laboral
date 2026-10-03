import React, { useState } from 'react';
import { 
  OPTIMAL_HYPERPARAMS_JSON, 
  STATISTICAL_TESTS_RESULTS, 
  StatisticalTestRow 
} from '../../../data/aiEngineMockData';
import { 
  Sliders, 
  Play, 
  RefreshCw, 
  Terminal, 
  CheckCircle2, 
  Sparkles, 
  Copy, 
  Check, 
  FlaskConical, 
  Layers, 
  FileJson,
  Cpu,
  ShieldCheck,
  RotateCcw
} from 'lucide-react';
import { playHoloClick, playCrystallizeSound } from '../../../utils/audioSynth';
import { Language, AppTheme } from '../../../types';
import { t } from '../../../utils/i18n';
import { ExplainabilityCard } from '../../Common/ExplainabilityCard';

interface HyperparamsStatsTabProps {
  language?: Language;
  theme?: AppTheme;
}

export const HyperparamsStatsTab: React.FC<HyperparamsStatsTabProps> = ({
  language = 'es',
  theme = 'dark',
}) => {
  // Hyperparameters interactive state
  const [params, setParams] = useState({
    maxDepth: 6,
    learningRate: 0.045,
    nEstimators: 350,
    subsample: 0.85,
    colsampleByTree: 0.80,
    regLambda: 1.25,
  });

  const [hasRunOpt, setHasRunOpt] = useState<boolean>(false);
  const [isGeneratingOpt, setIsGeneratingOpt] = useState<boolean>(false);
  const [copiedJson, setCopiedJson] = useState<boolean>(false);

  const isLight = theme === 'light';

  const handleRunOptimization = () => {
    setIsGeneratingOpt(true);
    playHoloClick(1000);
    setTimeout(() => {
      setIsGeneratingOpt(false);
      setHasRunOpt(true);
      playCrystallizeSound();
    }, 1500);
  };

  const handleResetOpt = () => {
    playHoloClick(700);
    setHasRunOpt(false);
  };

  const handleCopyJson = () => {
    playHoloClick(1100);
    navigator.clipboard.writeText(JSON.stringify(OPTIMAL_HYPERPARAMS_JSON, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* 1. TOP HEADER BAR */}
      <div className={`hud-glass p-5 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
        isLight ? 'border-slate-300 shadow-sm' : 'border-cyan-500/25'
      }`}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono-hud text-cyan-600 dark:text-cyan-400 font-bold uppercase tracking-wider">
              {t('hyperparamsTitle', language)}
            </span>
            <span className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
              isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950 border-cyan-500/30 text-cyan-300'
            }`}>
              Optuna v3.6 + SciPy
            </span>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-amber-500/20 border border-amber-400 text-amber-500 font-bold">
              Demostración
            </span>
          </div>
          <p className={`text-xs ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
            {t('hyperparamsSubtitle', language)}
          </p>
        </div>

        <button
          onClick={handleRunOptimization}
          disabled={isGeneratingOpt}
          className={`px-5 py-2.5 rounded-xl font-mono-hud text-xs font-bold flex items-center gap-2 transition-all cursor-pointer shadow-lg ${
            isGeneratingOpt
              ? 'bg-cyan-500/50 text-slate-950 cursor-not-allowed opacity-90'
              : isLight
                ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20'
                : 'bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-slate-950 shadow-cyan-500/20 glow-cyan'
          }`}
        >
          {isGeneratingOpt ? (
            <>
              <RefreshCw className={`w-4 h-4 animate-spin ${isLight ? 'text-white' : 'text-slate-950'}`} />
              <span>{t('optimizingParams', language)}</span>
            </>
          ) : (
            <>
              <Sparkles className={`w-4 h-4 fill-current ${isLight ? 'text-white' : 'text-slate-950'}`} />
              <span>{t('runOptuna', language)}</span>
            </>
          )}
        </button>
      </div>

      {/* 2. HYPERPARAMETER SLIDERS / CONFIGURATION */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Sliders Panel */}
        <div className="lg:col-span-7 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
              {t('currentConfig', language)}
            </h3>
            <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400">XGBClassifier (Tree booster)</span>
          </div>

          <div className="space-y-3.5 font-mono text-xs">
            {/* Max Depth */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className={isLight ? 'text-slate-700' : 'text-slate-300'}>max_depth (Profundidad Máxima)</span>
                <span className="text-cyan-600 dark:text-cyan-400 font-bold">{params.maxDepth}</span>
              </div>
              <input
                type="range"
                min="3"
                max="12"
                value={params.maxDepth}
                onChange={(e) => setParams({ ...params, maxDepth: Number(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
            </div>

            {/* Learning Rate */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className={isLight ? 'text-slate-700' : 'text-slate-300'}>learning_rate (Tasa de Aprendizaje η)</span>
                <span className="text-cyan-600 dark:text-cyan-400 font-bold">{params.learningRate}</span>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.30"
                step="0.005"
                value={params.learningRate}
                onChange={(e) => setParams({ ...params, learningRate: Number(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
            </div>

            {/* N Estimators */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className={isLight ? 'text-slate-700' : 'text-slate-300'}>n_estimators (Número de Árboles)</span>
                <span className="text-cyan-600 dark:text-cyan-400 font-bold">{params.nEstimators}</span>
              </div>
              <input
                type="range"
                min="50"
                max="1000"
                step="25"
                value={params.nEstimators}
                onChange={(e) => setParams({ ...params, nEstimators: Number(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
            </div>

            {/* Subsample */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className={isLight ? 'text-slate-700' : 'text-slate-300'}>subsample (Fracción de Muestras)</span>
                <span className="text-cyan-600 dark:text-cyan-400 font-bold">{params.subsample}</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={params.subsample}
                onChange={(e) => setParams({ ...params, subsample: Number(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
            </div>

            {/* Reg Lambda */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className={isLight ? 'text-slate-700' : 'text-slate-300'}>reg_lambda (Regularización L2)</span>
                <span className="text-cyan-600 dark:text-cyan-400 font-bold">{params.regLambda}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="5.0"
                step="0.25"
                value={params.regLambda}
                onChange={(e) => setParams({ ...params, regLambda: Number(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
              />
            </div>
          </div>
        </div>

        {/* JSON Code Viewer / Optimization Output */}
        <div className="lg:col-span-5 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-3 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileJson className="w-4 h-4 text-cyan-400" />
              <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                {hasRunOpt ? t('optimalFound', language) : 'JSON Payload (Scikit-Learn)'}
              </h3>
            </div>
            <button
              onClick={handleCopyJson}
              className={`px-2.5 py-1 rounded-lg border text-[11px] font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
                isLight 
                  ? 'bg-white hover:bg-slate-50 border-slate-300 text-slate-700' 
                  : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300'
              }`}
            >
              {copiedJson ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedJson ? t('copied', language) : t('copyJson', language)}</span>
            </button>
          </div>

          <div className={`p-4 rounded-xl border font-mono text-xs overflow-x-auto ${
            isLight ? 'bg-slate-900 text-cyan-300 border-slate-800' : 'bg-[#020408] text-cyan-300 border-slate-900'
          }`}>
            <pre className="text-[11px] leading-relaxed">
              {JSON.stringify(hasRunOpt ? OPTIMAL_HYPERPARAMS_JSON : params, null, 2)}
            </pre>
          </div>

          {hasRunOpt && (
            <div className={`p-2.5 rounded-xl border flex items-center justify-between text-[11px] font-mono ${
              isLight ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
            }`}>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Optuna: 50 trials | ROC-AUC +0.024</span>
              </div>
              <button
                onClick={handleResetOpt}
                className="text-xs underline cursor-pointer"
              >
                Reset
              </button>
            </div>
          )}

          <ExplainabilityCard
            language={language}
            theme={theme}
            title={language === 'en' ? 'Tuning Explainability: Bayesian Tree-structured Parzen Estimator' : 'Explicabilidad: Optimización Bayesiana de Hiperparámetros'}
            variableOrMetric="Optuna TPE Sampler"
            whatItIs={language === 'en'
              ? 'Automatic calibration of gradient boosting hyperparameters (depth, learning rate, regularization) to balance model capacity and prevent overfitting.'
              : 'Calibración automática del espacio de hiperparámetros (profundidad, tasa de aprendizaje, regularización L2) para maximizar la generalización.'}
            howToRead={language === 'en'
              ? 'L2 lambda regularization penalizes excessive tree complexity, keeping inference smooth across unseen survey clusters.'
              : 'El término de regularización L2 (reg_lambda) previene que el árbol memorice ruido muestral, asegurando estabilidad ante nuevas encuestas.'}
            policyImpact={language === 'en'
              ? 'Guarantees reliable counterfactual projections when simulating extreme policy shocks.'
              : 'Garantiza que las simulaciones de reformas contrafactuales no generen respuestas numéricas inestables.'}
          />
        </div>
      </div>

      {/* 3. STATISTICAL HYPOTHESIS TESTING TABLE */}
      <div className="hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
        <div>
          <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
            {t('statisticalHypothesisTitle', language)}
          </h3>
          <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
            {t('statisticalHypothesisSubtitle', language)}
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border-collapse">
            <thead>
              <tr className={`border-b ${isLight ? 'border-slate-200 text-sky-800' : 'border-slate-800 text-cyan-400'}`}>
                <th className="pb-2.5">Prueba Estadística</th>
                <th className="pb-2.5">Variable / Hipótesis</th>
                <th className="pb-2.5">Estadístico</th>
                <th className="pb-2.5">p-Valor / Umbral</th>
                <th className="pb-2.5">Diagnóstico / Conclusión</th>
                <th className="pb-2.5">Estado</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${isLight ? 'divide-slate-200 text-slate-700' : 'divide-slate-800/60 text-slate-300'}`}>
              {STATISTICAL_TESTS_RESULTS.map((row: any, idx: number) => {
                const isPassed = row.status === 'passed';
                return (
                  <tr key={idx} className={isLight ? 'hover:bg-slate-50' : 'hover:bg-slate-900/40'}>
                    <td className={`py-3 font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{row.testName}</td>
                    <td className={`text-[11px] ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{row.variable}</td>
                    <td className="text-cyan-600 dark:text-cyan-300 font-semibold">{row.statistic}</td>
                    <td className="font-bold text-emerald-500">
                      <div>{row.pValue}</div>
                      <div className="text-[10px] text-slate-400 font-normal">{row.criticalValue}</div>
                    </td>
                    <td className={`text-[11px] max-w-xs ${isLight ? 'text-slate-600' : 'text-slate-300'}`}>
                      {row.conclusion}
                    </td>
                    <td>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        isPassed
                          ? isLight ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : isLight ? 'bg-amber-100 text-amber-800 border-amber-300' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      }`}>
                        {isPassed 
                          ? (language === 'en' ? 'Validated' : 'Validado') 
                          : (language === 'en' ? 'Warning' : 'Alerta')}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <ExplainabilityCard
          language={language}
          theme={theme}
          title={language === 'en' ? 'Battery Explainability: Statistical Significance & Diagnostic Tests' : 'Explicabilidad: Batería de Pruebas y Robustez Econométrica'}
          variableOrMetric="SciPy Stats (p-values & Tests)"
          whatItIs={language === 'en'
            ? 'Full battery of non-parametric tests (Mann-Whitney, Kolmogorov-Smirnov, Shapiro-Wilk) verifying empirical assumptions.'
            : 'Conjunto de pruebas de hipótesis econométricas que validan la segmentación formal/informal, la ortogonalidad de factores y la normalidad residual.'}
          howToRead={language === 'en'
            ? 'p-values < 0.05 formally reject the null hypothesis, demonstrating statistically significant wage differences between sectors.'
            : 'Un p-valor < 0.0001 (***) confirma que las brechas salariales y de educación entre formales e informales son estructurales y no aleatorias.'}
          policyImpact={language === 'en'
            ? 'Provides scientific foundation required for ministerial whitepapers and academic peer review.'
            : 'Proporciona la fundamentación científica indispensable para respaldar proyectos de ley e informes técnicos ministeriales.'}
          benchmarksOrAlerts="Nivel de significancia α = 0.05 (Confianza del 95%)"
        />
      </div>


    </div>
  );
};
