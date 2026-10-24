import React from 'react';
import { WorkerAgent, StructuralFirm } from '../../types';
import { 
  X, 
  User, 
  Building2, 
  TrendingUp, 
  Crosshair, 
  CheckCircle2, 
  AlertTriangle,
  Layers
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';

interface AgentInspectorModalProps {
  worker: WorkerAgent | null;
  firm: StructuralFirm | null;
  onClose: () => void;
  onFocusEntity: (x: number, y: number, z: number) => void;
}

export const AgentInspectorModal = React.memo<AgentInspectorModalProps>(({
  worker,
  firm,
  onClose,
  onFocusEntity,
}) => {
  if (!worker && !firm) return null;

  return (
    <div className="absolute top-24 left-1/2 -translate-x-1/2 md:translate-x-0 md:left-auto md:right-92 z-30 pointer-events-auto w-84 max-w-[calc(100vw-32px)]">
      <div className="hud-glass-solid rounded-2xl border border-cyan-400/40 p-4 shadow-2xl backdrop-blur-2xl text-slate-100 holo-corner-tl space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-cyan-500/30 pb-2">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-400">
              {worker ? <User className="w-4 h-4" /> : <Building2 className="w-4 h-4" />}
            </div>
            <div>
              <div className="text-[9px] font-mono-hud text-cyan-400 uppercase tracking-wider">
                {worker ? 'TELEMETRÍA DE AGENTE' : 'ENTIDAD ESTRUCTURAL'}
              </div>
              <h3 className="font-display font-bold text-sm text-slate-100 truncate max-w-[190px]">
                {worker ? `Trabajador Boid #${worker.code}` : firm?.name}
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => {
                playHoloClick(900);
                if (worker) onFocusEntity(worker.x, worker.y, worker.z);
                if (firm) onFocusEntity(firm.x, firm.height / 2, firm.z);
              }}
              className="p-1.5 rounded-lg text-cyan-400 hover:text-cyan-200 hover:bg-cyan-500/20 transition-colors"
              title="Centrar Cámara 3D en este elemento"
            >
              <Crosshair className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => {
                playHoloClick(700);
                onClose();
              }}
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Worker Micro-Data Card (Atributos Reales del Modelo ITDT) */}
        {worker && (
          <div className="space-y-3 font-mono-hud text-xs">
            {/* Status & Sector */}
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-slate-400 text-[11px]">Estado Laboral ITDT:</span>
              <span
                className={`px-2 py-0.5 rounded text-[11px] font-bold flex items-center gap-1 ${
                  worker.sector === 'formal'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                }`}
              >
                {worker.sector === 'formal' && <CheckCircle2 className="w-3 h-3 text-cyan-400" />}
                {worker.sector === 'informal' && <AlertTriangle className="w-3 h-3 text-amber-400" />}
                {worker.sector === 'formal' ? 'FORMAL' : 'INFORMAL'}
              </span>
            </div>

            {/* Sexo, Educación y Zona */}
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Sexo (OIT):</span>
                <span className="font-semibold text-slate-200">{worker.gender}</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Zona Geográfica:</span>
                <span className="font-semibold text-slate-200">{worker.ruralZone}</span>
              </div>
            </div>

            <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px]">
              <span className="text-slate-400 block text-[10px]">Nivel Educativo:</span>
              <span className="font-semibold text-indigo-300">{worker.education}</span>
            </div>

            {/* Productividad Econométrica h_i y Cuidado Semanal H_care */}
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-[11px] text-slate-300 mb-0.5">
                  <span className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-cyan-400" /> Productividad Relativa (h_i):
                  </span>
                  <span className="font-bold text-cyan-300">{worker.productivityH.toFixed(3)}</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-cyan-400 h-full rounded-full glow-cyan"
                    style={{ width: `${Math.min(100, Math.max(10, (worker.productivityH / 2.0) * 100))}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] text-slate-300 mb-0.5">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3 h-3 text-amber-400" /> Horas de Cuidado Semanales (H_care,i):
                  </span>
                  <span className="font-bold text-amber-300">{worker.careHours.toFixed(1)} hrs/sem</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-amber-400 h-full rounded-full glow-amber"
                    style={{ width: `${Math.min(100, (worker.careHours / 48) * 100)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Alfabetización Digital & Probabilidad de Formalización */}
            <div className="p-2.5 rounded-xl bg-cyan-950/30 border border-cyan-500/30 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 block">Alfabetización Digital (K_dig):</span>
                <span className="text-sm font-bold text-emerald-400">
                  {(worker.digitalLit * 100).toFixed(1)}%
                </span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-cyan-400 block">Transición ITDT:</span>
                <span className="text-sm font-bold text-cyan-300">
                  {worker.formalizationProb}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Firm Micro-Data Card */}
        {firm && (
          <div className="space-y-3 font-mono-hud text-xs">
            {/* Type & Architecture */}
            <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
              <span className="text-slate-400 text-[11px]">Estructura 3D:</span>
              <span
                className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                  firm.type === 'formal'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                }`}
              >
                {firm.type === 'formal' ? 'Prisma Hexagonal Formal' : 'Red de Micelio Informal'}
              </span>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Sector:</span>
                <span className="font-semibold text-slate-200 truncate block">{firm.sectorCategory}</span>
              </div>
              <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Tamaño de Empleo:</span>
                <span className="font-semibold text-cyan-300">{firm.sizeEmployees} trabajadores</span>
              </div>
            </div>

            {/* Productivity & Compliance */}
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-[11px] text-slate-300 mb-0.5">
                  <span className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-cyan-400" /> Score de Productividad:
                  </span>
                  <span className="font-bold text-cyan-300">{firm.productivityScore}/100</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-cyan-400 h-full rounded-full glow-cyan"
                    style={{ width: `${firm.productivityScore}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] text-slate-300 mb-0.5">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3 h-3 text-emerald-400" /> Cumplimiento Tributario:
                  </span>
                  <span className="font-bold text-emerald-300">{firm.taxComplianceRate}%</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-400 h-full rounded-full"
                    style={{ width: `${firm.taxComplianceRate}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Productividad A_j de la unidad */}
            <div className="p-2.5 rounded-xl bg-slate-900/80 border border-cyan-500/20 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 block">Productividad A_j:</span>
                <span className="text-sm font-bold text-amber-300">
                  {firm.productivityScore} / 100
                </span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block">Vínculos de Luz:</span>
                <span className="text-xs text-cyan-300 font-semibold">
                  {firm.type === 'formal' ? 'Fibra Óptica Activa' : 'Dispersión Orgánica'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});
