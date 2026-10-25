import React, { useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid,
  Legend
} from 'recharts';
import { 
  ExtendedCohortData 
} from '../../../data/aiEngineMockData';
import { 
  Target, 
  Play, 
  RefreshCw, 
  Clock, 
  Sparkles, 
  CheckCircle2, 
  Sliders, 
  AlertCircle, 
  Zap,
  TrendingUp,
  Award,
  RotateCcw,
  AlertTriangle,
  Info
} from 'lucide-react';
import { playHoloClick, playCrystallizeSound } from '../../../utils/audioSynth';
import { fetchCohortProjectionsApi } from '../../../services/api';
import { INITIAL_POLICY_STATE } from '../../../data/mockData';
import { Language, AppTheme } from '../../../types';
import { t } from '../../../utils/i18n';
import { ExplainabilityCard } from '../../Common/ExplainabilityCard';

interface CohortProjectionsTabProps {
  language?: Language;
  theme?: AppTheme;
}

export const CohortProjectionsTab: React.FC<CohortProjectionsTabProps> = ({
  language = 'es',
  theme = 'dark',
}) => {
  const [cohortsList, setCohortsList] = useState<ExtendedCohortData[]>([]);
  const [selectedCohortId, setSelectedCohortId] = useState<string>('');
  const [hasRunCohort, setHasRunCohort] = useState<boolean>(false);
  const [isGeneratingCohort, setIsGeneratingCohort] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const isLight = theme === 'light';
  const currentCohort = cohortsList.find((c) => c.id === selectedCohortId) || cohortsList[0] || null;

  const cohortLabel = currentCohort ? (currentCohort.label || (currentCohort as any).name || 'Cohorte Sociodemográfica') : '';
  const populationShare = currentCohort?.populationShare ?? (currentCohort as any)?.sampleSize ?? null;
  const baseProb = currentCohort?.probability ?? (currentCohort as any)?.baseInformality ?? null;
  const projectedProb = (currentCohort as any)?.projectedInformality ?? null;
  const estimatedMonths = currentCohort?.estimatedMonths ?? null;

  const trajectoryData = (currentCohort as any)?.timeProjection || [];
  const driversList = currentCohort?.topDrivers || [];

  const handleRunProjection = async () => {
    setIsGeneratingCohort(true);
    setErrorMsg(null);
    playHoloClick(950);
    try {
      const res = await fetchCohortProjectionsApi(INITIAL_POLICY_STATE);
      if (res && res.cohorts && res.cohorts.length > 0) {
        setCohortsList(res.cohorts);
        setSelectedCohortId(res.cohorts[0].id);
      } else {
        setCohortsList([]);
        setSelectedCohortId('');
      }
      setHasRunCohort(true);
      playCrystallizeSound();
    } catch (e: any) {
      setErrorMsg(e?.message || 'Backend no disponible');
    } finally {
      setIsGeneratingCohort(false);
    }
  };

  const handleResetCohort = () => {
    playHoloClick(700);
    setErrorMsg(null);
    setHasRunCohort(false);
    setCohortsList([]);
    setSelectedCohortId('');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* 1. TOP ACTION & CONFIGURATION BAR */}
      <div className={`hud-glass p-5 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
        isLight ? 'border-slate-300 shadow-sm' : 'border-cyan-500/25'
      }`}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono-hud text-cyan-600 dark:text-cyan-400 font-bold uppercase tracking-wider">
              {t('cohortsTitle', language)}
            </span>
            <span className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
              isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950 border-cyan-500/30 text-cyan-300'
            }`}>
              Micro-Markov Models
            </span>
          </div>
          <p className={`text-xs ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
            {t('cohortsSubtitle', language)}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {cohortsList.length > 0 && (
            <div className="flex items-center gap-1.5 text-xs font-mono">
              <span className={isLight ? 'text-slate-600' : 'text-slate-400'}>{t('selectedCohort', language)}:</span>
              <select
                value={selectedCohortId}
                onChange={(e) => setSelectedCohortId(e.target.value)}
                className={`px-3 py-1.5 rounded-xl border text-xs font-mono cursor-pointer outline-none ${
                  isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900 border-slate-700 text-cyan-300'
                }`}
              >
                {cohortsList.map((c: any) => {
                  const share = c.populationShare ?? c.sampleSize;
                  return (
                    <option key={c.id} value={c.id}>
                      {c.label || c.name} {share != null ? `(${share}%)` : ''}
                    </option>
                  );
                })}
              </select>
            </div>
          )}

          <button
            onClick={handleRunProjection}
            disabled={isGeneratingCohort}
            className={`px-5 py-2.5 rounded-xl font-mono-hud text-xs font-bold flex items-center gap-2 transition-all cursor-pointer shadow-lg ${
              isGeneratingCohort
                ? 'bg-cyan-500/50 text-slate-950 cursor-not-allowed opacity-90'
                : isLight
                  ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20'
                  : 'bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-slate-950 shadow-cyan-500/20 glow-cyan'
            }`}
          >
            {isGeneratingCohort ? (
              <>
                <RefreshCw className={`w-4 h-4 animate-spin ${isLight ? 'text-white' : 'text-slate-950'}`} />
                <span>{language === 'en' ? 'Projecting...' : 'Proyectando...'}</span>
              </>
            ) : (
              <>
                <Play className={`w-4 h-4 fill-current ${isLight ? 'text-white' : 'text-slate-950'}`} />
                <span>{t('runCohortProjection', language)}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Aviso de Backend no disponible */}
      {errorMsg && (
        <div className={`p-4 rounded-xl border flex items-center justify-between gap-3 text-xs font-mono animate-in fade-in ${
          isLight ? 'bg-rose-50 border-rose-300 text-rose-800' : 'bg-rose-950/40 border-rose-500/40 text-rose-200'
        }`}>
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0" />
            <span><strong>Aviso:</strong> Backend no disponible. No se pudieron proyectar las cohortes en el servidor FastAPI.</span>
          </div>
          <button
            onClick={handleRunProjection}
            className={`px-3 py-1 rounded-lg border font-mono-hud text-xs cursor-pointer ${
              isLight ? 'bg-white border-rose-300 text-rose-700 hover:bg-rose-100' : 'bg-rose-900/50 border-rose-500/50 text-rose-200 hover:bg-rose-800/60'
            }`}
          >
            Reintentar
          </button>
        </div>
      )}

      {/* 2. ESTADO INICIAL */}
      {!hasRunCohort && !isGeneratingCohort && (
        <div className={`p-16 rounded-2xl border-2 border-dashed text-center flex flex-col items-center justify-center space-y-4 my-2 ${
          isLight ? 'border-slate-300 bg-white/60 text-slate-700' : 'border-slate-700/80 bg-slate-950/40 text-slate-300'
        }`}>
          <div className={`w-16 h-16 rounded-2xl border flex items-center justify-center shadow-inner ${
            isLight ? 'bg-slate-100 border-slate-300 text-slate-400' : 'bg-slate-900/80 border-slate-800 text-slate-500'
          }`}>
            <Target className="w-8 h-8 stroke-[1.5]" />
          </div>
          <div className="space-y-1 max-w-md">
            <p className={`text-sm font-mono font-semibold ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
              {t('cohortsEmptyPrompt', language)}
            </p>
            <p className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
              {t('cohortsEmptyDetail', language)}
            </p>
          </div>
        </div>
      )}

      {/* 3. SIMULACIÓN DE CARGA */}
      {isGeneratingCohort && (
        <div className={`hud-glass p-12 rounded-2xl border text-center flex flex-col items-center justify-center space-y-6 my-2 animate-in fade-in duration-200 ${
          isLight ? 'border-slate-300' : 'border-cyan-500/30'
        }`}>
          <div className="relative flex items-center justify-center">
            <div className={`w-16 h-16 rounded-full border-4 animate-spin ${
              isLight ? 'border-sky-200 border-t-sky-600' : 'border-cyan-500/20 border-t-cyan-400'
            }`} />
            <Target className="w-6 h-6 text-cyan-500 absolute animate-pulse" />
          </div>

          <div className="space-y-1">
            <h4 className={`text-sm font-display font-bold ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
              {t('cohortsProcessingTitle', language)}
            </h4>
            <p className={`text-xs font-mono ${isLight ? 'text-sky-700' : 'text-cyan-400/80'}`}>
              {t('cohortsProcessingDetail', language)}
            </p>
          </div>
        </div>
      )}

      {/* 4. SIN RESULTADOS CUANDO NO HAY COHORTES DE PANEL */}
      {hasRunCohort && !isGeneratingCohort && cohortsList.length === 0 && (
        <div className={`p-10 rounded-2xl border text-center flex flex-col items-center justify-center space-y-4 my-2 font-mono ${
          isLight ? 'border-amber-300 bg-amber-50/50 text-amber-900' : 'border-amber-500/30 bg-amber-950/20 text-amber-200'
        }`}>
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-500">
            <Info className="w-6 h-6" />
          </div>
          <div className="space-y-2 max-w-lg">
            <h4 className="text-sm font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">
              Sin resultados de proyecciones longitudinales de cohortes
            </h4>
            <p className="text-xs text-slate-400 dark:text-slate-400 leading-relaxed">
              Las transiciones temporales de cohortes requieren microdatos de panel longitudinal (seguimiento en olas sucesivas a los mismos individuos en el tiempo). Las encuestas oficiales actualmente cargadas (India PLFS 2024 y Nigeria NLFS 2023 Q3) son de corte transversal (cross-sectional).
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-500">
              Conforme a la regla de integridad de datos reales, no se generan transiciones simuladas ni datos sintéticos.
            </p>
          </div>
          <button
            onClick={handleResetCohort}
            className={`px-4 py-1.5 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              isLight ? 'bg-white border-amber-300 text-amber-900 hover:bg-amber-100' : 'bg-slate-900 border-amber-500/40 text-amber-300 hover:bg-slate-800'
            }`}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Restablecer</span>
          </button>
        </div>
      )}

      {/* 5. DESPLIEGUE DE RESULTADOS CUANDO HAY DATOS */}
      {hasRunCohort && !isGeneratingCohort && cohortsList.length > 0 && currentCohort && (
        <>
          {/* Header de Resultados */}
          <div className={`flex items-center justify-between pb-1 border-b ${
            isLight ? 'border-slate-300' : 'border-slate-800/80'
          }`}>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-xs font-mono text-emerald-500 font-bold uppercase tracking-wider">
                {t('cohortResultsAvailable', language)}: {cohortLabel}
              </span>
            </div>
            <button
              onClick={handleResetCohort}
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

          {/* 1. 4 KPI CARDS ESPECÍFICAS DE LA COHORTE */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('baselineInformalityCohort', language)}</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>
                  {baseProb !== null ? `${baseProb}%` : 'Sin datos'}
                </span>
                <span className="text-xs text-amber-500 font-mono">T=0 (2024)</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {populationShare !== null ? `${populationShare}% ` : ''}{language === 'en' ? 'population share' : 'participación en población'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('projectedInformalityCohort', language)}</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-display font-bold text-emerald-500">
                  {projectedProb !== null ? `${projectedProb}%` : 'Sin datos'}
                </span>
                <span className="text-xs text-emerald-500 font-mono">2034</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? '10-Year Horizon' : 'Horizonte a 10 Años'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('expectedTransition', language)}</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-sky-700' : 'text-cyan-300'}`}>
                  {baseProb !== null && projectedProb !== null ? `- ${(baseProb - projectedProb).toFixed(1)}%` : 'Sin datos'}
                </span>
                <span className="text-xs text-emerald-500 font-mono">Formalized</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? 'Net flow to formal sector' : 'Flujo neto hacia formalidad'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>Tiempo de Transición</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>
                  {estimatedMonths !== null ? `${estimatedMonths} m` : 'Sin datos'}
                </span>
                <span className="text-xs text-indigo-500 font-mono">Estimado</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? 'Average formalization speed' : 'Meses promedio para formalización'}
              </p>
            </div>
          </div>

          {/* 2. PROJECTION TRAJECTORY CHART & DEMOGRAPHICS */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Trajectory Chart */}
            <div className="lg:col-span-8 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
              <div>
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('transitionTrajectoryTitle', language)}
                </h3>
                <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('transitionTrajectorySubtitle', language)}
                </p>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trajectoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} />
                    <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(8, 12, 20, 0.95)', 
                        borderColor: isLight ? '#cbd5e1' : '#00f0ff', 
                        borderRadius: '12px',
                        fontSize: '11px',
                        color: isLight ? '#0f172a' : '#f8fafc'
                      }} 
                    />
                    <Bar dataKey="formalRate" fill="#00f0ff" radius={[4, 4, 0, 0]} name={t('formalLabel', language) + ' %'} />
                    <Bar dataKey="informalRate" fill="#f59e0b" radius={[4, 4, 0, 0]} name={t('informalLabel', language) + ' %'} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Chart Explainability: Cohort Longitudinal Formalization Trajectory' : 'Explicabilidad: Trayectoria Longitudinal de la Cohorte'}
                variableOrMetric={`Cohorte: ${cohortLabel}`}
                whatItIs={language === 'en'
                  ? 'Longitudinal transition projection (T0 to T+10) calculating the probability of switching from informal activity to formal employment for this demographic subgroup.'
                  : 'Proyección longitudinal a 10 años que modela la probabilidad de absorción en el empleo formal para este subgrupo sociodemográfico específico.'}
                howToRead={language === 'en'
                  ? 'Steeper upward slope in formal rate indicates high policy responsiveness and shorter time to formalize.'
                  : 'Una pendiente ascendente más pronunciada indica alta elasticidad ante los incentivos de política pública y menor tiempo de transición.'}
                policyImpact={language === 'en'
                  ? 'Identifies vulnerable cohorts requiring combined policy packages (e.g. child-care subsidies + dual training for young mothers).'
                  : 'Permite diseñar paquetes de apoyo complementario (ej: subsidio al cuidado infantil + formación dual para madres jóvenes).'}
                formulaOrMethod="Cadena de Markov no estacionaria: P(Formal_t+1 | Informal_t, X_i, Políticas)"
              />
            </div>

            {/* Policy Sensitivity & Drivers */}
            <div className="lg:col-span-4 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4 flex flex-col justify-between">
              <div>
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('policySensitivityTitle', language)}
                </h3>
                <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('policySensitivitySubtitle', language)}
                </p>
              </div>

              <div className="space-y-3 font-mono text-xs">
                {driversList.map((driver: any, dIdx: number) => (
                  <div key={dIdx} className={`p-3 rounded-xl border space-y-1.5 ${
                    isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-900/50 border-slate-800'
                  }`}>
                    <div className="flex justify-between items-start gap-2">
                      <span className={`text-[11px] leading-tight ${isLight ? 'text-slate-800' : 'text-slate-200'}`}>{driver.feature}</span>
                      <span className="text-cyan-600 dark:text-cyan-400 font-bold shrink-0">{driver.shapValue || `+${driver.importance}%`}</span>
                    </div>
                    <div className={`w-full h-1.5 rounded-full overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-800'}`}>
                      <div
                        className="bg-gradient-to-r from-cyan-400 to-emerald-400 h-full rounded-full"
                        style={{ width: `${Math.min(100, (driver.importance ?? 50))}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Driver Explainability: SHAP Contribution per Subgroup' : 'Explicabilidad: Palancas de Mayor Sensibilidad'}
                variableOrMetric="SHAP Local por Cohorte"
                whatItIs={language === 'en'
                  ? 'Subgroup-specific SHAP values showing which individual policy levers unlock the highest formalization gain for this demographic.'
                  : 'Valores SHAP desagregados que cuantifican qué palanca de política pública genera el mayor impacto neto para este grupo demográfico.'}
                howToRead={language === 'en'
                  ? 'A positive SHAP value (+0.34) indicates strong positive acceleration towards formal status.'
                  : 'Un valor SHAP positivo (+0.34) indica que el incentivo incrementa en 34 puntos la probabilidad marginal de formalizarse.'}
                policyImpact={language === 'en'
                  ? 'Enables tailored micro-policies instead of one-size-fits-all national mandates.'
                  : 'Permite diseñar micro-políticas a la medida en lugar de intervenciones genéricas de baja efectividad.'}
              />

              {currentCohort.barrier && (
                <div className={`p-2.5 rounded-xl border text-[10px] font-mono leading-relaxed ${
                  isLight ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-amber-950/40 border-amber-500/30 text-amber-300'
                }`}>
                  <div className="font-bold flex items-center gap-1 mb-0.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                    <span>Barrera Principal:</span>
                  </div>
                  <span>{currentCohort.barrier}</span>
                </div>
              )}
            </div>
          </div>


        </>
      )}

    </div>
  );
};
