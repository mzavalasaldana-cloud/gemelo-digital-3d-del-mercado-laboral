import React, { useState } from 'react';
import { CountryCode, ScenarioPreset, StructuralMetrics } from '../../types';
import { 
  X, 
  FileDown, 
  FileText, 
  FileSpreadsheet, 
  Download, 
  Sparkles, 
  CheckCircle2, 
  Loader2 
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';

interface ExportReportsModalProps {
  isOpen: boolean;
  onClose: () => void;
  country: CountryCode;
  scenario: ScenarioPreset;
  metrics: StructuralMetrics;
}

export const ExportReportsModal: React.FC<ExportReportsModalProps> = ({
  isOpen,
  onClose,
  country,
  scenario,
  metrics,
}) => {
  const [reportType, setReportType] = useState<'scenario' | 'compare' | 'country'>('scenario');
  const [format, setFormat] = useState<'pdf' | 'excel' | 'word'>('pdf');
  const [isGenerating, setIsGenerating] = useState(false);
  const [materializedDoc, setMaterializedDoc] = useState<{
    name: string;
    size: string;
    date: string;
  } | null>(null);

  if (!isOpen) return null;

  const handleGenerate = () => {
    playHoloClick(1000);
    setIsGenerating(true);
    setMaterializedDoc(null);

    setTimeout(() => {
      setIsGenerating(false);
      setMaterializedDoc({
        name: `Informe_GemeloDigital_${country}_${scenario}_2034.${format === 'pdf' ? 'pdf' : format === 'excel' ? 'xlsx' : 'docx'}`,
        size: '3.4 MB',
        date: new Date().toLocaleTimeString(),
      });
      playHoloClick(1200);
    }, 1800);
  };

  const handleDownloadFile = () => {
    if (!materializedDoc) return;
    playHoloClick(950);

    // Create realistic mock file payload for user download
    const exportPayload = {
      project: 'Gemelo Digital 3D del Mercado Laboral Formal-Informal',
      country,
      scenario,
      metricsSnapshot: metrics,
      generatedAt: new Date().toISOString(),
      disclaimer: 'Reporte generado en modo maqueta para diseño de políticas públicas de empleo decente.',
    };

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = materializedDoc.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-xl animate-fadeIn">
      <div className="hud-glass-solid w-full max-w-3xl rounded-3xl border border-purple-500/40 shadow-2xl flex flex-col overflow-hidden holo-corner-tl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-purple-500/20 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-400">
              <FileDown className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-display font-bold text-lg text-slate-100 tracking-wide">
                  CONSOLA DE EXPORTACIÓN & REPORTES EJECUTIVOS
                </h2>
                <span className="text-[10px] font-mono-hud px-2 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-700">
                  HOLOGRAPHIC EXPORTER
                </span>
              </div>
              <p className="text-xs font-mono-hud text-slate-400">
                Materialización de informes técnicos para ministerios de trabajo y agencias OIT
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              playHoloClick(700);
              onClose();
            }}
            className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 font-mono-hud text-xs">
          {/* Step 1: Tipo de Reporte */}
          <div className="space-y-2">
            <span className="text-slate-400 uppercase tracking-wider text-[11px] block">
              1. Seleccionar Tipo de Informe:
            </span>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                { id: 'scenario', title: 'Resultados de Escenario Activo', desc: 'Impacto detallado en empleo, salarios y costo fiscal' },
                { id: 'compare', title: 'Comparativa Multi-Escenario', desc: 'Matriz cruzada de políticas A vs B vs Shock E' },
                { id: 'country', title: 'Diagnóstico País & Informalidad', desc: 'Perfil macroeconómico estructural y microdatos' },
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => {
                    playHoloClick(800);
                    setReportType(t.id as typeof reportType);
                  }}
                  className={`p-3 rounded-2xl border text-left transition-all space-y-1 ${
                    reportType === t.id
                      ? 'bg-purple-500/20 text-purple-200 border-purple-400 glow-cyan'
                      : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="font-bold text-slate-200 text-xs">{t.title}</div>
                  <div className="text-[10px] text-slate-400">{t.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Step 2: Formato de Salida */}
          <div className="space-y-2">
            <span className="text-slate-400 uppercase tracking-wider text-[11px] block">
              2. Formato del Documento:
            </span>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'pdf', title: 'PDF Ejecutivo', icon: FileText },
                { id: 'excel', title: 'Hoja Excel (.xlsx)', icon: FileSpreadsheet },
                { id: 'word', title: 'Documento Word (.docx)', icon: FileText },
              ].map((f) => {
                const Icon = f.icon;
                return (
                  <button
                    key={f.id}
                    onClick={() => {
                      playHoloClick(850);
                      setFormat(f.id as typeof format);
                    }}
                    className={`p-3 rounded-2xl border flex items-center justify-center gap-2 transition-all font-bold ${
                      format === f.id
                        ? 'bg-purple-500/20 text-purple-300 border-purple-400'
                        : 'bg-slate-900/60 text-slate-400 border-slate-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{f.title}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Action Trigger */}
          <div>
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full py-3 px-4 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg glow-cyan transition-all disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-purple-300" />
                  <span>MATERIALIZANDO HOLOGRAMA DE DOCUMENTO...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-purple-300" />
                  <span>COMPILAR & MATERIALIZAR DOCUMENTO</span>
                </>
              )}
            </button>
          </div>

          {/* Holographic Materialization Tray */}
          {materializedDoc && (
            <div className="p-4 rounded-2xl bg-purple-950/30 border border-purple-500/40 space-y-3 animate-fadeIn">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-400 flex items-center justify-center text-purple-300">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div>
                    <div className="font-bold text-slate-100 text-xs truncate max-w-md">
                      {materializedDoc.name}
                    </div>
                    <span className="text-[10px] text-slate-400">
                      Tamaño: {materializedDoc.size} • Generado a las {materializedDoc.date}
                    </span>
                  </div>
                </div>

                <button
                  onClick={handleDownloadFile}
                  className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold flex items-center gap-1.5 transition-all shadow-md"
                >
                  <Download className="w-4 h-4" />
                  <span>Descargar Archivo</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
