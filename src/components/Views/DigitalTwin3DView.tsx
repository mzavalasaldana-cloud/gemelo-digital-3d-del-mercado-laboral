import React, { useState } from 'react';
import { 
  CountryCode, 
  UserRole, 
  ScenarioPreset, 
  PolicyParameters, 
  WorkerAgent, 
  StructuralFirm, 
  StructuralMetrics,
  Language,
  AppTheme
} from '../../types';
import { DigitalTwinScene } from '../DigitalTwin3D/DigitalTwinScene';
import { AgentInspectorModal } from '../HUD/AgentInspectorModal';
import { formatSimMonth } from '../../utils/timeSimulation';
import { t } from '../../utils/i18n';
import { 
  Play, 
  Pause, 
  Sparkles, 
  Eye, 
  Camera, 
  Sliders, 
  ChevronRight, 
  ChevronDown, 
  Layers, 
  Radio, 
  Zap,
  Info
} from 'lucide-react';
import { playHoloClick, playPolicyWaveSound } from '../../utils/audioSynth';

interface DigitalTwin3DViewProps {
  country: CountryCode;
  month: number;
  onMonthChange: (m: number) => void;
  year?: number;
  onYearChange?: (y: number) => void;
  scenario: ScenarioPreset;
  onSelectScenario: (s: ScenarioPreset) => void;
  policyParams: PolicyParameters;
  onChangePolicy: (p: PolicyParameters) => void;
  workers: WorkerAgent[];
  firms: StructuralFirm[];
  selectedWorker: WorkerAgent | null;
  selectedFirm: StructuralFirm | null;
  onSelectWorker: (w: WorkerAgent | null) => void;
  onSelectFirm: (f: StructuralFirm | null) => void;
  metrics: StructuralMetrics;
  policyWaveTrigger: number;
  onTriggerPolicyWave: () => void;
  isPlayingTimeline: boolean;
  onTogglePlay: () => void;
  playbackSpeed: number;
  onChangeSpeed: (s: number) => void;
  language?: Language;
  theme?: AppTheme;
}

