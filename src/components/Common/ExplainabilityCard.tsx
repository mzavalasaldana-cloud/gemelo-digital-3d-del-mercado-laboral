import React, { useState } from 'react';
import { 
  Lightbulb, 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  Layers, 
  TrendingUp, 
  Scale, 
  AlertCircle,
  FileSpreadsheet
} from 'lucide-react';
import { Language, AppTheme } from '../../types';

export interface ExplainabilityCardProps {
  title?: string;
  variableOrMetric?: string;
  whatItIs: string;
  howToRead: string;
  policyImpact: string;
  formulaOrMethod?: string;
  benchmarksOrAlerts?: string;
  defaultExpanded?: boolean;
  language?: Language;
  theme?: AppTheme;
  className?: string;
}

export const ExplainabilityCard: React.FC<ExplainabilityCardProps> = ({
  title,
  variableOrMetric,
  whatItIs,
  howToRead,
  policyImpact,
  formulaOrMethod,
  benchmarksOrAlerts,
  defaultExpanded = false,
  language = 'es',
  theme = 'dark',
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(defaultExpanded);
  const isLight = theme === 'light';

  const defaultTitle = language === 'en' 
    ? 'Econometric Interpretation & Explainability' 
    : 'Interpretabilidad & Explicabilidad Econométrica';

  const displayTitle = title || defaultTitle;

  return (
    <div 
      className={`rounded-xl border transition-all duration-200 mt-2.5 overflow-hidden ${
        isLight
          ? 'bg-slate-50/95 border-sky-300/60 shadow-xs'
          : 'bg-slate-950/70 border-cyan-500/25 shadow-sm'
      } ${className}`}
    >
      {/* Header Button to Toggle */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full px-3.5 py-2.5 flex items-center justify-between text-left transition-colors cursor-pointer ${
          isLight
            ? 'hover:bg-sky-100/60 text-slate-800'
            : 'hover:bg-cyan-950/40 text-slate-200'
        }`}
      >
        <div className="flex items-center gap-2">
          <div className={`p-1 rounded-md ${
            isLight ? 'bg-sky-100 text-sky-700' : 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
          }`}>
            <Lightbulb className="w-3.5 h-3.5 animate-pulse" />
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-xs font-mono-hud font-semibold ${
              isLight ? 'text-sky-900' : 'text-cyan-300'
            }`}>
              {displayTitle}
            </span>
            {variableOrMetric && (
              <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
                isLight 
                  ? 'bg-white border-slate-300 text-slate-700' 
                  : 'bg-slate-900 border-slate-700 text-slate-300'
              }`}>
                {variableOrMetric}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-mono ${
            isLight ? 'text-slate-500' : 'text-slate-400'
          }`}>
            {isExpanded 
              ? (language === 'en' ? 'Hide guide' : 'Ocultar guía') 
              : (language === 'en' ? 'Show guide' : 'Ver explicación')}
          </span>
          {isExpanded ? (
            <ChevronUp className="w-3.5 h-3.5 text-cyan-500" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-cyan-500" />
          )}
        </div>
      </button>

      {/* Expanded Content Area */}
      {isExpanded && (
        <div className={`px-4 py-3.5 border-t text-xs space-y-3 font-sans ${
          isLight ? 'border-sky-200 bg-white/70 text-slate-700' : 'border-cyan-500/20 bg-slate-900/40 text-slate-300'
        }`}>
          {/* 1. What it represents */}
          <div className="flex items-start gap-2.5">
            <div className="mt-0.5 shrink-0 text-cyan-500">
              <Layers className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className={`font-mono-hud font-bold text-[11px] uppercase tracking-wider block mb-0.5 ${
                isLight ? 'text-slate-900' : 'text-slate-100'
              }`}>
                {language === 'en' ? '🎯 What it represents / Objective:' : '🎯 ¿Qué representa / Objetivo:'}
              </span>
              <p className="leading-relaxed">{whatItIs}</p>
            </div>
          </div>

          {/* 2. Technical Reading / How to Interpret */}
          <div className="flex items-start gap-2.5">
            <div className="mt-0.5 shrink-0 text-amber-500">
              <TrendingUp className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className={`font-mono-hud font-bold text-[11px] uppercase tracking-wider block mb-0.5 ${
                isLight ? 'text-slate-900' : 'text-slate-100'
              }`}>
                {language === 'en' ? '🔍 Technical Reading & Interpretation:' : '🔍 Lectura Técnica & Cómo Interpretarlo:'}
              </span>
              <p className="leading-relaxed">{howToRead}</p>
            </div>
          </div>

          {/* 3. Policy & Decision Impact */}
          <div className="flex items-start gap-2.5">
            <div className="mt-0.5 shrink-0 text-emerald-500">
              <Scale className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className={`font-mono-hud font-bold text-[11px] uppercase tracking-wider block mb-0.5 ${
                isLight ? 'text-slate-900' : 'text-slate-100'
              }`}>
                {language === 'en' ? '🏛️ Public Policy Impact & Decision Making:' : '🏛️ Implicación en Políticas Públicas & Decisión:'}
              </span>
              <p className="leading-relaxed">{policyImpact}</p>
            </div>
          </div>

          {/* Optional Formula / Methodology */}
          {formulaOrMethod && (
            <div className={`p-2.5 rounded-lg border font-mono text-[11px] flex items-center gap-2 ${
              isLight ? 'bg-slate-100 border-slate-300 text-slate-800' : 'bg-slate-950 border-slate-800 text-cyan-300'
            }`}>
              <FileSpreadsheet className="w-3.5 h-3.5 shrink-0 text-cyan-500" />
              <span><b>{language === 'en' ? 'Method/Formula:' : 'Fórmula/Método:'}</b> {formulaOrMethod}</span>
            </div>
          )}

          {/* Optional Benchmarks / Alerts */}
          {benchmarksOrAlerts && (
            <div className={`p-2.5 rounded-lg border text-[11px] flex items-center gap-2 ${
              isLight ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-amber-950/30 border-amber-500/30 text-amber-300'
            }`}>
              <AlertCircle className="w-3.5 h-3.5 shrink-0 text-amber-500" />
              <span><b>{language === 'en' ? 'Thresholds / Alert Limits:' : 'Umbrales & Límites Críticos:'}</b> {benchmarksOrAlerts}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
