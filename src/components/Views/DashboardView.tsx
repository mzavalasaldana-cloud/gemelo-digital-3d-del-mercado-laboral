import React, { useMemo } from 'react';
import { 
  CountryCode, 
  UserRole, 
  ScenarioPreset, 
  PolicyParameters, 
  StructuralMetrics,
  SimulationRun,
  Language,
  AppTheme
} from '../../types';
import { COUNTRY_PROFILES, INITIAL_POLICY_STATE } from '../../data/mockData';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  CartesianGrid, 
  ReferenceLine,
  AreaChart,
  Area
} from 'recharts';
import { 
  TrendingDown, 
  TrendingUp, 
  DollarSign, 
  Sliders, 
  RotateCcw, 
  Play, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  Award,
  BarChart3,
  LineChart as LineChartIcon,
  Layers,
  Info
} from 'lucide-react';
import { playHoloClick, playPolicyWaveSound } from '../../utils/audioSynth';
import { t } from '../../utils/i18n';
import { ExplainabilityCard } from '../Common/ExplainabilityCard';

interface DashboardViewProps {
  country: CountryCode;
  scenario: ScenarioPreset;
  onSelectScenario: (s: ScenarioPreset) => void;
  policyParams: PolicyParameters;
  onChangePolicy: (params: PolicyParameters) => void;
  metrics: StructuralMetrics;
  onNavigateTo3D: () => void;
  onTriggerSimulation: () => void;
  simRuns: SimulationRun[];
  role: UserRole;
  language?: Language;
  theme?: AppTheme;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  country,
  scenario,
  onSelectScenario,
  policyParams,
  onChangePolicy,
  metrics,
  onNavigateTo3D,
  onTriggerSimulation,
  language = 'es',
  theme = 'dark',
}) => {
  const profile = COUNTRY_PROFILES[country];
  const baseInformality = profile.baseInformalityRate;
  const informalityDelta = Number((metrics.informalityRate - baseInformality).toFixed(1));
  const isReduced = informalityDelta <= 0;
  const isLight = theme === 'light';

  // 1. Time Series Projections (2015 - 2034) based on current policies
  const timeSeriesData = useMemo(() => {
    const data = [];
    // Historical 2015-2023
    const histYears = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023];
    histYears.forEach((yr, idx) => {
      // Small historical variations
      const covidBump = yr === 2020 ? 3.2 : yr === 2021 ? 2.1 : 0;
      const inf = baseInformality + (idx - 4) * 0.4 + covidBump;
      const form = Math.max(5, (100 - inf) * 0.9);
      const unemp = Number((100 - inf - form).toFixed(1));
      data.push({
        year: yr.toString(),
        informalidad: Number(inf.toFixed(1)),
        formalidad: Number(form.toFixed(1)),
        desempleo: unemp,
        tipo: t('historical', language)
      });
    });

    // 2024 (Current)
    const currentFormal = Number(((100 - metrics.informalityRate) * 0.92).toFixed(1));
    const currentUnemp = Number((100 - metrics.informalityRate - currentFormal).toFixed(1));
    data.push({
      year: '2024',
      informalidad: Number(metrics.informalityRate.toFixed(1)),
      formalidad: currentFormal,
      desempleo: currentUnemp,
      tipo: t('current', language)
    });

    // Projected 2025-2034 with policy convergence
    const targetInf = metrics.informalityRate;
    for (let yr = 2025; yr <= 2034; yr++) {
      const step = (yr - 2024) / 10;
      // Convergence towards structural policy impact
      const projectedInf = Math.max(38, targetInf - (policyParams.skillsTrainingCoverage * 0.05 * step));
      const projectedForm = (100 - projectedInf) * 0.93;
      const projectedUnemp = Number((100 - projectedInf - projectedForm).toFixed(1));
      data.push({
        year: yr.toString(),
        informalidad: Number(projectedInf.toFixed(1)),
        formalidad: Number(projectedForm.toFixed(1)),
        desempleo: projectedUnemp,
        tipo: t('projected', language)
      });
    }

    return data;
  }, [baseInformality, metrics.informalityRate, policyParams.skillsTrainingCoverage, language]);

  // 2. Bar Chart: Baseline vs Current Policy Intervention Comparison
  const comparisonData = useMemo(() => {
    const baseFormal = (100 - baseInformality) * 0.9;
    const currentFormal = (100 - metrics.informalityRate) * 0.92;
    const baseFiscalRev = ((2500 * (baseFormal / 100)) * 0.18 * 30) / 10;
    const baseDecentWork = Math.round(60 + (100 - baseInformality) * 0.3);

    const baseKey = t('baselineLabel', language);
    const interventionKey = t('interventionLabel', language);

    return [
      {
        indicador: t('informalityRate', language) + ' (%)',
        [baseKey]: Number(baseInformality.toFixed(1)),
        [interventionKey]: Number(metrics.informalityRate.toFixed(1)),
      },
      {
        indicador: (language === 'en' ? 'Formal Employment (%)' : 'Empleo Formal (%)'),
        [baseKey]: Number(baseFormal.toFixed(1)),
        [interventionKey]: Number(currentFormal.toFixed(1)),
      },
      {
        indicador: (language === 'en' ? 'Fiscal Revenue ($M)' : 'Recaudación Fiscal ($M)'),
        [baseKey]: Number(baseFiscalRev.toFixed(1)),
        [interventionKey]: Number(metrics.fiscalRevenueMillionUSD.toFixed(1)),
      },
      {
        indicador: (language === 'en' ? 'Decent Work Index' : 'Índice Empleo Decente'),
        [baseKey]: baseDecentWork,
        [interventionKey]: metrics.decentWorkIndex,
      },
    ];
  }, [baseInformality, metrics, language]);

  // 3. Sector Distribution Composition Data
  const sectorCompositionData = useMemo(() => {
    const infRate = metrics.informalityRate / 100;
    const formRate = 1 - infRate;

    return [
      { name: '2024', formalManufactura: Math.round(formRate * 35), formalServiciosTech: Math.round(formRate * 25), formalRetail: Math.round(formRate * 40), informalAmbulante: Math.round(infRate * 58), informalTalleres: Math.round(infRate * 42) },
      { name: '2026', formalManufactura: Math.round(formRate * 38), formalServiciosTech: Math.round(formRate * 28), formalRetail: Math.round(formRate * 34), informalAmbulante: Math.round(infRate * 54), informalTalleres: Math.round(infRate * 46) },
      { name: '2028', formalManufactura: Math.round(formRate * 42), formalServiciosTech: Math.round(formRate * 32), formalRetail: Math.round(formRate * 26), informalAmbulante: Math.round(infRate * 50), informalTalleres: Math.round(infRate * 50) },
      { name: '2030', formalManufactura: Math.round(formRate * 45), formalServiciosTech: Math.round(formRate * 36), formalRetail: Math.round(formRate * 19), informalAmbulante: Math.round(infRate * 46), informalTalleres: Math.round(infRate * 54) },
    ];
  }, [metrics.informalityRate]);

  // Handle slider changes
  const handleSlider = (key: keyof PolicyParameters, value: number) => {
    onChangePolicy({
      ...policyParams,
      [key]: value,
    });
  };

  const tooltipStyle = {
    backgroundColor: isLight ? 'rgba(255, 255, 255, 0.95)' : 'rgba(8, 12, 20, 0.95)',
    borderColor: isLight ? '#cbd5e1' : '#00f0ff44',
    borderRadius: '0.75rem',
    fontSize: '12px',
    color: isLight ? '#0f172a' : '#f8fafc',
    boxShadow: isLight ? '0 4px 12px rgba(0,0,0,0.08)' : '0 8px 32px rgba(0,0,0,0.5)',
  };

  return (
    <div className={`w-full h-full pt-20 pb-8 px-6 overflow-y-auto transition-colors duration-200 ${
      isLight ? 'bg-slate-100 text-slate-800' : 'bg-[#05070c] text-slate-200'
    }`}>
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Top Header & Fast Overview Bar */}
        <div className={`flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-5 ${
          isLight ? 'border-slate-300' : 'border-cyan-500/20'
        }`}>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl">{profile.flag}</span>
              <h2 className={`text-xl font-display font-bold tracking-wide ${
                isLight ? 'text-slate-900' : 'text-slate-100'
              }`}>
                {t('diagnosticDashboard', language)}: {profile.name}
              </h2>
              <span className={`text-xs px-2.5 py-0.5 rounded-full border font-mono ${
                isLight 
                  ? 'bg-sky-50 border-sky-300 text-sky-800' 
                  : 'bg-cyan-950/80 border-cyan-500/30 text-cyan-300'
              }`}>
                {t('activeLaborForce', language)}: {(((metrics?.formalWorkersCount ?? 0) + (metrics?.informalWorkersCount ?? 0))).toLocaleString()}
              </span>
            </div>
            <p className={`text-xs font-mono-hud mt-1 ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              {t('dashboardDesc', language)}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                playHoloClick(1000);
                onTriggerSimulation();
              }}
              className={`px-4 py-2 rounded-xl font-mono-hud text-xs font-semibold flex items-center gap-2 shadow-lg transition-all cursor-pointer ${
                isLight
                  ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20'
                  : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-cyan-500/20'
              }`}
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {t('runSimulationAction', language)}
            </button>

            <button
              onClick={() => {
                playHoloClick(1100);
                onNavigateTo3D();
              }}
              className={`px-4 py-2 rounded-xl font-mono-hud text-xs flex items-center gap-2 transition-all cursor-pointer ${
                isLight
                  ? 'bg-white hover:bg-slate-50 text-sky-800 border border-slate-300 shadow-sm'
                  : 'bg-slate-900/90 hover:bg-cyan-950/80 text-cyan-300 border border-cyan-500/40 glow-cyan'
              }`}
            >
              <Layers className={`w-3.5 h-3.5 ${isLight ? 'text-sky-600' : 'text-cyan-400'}`} />
              {t('open3DTwin', language)}
            </button>
          </div>
        </div>

        {/* 4 High-Impact KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* KPI 1: Tasa de Informalidad */}
          <div className="hud-glass p-4 rounded-2xl border border-cyan-500/25 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/10 transition-all pointer-events-none" />
            <div className={`flex items-center justify-between text-xs font-mono-hud ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              <span>{t('informalityRate', language)}</span>
              {isReduced ? (
                <span className="flex items-center gap-1 text-emerald-500 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                  <TrendingDown className="w-3.5 h-3.5" />
                  {informalityDelta}%
                </span>
              ) : (
                <span className="flex items-center gap-1 text-rose-500 font-semibold bg-rose-500/10 px-2 py-0.5 rounded-md border border-rose-500/20">
                  <TrendingUp className="w-3.5 h-3.5" />
                  +{informalityDelta}%
                </span>
              )}
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className={`text-3xl font-display font-bold tracking-tight ${isLight ? 'text-slate-900' : 'text-white'}`}>
                {metrics.informalityRate.toFixed(1)}%
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                Base: {baseInformality}%
              </span>
            </div>
            <div className={`mt-3 w-full rounded-full h-1.5 overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-900'}`}>
              <div 
                className="h-full bg-gradient-to-r from-amber-500 to-rose-500 transition-all duration-500" 
                style={{ width: `${Math.min(100, metrics.informalityRate)}%` }} 
              />
            </div>
            <div className={`mt-2 text-[11px] flex justify-between font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              <span>{(metrics?.informalWorkersCount ?? 0).toLocaleString()} {t('informalWorkers', language)}</span>
            </div>
          </div>

          {/* KPI 2: Índice de Gini */}
          <div className="hud-glass p-4 rounded-2xl border border-cyan-500/25 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition-all pointer-events-none" />
            <div className={`flex items-center justify-between text-xs font-mono-hud ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              <span>{t('inequalityGini', language)}</span>
              <span className="text-xs text-indigo-500 font-mono">0 - 1</span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className={`text-3xl font-display font-bold tracking-tight ${isLight ? 'text-indigo-700' : 'text-indigo-300'}`}>
                {metrics.giniIndex.toFixed(3)}
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                Base: {profile.baseGini.toFixed(3)}
              </span>
            </div>
            <div className={`mt-3 w-full rounded-full h-1.5 overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-900'}`}>
              <div 
                className="h-full bg-indigo-500 transition-all duration-500" 
                style={{ width: `${(metrics.giniIndex / 0.6) * 100}%` }} 
              />
            </div>
            <div className={`mt-2 text-[11px] flex justify-between font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              <span>{metrics.giniIndex < 0.42 ? (language === 'en' ? 'Moderate polarization' : 'Moderada polarización') : (language === 'en' ? 'High concentration' : 'Alta concentración')}</span>
            </div>
          </div>

          {/* KPI 3: Balance Fiscal & Costo de Políticas */}
          <div className="hud-glass p-4 rounded-2xl border border-cyan-500/25 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-all pointer-events-none" />
            <div className={`flex items-center justify-between text-xs font-mono-hud ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              <span>{t('fiscalBalance', language)}</span>
              <DollarSign className="w-3.5 h-3.5 text-emerald-500" />
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className={`text-3xl font-display font-bold tracking-tight ${isLight ? 'text-emerald-700' : 'text-emerald-300'}`}>
                +${(metrics.fiscalRevenueMillionUSD - metrics.policyCostMillionUSD).toFixed(1)}M
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>USD/{language === 'en' ? 'yr' : 'año'}</span>
            </div>
            <div className={`mt-3 text-[11px] font-mono flex justify-between border-t pt-2 ${
              isLight ? 'border-slate-200 text-slate-600' : 'border-slate-800 text-slate-400'
            }`}>
              <span>{language === 'en' ? 'Revenue' : 'Recaudación'}: +${metrics.fiscalRevenueMillionUSD.toFixed(1)}M</span>
              <span className="text-rose-500">{language === 'en' ? 'Cost' : 'Costo'}: -${metrics.policyCostMillionUSD.toFixed(1)}M</span>
            </div>
          </div>

          {/* KPI 4: Índice OIT Empleo Decente */}
          <div className="hud-glass p-4 rounded-2xl border border-cyan-500/25 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/10 transition-all pointer-events-none" />
            <div className={`flex items-center justify-between text-xs font-mono-hud ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              <span>{t('iloDecentWork', language)}</span>
              <Award className="w-4 h-4 text-cyan-500" />
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className={`text-3xl font-display font-bold tracking-tight ${isLight ? 'text-sky-700' : 'text-cyan-300'}`}>
                {metrics.decentWorkIndex}
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>/ 100</span>
            </div>
            <div className={`mt-3 w-full rounded-full h-1.5 overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-900'}`}>
              <div 
                className="h-full bg-cyan-400 transition-all duration-500 glow-cyan" 
                style={{ width: `${metrics.decentWorkIndex}%` }} 
              />
            </div>
            <div className={`mt-2 text-[11px] flex justify-between font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              <span>{language === 'en' ? 'Social security, fair wage, stability' : 'Seguridad social, salario justo y estabilidad'}</span>
            </div>
          </div>
        </div>

        {/* Main 2-Column Analytical Layout: Left Integrated Policy Sidebar + Right Interactive Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* LEFT COLUMN: Integrated Policy & Scenario Sliders (4 cols) */}
          <div className="lg:col-span-4 hud-glass p-5 rounded-2xl border border-cyan-500/25 space-y-6">
            <div className={`flex items-center justify-between border-b pb-3 ${
              isLight ? 'border-slate-200' : 'border-cyan-500/20'
            }`}>
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-cyan-500" />
                <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                  {t('policyEngineTitle', language)}
                </h3>
              </div>
              <button
                onClick={() => {
                  playHoloClick(800);
                  onChangePolicy(INITIAL_POLICY_STATE);
                  onSelectScenario('BASELINE');
                }}
                className={`text-[11px] font-mono-hud flex items-center gap-1 transition-colors cursor-pointer ${
                  isLight ? 'text-slate-500 hover:text-sky-700' : 'text-slate-400 hover:text-cyan-300'
                }`}
                title="Reset"
              >
                <RotateCcw className="w-3 h-3" />
                {t('resetPolicies', language)}
              </button>
            </div>

            {/* Scenario Quick Buttons */}
            <div>
              <span className="text-[10px] font-mono-hud text-cyan-600 dark:text-cyan-400 uppercase tracking-wider block mb-2 font-bold">
                {t('scenariosTitle', language)}
              </span>
              <div className="grid grid-cols-1 gap-1.5">
                <button
                  onClick={() => onSelectScenario('BASELINE')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'BASELINE'
                      ? isLight ? 'bg-sky-50 text-sky-900 border-sky-400 shadow-sm' : 'bg-cyan-500/20 text-cyan-300 border-cyan-400 glow-cyan'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <span className="font-medium">{t('scenarioBaseline', language)}</span>
                  {scenario === 'BASELINE' && <CheckCircle2 className="w-3.5 h-3.5 text-cyan-500" />}
                </button>

                <button
                  onClick={() => onSelectScenario('SCENARIO_A_REGISTRATION')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'SCENARIO_A_REGISTRATION'
                      ? isLight ? 'bg-sky-50 text-sky-900 border-sky-400 shadow-sm' : 'bg-cyan-500/20 text-cyan-300 border-cyan-400 glow-cyan'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium">{t('scenarioRegistration', language)}</span>
                    <span className={`text-[10px] ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>-80% {language === 'en' ? 'registration cost' : 'costo formalización'}</span>
                  </div>
                  {scenario === 'SCENARIO_A_REGISTRATION' && <Sparkles className="w-3.5 h-3.5 text-cyan-500" />}
                </button>

                <button
                  onClick={() => onSelectScenario('SCENARIO_B_WORKER_SUBSIDY')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'SCENARIO_B_WORKER_SUBSIDY'
                      ? isLight ? 'bg-emerald-50 text-emerald-900 border-emerald-400 shadow-sm' : 'bg-emerald-500/20 text-emerald-300 border-emerald-400'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium">{t('scenarioSubsidy', language)}</span>
                    <span className={`text-[10px] ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>$75/mo + 60% {language === 'en' ? 'skilling' : 'capacitación'}</span>
                  </div>
                  {scenario === 'SCENARIO_B_WORKER_SUBSIDY' && <Sparkles className="w-3.5 h-3.5 text-emerald-500" />}
                </button>

                <button
                  onClick={() => onSelectScenario('SCENARIO_E_AUTOMATION_SHOCK')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'SCENARIO_E_AUTOMATION_SHOCK'
                      ? isLight ? 'bg-rose-50 text-rose-900 border-rose-400 shadow-sm' : 'bg-rose-500/20 text-rose-300 border-rose-400'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium text-rose-600 dark:text-rose-300">{t('scenarioAutomation', language)}</span>
                    <span className="text-[10px] text-rose-500/80">{language === 'en' ? 'Displacement from AI & tech' : 'Desplazamiento por automatización'}</span>
                  </div>
                  {scenario === 'SCENARIO_E_AUTOMATION_SHOCK' && <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />}
                </button>
              </div>
            </div>

            {/* Policy Tuning Sliders */}
            <div className={`space-y-4 pt-2 border-t ${isLight ? 'border-slate-200' : 'border-slate-800'}`}>
              <span className="text-[10px] font-mono-hud text-cyan-600 dark:text-cyan-400 uppercase tracking-wider block font-bold">
                {language === 'en' ? 'Fiscal & Regulatory Levers' : 'Palancas de Intervención Fiscal & Regulatoria'}
              </span>

              {/* Slider 1: Reducción Costos Registro */}
              <div>
                <div className={`flex justify-between text-xs font-mono-hud mb-1 ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
                  <span>{t('registrationCost', language)}</span>
                  <span className="text-cyan-600 dark:text-cyan-400 font-bold">{policyParams.registrationCostReduction}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={policyParams.registrationCostReduction}
                  onChange={(e) => handleSlider('registrationCostReduction', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
                <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>{t('registrationCostDesc', language)}</span>
              </div>

              {/* Slider 2: Subsidio MiPyME */}
              <div>
                <div className={`flex justify-between text-xs font-mono-hud mb-1 ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
                  <span>{t('smeSubsidy', language)}</span>
                  <span className="text-emerald-500 font-bold">${policyParams.smeSubsidyUSDMonth} USD/{language === 'en' ? 'mo' : 'mes'}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="150"
                  step="5"
                  value={policyParams.smeSubsidyUSDMonth}
                  onChange={(e) => handleSlider('smeSubsidyUSDMonth', Number(e.target.value))}
                  className="w-full accent-emerald-400 cursor-pointer"
                />
                <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>{t('smeSubsidyDesc', language)}</span>
              </div>

              {/* Slider 3: Capacitación en Habilidades */}
              <div>
                <div className={`flex justify-between text-xs font-mono-hud mb-1 ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
                  <span>{t('skillsTraining', language)}</span>
                  <span className="text-cyan-600 dark:text-cyan-400 font-bold">{policyParams.skillsTrainingCoverage}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={policyParams.skillsTrainingCoverage}
                  onChange={(e) => handleSlider('skillsTrainingCoverage', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
                <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>{t('skillsTrainingDesc', language)}</span>
              </div>

              {/* Slider 4: Impuesto Protección Social */}
              <div>
                <div className={`flex justify-between text-xs font-mono-hud mb-1 ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
                  <span>{t('socialTax', language)}</span>
                  <span className="text-indigo-500 font-bold">{policyParams.socialProtectionTax}%</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="45"
                  step="2"
                  value={policyParams.socialProtectionTax}
                  onChange={(e) => handleSlider('socialProtectionTax', Number(e.target.value))}
                  className="w-full accent-indigo-400 cursor-pointer"
                />
                <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>{t('socialTaxDesc', language)}</span>
              </div>

              {/* Slider 5: Inspección Inteligente */}
              <div>
                <div className={`flex justify-between text-xs font-mono-hud mb-1 ${isLight ? 'text-slate-800' : 'text-slate-300'}`}>
                  <span>{t('smartInspection', language)}</span>
                  <span className="text-cyan-600 dark:text-cyan-400 font-bold">{policyParams.smartInspectionCoverage}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={policyParams.smartInspectionCoverage}
                  onChange={(e) => handleSlider('smartInspectionCoverage', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
                <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>{t('smartInspectionDesc', language)}</span>
              </div>
            </div>

            {/* Policy Wave Trigger */}
            <div className="pt-2">
              <button
                onClick={() => {
                  playPolicyWaveSound();
                  onTriggerSimulation();
                }}
                className={`w-full py-2.5 rounded-xl font-mono-hud text-xs font-medium flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  isLight 
                    ? 'bg-sky-50 hover:bg-sky-100 text-sky-800 border border-sky-300' 
                    : 'bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-400/50 glow-cyan'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
                {t('triggerPolicyWave', language)}
              </button>
            </div>
          </div>

          {/* RIGHT COLUMN: Interactive Charts & Analytical Grid (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* Chart 1: Time Series Projections (2015-2034) */}
            <div className="hud-glass p-5 rounded-2xl border border-cyan-500/25">
              <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 border-b pb-3 ${
                isLight ? 'border-slate-200' : 'border-cyan-500/20'
              }`}>
                <div className="flex items-center gap-2">
                  <LineChartIcon className="w-4 h-4 text-cyan-500" />
                  <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('projectionEvolution', language)}
                  </h3>
                </div>
                <span className={`text-[11px] font-mono-hud px-2.5 py-1 rounded-lg border ${
                  isLight ? 'bg-slate-100 text-slate-600 border-slate-200' : 'bg-slate-900/60 text-slate-400 border-slate-800'
                }`}>
                  {language === 'en' ? 'Dashed: Policy Convergence (2024+)' : 'Línea discontinua: Convergencia de Política (2024+)'}
                </span>
              </div>

              <div className="w-full h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={timeSeriesData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} opacity={0.6} />
                    <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} unit="%" domain={[0, 100]} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace', paddingTop: '10px' }} />
                    <ReferenceLine x="2024" stroke="#00f0ff" strokeDasharray="4 4" label={{ value: (language === 'en' ? 'Current (2024)' : 'Actual (2024)'), fill: '#00f0ff', fontSize: 11 }} />
                    <Line 
                      type="monotone" 
                      dataKey="informalidad" 
                      name={t('informalLabel', language) + ' %'} 
                      stroke="#f59e0b" 
                      strokeWidth={2.5} 
                      dot={{ r: 3, fill: '#f59e0b' }} 
                      activeDot={{ r: 6, stroke: '#ffffff' }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="formalidad" 
                      name={t('formalLabel', language) + ' %'} 
                      stroke="#00f0ff" 
                      strokeWidth={2.5} 
                      dot={{ r: 3, fill: '#00f0ff' }} 
                      activeDot={{ r: 6, stroke: '#ffffff' }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="desempleo" 
                      name={t('unemploymentLabel', language) + ' %'} 
                      stroke="#94a3b8" 
                      strokeWidth={1.5} 
                      strokeDasharray="3 3" 
                      dot={false} 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className={`mt-2 text-[11px] font-mono-hud flex items-center gap-1.5 ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                <Info className="w-3 h-3 text-cyan-500" />
                <span>{language === 'en' ? `SARIMA estimation model integrated with World Bank wage elasticities for ${profile.name}.` : `Modelo estimativo SARIMA integrado con elasticidades salariales del Banco Mundial para ${profile.name}.`}</span>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Chart Explainability: Labor Market Time Series (2015-2034)' : 'Explicabilidad: Serie Temporal de Transición Laboral (2015-2034)'}
                variableOrMetric="Informalidad vs Formalidad %"
                whatItIs={language === 'en' 
                  ? 'Historical time series (2015-2023) and 10-year policy-driven econometric projection (2024-2034) of formal employment, informal employment, and unemployment rates.'
                  : 'Evolución histórica empírica (2015-2023) y proyección econométrica a 10 años (2024-2034) de las tasas de formalidad, informalidad y desempleo bajo las políticas activas.'}
                howToRead={language === 'en'
                  ? 'The solid amber curve tracks historical informality including exogenous shocks (e.g. 2020 COVID-19). The solid cyan curve represents dynamic formal employment convergence.'
                  : 'La curva dorada muestra la informalidad histórica con shocks macroeconómicos. La curva cian proyecta la tasa de formalización convergente impulsada por las palancas regulatorias y fiscales.'}
                policyImpact={language === 'en'
                  ? 'Measures long-term policy persistence and structural absorption capacity to fulfill ILO Decent Work Goal 8.3.'
                  : 'Evalúa la capacidad de absorción estructural y persistencia temporal para alcanzar la meta ODS 8.3 de formalización inclusiva.'}
                formulaOrMethod="SARIMA(p,d,q) + Elasticidad: ΔInf_t = -α*(Subsidio_t)^0.5 - β*(Capacitación_t)^0.8"
                benchmarksOrAlerts={language === 'en' ? 'Target: Achieve <45% informality by 2030' : 'Meta Crítica: Reducir la informalidad por debajo del 45% hacia el año 2030'}
              />
            </div>

            {/* Chart 2: Comparison Bar Chart (Baseline vs Current Policy) */}
            <div className="hud-glass p-5 rounded-2xl border border-cyan-500/25">
              <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 border-b pb-3 ${
                isLight ? 'border-slate-200' : 'border-cyan-500/20'
              }`}>
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-emerald-500" />
                  <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('baselineVsIntervention', language)}
                  </h3>
                </div>
                <div className="flex items-center gap-4 text-xs font-mono-hud">
                  <span className={`flex items-center gap-1.5 ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                    <span className="w-3 h-3 bg-slate-500 rounded-sm" /> {t('baselineLabel', language)}
                  </span>
                  <span className="flex items-center gap-1.5 text-cyan-600 dark:text-cyan-300">
                    <span className="w-3 h-3 bg-cyan-400 rounded-sm" /> {t('interventionLabel', language)}
                  </span>
                </div>
              </div>

              <div className="w-full h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparisonData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} opacity={0.6} />
                    <XAxis dataKey="indicador" stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Bar dataKey={t('baselineLabel', language)} fill="#64748b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey={t('interventionLabel', language)} fill="#00f0ff" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Chart Explainability: Baseline vs Policy Reform Impact' : 'Explicabilidad: Impacto Estructural Comparativo (Baseline vs Reforma)'}
                variableOrMetric="Delta Macroeconómico Neto"
                whatItIs={language === 'en'
                  ? 'Paired column comparison contrasting the inertial baseline against the simulated public policy reform package across 4 core indicators.'
                  : 'Comparativa en columnas pareadas que contrasta la inercia sin reformas frente al paquete de políticas simulado en los 4 indicadores clave.'}
                howToRead={language === 'en'
                  ? 'Gray bars represent status quo without intervention. Cyan bars depict the simulated outcome with social security incentives, registration cost cuts, and training.'
                  : 'Las barras grises reflejan el statu quo inercial; las barras cian indican el impacto directo del paquete de reformas.'}
                policyImpact={language === 'en'
                  ? 'Proves fiscal sustainability: higher formal tax collections offset expenditure in SME hiring subsidies and training programs.'
                  : 'Demuestra la sostenibilidad fiscal: el aumento en recaudación tributaria formal compensa el gasto en subsidios salariales y digitalización.'}
                formulaOrMethod="Balance Neto = Recaudación Formal Proyectada - Costo Total de Políticas"
              />
            </div>

            {/* Chart 3: Sector Distribution Area Chart */}
            <div className="hud-glass p-5 rounded-2xl border border-cyan-500/25">
              <div className={`flex items-center justify-between mb-4 border-b pb-3 ${
                isLight ? 'border-slate-200' : 'border-cyan-500/20'
              }`}>
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-indigo-500" />
                  <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('sectorCompositionTitle', language)}
                  </h3>
                </div>
                <span className={`text-xs font-mono-hud ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{language === 'en' ? 'Estimated share %' : 'Participación estimada'}</span>
              </div>

              <div className="w-full h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={sectorCompositionData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} opacity={0.6} />
                    <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
                    <Area type="monotone" dataKey="formalManufactura" name={language === 'en' ? 'Formal: Manufacturing' : 'Formal: Manufactura'} stackId="1" stroke="#00f0ff" fill="#00f0ff" fillOpacity={0.35} />
                    <Area type="monotone" dataKey="formalServiciosTech" name={language === 'en' ? 'Formal: Tech & Services' : 'Formal: Tech & Servicios'} stackId="1" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.35} />
                    <Area type="monotone" dataKey="formalRetail" name={language === 'en' ? 'Formal: Retail' : 'Formal: Comercio'} stackId="1" stroke="#818cf8" fill="#818cf8" fillOpacity={0.35} />
                    <Area type="monotone" dataKey="informalTalleres" name={language === 'en' ? 'Informal: Urban Workshops' : 'Informal: Talleres Urbanos'} stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.35} />
                    <Area type="monotone" dataKey="informalAmbulante" name={language === 'en' ? 'Informal: Street Vendors' : 'Informal: Vía Pública'} stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.35} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Chart Explainability: Sectoral Workforce Composition' : 'Explicabilidad: Composición y Reasignación Sectorial'}
                variableOrMetric="Distribución Sectorial % (2024-2030)"
                whatItIs={language === 'en'
                  ? 'Stacked area chart displaying workforce reallocation between high-productivity formal sectors (manufacturing, tech services) and informal subsistence activities.'
                  : 'Gráfico de áreas apiladas que modela la reasignación de mano de obra desde actividades informales de subsistencia hacia sectores formales de mayor productividad.'}
                howToRead={language === 'en'
                  ? 'Expanding cyan/blue areas indicate structural modernization and value-added employment growth. Contracting red/amber areas reflect informal contraction.'
                  : 'El ensanchamiento de las áreas azul y cian refleja modernización productiva; el encogimiento de las bandas roja y dorada confirma la formalización gradual.'}
                policyImpact={language === 'en'
                  ? 'Informs industrial and vocational training policies to prevent skill mismatches during economic transitions.'
                  : 'Orienta la política de formación dual y desarrollo productivo local para evitar cuellos de botella de habilidades en sectores estratégicos.'}
              />
            </div>


          </div>
        </div>

      </div>
    </div>
  );
};
