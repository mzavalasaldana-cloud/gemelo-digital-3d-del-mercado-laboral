import React from 'react';
import { 
  PolicyParameters, 
  UserRole, 
  ScenarioPreset 
} from '../../types';
import { 
  Sliders, 
  Lock, 
  Radio, 
  RotateCcw, 
  DollarSign, 
  GraduationCap, 
  ShieldAlert, 
  FileCheck2,
  Sparkles,
  Zap
} from 'lucide-react';
import { playHoloClick, playPolicyWaveSound } from '../../utils/audioSynth';

interface PolicyPanelProps {
  policyParams: PolicyParameters;
  onChangePolicy: (params: PolicyParameters) => void;
  role: UserRole;
  scenario: ScenarioPreset;
  onTriggerPolicyWave: () => void;
  onResetPolicies: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const PolicyPanel: React.FC<PolicyPanelProps> = ({
  policyParams,
  onChangePolicy,
  role,
  onTriggerPolicyWave,
  onResetPolicies,
  isCollapsed,
  onToggleCollapse,
}) => {
  const canEdit = role === 'ADMIN' || role === 'POLICY_ANALYST';

  const handleSliderChange = (key: keyof PolicyParameters, value: number) => {
    if (!canEdit) return;
    playHoloClick(600 + value * 5);
    onChangePolicy({
      ...policyParams,
      [key]: value,
    });
    // Trigger wave on slider adjustment
    onTriggerPolicyWave();
    playPolicyWaveSound();
  };

  if (isCollapsed) {
    return (
      <div 
        onPointerDown={(e) => e.stopPropagation()}
        onWheel={(e) => e.stopPropagation()}
        className="absolute top-20 left-4 z-20 pointer-events-auto"
      >
        <button
          onClick={onToggleCollapse}
          className="hud-glass p-3 rounded-2xl border border-cyan-500/30 text-cyan-300 hover:border-cyan-400 glow-cyan transition-all flex items-center gap-2 font-mono-hud text-xs"
        >
          <Sliders className="w-4 h-4 text-cyan-400" />
          <span>POLÍTICAS</span>
        </button>
      </div>
    );
  }

  return (
    <aside 
      onPointerDown={(e) => e.stopPropagation()}
      onWheel={(e) => e.stopPropagation()}
      className="absolute top-20 left-4 bottom-28 w-80 max-w-[calc(100vw-32px)] z-20 pointer-events-auto flex flex-col"
    >
      <div className="hud-glass rounded-2xl border border-cyan-500/30 p-4 flex-1 flex flex-col gap-3 shadow-2xl backdrop-blur-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2.5">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-400/40">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-display font-bold text-xs tracking-wider text-slate-100 uppercase">
                Panel de Políticas
              </h2>
              <span className="text-[10px] font-mono-hud text-cyan-400">
                SIMULADOR DE INTERVENCIÓN
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={onResetPolicies}
              disabled={!canEdit}
              className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800 disabled:opacity-40 transition-colors"
              title="Restablecer Parámetros Base"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onToggleCollapse}
              className="text-[10px] font-mono-hud px-2 py-1 rounded bg-slate-800/80 text-slate-400 hover:text-slate-200"
            >
              MIN
            </button>
          </div>
        </div>

        {/* Role Warning for Researcher */}
        {!canEdit && (
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-2 text-[11px] text-amber-300 font-mono-hud">
            <Lock className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
            <span>Modo Consulta: Se requiere rol de Analista o Administrador para alterar políticas públicas.</span>
          </div>
        )}

        {/* Sliders Container */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {/* 1. Reducción de Costos de Registro */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-mono-hud">
              <span className="text-slate-300 flex items-center gap-1.5">
                <FileCheck2 className="w-3.5 h-3.5 text-cyan-400" />
                Costos de Registro
              </span>
              <span className="font-bold text-cyan-300">
                -{policyParams.registrationCostReduction}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              disabled={!canEdit}
              value={policyParams.registrationCostReduction}
              onChange={(e) => handleSliderChange('registrationCostReduction', Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 disabled:opacity-40"
            />
            <p className="text-[10px] text-slate-400 leading-tight">
              Reduce la fricción burocrática y aranceles notariales para formalizar microempresas.
            </p>
          </div>

          {/* 2. Subsidio PYME ($/mes) */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-mono-hud">
              <span className="text-slate-300 flex items-center gap-1.5">
                <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                Subsidio PYME
              </span>
              <span className="font-bold text-emerald-300">
                ${policyParams.smeSubsidyUSDMonth} /mes
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={150}
              step={5}
              disabled={!canEdit}
              value={policyParams.smeSubsidyUSDMonth}
              onChange={(e) => handleSliderChange('smeSubsidyUSDMonth', Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400 disabled:opacity-40"
            />
            <p className="text-[10px] text-slate-400 leading-tight">
              Transferencia directa de alivio en cuotas de seguridad social durante los primeros 12 meses.
            </p>
          </div>

          {/* 3. Capacitación & Certificación de Habilidades */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-mono-hud">
              <span className="text-slate-300 flex items-center gap-1.5">
                <GraduationCap className="w-3.5 h-3.5 text-indigo-400" />
                Capacitación Laboral
              </span>
              <span className="font-bold text-indigo-300">
                {policyParams.skillsTrainingCoverage}% cobertura
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              disabled={!canEdit}
              value={policyParams.skillsTrainingCoverage}
              onChange={(e) => handleSliderChange('skillsTrainingCoverage', Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-400 disabled:opacity-40"
            />
            <p className="text-[10px] text-slate-400 leading-tight">
              Programas de certificación técnica y digitalización para trabajadores de talleres informales.
            </p>
          </div>

          {/* 4. Impuestos & Protección Social */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-mono-hud">
              <span className="text-slate-300 flex items-center gap-1.5">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                Piso Protección Social
              </span>
              <span className="font-bold text-amber-300">
                {policyParams.socialProtectionTax}% PIB
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={40}
              step={2}
              disabled={!canEdit}
              value={policyParams.socialProtectionTax}
              onChange={(e) => handleSliderChange('socialProtectionTax', Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400 disabled:opacity-40"
            />
            <p className="text-[10px] text-slate-400 leading-tight">
              Tasa contributiva de cobertura médica y seguro de cesantía financiado solidariamente.
            </p>
          </div>

          {/* 5. Fiscalización Inteligente */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-mono-hud">
              <span className="text-slate-300 flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-rose-400" />
                Inspección Laboral
              </span>
              <span className="font-bold text-rose-300">
                {policyParams.smartInspectionCoverage}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={80}
              step={5}
              disabled={!canEdit}
              value={policyParams.smartInspectionCoverage}
              onChange={(e) => handleSliderChange('smartInspectionCoverage', Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-rose-400 disabled:opacity-40"
            />
            <p className="text-[10px] text-slate-400 leading-tight">
              Monitoreo predictivo con satélite y cruces de facturación para detectar empleo no registrado.
            </p>
          </div>
        </div>

        {/* Action Trigger Button */}
        <div className="pt-2 border-t border-cyan-500/20">
          <button
            onClick={() => {
              playPolicyWaveSound();
              onTriggerPolicyWave();
            }}
            disabled={!canEdit}
            className="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-slate-950 font-bold font-mono-hud text-xs flex items-center justify-center gap-2 shadow-lg glow-cyan transition-all disabled:opacity-40"
          >
            <Zap className="w-4 h-4 text-slate-950" />
            <span>EMITIR ONDA DE BARRIDO</span>
          </button>
          <div className="mt-1.5 text-center text-[9px] font-mono-hud text-cyan-400/80 flex items-center justify-center gap-1">
            <Sparkles className="w-2.5 h-2.5" />
            Propaga el impacto en la topografía y recalcula boids
          </div>
        </div>
      </div>
    </aside>
  );
};
