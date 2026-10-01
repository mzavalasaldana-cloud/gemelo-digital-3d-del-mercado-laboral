import React from 'react';
import { CountryCode, StructuralMetrics, Language, AppTheme } from '../../types';
import { 
  X, 
  Award, 
  Coins,
  ShieldCheck,
  Heart,
  Users,
  Scale
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';
import { t } from '../../utils/i18n';
import { ExplainabilityCard } from '../Common/ExplainabilityCard';


interface ILODecentWorkModalProps {
  isOpen: boolean;
  onClose: () => void;
  country: CountryCode;
  metrics: StructuralMetrics;
  language?: Language;
  theme?: AppTheme;
}

export const ILODecentWorkModal: React.FC<ILODecentWorkModalProps> = ({
  isOpen,
  onClose,
  country,
  metrics,
  language = 'es',
  theme = 'dark',
}) => {
  if (!isOpen) return null;

  const isLight = theme === 'light';

  const decentWorkPillars = [
    {
      id: 'pillar-wage',
      title: t('pillarWageTitle', language),
      icon: Coins,
      score: Math.min(100, Math.round(metrics.avgFormalWageUSD * 3.2)),
      description: t('pillarWageDesc', language),
      status: metrics.avgFormalWageUSD > 18 ? t('pillarWageAdequate', language) : t('pillarWageCritical', language),
      isGood: metrics.avgFormalWageUSD > 18,
    },
    {
      id: 'pillar-protection',
      title: t('pillarProtectionTitle', language),
      icon: ShieldCheck,
      score: Math.min(100, Math.round(100 - metrics.informalityRate + 12)),
      description: t('pillarProtectionDesc', language),
      status: metrics.informalityRate < 75 ? t('pillarProtectionGood', language) : t('pillarProtectionBad', language),
      isGood: metrics.informalityRate < 75,
    },
    {
      id: 'pillar-safety',
      title: t('pillarSafetyTitle', language),
      icon: Heart,
      score: 64,
      description: t('pillarSafetyDesc', language),
      status: t('pillarSafetyStatus', language),
      isGood: true,
    },
    {
      id: 'pillar-dialogue',
      title: t('pillarDialogueTitle', language),
      icon: Users,
      score: 52,
      description: t('pillarDialogueDesc', language),
      status: t('pillarDialogueStatus', language),
      isGood: false,
    },
    {
      id: 'pillar-gender',
      title: t('pillarGenderTitle', language),
      icon: Scale,
      score: 58,
      description: t('pillarGenderDesc', language),
      status: t('pillarGenderStatus', language),
      isGood: false,
    },
  ];

  const overallDecentScore = Math.round(
    decentWorkPillars.reduce((acc, p) => acc + p.score, 0) / decentWorkPillars.length
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-xl animate-fadeIn">
      <div className={`hud-glass-solid w-full max-w-4xl h-[84vh] rounded-3xl border shadow-2xl flex flex-col overflow-hidden holo-corner-tl ${
        isLight ? 'border-emerald-500/50 bg-white/95 text-slate-800' : 'border-emerald-500/40 text-slate-100'
      }`}>
        {/* Header */}
        <div className={`px-6 py-4 border-b flex items-center justify-between ${
          isLight ? 'border-emerald-500/30 bg-emerald-50/60' : 'border-emerald-500/20 bg-slate-950/40'
        }`}>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-500 border border-emerald-400 glow-cyan">
              <Award className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className={`font-display font-bold text-lg tracking-wide ${
                  isLight ? 'text-slate-900' : 'text-slate-100'
                }`}>
                  {t('iloModalTitle', language)}
                </h2>
                <span className={`text-[10px] font-mono-hud px-2 py-0.5 rounded border ${
                  isLight ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-emerald-950 text-emerald-300 border-emerald-700'
                }`}>
                  {t('iloModalBadge', language)}
                </span>
              </div>
              <p className={`text-xs font-mono-hud ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                {t('iloModalSubtitle', language)}
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              playHoloClick(700);
              onClose();
            }}
            className={`p-2 rounded-xl transition-colors cursor-pointer ${
              isLight ? 'text-slate-500 hover:text-rose-600 hover:bg-slate-100' : 'text-slate-400 hover:text-rose-400 hover:bg-slate-800'
            }`}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 font-mono-hud text-xs">
          {/* Top Score Banner */}
          <div className={`p-5 rounded-2xl border flex items-center justify-between ${
            isLight ? 'bg-emerald-50/80 border-emerald-300' : 'bg-emerald-500/10 border border-emerald-500/40'
          }`}>
            <div>
              <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider block">
                {t('iloGlobalScoreTitle', language)} ({country})
              </span>
              <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-300 mt-1">
                {overallDecentScore} / 100
              </div>
              <span className={`text-[11px] ${isLight ? 'text-slate-600' : 'text-slate-300'}`}>
                {t('iloOds8Desc', language)}
              </span>
            </div>

            <div className="text-right">
              <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                {t('policyDiagnosisLabel', language)}:
              </span>
              <span className="text-xs font-bold text-cyan-600 dark:text-cyan-300">
                {overallDecentScore > 60 ? t('sustainableTransition', language) : t('precarizationAlert', language)}
              </span>
            </div>
          </div>

          {/* Pillars List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {decentWorkPillars.map((pillar) => {
              const Icon = pillar.icon;
              return (
                <div
                  key={pillar.id}
                  className={`p-4 rounded-2xl border transition-all space-y-2.5 ${
                    isLight 
                      ? 'bg-slate-50 border-slate-200 hover:border-emerald-400/60 shadow-sm' 
                      : 'bg-slate-900/60 border-slate-800 hover:border-emerald-500/30'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-500">
                        <Icon className="w-4 h-4" />
                      </div>
                      <h4 className={`font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-200'}`}>
                        {pillar.title}
                      </h4>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        pillar.isGood
                          ? isLight ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : isLight ? 'bg-amber-100 text-amber-800 border-amber-300' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                      }`}
                    >
                      {pillar.status}
                    </span>
                  </div>

                  <p className={`text-[11px] leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                    {pillar.description}
                  </p>

                  <div>
                    <div className={`flex justify-between text-[11px] mb-0.5 ${isLight ? 'text-slate-700' : 'text-slate-300'}`}>
                      <span>{t('complianceLevel', language)}:</span>
                      <span className="font-bold text-emerald-600 dark:text-emerald-300">{pillar.score}%</span>
                    </div>
                    <div className={`w-full h-2 rounded-full overflow-hidden ${isLight ? 'bg-slate-200' : 'bg-slate-800'}`}>
                      <div
                        className="bg-gradient-to-r from-cyan-400 to-emerald-400 h-full rounded-full"
                        style={{ width: `${pillar.score}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <ExplainabilityCard
            language={language}
            theme={theme}
            title={language === 'en' ? 'Pillars Explainability: ILO Decent Work Measurement Framework' : 'Explicabilidad: Marco de Trabajo Decente y ODS 8 OIT'}
            variableOrMetric="Índice Compuesto OIT (0-100)"
            whatItIs={language === 'en'
              ? 'Multi-dimensional evaluation framework synthesized from the 4 strategic pillars of the ILO (Fair wages, social protection, workplace safety, and gender equality).'
              : 'Marco de evaluación multidimensional basado en los 4 pilares estratégicos de la OIT (Empleo con derechos, protección social, seguridad ocupacional e igualdad de género).'}
            howToRead={language === 'en'
              ? 'Scores above 70% indicate robust compliance. Scores below 50% flag urgent structural deficits in labor protections.'
              : 'Puntajes superiores a 70% representan cumplimiento adecuado; puntajes inferiores a 50% señalan déficits severos de precarización laboral.'}
            policyImpact={language === 'en'
              ? 'Guides targeted policy interventions to raise quality of life and formal contractual security.'
              : 'Orienta la asignación presupuestaria hacia los pilares más rezagados para acelerar la consecución de las metas 2030 de la ONU.'}
            benchmarksOrAlerts="Meta ODS 8.3: Trabajo Decente > 75 puntos hacia 2030"
          />

          {/* Justification Box */}
          <div className={`p-4 rounded-2xl border space-y-1 text-[11px] ${
            isLight ? 'bg-slate-50 border-slate-200 text-slate-600' : 'bg-slate-900/40 border-slate-800 text-slate-400'
          }`}>
            <span className="text-cyan-600 dark:text-cyan-400 font-bold uppercase tracking-wider text-[10px] block">
              {t('whyIncludedTitle', language)}
            </span>
            <p>
              {t('whyIncludedText', language)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

