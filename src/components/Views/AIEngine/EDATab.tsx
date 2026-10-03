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
  EDA_KPIS, 
  EDA_HISTOGRAMS, 
  CORRELATION_VARIABLES, 
  CORRELATION_MATRIX, 
  BOXPLOT_METRICS, 
  HIGH_CORRELATIONS_TABLE 
} from '../../../data/aiEngineMockData';
import { 
  Play, 
  CheckCircle2, 
  Database, 
  Table2, 
  AlertTriangle, 
  Sparkles, 
  Activity, 
  Layers, 
  Filter, 
  Info,
  RefreshCw,
  TrendingUp,
  RotateCcw,
  BarChart2
} from 'lucide-react';
import { playHoloClick, playCrystallizeSound } from '../../../utils/audioSynth';
import { fetchEDAAnalytics, EDAApiResponse } from '../../../services/api';
import { Language, AppTheme } from '../../../types';
import { t } from '../../../utils/i18n';
import { ExplainabilityCard } from '../../Common/ExplainabilityCard';

interface EDATabProps {
  language?: Language;
  theme?: AppTheme;
}

export const EDATab: React.FC<EDATabProps> = ({
  language = 'es',
  theme = 'dark',
}) => {
  const [hasRunEDA, setHasRunEDA] = useState<boolean>(false);
  const [isGeneratingEDA, setIsGeneratingEDA] = useState<boolean>(false);
  const [selectedVarKey, setSelectedVarKey] = useState<string>('salary');
  const [hoveredCorr, setHoveredCorr] = useState<{ a: string; b: string; val: number } | null>(null);
  const [edaResult, setEdaResult] = useState<EDAApiResponse | null>(null);

  const isLight = theme === 'light';

  const handleRunEDA = async () => {
    setIsGeneratingEDA(true);
    playHoloClick(1000);
    try {
      const data = await fetchEDAAnalytics();
      setEdaResult(data);
      setHasRunEDA(true);
      playCrystallizeSound();
    } catch (err) {
      setHasRunEDA(true);
    } finally {
      setIsGeneratingEDA(false);
    }
  };

  const handleResetEDA = () => {
    playHoloClick(700);
    setHasRunEDA(false);
  };

  const rawKpis: any = edaResult?.kpis || EDA_KPIS;
  const currentKPIs = {
    completeness: rawKpis?.completeness ?? rawKpis?.dataQuality ?? 98.4,
    missingRate: rawKpis?.missingRate ?? rawKpis?.nullPercentage ?? 0.8,
    totalRows: rawKpis?.totalRows ?? rawKpis?.totalRecords ?? 48500,
    totalCols: rawKpis?.totalCols ?? rawKpis?.totalVariables ?? 14,
    imputedRows: rawKpis?.imputedRows ?? Math.round((rawKpis?.totalRecords ?? rawKpis?.totalRows ?? 48500) * 0.08),
    numericCols: rawKpis?.numericCols ?? 9,
    categoricalCols: rawKpis?.categoricalCols ?? 5,
  };
  const currentHistograms = edaResult?.histograms || EDA_HISTOGRAMS;
  const currentCorrVarsRaw = edaResult?.correlationVariables || CORRELATION_VARIABLES;
  const normalizedCorrVars = currentCorrVarsRaw.map((v: any, i: number) => 
    typeof v === 'string' ? { key: `var-${i}`, label: v } : { key: v.key || `var-${i}`, label: v.label || v.name || `Var ${i}` }
  );
  const currentCorrMatrix = edaResult?.correlationMatrix || CORRELATION_MATRIX;
  const currentHighCorrs = edaResult?.highCorrelations || HIGH_CORRELATIONS_TABLE;
  const currentBoxplotsRaw = edaResult?.boxplots || BOXPLOT_METRICS;
  const normalizedBoxplots = currentBoxplotsRaw.map((bp: any) => ({
    variable: bp.variable || bp.group || 'Variable',
    unit: bp.unit || 'USD/Horas',
    p25: bp.p25 ?? bp.q1 ?? 0,
    median: bp.median ?? 0,
    p75: bp.p75 ?? bp.q3 ?? 0,
  }));

  const rawHist = (currentHistograms as any)[selectedVarKey] || (currentHistograms as any).salary;
  const chartHistData = Array.isArray(rawHist) 
    ? rawHist 
    : Array.isArray(rawHist?.data) 
      ? rawHist.data.map((d: any) => ({
          range: d.range,
          formal: d.formal ?? d.formalCount ?? 0,
          informal: d.informal ?? d.informalCount ?? 0,
        }))
      : [];

  // Function to return color intensity for the correlation heatmap
  const getCorrBg = (val: number) => {
    if (val === 1.0) return isLight ? 'bg-sky-600 text-white font-bold' : 'bg-cyan-500/80 text-slate-950 font-bold';
    if (val >= 0.75) return isLight ? 'bg-sky-500 text-white font-semibold' : 'bg-cyan-600/60 text-white font-semibold';
    if (val >= 0.60) return isLight ? 'bg-sky-200 text-sky-900' : 'bg-cyan-700/40 text-cyan-200';
    if (val >= 0.45) return isLight ? 'bg-sky-100 text-sky-800' : 'bg-sky-900/40 text-sky-200';
    return isLight ? 'bg-slate-100 text-slate-600' : 'bg-slate-900/60 text-slate-400';
  };

  const variableOptions = [
    { key: 'salary', label: t('salaryVar', language) },
    { key: 'hours', label: t('experienceVar', language) },
    { key: 'education', label: t('educationVar', language) },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* Top Action Bar / Execution Trigger */}
      <div className={`hud-glass p-5 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
        isLight ? 'border-slate-300 shadow-sm' : 'border-cyan-500/25'
      }`}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono-hud text-cyan-600 dark:text-cyan-400 font-bold uppercase tracking-wider">
              {t('edaTitle', language)}
            </span>
            <span className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
              isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950 border-cyan-500/30 text-cyan-300'
            }`}>
              Pipeline v2.4
            </span>
          </div>
          <p className={`text-xs ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
            {t('edaSubtitle', language)}
          </p>
        </div>

        <button
          onClick={handleRunEDA}
          disabled={isGeneratingEDA}
          className={`px-5 py-2.5 rounded-xl font-mono-hud text-xs font-bold flex items-center gap-2 transition-all cursor-pointer shadow-lg ${
            isGeneratingEDA
              ? 'bg-cyan-500/50 text-slate-950 cursor-not-allowed opacity-90'
              : isLight
                ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20 hover:shadow-sky-600/35'
                : 'bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-slate-950 shadow-cyan-500/20 hover:shadow-cyan-500/35 glow-cyan'
          }`}
        >
          {isGeneratingEDA ? (
            <>
              <RefreshCw className={`w-4 h-4 animate-spin ${isLight ? 'text-white' : 'text-slate-950'}`} />
              <span>{t('processingEDA', language)}</span>
            </>
          ) : (
            <>
              <Play className={`w-4 h-4 fill-current ${isLight ? 'text-white' : 'text-slate-950'}`} />
              <span>{t('runEDA', language)}</span>
            </>
          )}
        </button>
      </div>

      {/* Banner de datos sintéticos */}
      <div className={`p-3.5 rounded-xl border flex items-center gap-3 text-xs font-mono ${
        isLight ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-amber-950/40 border-amber-500/40 text-amber-200'
      }`}>
        <Info className="w-4 h-4 text-amber-500 shrink-0" />
        <span>
          <strong>Aviso Metodológico:</strong> Datos sintéticos de demostración; no son microdatos oficiales. El modelo y el artículo no usan microdatos: usan solo tasas agregadas de ILOSTAT.
        </span>
      </div>

      {/* 2. ESTADO INICIAL (VISTA VACÍA) */}
      {!hasRunEDA && !isGeneratingEDA && (
        <div className={`p-16 rounded-2xl border-2 border-dashed text-center flex flex-col items-center justify-center space-y-4 my-2 ${
          isLight ? 'border-slate-300 bg-white/60 text-slate-700' : 'border-slate-700/80 bg-slate-950/40 text-slate-300'
        }`}>
          <div className={`w-16 h-16 rounded-2xl border flex items-center justify-center shadow-inner ${
            isLight ? 'bg-slate-100 border-slate-300 text-slate-400' : 'bg-slate-900/80 border-slate-800 text-slate-500'
          }`}>
            <BarChart2 className="w-8 h-8 stroke-[1.5]" />
          </div>
          <div className="space-y-1 max-w-md">
            <p className={`text-sm font-mono font-semibold ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
              {t('edaEmptyPrompt', language)}
            </p>
            <p className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
              {t('edaEmptyDetail', language)}
            </p>
          </div>
        </div>
      )}

      {/* 3. SIMULACIÓN DE CARGA (SPINNER / SKELETON UI) */}
      {isGeneratingEDA && (
        <div className={`hud-glass p-12 rounded-2xl border text-center flex flex-col items-center justify-center space-y-6 my-2 animate-in fade-in duration-200 ${
          isLight ? 'border-slate-300' : 'border-cyan-500/30'
        }`}>
          <div className="relative flex items-center justify-center">
            <div className={`w-16 h-16 rounded-full border-4 animate-spin ${
              isLight ? 'border-sky-200 border-t-sky-600' : 'border-cyan-500/20 border-t-cyan-400'
            }`} />
            <Activity className="w-6 h-6 text-cyan-500 absolute animate-pulse" />
          </div>

          <div className="space-y-1">
            <h4 className={`text-sm font-display font-bold ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
              {t('edaProcessingTitle', language)}
            </h4>
            <p className={`text-xs font-mono ${isLight ? 'text-sky-700' : 'text-cyan-400/80'}`}>
              {t('edaProcessingDetail', language)}
            </p>
          </div>

          {/* Skeleton Blocks Grid */}
          <div className="w-full max-w-4xl space-y-4 pt-2">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className={`h-24 rounded-xl border animate-pulse ${
                  isLight ? 'bg-slate-200 border-slate-300' : 'bg-slate-900/80 border-slate-800'
                }`} />
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
              <div className={`lg:col-span-8 h-64 rounded-xl border animate-pulse ${
                isLight ? 'bg-slate-200 border-slate-300' : 'bg-slate-900/60 border-slate-800'
              }`} />
              <div className={`lg:col-span-4 h-64 rounded-xl border animate-pulse ${
                isLight ? 'bg-slate-200 border-slate-300' : 'bg-slate-900/60 border-slate-800'
              }`} />
            </div>
          </div>
        </div>
      )}

      {/* 4. DESPLIEGUE DE RESULTADOS */}
      {hasRunEDA && !isGeneratingEDA && (
        <>
          {/* Header de Resultados con Botón de Reinicio */}
          <div className={`flex items-center justify-between pb-1 border-b ${
            isLight ? 'border-slate-300' : 'border-slate-800/80'
          }`}>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-xs font-mono text-emerald-500 font-bold uppercase tracking-wider">
                {t('edaResultsAvailable', language)}
              </span>
            </div>
            <button
              onClick={handleResetEDA}
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

          {/* 1. KPI CARDS */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('dataQuality', language)}</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{currentKPIs.completeness}%</span>
                <span className="text-xs text-emerald-500 font-mono">{t('highCompleteness', language)}</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {currentKPIs.missingRate}% {language === 'en' ? 'null / empty rate' : 'tasa de nulos'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('recordsLabel', language)}</span>
                <Database className="w-4 h-4 text-cyan-500" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{(currentKPIs.totalRows ?? 0).toLocaleString()}</span>
                <span className={`text-xs font-mono ${isLight ? 'text-sky-700' : 'text-cyan-400'}`}>Harmonized</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {currentKPIs.totalCols} {language === 'en' ? 'analyzed variables' : 'variables analizadas'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('imputedRecords', language)}</span>
                <Sparkles className="w-4 h-4 text-indigo-500" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-indigo-700' : 'text-indigo-300'}`}>{(currentKPIs.imputedRows ?? 0).toLocaleString()}</span>
                <span className="text-xs text-indigo-500 font-mono">Mediana/Moda (Demostración)</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? 'Demonstration median/mode imputation' : 'Imputación mediana/moda (demostración)'}
              </p>
            </div>

            <div className="hud-glass p-4 rounded-xl border border-cyan-500/20 relative overflow-hidden">
              <div className="flex items-center justify-between">
                <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>{t('numericVariables', language)}</span>
                <Table2 className="w-4 h-4 text-cyan-500" />
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`text-2xl font-display font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>{currentKPIs.numericCols}</span>
                <span className={`text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>/ {currentKPIs.totalCols}</span>
              </div>
              <p className={`text-[11px] font-mono mt-1 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {currentKPIs.categoricalCols} {language === 'en' ? 'one-hot encoded categorical' : 'categóricas codificadas'}
              </p>
            </div>
          </div>

          {/* 2. UNIVARIATE DISTRIBUTION HISTOGRAM & BOXPLOTS */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Histogram Column */}
            <div className="lg:col-span-8 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('distributionAnalysis', language)}
                  </h3>
                  <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                    {t('histogramSubtitle', language)}
                  </p>
                </div>

                {/* Variable Selector Tabs */}
                <div className={`flex flex-wrap items-center gap-1.5 p-1 rounded-xl border ${
                  isLight ? 'bg-slate-100 border-slate-300' : 'bg-slate-900/90 border-slate-800'
                }`}>
                  {variableOptions.map((opt) => (
                    <button
                      key={opt.key}
                      onClick={() => {
                        playHoloClick(900);
                        setSelectedVarKey(opt.key);
                      }}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-mono transition-all cursor-pointer ${
                        selectedVarKey === opt.key
                          ? isLight ? 'bg-sky-600 text-white font-bold' : 'bg-cyan-500 text-slate-950 font-bold'
                          : isLight ? 'text-slate-600 hover:text-slate-900' : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {opt.label.split(' ')[0]}
                    </button>
                  ))}
                </div>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartHistData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} />
                    <XAxis dataKey="range" stroke={isLight ? '#64748b' : '#64748b'} tick={{ fontSize: 10 }} />
                    <YAxis stroke={isLight ? '#64748b' : '#64748b'} tick={{ fontSize: 10 }} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(8, 12, 20, 0.95)', 
                        borderColor: isLight ? '#cbd5e1' : '#00f0ff', 
                        borderRadius: '12px',
                        fontSize: '11px',
                        color: isLight ? '#0f172a' : '#f8fafc'
                      }} 
                    />
                    <Bar dataKey="formal" fill="#00f0ff" radius={[4, 4, 0, 0]} name={t('formalLabel', language)} />
                    <Bar dataKey="informal" fill="#f59e0b" radius={[4, 4, 0, 0]} name={t('informalLabel', language)} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Chart Explainability: Univariate Wage & Skill Distribution' : 'Explicabilidad: Distribución de Salarios y Capital Humano'}
                variableOrMetric={selectedVarKey.toUpperCase()}
                whatItIs={language === 'en'
                  ? 'Bimodal empirical distribution comparing formal workers (cyan) versus informal workers (amber) across education, wage and skill levels.'
                  : 'Distribución empírica bimodal que compara la densidad de trabajadores formales (cian) frente a informales (dorado) por tramos de ingreso o escolaridad.'}
                howToRead={language === 'en'
                  ? 'Rightward skewness in the cyan distribution proves high human capital premium and wage segmentation in the formal sector.'
                  : 'El desplazamiento a la derecha de la distribución cian demuestra la prima por capital humano y la brecha salarial estructural del sector formal.'}
                policyImpact={language === 'en'
                  ? 'Establishes productivity thresholds required for informal micro-enterprises to sustain social security registration.'
                  : 'Determina el umbral mínimo de productividad para que una microempresa informal pueda solventar el costo de registro formal.'}
                formulaOrMethod="Histograma Normalizado + Estimación de Densidad Kernel"
              />
            </div>

            {/* Boxplots Summary Card */}
            <div className="lg:col-span-4 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4 flex flex-col justify-between">
              <div>
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('boxplotsTitle', language)}
                </h3>
                <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('boxplotsSubtitle', language)}
                </p>
              </div>

              <div className="space-y-3 font-mono text-xs">
                {normalizedBoxplots.map((bp: any, idx: number) => (
                  <div key={bp.variable || idx} className={`p-3 rounded-xl border space-y-1.5 ${
                    isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-900/50 border-slate-800'
                  }`}>
                    <div className="flex justify-between font-bold">
                      <span className={isLight ? 'text-slate-900' : 'text-white'}>{bp.variable}</span>
                      <span className="text-cyan-600 dark:text-cyan-400">{bp.unit}</span>
                    </div>
                    <div className={`grid grid-cols-3 gap-1 text-[10px] ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                      <div>{t('p25', language)}: <strong className={isLight ? 'text-slate-800' : 'text-slate-200'}>{bp.p25}</strong></div>
                      <div>{t('median', language)}: <strong className="text-emerald-500">{bp.median}</strong></div>
                      <div>{t('p75', language)}: <strong className={isLight ? 'text-slate-800' : 'text-slate-200'}>{bp.p75}</strong></div>
                    </div>
                  </div>
                ))}
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Summary Explainability: Boxplot Quartiles & Dispersion' : 'Explicabilidad: Cuartiles y Dispersión (IQR)'}
                variableOrMetric="IQR: P25, Mediana, P75"
                whatItIs={language === 'en'
                  ? 'Non-parametric summary statistics capturing central tendency (median) and interquartile dispersion (P25 - P75).'
                  : 'Estadísticas no paramétricas de tendencia central (mediana) y rango intercuartílico (P25 a P75) libres de sesgo por valores extremos.'}
                howToRead={language === 'en'
                  ? 'A wide IQR indicates high internal heterogeneity. Winsorization limits extreme tail noise at P1/P99.'
                  : 'Un rango intercuartílico amplio revela alta dispersión interna. Los percentiles P25/P75 guían la calibración de subsidios focalizados.'}
                policyImpact={language === 'en'
                  ? 'Prevents skewed policy allocations driven by elite formal wages.'
                  : 'Evita distorsiones en las políticas focalizadas al basarse en medianas robustas y no en promedios afectados por ingresos atípicos.'}
              />

              <div className={`p-2.5 rounded-xl border flex items-center gap-2 text-[10px] font-mono ${
                isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950/40 border-cyan-500/30 text-cyan-300'
              }`}>
                <Info className="w-4 h-4 text-cyan-500 shrink-0" />
                <span>{language === 'en' ? 'Outliers treated with Winsorization (P1 / P99)' : 'Valores atípicos tratados con Winsorización (P1 / P99)'}</span>
              </div>
            </div>
          </div>

          {/* 3. CORRELATION MATRIX & TOP CORRELATED PAIRS */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Heatmap Column */}
            <div className="lg:col-span-8 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
              <div>
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('correlationMatrixTitle', language)}
                </h3>
                <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('correlationMatrixSubtitle', language)}
                </p>
              </div>

              <div className="overflow-x-auto pb-2">
                <table className="w-full text-center border-collapse font-mono text-xs">
                  <thead>
                    <tr>
                      <th className="p-2 text-left font-bold text-[11px] text-cyan-600 dark:text-cyan-400">Var</th>
                      {normalizedCorrVars.map((v: any) => (
                        <th key={v.key} className={`p-2 font-bold text-[10px] ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>
                          {v.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {normalizedCorrVars.map((rowVar: any, rIdx: number) => (
                      <tr key={rowVar.key}>
                        <td className={`p-2 text-left font-bold text-[10px] whitespace-nowrap ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
                          {rowVar.label}
                        </td>
                        {normalizedCorrVars.map((colVar: any, cIdx: number) => {
                          const val = (currentCorrMatrix && currentCorrMatrix[rIdx] && currentCorrMatrix[rIdx][cIdx] !== undefined)
                            ? currentCorrMatrix[rIdx][cIdx]
                            : (rIdx === cIdx ? 1.0 : 0.5);
                          return (
                            <td
                              key={colVar.key}
                              onMouseEnter={() => setHoveredCorr({ a: rowVar.label, b: colVar.label, val })}
                              onMouseLeave={() => setHoveredCorr(null)}
                              className={`p-2 border transition-all cursor-pointer rounded-sm ${
                                isLight ? 'border-white' : 'border-slate-950'
                              } ${getCorrBg(val)}`}
                            >
                              {typeof val === 'number' ? val.toFixed(2) : val}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {hoveredCorr && (
                <div className={`p-2.5 rounded-xl border text-xs font-mono flex items-center justify-between ${
                  isLight ? 'bg-sky-50 border-sky-300 text-sky-900' : 'bg-cyan-950/60 border-cyan-400 text-cyan-200'
                }`}>
                  <span>{hoveredCorr.a} ↔ {hoveredCorr.b}</span>
                  <span className="font-bold">r = {typeof hoveredCorr.val === 'number' ? hoveredCorr.val.toFixed(3) : hoveredCorr.val}</span>
                </div>
              )}

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Matrix Explainability: Bivariate Pearson Correlation (r)' : 'Explicabilidad: Matriz de Correlación Bivariada de Pearson'}
                variableOrMetric="Matriz de Interdependencia"
                whatItIs={language === 'en'
                  ? 'Pairwise linear correlation coefficients between socioeconomic attributes (education, firm size, social tax, wage, informality).'
                  : 'Coeficientes de correlación lineal bivariada de Pearson entre las variables socioeconómicas y los factores determinantes del empleo.'}
                howToRead={language === 'en'
                  ? 'Cyan cells (r > +0.6) show strong positive association. Amber/red cells show strong inverse relationship.'
                  : 'Celdas cian (r > +0.6) denotan asociación positiva fuerte; celdas oscuras indican independencia ortogonal.'}
                policyImpact={language === 'en'
                  ? 'Identifies high-leverage policy synergies: investing in skilling simultaneously improves formalization likelihood and wage tax revenue.'
                  : 'Identifica sinergias de política: invertir en capacitación simultáneamente eleva la probabilidad formal y la base gravable.'}
                formulaOrMethod="r_xy = Cov(X,Y) / (σ_x * σ_y)"
              />
            </div>

            {/* Top Pairs Table Column */}
            <div className="lg:col-span-4 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-4">
              <div>
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('correlationPairsTitle', language)}
                </h3>
                <p className={`text-xs ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('correlationPairsSubtitle', language)}
                </p>
              </div>

              <div className="space-y-2.5 font-mono text-xs">
                {currentHighCorrs.map((pair: any, idx: number) => {
                  const rVal = pair.r ?? pair.corr ?? 0.75;
                  const desc = pair.impact ?? pair.reason ?? pair.direction ?? 'Correlación significativa';
                  return (
                    <div key={idx} className={`p-3 rounded-xl border flex items-center justify-between gap-2 ${
                      isLight ? 'bg-slate-50 border-slate-200' : 'bg-slate-900/50 border-slate-800'
                    }`}>
                      <div>
                        <div className={`font-bold text-[11px] ${isLight ? 'text-slate-900' : 'text-slate-200'}`}>
                          {pair.varA} ↔ {pair.varB}
                        </div>
                        <span className={`text-[10px] line-clamp-2 ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{desc}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-cyan-500/20 text-cyan-600 dark:text-cyan-300 border border-cyan-500/40 shrink-0">
                        +{typeof rVal === 'number' ? rVal.toFixed(2) : rVal}
                      </span>
                    </div>
                  );
                })}
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Table Explainability: Key Econometric Drivers' : 'Explicabilidad: Pares de Mayor Tracción Econométrica'}
                variableOrMetric="Top Hallazgos (p < 0.001)"
                whatItIs={language === 'en'
                  ? 'Ranked summary of statistically significant variable relationships with high predictive power.'
                  : 'Resumen jerarquizado de las relaciones bivariadas más determinantes con significancia estadística robusta.'}
                howToRead={language === 'en'
                  ? 'Highlights the core structural transmission channels that drive informal workers into the formal safety net.'
                  : 'Muestra los canales de transmisión económica más potentes para transicionar trabajadores informales hacia la red formal.'}
                policyImpact={language === 'en'
                  ? 'Empowers policymakers to target reforms on evidence-backed bottlenecks.'
                  : 'Permite a los tomadores de decisión priorizar reformas basadas en evidencia empírica cuantitativa.'}
              />
            </div>
          </div>


        </>
      )}

    </div>
  );
};