export const DigitalTwin3DView: React.FC<DigitalTwin3DViewProps> = ({
  country,
  month,
  onMonthChange,
  year,
  onYearChange,
  scenario,
  onSelectScenario,
  policyParams,
  onChangePolicy,
  workers,
  firms,
  selectedWorker,
  selectedFirm,
  onSelectWorker,
  onSelectFirm,
  metrics,
  policyWaveTrigger,
  onTriggerPolicyWave,
  isPlayingTimeline,
  onTogglePlay,
  playbackSpeed,
  onChangeSpeed,
  language = 'es',
  theme = 'dark',
}) => {
  const [deepZoomLevel, setDeepZoomLevel] = useState<'satellite' | 'isometric' | 'street'>('isometric');
  const [showQuickPolicyDrawer, setShowQuickPolicyDrawer] = useState(false);
  const [showLegend, setShowLegend] = useState(false);
  const isLight = theme === 'light';

  return (
    <div className={`relative w-full h-full overflow-hidden select-none transition-colors duration-200 ${
      isLight ? 'bg-slate-100 text-slate-800' : 'bg-[#04060b] text-slate-100'
    }`}>
      {/* 100% Screen Dedicated Canvas 3D */}
      <div className="absolute inset-0 z-0">
        <DigitalTwinScene
          country={country}
          month={month}
          year={year}
          scenario={scenario}
          policyParams={policyParams}
          workers={workers}
          firms={firms}
          selectedWorker={selectedWorker}
          selectedFirm={selectedFirm}
          onSelectWorker={onSelectWorker}
          onSelectFirm={onSelectFirm}
          deepZoomLevel={deepZoomLevel}
          setDeepZoomLevel={setDeepZoomLevel}
          isSimulatingTimeline={isPlayingTimeline}
          policyWaveTrigger={policyWaveTrigger}
          theme={theme}
        />
      </div>

      {/* Floating Minimal HUD: Top-Right Live Metrics Pill */}
      <div className="absolute top-20 right-6 z-20 pointer-events-auto flex items-center gap-2">
        <div className="hud-glass px-4 py-2 rounded-2xl border border-cyan-500/30 flex items-center gap-4 text-xs font-mono-hud shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-slate-400">Informalidad:</span>
            <span className="text-cyan-300 font-bold text-sm">{metrics.informalityRate.toFixed(1)}%</span>
          </div>
          <div className="h-4 w-px bg-slate-700" />
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Gini:</span>
            <span className="text-indigo-300 font-bold text-sm">{metrics.giniIndex.toFixed(3)}</span>
          </div>
          <div className="h-4 w-px bg-slate-700" />
          <div className="flex items-center gap-2">
            <span className="text-slate-400">OIT Decente:</span>
            <span className="text-emerald-400 font-bold text-sm">{metrics.decentWorkIndex}/100</span>
          </div>
        </div>

        {/* Legend Toggle Button */}
        <button
          onClick={() => setShowLegend(!showLegend)}
          className={`p-2.5 rounded-xl border transition-all text-xs font-mono-hud flex items-center gap-1.5 cursor-pointer backdrop-blur-md ${
            showLegend 
              ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400' 
              : 'hud-glass text-slate-300 border-cyan-500/30 hover:border-cyan-400'
          }`}
          title="Leyenda de entidades espaciales"
        >
          <Info className="w-4 h-4 text-cyan-400" />
          <span className="hidden sm:inline">Leyenda</span>
        </button>
      </div>

      {/* Spatial Entity Legend Popup */}
      {showLegend && (
        <div className="absolute top-32 right-6 z-20 hud-glass-solid p-3.5 rounded-2xl border border-cyan-500/30 w-72 text-xs font-mono-hud shadow-2xl backdrop-blur-xl">
          <div className="text-cyan-400 font-bold uppercase tracking-wider mb-2.5 text-[10px]">
            Simbología Holográfica 3D
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2.5">
              <div className="w-3.5 h-3.5 rounded-sm bg-cyan-400 glow-cyan border border-cyan-300" />
              <div>
                <span className="text-slate-200 font-semibold block">Prisma de Cristal Formal</span>
                <span className="text-[10px] text-slate-400">Empresas registradas con filamentos láser</span>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-3.5 h-3.5 rounded-full bg-amber-500 border border-amber-300" />
              <div>
                <span className="text-slate-200 font-semibold block">Enjambre de Micelio Informal</span>
                <span className="text-[10px] text-slate-400">Unidades orgánicas con zarcillos en valles</span>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-2.5 h-2.5 rounded-full bg-cyan-300" />
              <div>
                <span className="text-slate-200 font-semibold block">Boids Formales (Órbita Rectilínea)</span>
                <span className="text-[10px] text-slate-400">Trabajadores con contrato y alta productividad</span>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <div>
                <span className="text-slate-200 font-semibold block">Boids Informales (Movimiento Browniano)</span>
                <span className="text-[10px] text-slate-400">Trabajadores ambulantes o de taller no regulado</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Floating Minimal HUD: Top-Left Quick Scenario Chips & Policy Drawer */}
      <div className="absolute top-20 left-6 z-20 pointer-events-auto space-y-2">
        <div className="hud-glass p-1.5 rounded-2xl border border-cyan-500/30 flex items-center gap-1.5 shadow-xl backdrop-blur-md">
          <button
            onClick={() => onSelectScenario('BASELINE')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono-hud transition-all cursor-pointer ${
              scenario === 'BASELINE'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/50 glow-cyan'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Línea Base
          </button>
          <button
            onClick={() => onSelectScenario('SCENARIO_A_REGISTRATION')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono-hud transition-all cursor-pointer ${
              scenario === 'SCENARIO_A_REGISTRATION'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/50 glow-cyan'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            A: Formalización
          </button>
          <button
            onClick={() => onSelectScenario('SCENARIO_B_WORKER_SUBSIDY')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono-hud transition-all cursor-pointer ${
              scenario === 'SCENARIO_B_WORKER_SUBSIDY'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            B: Subsidio MiPyME
          </button>
          <button
            onClick={() => onSelectScenario('SCENARIO_E_AUTOMATION_SHOCK')}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono-hud transition-all cursor-pointer ${
              scenario === 'SCENARIO_E_AUTOMATION_SHOCK'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-400/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            E: Choque Tech
          </button>

          <div className="h-4 w-px bg-slate-700 mx-1" />

          {/* Toggle Quick Sliders */}
          <button
            onClick={() => {
              playHoloClick(900);
              setShowQuickPolicyDrawer(!showQuickPolicyDrawer);
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-mono-hud flex items-center gap-1.5 transition-all cursor-pointer ${
              showQuickPolicyDrawer
                ? 'bg-cyan-500 text-slate-950 font-bold'
                : 'text-cyan-300 hover:bg-cyan-950/40'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Ajustes</span>
            <ChevronDown className={`w-3 h-3 transition-transform ${showQuickPolicyDrawer ? 'rotate-180' : ''}`} />
          </button>

          {/* Policy Wave Pulse Button */}
          <button
            onClick={() => {
              playPolicyWaveSound();
              onTriggerPolicyWave();
            }}
            className="p-1.5 rounded-xl text-cyan-300 hover:bg-cyan-500/20 border border-cyan-500/30 transition-all cursor-pointer"
            title="Emitir Onda de Política"
          >
            <Sparkles className="w-4 h-4 text-cyan-400" />
          </button>
        </div>

        {/* Minimal Semi-Transparent Quick Policy Slider Drawer */}
        {showQuickPolicyDrawer && (
          <div className="hud-glass-solid p-4 rounded-2xl border border-cyan-500/40 w-80 text-xs font-mono-hud space-y-3.5 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2">
              <span className="text-[10px] text-cyan-400 uppercase tracking-wider font-bold">
                Controles Dinámicos Rápidos
              </span>
              <span className="text-[10px] text-slate-400">Impacto en tiempo real</span>
            </div>

            {/* Reducción Costos Registro */}
            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Reducción Costos Registro</span>
                <span className="text-cyan-400 font-bold">{policyParams.registrationCostReduction}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={policyParams.registrationCostReduction}
                onChange={(e) => onChangePolicy({ ...policyParams, registrationCostReduction: Number(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Subsidio MiPyME */}
            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Subsidio Salarial MiPyME</span>
                <span className="text-emerald-400 font-bold">${policyParams.smeSubsidyUSDMonth} USD/mes</span>
              </div>
              <input
                type="range"
                min="0"
                max="150"
                step="5"
                value={policyParams.smeSubsidyUSDMonth}
                onChange={(e) => onChangePolicy({ ...policyParams, smeSubsidyUSDMonth: Number(e.target.value) })}
                className="w-full accent-emerald-400 cursor-pointer"
              />
            </div>

            {/* Capacitación */}
            <div>
              <div className="flex justify-between text-slate-300 mb-1">
                <span>Capacitación en Habilidades</span>
                <span className="text-cyan-400 font-bold">{policyParams.skillsTrainingCoverage}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={policyParams.skillsTrainingCoverage}
                onChange={(e) => onChangePolicy({ ...policyParams, skillsTrainingCoverage: Number(e.target.value) })}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            <button
              onClick={() => {
                playPolicyWaveSound();
                onTriggerPolicyWave();
              }}
              className="w-full py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-400 font-mono-hud text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer glow-cyan"
            >
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              Propagar Choque Estructural
            </button>
          </div>
        )}
      </div>

      {/* Floating Bottom Center: Minimalist Timeline Bar with Scrubbing */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 pointer-events-auto max-w-[95vw]">
        <div className={`px-4 sm:px-5 py-3 rounded-2xl border flex items-center gap-3 sm:gap-4 text-xs font-mono-hud shadow-2xl backdrop-blur-md ${
          isLight 
            ? 'bg-white/95 border-slate-300 text-slate-800 shadow-slate-900/15' 
            : 'hud-glass border-cyan-500/30 text-slate-200'
        }`}>
          {/* Play/Pause Button */}
          <button
            onClick={() => {
              playHoloClick(1000);
              onTogglePlay();
            }}
            className={`p-2 rounded-xl transition-all cursor-pointer ${
              isPlayingTimeline 
                ? 'bg-amber-500 text-slate-950 glow-amber' 
                : isLight
                  ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-600/30'
                  : 'bg-cyan-500 text-slate-950 glow-cyan'
            }`}
            title={isPlayingTimeline ? (language === 'en' ? 'Pause' : 'Pausar') : (language === 'en' ? 'Play' : 'Reproducir')}
          >
            {isPlayingTimeline ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
          </button>

          {/* Current Month & Year Badge */}
          <div className="flex flex-col min-w-[150px]">
            <span className={`text-[10px] uppercase font-semibold tracking-wider ${
              isLight ? 'text-sky-700' : 'text-cyan-400/80'
            }`}>
              {t('timelineHorizon', (language || 'es') as Language)}
            </span>
            <span className={`text-sm sm:text-base font-display font-bold ${
              isLight ? 'text-slate-900' : 'text-cyan-300'
            }`}>
              {formatSimMonth(month, (language || 'es') as 'es' | 'en')}
            </span>
          </div>

          {/* Monthly Timeline Scrubber (120 continuous monthly steps) */}
          <div className="w-48 sm:w-80 flex flex-col gap-1">
            <input
              type="range"
              min="0"
              max="120"
              step="1"
              value={month}
              onChange={(e) => onMonthChange(Number(e.target.value))}
              className={`w-full cursor-pointer h-2 rounded-lg appearance-none ${
                isLight ? 'accent-sky-600 bg-slate-200' : 'accent-cyan-400 bg-slate-800'
              }`}
            />
            <div className="flex justify-between text-[9px] text-slate-400 font-mono">
              <span>{language === 'en' ? 'M0 (Jan 24)' : 'Mes 0 (Ene 2024)'}</span>
              <span>{language === 'en' ? 'M60 (2029)' : 'Mes 60 (2029)'}</span>
              <span>{language === 'en' ? 'M120 (Dec 33)' : 'Mes 120 (Dic 2033)'}</span>
            </div>
          </div>

          <div className={`h-6 w-px ${isLight ? 'bg-slate-300' : 'bg-slate-700'}`} />

          {/* Speed Selector */}
          <div className={`flex items-center gap-1 p-1 rounded-xl border ${
            isLight ? 'bg-slate-100 border-slate-300' : 'bg-slate-900/60 border-slate-800'
          }`}>
            {[1, 2, 4].map((spd) => (
              <button
                key={spd}
                onClick={() => {
                  playHoloClick(850);
                  onChangeSpeed(spd);
                }}
                className={`px-2 py-1 rounded-lg text-[10px] font-mono transition-all cursor-pointer ${
                  playbackSpeed === spd 
                    ? isLight
                      ? 'bg-sky-600 text-white font-bold'
                      : 'bg-cyan-500 text-slate-950 font-bold' 
                    : isLight
                      ? 'text-slate-600 hover:text-slate-900'
                      : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>

          <div className={`h-6 w-px hidden sm:block ${isLight ? 'bg-slate-300' : 'bg-slate-700'}`} />

          {/* Camera Deep Zoom Controls */}
          <div className="hidden sm:flex items-center gap-1">
            <button
              onClick={() => {
                playHoloClick(750);
                setDeepZoomLevel('satellite');
              }}
              className={`px-2.5 py-1 rounded-xl text-[11px] font-mono transition-all cursor-pointer ${
                deepZoomLevel === 'satellite'
                  ? isLight
                    ? 'bg-sky-100 text-sky-800 border border-sky-300 font-bold'
                    : 'bg-cyan-500/20 text-cyan-300 border border-cyan-400'
                  : isLight
                    ? 'text-slate-500 hover:text-slate-800'
                    : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {language === 'en' ? 'Satellite' : 'Satélite'}
            </button>
            <button
              onClick={() => {
                playHoloClick(750);
                setDeepZoomLevel('isometric');
              }}
              className={`px-2.5 py-1 rounded-xl text-[11px] font-mono transition-all cursor-pointer ${
                deepZoomLevel === 'isometric'
                  ? isLight
                    ? 'bg-sky-100 text-sky-800 border border-sky-300 font-bold'
                    : 'bg-cyan-500/20 text-cyan-300 border border-cyan-400'
                  : isLight
                    ? 'text-slate-500 hover:text-slate-800'
                    : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {language === 'en' ? 'Isometric' : 'Isométrico'}
            </button>
            <button
              onClick={() => {
                playHoloClick(750);
                setDeepZoomLevel('street');
              }}
              className={`px-2.5 py-1 rounded-xl text-[11px] font-mono transition-all cursor-pointer ${
                deepZoomLevel === 'street'
                  ? isLight
                    ? 'bg-sky-100 text-sky-800 border border-sky-300 font-bold'
                    : 'bg-cyan-500/20 text-cyan-300 border border-cyan-400'
                  : isLight
                    ? 'text-slate-500 hover:text-slate-800'
                    : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {language === 'en' ? 'Street' : 'Micro'}
            </button>
          </div>
        </div>
      </div>

      {/* Floating Micro-Data Entity Inspector Modal */}
      <AgentInspectorModal
        worker={selectedWorker}
        firm={selectedFirm}
        onClose={() => {
          onSelectWorker(null);
          onSelectFirm(null);
        }}
        onFocusEntity={() => {
          setDeepZoomLevel('street');
        }}
      />
    </div>
  );
};
