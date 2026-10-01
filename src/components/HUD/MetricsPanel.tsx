import React, { useState } from 'react';
import { 
  StructuralMetrics, 
  SimulationRun, 
  CountryCode 
} from '../../types';
import { COUNTRY_PROFILES } from '../../data/mockData';
import { 
  Activity, 
  BarChart3, 
  TrendingDown, 
  TrendingUp, 
  DollarSign, 
  History, 
  CheckCircle2, 
  AlertCircle, 
  PlayCircle,
  Percent,
  Users
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';

interface MetricsPanelProps {
  metrics: StructuralMetrics;
  country: CountryCode;
  simRuns: SimulationRun[];
  onTriggerNewSimulation: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  metrics,
  country,
  simRuns,
  onTriggerNewSimulation,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [activeTab, setActiveTab] = useState<'metrics' | 'simulations'>('metrics');
  const countryProfile = COUNTRY_PROFILES[country];

  const informalityDelta = (metrics.informalityRate - countryProfile.baseInformalityRate).toFixed(1);
  const isImproving = Number(informalityDelta) < 0;

  if (isCollapsed) {
    return (
      <div 
        onPointerDown={(e) => e.stopPropagation()}
        onWheel={(e) => e.stopPropagation()}
        className="absolute top-20 right-4 z-20 pointer-events-auto"
      >
        <button
          onClick={onToggleCollapse}
          className="hud-glass p-3 rounded-2xl border border-cyan-500/30 text-cyan-300 hover:border-cyan-400 glow-cyan transition-all flex items-center gap-2 font-mono-hud text-xs"
        >
          <Activity className="w-4 h-4 text-cyan-400" />
          <span>MÉTRICAS</span>
        </button>
      </div>
    );
  }

  return (
    <aside 
      onPointerDown={(e) => e.stopPropagation()}
      onWheel={(e) => e.stopPropagation()}
      className="absolute top-20 right-4 bottom-28 w-84 max-w-[calc(100vw-32px)] z-20 pointer-events-auto flex flex-col"
    >
      <div className="hud-glass rounded-2xl border border-cyan-500/30 p-4 flex-1 flex flex-col gap-3 shadow-2xl backdrop-blur-xl overflow-hidden">
        {/* Header & Tabs */}
        <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-400/40">
              <BarChart3 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-display font-bold text-xs tracking-wider text-slate-100 uppercase">
                Métricas Estructurales
              </h2>
              <span className="text-[10px] font-mono-hud text-cyan-400">
                INDICADORES MACRO Y EQUILIBRIO
              </span>
            </div>
          </div>

          <button
            onClick={onToggleCollapse}
            className="text-[10px] font-mono-hud px-2 py-1 rounded bg-slate-800/80 text-slate-400 hover:text-slate-200"
          >
            MIN
          </button>
        </div>

        {/* Tab switch */}
        <div className="flex rounded-xl bg-slate-900/80 p-1 border border-slate-800 text-xs font-mono-hud">
          <button
            onClick={() => {
              playHoloClick(800);
              setActiveTab('metrics');
            }}
            className={`flex-1 py-1.5 rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'metrics'
                ? 'bg-cyan-500/25 text-cyan-300 font-semibold border border-cyan-400/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            Equilibrio 3D
          </button>
          <button
            onClick={() => {
              playHoloClick(800);
              setActiveTab('simulations');
            }}
            className={`flex-1 py-1.5 rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'simulations'
                ? 'bg-cyan-500/25 text-cyan-300 font-semibold border border-cyan-400/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            Corridas ({simRuns.length})
          </button>
        </div>

        {/* Tab Content: Live Metrics */}
        {activeTab === 'metrics' ? (
          <div className="flex-1 overflow-y-auto space-y-3.5 pr-1">
            {/* Odometer 1: Tasa de Informalidad */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/20 relative overflow-hidden">
              <div className="flex items-center justify-between text-xs font-mono-hud text-slate-400 mb-1">
                <span className="flex items-center gap-1.5">
                  <Percent className="w-3.5 h-3.5 text-amber-400" />
                  Tasa de Informalidad
                </span>
                <span
                  className={`flex items-center text-[11px] font-bold px-1.5 py-0.5 rounded ${
                    isImproving
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}
                >
                  {isImproving ? <TrendingDown className="w-3 h-3 mr-0.5" /> : <TrendingUp className="w-3 h-3 mr-0.5" />}
                  {Number(informalityDelta) > 0 ? `+${informalityDelta}` : informalityDelta}%
                </span>
              </div>

              <div className="flex items-baseline gap-2">
                <span className="font-mono-hud font-extrabold text-3xl text-amber-300 tracking-tight glow-text-amber">
                  {metrics.informalityRate.toFixed(1)}%
                </span>
                <span className="text-[10px] font-mono-hud text-slate-400">
                  (Base: {countryProfile.baseInformalityRate}%)
                </span>
              </div>

              {/* Progress bar visual */}
              <div className="w-full bg-slate-800 h-2 rounded-full mt-2 overflow-hidden flex">
                <div
                  className="bg-cyan-400 h-full transition-all duration-700 glow-cyan"
                  style={{ width: `${100 - metrics.informalityRate}%` }}
                  title="Sector Formal"
                />
                <div
                  className="bg-amber-400 h-full transition-all duration-700 glow-amber"
                  style={{ width: `${metrics.informalityRate}%` }}
                  title="Sector Informal"
                />
              </div>
            </div>

            {/* Odometer 2: Índice de Gini (Desigualdad salarial) */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/20">
              <div className="flex items-center justify-between text-xs font-mono-hud text-slate-400 mb-1">
                <span>Índice de Gini Salarial</span>
                <span className="text-[10px] text-cyan-400">Brecha Formal / Informal</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="font-mono-hud font-extrabold text-2xl text-cyan-300 tracking-tight glow-text-cyan">
                  {metrics.giniIndex.toFixed(3)}
                </span>
                <span className="text-[10px] font-mono-hud text-slate-400">
                  [0 = Igualdad perfecta]
                </span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-500 h-full transition-all duration-700"
                  style={{ width: `${metrics.giniIndex * 100}%` }}
                />
              </div>
            </div>

            {/* Población por Sector (Boids volumétricos) */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/20 space-y-2">
              <div className="flex items-center justify-between text-xs font-mono-hud text-slate-300">
                <span className="flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5 text-cyan-400" />
                  Distribución de Agentes
                </span>
                <span className="text-[10px] text-slate-400">Total Boids: 2,500</span>
              </div>

              <div className="grid grid-cols-3 gap-1.5 text-center font-mono-hud text-xs">
                <div className="p-2 rounded-lg bg-cyan-950/40 border border-cyan-500/30">
                  <div className="text-[10px] text-cyan-400">Formales</div>
                  <div className="text-base font-bold text-cyan-300">
                    {metrics.formalWorkersCount}
                  </div>
                </div>
                <div className="p-2 rounded-lg bg-amber-950/40 border border-amber-500/30">
                  <div className="text-[10px] text-amber-400">Informales</div>
                  <div className="text-base font-bold text-amber-300">
                    {metrics.informalWorkersCount}
                  </div>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-700">
                  <div className="text-[10px] text-slate-400">Inactivos</div>
                  <div className="text-base font-bold text-slate-300">
                    {metrics.unemployedCount}
                  </div>
                </div>
              </div>
            </div>

            {/* Salario Promedio y Brecha */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/20 space-y-1.5">
              <div className="flex items-center justify-between text-xs font-mono-hud text-slate-300">
                <span className="flex items-center gap-1.5">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                  Salario Promedio Diario
                </span>
                <span className="text-[10px] text-slate-400">USD/día</span>
              </div>
              <div className="flex items-center justify-between font-mono-hud text-xs">
                <span className="text-cyan-400 font-semibold">
                  Formal: ${metrics.avgFormalWageUSD.toFixed(1)}
                </span>
                <span className="text-slate-500">vs</span>
                <span className="text-amber-400 font-semibold">
                  Informal: ${metrics.avgInformalWageUSD.toFixed(1)}
                </span>
              </div>
              <div className="text-[10px] font-mono-hud text-slate-400">
                Brecha: +{((metrics.avgFormalWageUSD / metrics.avgInformalWageUSD - 1) * 100).toFixed(0)}% a favor del sector formal
              </div>
            </div>

            {/* Balance Fiscal y Costo */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/20 flex items-center justify-between font-mono-hud text-xs">
              <div>
                <div className="text-[10px] text-slate-400">Recaudación Adicional</div>
                <div className="font-bold text-emerald-400">
                  +${metrics.fiscalRevenueMillionUSD.toFixed(1)}M USD
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-400">Costo Subsidios/Mes</div>
                <div className="font-bold text-rose-400">
                  -${metrics.policyCostMillionUSD.toFixed(1)}M USD
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Tab: Historial de Corridas de Simulación */
          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-mono-hud text-slate-400">
                Ejecuciones recientes del gemelo
              </span>
              <button
                onClick={onTriggerNewSimulation}
                className="text-[10px] font-mono-hud px-2 py-1 rounded bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 border border-cyan-400/40 flex items-center gap-1"
              >
                <PlayCircle className="w-3 h-3 text-cyan-400" />
                Nueva Corrida
              </button>
            </div>

            {simRuns.map((run) => (
              <div
                key={run.id}
                className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-cyan-500/30 transition-all font-mono-hud text-xs space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200 truncate max-w-[180px]">
                    {run.name}
                  </span>
                  {run.status === 'completada' && (
                    <span className="flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-950/50 px-1.5 py-0.5 rounded border border-emerald-800">
                      <CheckCircle2 className="w-3 h-3" /> OK
                    </span>
                  )}
                  {run.status === 'en_ejecucion' && (
                    <span className="flex items-center gap-1 text-[10px] text-cyan-400 bg-cyan-950/50 px-1.5 py-0.5 rounded border border-cyan-800 animate-pulse">
                      <PlayCircle className="w-3 h-3" /> RUN
                    </span>
                  )}
                  {run.status === 'error' && (
                    <span className="flex items-center gap-1 text-[10px] text-rose-400 bg-rose-950/50 px-1.5 py-0.5 rounded border border-rose-800">
                      <AlertCircle className="w-3 h-3" /> ERR
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between text-[10px] text-slate-400">
                  <span>{run.country} • {run.timestamp}</span>
                  <span
                    className={
                      run.informalityChange < 0 ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'
                    }
                  >
                    {run.informalityChange > 0 ? `+${run.informalityChange}%` : `${run.informalityChange}%`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
};
