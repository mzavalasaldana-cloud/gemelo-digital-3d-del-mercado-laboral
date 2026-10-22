import React, { useMemo, useState, useEffect } from 'react';
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
import { BACKEND_URL } from '../../services/api';
import trayectoriasData from '../../data/trayectorias_mensuales.json';
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
  const currentInf = metrics?.informalityRate ?? baseInformality;
  const informalityDelta = Number((currentInf - baseInformality).toFixed(1));
  const isReduced = informalityDelta <= 0;
  const isLight = theme === 'light';

  const [evolutionTab, setEvolutionTab] = useState<'sim' | 'hist'>('sim');

  // 1. Serie Histórica de ILOSTAT leída de la API (/api/v1/simulation/historical)
  const [historicalData, setHistoricalData] = useState<any[]>([]);

  useEffect(() => {
    let isMounted = true;
    fetch(`${BACKEND_URL}/api/v1/simulation/historical?country=${encodeURIComponent(country)}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (isMounted && Array.isArray(data) && data.length > 0) {
          setHistoricalData(data);
        }
      })
      .catch(() => {});
    return () => {
      isMounted = false;
    };
  }, [country]);

  // Fallback con metadatos exactos de ILOSTAT tal como vienen en data/ilostat_series_historicas.csv
  const historicalILOSTAT = useMemo(() => {
    if (historicalData.length > 0) return historicalData;
    const codeMap: Record<CountryCode, Array<{ year: string; anio: number; informalidad: number; mujeres: number; hombres: number; formalidad: number; fuente: string }>> = {
      KENYA: [
        { year: '2019', anio: 2019, informalidad: 86.49, mujeres: 90.19, hombres: 83.12, formalidad: 13.51, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22KEN%22%5D%7D&observations=1&limit=200)' },
      ],
      NIGERIA: [
        { year: '2022', anio: 2022, informalidad: 93.92, mujeres: 96.58, hombres: 91.52, formalidad: 6.08, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22NGA%22%5D%7D&observations=1&limit=200)' },
      ],
      INDIA: [
        { year: '2010', anio: 2010, informalidad: 88.29, mujeres: 91.49, hombres: 87.18, formalidad: 11.71, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22IND%22%5D%7D&observations=1&limit=200)' },
        { year: '2012', anio: 2012, informalidad: 87.18, mujeres: 90.11, hombres: 86.20, formalidad: 12.82, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22IND%22%5D%7D&observations=1&limit=200)' },
        { year: '2018', anio: 2018, informalidad: 88.61, mujeres: 89.93, hombres: 88.25, formalidad: 11.39, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22IND%22%5D%7D&observations=1&limit=200)' },
        { year: '2019', anio: 2019, informalidad: 88.91, mujeres: 90.86, hombres: 88.28, formalidad: 11.09, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22IND%22%5D%7D&observations=1&limit=200)' },
        { year: '2020', anio: 2020, informalidad: 90.26, mujeres: 92.35, hombres: 89.53, formalidad: 9.74, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22IND%22%5D%7D&observations=1&limit=200)' },
        { year: '2021', anio: 2021, informalidad: 89.11, mujeres: 91.59, hombres: 88.21, formalidad: 10.89, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22IND%22%5D%7D&observations=1&limit=200)' },
        { year: '2022', anio: 2022, informalidad: 89.03, mujeres: 91.32, hombres: 88.18, formalidad: 10.97, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22IND%22%5D%7D&observations=1&limit=200)' },
      ],
      BANGLADESH: [
        { year: '2010', anio: 2010, informalidad: 87.81, mujeres: 92.26, hombres: 85.91, formalidad: 12.19, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22BGD%22%5D%7D&observations=1&limit=200)' },
        { year: '2013', anio: 2013, informalidad: 89.42, mujeres: 93.73, hombres: 87.67, formalidad: 10.58, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22BGD%22%5D%7D&observations=1&limit=200)' },
        { year: '2017', anio: 2017, informalidad: 94.70, mujeres: 96.57, hombres: 93.88, formalidad: 5.30, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22BGD%22%5D%7D&observations=1&limit=200)' },
        { year: '2022', anio: 2022, informalidad: 82.00, mujeres: 93.88, hombres: 78.44, formalidad: 18.00, fuente: 'ILOSTAT SDMX / DBnomics (https://api.db.nomics.world/v22/series/ILO/EMP_NIFL_SEX_RT?dimensions=%7B%22ref_area%22%3A%5B%22BGD%22%5D%7D&observations=1&limit=200)' },
      ],
    };
    return codeMap[country] || codeMap.KENYA;
  }, [historicalData, country]);

  // 2. Trayectoria mensual simulada del modelo (meses 1 a 120 de la política)
  // Leída directamente de la API (/api/v1/simulation/trajectories) con su banda de IC al 95%
  const [apiTrajectory, setApiTrajectory] = useState<any[]>([]);

  useEffect(() => {
    let isMounted = true;
    const scClean = (scenario || 'A').toUpperCase().replace('SCENARIO_', '').split('_')[0] || 'A';
    fetch(`${BACKEND_URL}/api/v1/simulation/trajectories?country=${encodeURIComponent(country)}&scenario=${encodeURIComponent(scClean)}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (isMounted && data && Array.isArray(data.simulation) && data.simulation.length > 0) {
          setApiTrajectory(data.simulation);
        }
      })
      .catch(() => {});
    return () => {
      isMounted = false;
    };
  }, [country, scenario]);

  const simulatedTrajectory = useMemo(() => {
    if (apiTrajectory.length > 0) return apiTrajectory;
    const scClean = (scenario || 'A').toUpperCase().replace('SCENARIO_', '').split('_')[0] || 'A';
    const cClean = (country || 'KENYA').toUpperCase();
    const cData = (trayectoriasData as any)[cClean] || (trayectoriasData as any)['KENYA'];
    const scData = cData?.[scClean] || cData?.['A'] || [];
    return scData.map((item: any) => ({
      mes: item.month,
      periodo: `Mes ${item.month}`,
      informalidad: item.informality_total,
      informalidad_ci_low: item.informality_total_ci?.[0] ?? item.informality_total,
      informalidad_ci_high: item.informality_total_ci?.[1] ?? item.informality_total,
      mujeres: item.informality_female,
      mujeres_ci_low: item.informality_female_ci?.[0] ?? item.informality_female,
      mujeres_ci_high: item.informality_female_ci?.[1] ?? item.informality_female,
      hombres: item.informality_male,
      hombres_ci_low: item.informality_male_ci?.[0] ?? item.informality_male,
      hombres_ci_high: item.informality_male_ci?.[1] ?? item.informality_male,
      brecha: item.gender_gap,
      formalidad: Number((100 - item.informality_total).toFixed(2)),
      formal_firms_ratio: item.formal_firms_ratio ?? 0.05,
      annual_exit_rate: item.annual_exit_rate ?? 0.0,
      recaudacion: item.fiscal_revenue ?? 0.0,
      gini: item.gini_index ?? 0.288,
      tipo: 'Simulación ITDT (meses 1-120 de la política)',
    }));
  }, [apiTrajectory, country, scenario]);

  // Exponer para verificación de Playwright
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__dashboardTrajectory = simulatedTrajectory;
      (window as any).__itdtDebug = {
        ...((window as any).__itdtDebug || {}),
        country,
        scenario: (scenario || 'A').toUpperCase().replace('SCENARIO_', '').split('_')[0] || 'A',
        trajectoryPointsCount: simulatedTrajectory.length,
        trajectoryPoints: simulatedTrajectory,
      };
    }
  }, [simulatedTrajectory, country, scenario]);

  // 3. Bar Chart: Baseline vs Current Policy Intervention Comparison
  const comparisonData = useMemo(() => {
    const baseFormal = Number((100 - baseInformality).toFixed(2));
    const currentFormal = Number((100 - currentInf).toFixed(2));
    const baseKey = t('baselineLabel', language);
    const interventionKey = t('interventionLabel', language);

    // Cifras base del Escenario A leídas directamente del modelo ITDT
    const cClean = (country || 'KENYA').toUpperCase();
    const cData = (trayectoriasData as any)[cClean] || (trayectoriasData as any)['KENYA'];
    const aData = cData?.['A'] || [];
    const aLast = aData.length > 0 ? aData[aData.length - 1] : null;
    const baseRev = aLast ? Number(aLast.fiscal_revenue.toFixed(1)) : 1381.1;
    const baseGap = aLast ? Number(aLast.gender_gap.toFixed(2)) : 7.20;

    const currentRev = Number((metrics?.fiscalRevenueModelUnits ?? metrics?.fiscalRevenue ?? baseRev).toFixed(1));
    const currentGap = Number((metrics?.genderGap ?? baseGap).toFixed(2));

    return [
      {
        indicador: t('informalityRate', language) + ' (%)',
        [baseKey]: Number(baseInformality.toFixed(2)),
        [interventionKey]: Number(currentInf.toFixed(2)),
      },
      {
        indicador: (language === 'en' ? 'Formal Employment (%)' : 'Empleo Formal (%)'),
        [baseKey]: baseFormal,
        [interventionKey]: currentFormal,
      },
      {
        indicador: (language === 'en' ? 'Fiscal Revenue (Model Units)' : 'Recaudación Fiscal (Unidades Modelo)'),
        [baseKey]: baseRev,
        [interventionKey]: currentRev,
      },
      {
        indicador: (language === 'en' ? 'Gender Gap (pp)' : 'Brecha de Género (pp)'),
        [baseKey]: baseGap,
        [interventionKey]: currentGap,
      },
    ];
  }, [baseInformality, currentInf, metrics, country, language]);

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
                {language === 'en'
                  ? `Visualized agents: ${(((metrics?.formalWorkersCount ?? 0) + (metrics?.informalWorkersCount ?? 0))).toLocaleString()} (representation of N_W = 6,000 from model)`
                  : `Agentes visualizados: ${(((metrics?.formalWorkersCount ?? 0) + (metrics?.informalWorkersCount ?? 0))).toLocaleString()} (representación de N_W = 6 000 del modelo)`}
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
                {(metrics?.informalityRate ?? baseInformality).toFixed(1)}%
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                Base: {baseInformality}%
              </span>
            </div>
            <div className={`mt-3 w-full rounded-full h-1.5 overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-900'}`}>
              <div 
                className="h-full bg-gradient-to-r from-amber-500 to-rose-500 transition-all duration-500" 
                style={{ width: `${Math.min(100, metrics?.informalityRate ?? baseInformality)}%` }} 
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
                {(metrics?.giniIndex ?? profile.baseGini).toFixed(3)}
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                Base: {profile.baseGini.toFixed(3)}
              </span>
            </div>
            <div className={`mt-3 w-full rounded-full h-1.5 overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-900'}`}>
              <div 
                className="h-full bg-indigo-500 transition-all duration-500" 
                style={{ width: `${((metrics?.giniIndex ?? profile.baseGini) / 0.6) * 100}%` }} 
              />
            </div>
            <div className={`mt-2 text-[11px] flex justify-between font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
              <span>{(metrics?.giniIndex ?? profile.baseGini) < 0.42 ? (language === 'en' ? 'Moderate polarization' : 'Moderada polarización') : (language === 'en' ? 'High concentration' : 'Alta concentración')}</span>
            </div>
          </div>

          {/* KPI 3: Recaudación Fiscal (Unidades del modelo) */}
          <div className="hud-glass p-4 rounded-2xl border border-cyan-500/25 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-all pointer-events-none" />
            <div className={`flex items-center justify-between text-xs font-mono-hud ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              <span>{language === 'en' ? 'Fiscal Revenue' : 'Recaudación Fiscal'}</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-mono">
                {language === 'en' ? 'Model Units' : 'Unidades del Modelo'}
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className={`text-3xl font-display font-bold tracking-tight ${isLight ? 'text-emerald-700' : 'text-emerald-300'}`}>
                +{(metrics?.fiscalRevenueModelUnits ?? metrics?.fiscalRevenue ?? 0).toFixed(1)}
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {language === 'en' ? 'u.m. / yr' : 'u.m. / año'}
              </span>
            </div>
            <div className={`mt-3 text-[11px] font-mono flex justify-between border-t pt-2 ${
              isLight ? 'border-slate-200 text-slate-600' : 'border-slate-800 text-slate-400'
            }`}>
              <span>{language === 'en' ? 'Corporate' : 'Sociedades'}: +{(metrics?.corporateTaxRevenueModelUnits ?? metrics?.corporateTaxRevenue ?? 0).toFixed(1)}</span>
              <span className="text-cyan-400">{language === 'en' ? 'Labor' : 'Seg. Social'}: +{(metrics?.laborContributionsModelUnits ?? metrics?.laborContributionsRevenue ?? 0).toFixed(1)}</span>
            </div>
          </div>

          {/* KPI 4: Brecha de Género en Informalidad */}
          <div className="hud-glass p-4 rounded-2xl border border-cyan-500/25 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/10 transition-all pointer-events-none" />
            <div className={`flex items-center justify-between text-xs font-mono-hud ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              <span>{language === 'en' ? 'Gender Gap' : 'Brecha de Género'}</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 font-mono">
                F − M (pp)
              </span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className={`text-3xl font-display font-bold tracking-tight ${isLight ? 'text-sky-700' : 'text-cyan-300'}`}>
                {metrics?.genderGap !== undefined ? (metrics.genderGap >= 0 ? `+${metrics.genderGap.toFixed(2)}` : metrics.genderGap.toFixed(2)) : '+1.63'}
              </span>
              <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>p.p.</span>
            </div>
            <div className={`mt-3 text-[11px] font-mono flex justify-between border-t pt-2 ${
              isLight ? 'border-slate-200 text-slate-600' : 'border-slate-800 text-slate-400'
            }`}>
              <span>{language === 'en' ? 'Female' : 'Mujeres'}: {(metrics?.informalityFemale ?? 87.3).toFixed(1)}%</span>
              <span className="text-slate-400">{language === 'en' ? 'Male' : 'Hombres'}: {(metrics?.informalityMale ?? 85.6).toFixed(1)}%</span>
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
                  onClick={() => onSelectScenario('A')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'A' || scenario === 'BASELINE'
                      ? isLight ? 'bg-sky-50 text-sky-900 border-sky-400 shadow-sm' : 'bg-cyan-500/20 text-cyan-300 border-cyan-400 glow-cyan'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium">Escenario A: Status Quo</span>
                    <span className={`text-[10px] ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>Inercial con cobertura digital básica (+0.15 p.p./mes)</span>
                  </div>
                  {(scenario === 'A' || scenario === 'BASELINE') && <CheckCircle2 className="w-3.5 h-3.5 text-cyan-500" />}
                </button>

                <button
                  onClick={() => onSelectScenario('B1')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'B1'
                      ? isLight ? 'bg-sky-50 text-sky-900 border-sky-400 shadow-sm' : 'bg-cyan-500/20 text-cyan-300 border-cyan-400 glow-cyan'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium">Escenario B1: GovTech Moderado</span>
                    <span className={`text-[10px] ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>Auditoría digital κ×2.5 + facturación electrónica</span>
                  </div>
                  {scenario === 'B1' && <Sparkles className="w-3.5 h-3.5 text-cyan-500" />}
                </button>

                <button
                  onClick={() => onSelectScenario('B2')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'B2'
                      ? isLight ? 'bg-rose-50 text-rose-900 border-rose-400 shadow-sm' : 'bg-rose-500/20 text-rose-300 border-rose-400'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium text-rose-600 dark:text-rose-300">Escenario B2: GovTech Intensivo</span>
                    <span className="text-[10px] text-rose-500/80">GovTech + triplicación de sanciones (μ0, μ1 × 3)</span>
                  </div>
                  {scenario === 'B2' && <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />}
                </button>

                <button
                  onClick={() => onSelectScenario('C')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'C'
                      ? isLight ? 'bg-purple-50 text-purple-900 border-purple-400 shadow-sm' : 'bg-purple-500/20 text-purple-300 border-purple-400'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium text-purple-600 dark:text-purple-300">Escenario C: Red de Cuidados</span>
                    <span className="text-[10px] text-purple-500/80">Reducción 60% cuidado infantil no remunerado en mujeres</span>
                  </div>
                  {scenario === 'C' && <Sparkles className="w-3.5 h-3.5 text-purple-500" />}
                </button>

                <button
                  onClick={() => onSelectScenario('D')}
                  className={`p-2.5 rounded-xl text-left text-xs font-mono-hud transition-all border flex items-center justify-between cursor-pointer ${
                    scenario === 'D'
                      ? isLight ? 'bg-emerald-50 text-emerald-900 border-emerald-400 shadow-sm' : 'bg-emerald-500/20 text-emerald-300 border-emerald-400'
                      : isLight ? 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-medium text-emerald-600 dark:text-emerald-300">Escenario D: Integrado</span>
                    <span className="text-[10px] text-emerald-500/80">B2 + C + subsidio 80% DCC (L≤10) + protección social</span>
                  </div>
                  {scenario === 'D' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />}
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
                  <span className="text-emerald-500 font-bold">{policyParams.smeSubsidyUSDMonth} u.m./{language === 'en' ? 'mo' : 'mes'}</span>
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
            
            {/* Chart 1: Trayectoria de Simulación ITDT & Validación Histórica ILOSTAT */}
            <div className="hud-glass p-5 rounded-2xl border border-cyan-500/25">
              <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 border-b pb-3 ${
                isLight ? 'border-slate-200' : 'border-cyan-500/20'
              }`}>
                <div className="flex items-center gap-2">
                  <LineChartIcon className="w-4 h-4 text-cyan-500" />
                  <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {evolutionTab === 'sim' 
                      ? (language === 'en' ? 'ITDT Simulation (Policy Months 1-120)' : 'Simulación ITDT (meses 1-120 de la política)')
                      : (language === 'en' ? 'Official ILOSTAT Historical Series (EMP_NIFL_SEX_RT)' : 'Serie Histórica Oficial ILOSTAT (EMP_NIFL_SEX_RT)')}
                  </h3>
                </div>
                <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] font-mono">
                  <button
                    onClick={() => setEvolutionTab('sim')}
                    className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                      evolutionTab === 'sim'
                        ? 'bg-cyan-500 text-slate-950 font-bold'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {language === 'en' ? 'ITDT Simulation (Months 0-120)' : 'Simulación ITDT (Meses 0-120)'}
                  </button>
                  <button
                    onClick={() => setEvolutionTab('hist')}
                    className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                      evolutionTab === 'hist'
                        ? 'bg-cyan-500 text-slate-950 font-bold'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {language === 'en' ? 'ILOSTAT by Gender' : 'Histórico ILOSTAT por Sexo'}
                  </button>
                </div>
              </div>

              <div className="w-full h-72">
                <ResponsiveContainer width="100%" height="100%">
                  {evolutionTab === 'sim' ? (
                    <LineChart data={simulatedTrajectory} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} opacity={0.6} />
                      <XAxis 
                        dataKey="periodo" 
                        stroke="#64748b" 
                        tick={{ fontSize: 10, fill: '#64748b' }} 
                        label={{ 
                          value: language === 'en' ? 'Policy month' : 'Mes de la política', 
                          position: 'insideBottom', 
                          offset: -10,
                          fill: '#64748b',
                          fontSize: 11
                        }}
                      />
                      <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} unit="%" domain={[0, 100]} />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace', paddingTop: '15px' }} />
                      <Area 
                        type="monotone" 
                        dataKey="informalidad_ci_high" 
                        stroke="none" 
                        fill="#f59e0b" 
                        fillOpacity={0.15} 
                        name="IC 95% Informalidad" 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="informalidad" 
                        name={t('informalLabel', language) + ' Total %'} 
                        stroke="#f59e0b" 
                        strokeWidth={2.5} 
                        dot={false} 
                        activeDot={{ r: 5, stroke: '#ffffff' }} 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="formalidad" 
                        name={t('formalLabel', language) + ' %'} 
                        stroke="#00f0ff" 
                        strokeWidth={2.5} 
                        dot={false} 
                        activeDot={{ r: 5, stroke: '#ffffff' }} 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="mujeres" 
                        name={language === 'en' ? 'Women (Informality %)' : 'Mujeres (Informalidad %)'} 
                        stroke="#ec4899" 
                        strokeWidth={1.8} 
                        strokeDasharray="4 4"
                        dot={false} 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="hombres" 
                        name={language === 'en' ? 'Men (Informality %)' : 'Hombres (Informalidad %)'} 
                        stroke="#38bdf8" 
                        strokeWidth={1.8} 
                        strokeDasharray="4 4"
                        dot={false} 
                      />
                    </LineChart>
                  ) : (
                    <LineChart data={historicalILOSTAT} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={isLight ? '#e2e8f0' : '#1e293b'} opacity={0.6} />
                      <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} />
                      <YAxis stroke="#64748b" tick={{ fontSize: 11, fill: '#64748b' }} unit="%" domain={[70, 100]} />
                      <Tooltip contentStyle={tooltipStyle} />
                      <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace', paddingTop: '10px' }} />
                      <Line 
                        type="monotone" 
                        dataKey="informalidad" 
                        name="Total ILOSTAT %" 
                        stroke="#f59e0b" 
                        strokeWidth={2.5} 
                        connectNulls={false}
                        dot={{ r: 5, fill: '#f59e0b' }} 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="mujeres" 
                        name={language === 'en' ? 'Women ILOSTAT %' : 'Mujeres ILOSTAT %'} 
                        stroke="#ec4899" 
                        strokeWidth={2.0} 
                        connectNulls={false}
                        dot={{ r: 4, fill: '#ec4899' }} 
                      />
                      <Line 
                        type="monotone" 
                        dataKey="hombres" 
                        name={language === 'en' ? 'Men ILOSTAT %' : 'Hombres ILOSTAT %'} 
                        stroke="#38bdf8" 
                        strokeWidth={2.0} 
                        connectNulls={false}
                        dot={{ r: 4, fill: '#38bdf8' }} 
                      />
                    </LineChart>
                  )}
                </ResponsiveContainer>
              </div>

              <div className={`mt-2 text-[11px] font-mono-hud flex items-center gap-1.5 ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                <Info className="w-3 h-3 text-cyan-500" />
                <span>
                  {evolutionTab === 'sim'
                    ? (language === 'en' 
                        ? `ITDT Simulation (Policy Months 1-120): Scenario ${scenario} monthly trajectory for ${profile.name}. Model contains zero unemployment.`
                        : `Simulación ITDT (meses 1-120 de la política): trayectoria mensual del Escenario ${scenario} para ${profile.name}. El modelo no contempla desempleo.`)
                    : (language === 'en'
                        ? 'Official historical empirical data: ILOSTAT EMP_NIFL_SEX_RT downloaded via SDMX (data/ilostat_series_historicas.csv). Observed values only, without interpolation.'
                        : 'Fuente histórica oficial: ILOSTAT EMP_NIFL_SEX_RT descargado vía SDMX (data/ilostat_series_historicas.csv). Solo valores reales observados, sin interpolar.')}
                </span>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Chart Explainability: ITDT Policy Trajectory' : 'Explicabilidad: Trayectoria de Política ITDT'}
                variableOrMetric="Informalidad Total y Brecha de Género"
                whatItIs={language === 'en' 
                  ? 'Monthly trajectory (months 0 to 120 of the policy intervention) simulated by the ITDT multi-agent model calibrated on official ILOSTAT microdata and aggregates.'
                  : 'Trayectoria mensual (meses 0 a 120 de la política) generada por el modelo multi-agente ITDT calibrado sobre microdatos y agregados de ILOSTAT.'}
                howToRead={language === 'en'
                  ? 'Amber curve tracks total informality. Pink and sky dashed lines illustrate gender gaps. Cyan curve shows formal employment absorption. The model has no unemployment.'
                  : 'La curva dorada muestra la informalidad total. Las líneas discontinua rosa y celeste reflejan la brecha de género (mujeres vs hombres). El modelo no contempla desempleo.'}
                policyImpact={language === 'en'
                  ? 'Captures structural transitions, compliance elasticity, and female care penalty alleviation towards ILO Decent Work targets.'
                  : 'Evalúa la absorción formal y el cierre de brechas de género a lo largo de 120 meses bajo los parámetros del escenario.'}
                formulaOrMethod="Simulación multi-agente ITDT (N_W=6000, N_F=600) calibrada por SMM sobre microdatos y agregados de ILOSTAT (EMP_NIFL_SEX_RT). Sin desempleo."
                benchmarksOrAlerts={language === 'en' ? 'Calibrated outputs strictly verified against outputs/policy_experiments_results.json' : 'Salidas calibradas verificadas contra outputs/policy_experiments_results.json'}
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
