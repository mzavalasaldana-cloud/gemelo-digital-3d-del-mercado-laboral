import React, { useState } from 'react';
import { CountryCode, DatasetEntry } from '../../types';
import { MOCK_DATASETS } from '../../data/mockData';
import { 
  X, 
  Database, 
  UploadCloud, 
  CheckCircle2, 
  Sparkles, 
  FileSpreadsheet, 
  Globe2, 
  Layers,
  ArrowRight
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';

interface DatasetManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeCountry: CountryCode;
  onSelectDatasetCountry: (country: CountryCode) => void;
}

export const DatasetManagerModal: React.FC<DatasetManagerModalProps> = ({
  isOpen,
  onClose,
  activeCountry,
  onSelectDatasetCountry,
}) => {
  const [datasets, setDatasets] = useState<DatasetEntry[]>(MOCK_DATASETS);
  const [hoveredDataset, setHoveredDataset] = useState<DatasetEntry | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedInfo, setUploadedInfo] = useState<{
    fileName: string;
    rowsCount: number;
    colsCount: number;
    verified: boolean;
  } | null>(null);

  if (!isOpen) return null;

  const handleSimulatedDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    playHoloClick(1100);

    const file = e.dataTransfer.files[0];
    const fileName = file ? file.name : 'microdatos_encuesta_hogares_2024.csv';

    setUploadedInfo({
      fileName,
      rowsCount: 428500,
      colsCount: 38,
      verified: true,
    });
  };

  const handleSimulatedFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      playHoloClick(1100);
      setUploadedInfo({
        fileName: file.name,
        rowsCount: 312000,
        colsCount: 42,
        verified: true,
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-xl animate-fadeIn">
      <div className="hud-glass-solid w-full max-w-4xl h-[84vh] rounded-3xl border border-sky-500/40 shadow-2xl flex flex-col overflow-hidden holo-corner-tl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-sky-500/20 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-sky-500/20 text-sky-300 border border-sky-400">
              <Database className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-display font-bold text-lg text-slate-100 tracking-wide">
                  PUERTO DE GESTIÓN DE DATASETS
                </h2>
                <span className="text-[10px] font-mono-hud px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-700">
                  HARMONIZED REPOSITORY
                </span>
              </div>
              <p className="text-xs font-mono-hud text-slate-400">
                Encuestas nacionales de fuerza laboral, paneles de microempresas y calibración topográfica
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

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* 1. Drag & Drop Upload Vortex */}
          <div className="space-y-2">
            <h3 className="text-xs font-mono-hud text-sky-400 font-semibold uppercase tracking-wider flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-sky-400" />
              Puerto de Carga Vórtice (CSV / JSON / Stata .dta):
            </h3>

            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleSimulatedDrop}
              className={`p-6 rounded-2xl border-2 border-dashed transition-all flex flex-col items-center justify-center text-center cursor-pointer relative overflow-hidden ${
                isDragging
                  ? 'border-sky-400 bg-sky-500/20 glow-cyan'
                  : 'border-sky-500/30 bg-slate-900/50 hover:border-sky-500/50'
              }`}
            >
              <input
                type="file"
                accept=".csv,.json,.dta,.xlsx"
                onChange={handleSimulatedFileInput}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />

              {uploadedInfo ? (
                <div className="space-y-2 font-mono-hud text-xs animate-fadeIn">
                  <div className="w-12 h-12 mx-auto rounded-full bg-emerald-500/20 border border-emerald-400 flex items-center justify-center text-emerald-300">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div className="font-bold text-slate-100 text-sm">{uploadedInfo.fileName}</div>
                  <div className="flex items-center justify-center gap-4 text-slate-400 text-[11px]">
                    <span>Registros: <strong className="text-cyan-300">{(uploadedInfo.rowsCount ?? 0).toLocaleString()}</strong></span>
                    <span>•</span>
                    <span>Variables: <strong className="text-cyan-300">{uploadedInfo.colsCount}</strong></span>
                    <span>•</span>
                    <span className="text-emerald-400 flex items-center gap-1 font-semibold">
                      <Sparkles className="w-3 h-3" /> Anillo de Integridad Verificado
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Variables detectadas: ingreso_diario, tipo_establecimiento, cotiza_seguridad_social, sector_actividad.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="w-12 h-12 mx-auto rounded-full bg-sky-500/20 border border-sky-400/40 flex items-center justify-center text-sky-300">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div className="text-sm font-bold text-slate-200 font-mono-hud">
                    Arrastra tu archivo de microdatos aquí o haz clic para explorar
                  </div>
                  <p className="text-xs text-slate-400 max-w-md">
                    El motor armonizará automáticamente las columnas con la ontología formal-informal del gemelo digital 3D.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* 2. Carrusel de Cristales de Memoria (Saved Datasets) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-mono-hud text-sky-400 font-semibold uppercase tracking-wider flex items-center gap-2">
                <Database className="w-4 h-4 text-sky-400" />
                Cristales de Memoria Almacenados (Datasets Pre-Cargados):
              </h3>
              <span className="text-[10px] font-mono-hud text-slate-400">
                Pasa el cursor o haz clic para sincronizar la topografía 3D
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {datasets.map((ds) => {
                const isActive = activeCountry === ds.country;
                return (
                  <div
                    key={ds.id}
                    onMouseEnter={() => setHoveredDataset(ds)}
                    onMouseLeave={() => setHoveredDataset(null)}
                    onClick={() => {
                      playHoloClick(900);
                      onSelectDatasetCountry(ds.country);
                    }}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer font-mono-hud text-xs space-y-2.5 ${
                      isActive
                        ? 'bg-sky-500/20 border-sky-400 glow-cyan'
                        : 'bg-slate-900/60 border-slate-800 hover:border-sky-500/40 hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <FileSpreadsheet className="w-4 h-4 text-sky-400 flex-shrink-0" />
                        <div>
                          <div className="font-bold text-slate-100 text-sm leading-tight">
                            {ds.name}
                          </div>
                          <span className="text-[10px] text-slate-400 block mt-0.5">
                            {ds.institution} • {ds.yearSpan}
                          </span>
                        </div>
                      </div>

                      {isActive ? (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-sky-950 text-sky-300 font-semibold border border-sky-700 whitespace-nowrap">
                          ACTIVO EN 3D
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-500 hover:text-sky-300 flex items-center gap-1">
                          Cargar <ArrowRight className="w-3 h-3" />
                        </span>
                      )}
                    </div>

                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      {ds.description}
                    </p>

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {ds.variables.map((v, i) => (
                        <span
                          key={i}
                          className="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400"
                        >
                          #{v}
                        </span>
                      ))}
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-2 border-t border-slate-800">
                      <span>Muestra: {ds.sampleSize}</span>
                      <span>Registros: {(ds.recordsCount ?? 0).toLocaleString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
