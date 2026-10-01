import React, { useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  FastForward, 
  Sparkles,
  Waves
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';

interface TimelineControllerProps {
  currentYear: number;
  onYearChange: (year: number) => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  playbackSpeed: number;
  onChangeSpeed: (speed: number) => void;
  lightRiverMode: boolean;
  onToggleLightRiver: () => void;
}

export const TimelineController: React.FC<TimelineControllerProps> = ({
  currentYear,
  onYearChange,
  isPlaying,
  onTogglePlay,
  playbackSpeed,
  onChangeSpeed,
  lightRiverMode,
  onToggleLightRiver,
}) => {
  const minYear = 2015;
  const maxYear = 2034;
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    if (isPlaying) {
      const intervalMs = Math.max(250, 1000 / playbackSpeed);
      timerRef.current = window.setInterval(() => {
        onYearChange(currentYear >= maxYear ? minYear : currentYear + 1);
      }, intervalMs);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, currentYear, playbackSpeed, onYearChange]);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    playHoloClick(400 + (val - minYear) * 30);
    onYearChange(val);
  };

  return (
    <div className="absolute bottom-3 left-4 right-4 z-20 pointer-events-none flex justify-center">
      <div 
        onPointerDown={(e) => e.stopPropagation()}
        onWheel={(e) => e.stopPropagation()}
        className="hud-glass px-5 py-2.5 rounded-2xl border border-cyan-500/30 flex flex-col md:flex-row items-center gap-4 shadow-2xl backdrop-blur-xl pointer-events-auto max-w-4xl w-full"
      >
        {/* Playback Controls & Speed */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              playHoloClick(800);
              onYearChange(minYear);
            }}
            className="p-2 rounded-xl text-slate-400 hover:text-cyan-300 hover:bg-slate-800 transition-colors"
            title="Reiniciar a 2015"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => {
              playHoloClick(1000);
              onTogglePlay();
            }}
            className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold shadow-md glow-cyan transition-all"
            title={isPlaying ? 'Pausar Simulación Temporal' : 'Reproducir Línea de Tiempo'}
          >
            {isPlaying ? <Pause className="w-4 h-4 fill-slate-950" /> : <Play className="w-4 h-4 fill-slate-950 ml-0.5" />}
          </button>

          {/* Speed Selector */}
          <div className="flex bg-slate-900/80 p-0.5 rounded-lg border border-slate-800 font-mono-hud text-[10px]">
            {[1, 2, 5].map((s) => (
              <button
                key={s}
                onClick={() => {
                  playHoloClick(900);
                  onChangeSpeed(s);
                }}
                className={`px-2 py-1 rounded transition-all ${
                  playbackSpeed === s
                    ? 'bg-cyan-500/30 text-cyan-300 font-bold border border-cyan-500/50'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>

        {/* Scrubbing Dial & Slider */}
        <div className="flex-1 w-full flex flex-col gap-1">
          <div className="flex items-center justify-between text-xs font-mono-hud">
            <span className="text-slate-400 flex items-center gap-1.5">
              <FastForward className="w-3.5 h-3.5 text-cyan-400" />
              LÍNEA TEMPORAL DE POLÍTICAS
            </span>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400">Año de Proyección:</span>
              <span className="font-extrabold text-lg text-cyan-300 tracking-wider glow-text-cyan">
                {currentYear}
              </span>
            </div>
          </div>

          <div className="relative flex items-center">
            <input
              type="range"
              min={minYear}
              max={maxYear}
              step={1}
              value={currentYear}
              onChange={handleSliderChange}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
          </div>

          <div className="flex justify-between text-[9px] font-mono-hud text-slate-500 px-0.5">
            <span>2015 (Histórico)</span>
            <span>2020 (Shock)</span>
            <span>2025 (Transición)</span>
            <span>2030 (Agenda OIT)</span>
            <span>2034 (Horizonte)</span>
          </div>
        </div>

        {/* Light Rivers / Trails Toggle */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
          <button
            onClick={() => {
              playHoloClick(950);
              onToggleLightRiver();
            }}
            className={`px-3 py-2 rounded-xl text-xs font-mono-hud transition-all flex items-center gap-1.5 whitespace-nowrap ${
              lightRiverMode
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 glow-amber'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
            title="Activar o desactivar estelas lumínicas para ver ríos de migración informal a formal"
          >
            <Waves className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">Ríos Migratorios</span>
            {lightRiverMode && <Sparkles className="w-3 h-3 text-amber-300 animate-spin" />}
          </button>
        </div>
      </div>
    </div>
  );
};
