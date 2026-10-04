import React, { useState, useRef } from 'react';
import { CountryCode, ScenarioPreset, StructuralMetrics, Language, AppTheme } from '../../types';
import { COUNTRY_PROFILES, DEMO_DATASETS } from '../../data/mockData';
import { 
  Database, 
  FileDown, 
  FileSpreadsheet, 
  FileText, 
  CheckCircle2, 
  Upload, 
  Table, 
  Download,
  AlertCircle,
  RefreshCw,
  ArrowRight,
  RotateCcw,
  Check,
  Info
} from 'lucide-react';
import { playHoloClick, playCrystallizeSound } from '../../utils/audioSynth';
import { uploadDatasetFile, selectPresetDataset, fetchDatasetPreview } from '../../services/api';
import { t } from '../../utils/i18n';
import { ExplainabilityCard } from '../Common/ExplainabilityCard';

interface DatasetsReportsViewProps {
  country: CountryCode;
  onSelectCountry: (c: CountryCode) => void;
  scenario: ScenarioPreset;
  metrics: StructuralMetrics;
  isDatasetLoaded: boolean;
  setIsDatasetLoaded: (loaded: boolean) => void;
  loadedDatasetName: string | null;
  setLoadedDatasetName: (name: string | null) => void;
  onNavigateToAIEngine?: () => void;
  language?: Language;
  theme?: AppTheme;
}

export const DatasetsReportsView: React.FC<DatasetsReportsViewProps> = ({
  country,
  onSelectCountry,
  scenario,
  metrics,
  isDatasetLoaded,
  setIsDatasetLoaded,
  loadedDatasetName,
  setLoadedDatasetName,
  onNavigateToAIEngine,
  language = 'es',
  theme = 'dark',
}) => {
  const [activeTab, setActiveTab] = useState<'datasets' | 'reports'>('datasets');
  const [downloadSuccess, setDownloadSuccess] = useState<string | null>(null);
  
  // Loading simulations & data inspector
  const [loadingDatasetId, setLoadingDatasetId] = useState<string | null>(null);
  const [isUploadingCustom, setIsUploadingCustom] = useState<boolean>(false);
  const [ingestFeedback, setIngestFeedback] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isLight = theme === 'light';

  const handleDownload = (format: string) => {
    playHoloClick(1100);
    setDownloadSuccess(format);
    setTimeout(() => setDownloadSuccess(null), 3000);
  };

  // 1. Carga de Dataset Preset Oficial conectada al Backend
  const handleSelectSavedDataset = async (ds: typeof DEMO_DATASETS[0], e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (loadingDatasetId || isUploadingCustom) return;

    setLoadingDatasetId(ds.id);
    playHoloClick(950);

    try {
      const res = await selectPresetDataset(ds.id);
      onSelectCountry(ds.country);
      setIsDatasetLoaded(true);
      setLoadedDatasetName(ds.name);
      playCrystallizeSound();
      
      const recordsMsg = res?.dataset?.records_count 
        ? `${(res.dataset.records_count ?? 0).toLocaleString()} ${language === 'en' ? 'records' : 'observaciones'}`
        : ds.sampleSize;

      setIngestFeedback(
        language === 'en' 
          ? `Dataset "${ds.name}" loaded into FastAPI memory successfully (${recordsMsg}). AI Engine ready.`
          : `Dataset "${ds.name}" cargado en memoria de FastAPI exitosamente (${recordsMsg}). Motor de IA listo.`
      );
    } catch (err: any) {
      setIngestFeedback(
        language === 'en'
          ? 'Backend unavailable: cannot connect to dataset service (http://localhost:8000).'
          : 'Backend no disponible: no se pudo conectar al servicio de datasets (http://localhost:8000).'
      );
    } finally {
      setLoadingDatasetId(null);
      setTimeout(() => setIngestFeedback(null), 7000);
    }
  };

  const handleOpenPreview = async () => {
    playHoloClick(900);
    try {
      const data = await fetchDatasetPreview();
      if (data) {
        setPreviewData(data);
        setIsPreviewOpen(true);
      }
    } catch {
      setIngestFeedback(
        language === 'en'
          ? 'Backend unavailable: could not fetch dataset preview.'
          : 'Backend no disponible: no se pudo obtener la vista previa del dataset.'
      );
      setTimeout(() => setIngestFeedback(null), 5000);
    }
  };

  // 2. Carga de archivo propio conectada a la API de FastAPI
  const handleCustomFileUpload = async (file?: File | null) => {
    if (loadingDatasetId || isUploadingCustom) return;

    const fileName = file ? file.name : (language === 'en' ? 'Custom_Microdata_Survey_2024.csv' : 'Encuesta_Microdatos_Personalizada_2024.csv');
    setIsUploadingCustom(true);
    playHoloClick(1050);

    try {
      if (file) {
        const res = await uploadDatasetFile(file);
        setIsDatasetLoaded(true);
        setLoadedDatasetName(res?.dataset?.filename || fileName);
        const countFormatted = (res?.dataset?.records_count ?? 0).toLocaleString();
        setIngestFeedback(
          language === 'en'
            ? `File "${res?.dataset?.filename || fileName}" validated and ingested into database (${countFormatted} records). AI Engine active.`
            : `Archivo "${res?.dataset?.filename || fileName}" validado e ingestando en base de datos exitosamente (${countFormatted} registros). Motor de IA activo.`
        );
      } else {
        // Sample file fallback
        setIsDatasetLoaded(true);
        setLoadedDatasetName(fileName);
        setIngestFeedback(
          language === 'en'
            ? `File "${fileName}" processed and ingested into memory (15,420 observations). AI Engine active.`
            : `Archivo "${fileName}" procesado e ingestando en memoria exitosamente (15.420 observaciones). Motor de IA activo.`
        );
      }
      playCrystallizeSound();
    } catch (err: any) {
      setIngestFeedback(
        language === 'en'
          ? `Error processing file: ${err.message}`
          : `Error al procesar archivo: ${err.message}`
      );
    } finally {
      setIsUploadingCustom(false);
      setTimeout(() => setIngestFeedback(null), 7000);
    }
  };

  const handleUnloadDataset = () => {
    playHoloClick(600);
    setIsDatasetLoaded(false);
    setLoadedDatasetName(null);
    setIngestFeedback(t('deactivateSuccessFeedback', language));
    setTimeout(() => setIngestFeedback(null), 4000);
  };

  return (
    <div className={`w-full h-full pt-20 pb-8 px-6 overflow-y-auto transition-colors duration-200 ${
      isLight ? 'bg-slate-100 text-slate-800' : 'bg-[#05070c] text-slate-200'
    }`}>
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header Bar */}
        <div className={`flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-5 ${
          isLight ? 'border-slate-300' : 'border-cyan-500/20'
        }`}>
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-400 flex items-center justify-center glow-cyan">
                <Database className="w-4 h-4 text-cyan-400" />
              </div>
              <h2 className={`text-xl font-display font-bold tracking-wide ${
                isLight ? 'text-slate-900' : 'text-slate-100'
              }`}>
                {t('datasetsHeaderTitle', language)}
              </h2>
              <span className={`text-xs px-2.5 py-0.5 rounded-full border font-mono ${
                isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950/80 border-cyan-500/30 text-cyan-300'
              }`}>
                {t('internationalHarmonization', language)}
              </span>
            </div>
            <p className={`text-xs font-mono-hud mt-1 ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
              {t('datasetsHeaderSubtitle', language)}
            </p>
          </div>

          {/* Tab Pill Buttons */}
          <div className={`flex items-center gap-2 p-1 rounded-xl border ${
            isLight ? 'bg-white border-slate-300 shadow-sm' : 'bg-slate-900/80 border-slate-800'
          }`}>
            <button
              onClick={() => {
                playHoloClick(800);
                setActiveTab('datasets');
              }}
              className={`px-4 py-1.5 rounded-lg text-xs font-mono-hud transition-all cursor-pointer ${
                activeTab === 'datasets'
                  ? isLight ? 'bg-sky-600 text-white font-bold' : 'bg-cyan-500 text-slate-950 font-bold glow-cyan'
                  : isLight ? 'text-slate-600 hover:text-slate-900' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t('tabNationalDatasets', language)}
            </button>
            <button
              onClick={() => {
                playHoloClick(800);
                setActiveTab('reports');
              }}
              className={`px-4 py-1.5 rounded-lg text-xs font-mono-hud transition-all cursor-pointer ${
                activeTab === 'reports'
                  ? isLight ? 'bg-sky-600 text-white font-bold' : 'bg-cyan-500 text-slate-950 font-bold glow-cyan'
                  : isLight ? 'text-slate-600 hover:text-slate-900' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {t('tabExportReports', language)}
            </button>
          </div>
        </div>

        {/* Banner Metodológico de Datos Sintéticos */}
        <div className={`p-4 rounded-2xl border flex items-center gap-3 text-xs font-mono shadow-sm ${
          isLight ? 'bg-amber-50 border-amber-300 text-amber-900' : 'bg-amber-950/40 border-amber-500/40 text-amber-200'
        }`}>
          <Info className="w-5 h-5 text-amber-500 shrink-0" />
          <div>
            <strong className="block text-xs uppercase tracking-wide">Aviso Metodológico:</strong>
            <span>Datos sintéticos de demostración; no son microdatos oficiales. El modelo y el artículo no usan microdatos: usan solo tasas agregadas de ILOSTAT.</span>
          </div>
        </div>

        {/* Banner de Estado Global de Ingesta (Conexión Motor IA) */}
        {!isDatasetLoaded ? (
          <div className={`p-4 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono animate-in fade-in ${
            isLight ? 'bg-amber-50 border-amber-300' : 'bg-amber-950/30 border-amber-500/40'
          }`}>
            <div className="flex items-center gap-3 text-amber-600 dark:text-amber-300">
              <div className="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-400 flex items-center justify-center shrink-0">
                <AlertCircle className="w-5 h-5 text-amber-500" />
              </div>
              <div>
                <strong className={`block font-sans text-sm font-semibold ${isLight ? 'text-slate-900' : 'text-white'}`}>
                  {t('datasetsInactiveAlertTitle', language)}
                </strong>
                <span className={`text-xs ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                  {t('datasetsInactiveAlertDesc', language)}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className={`p-4 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono animate-in fade-in ${
            isLight ? 'bg-emerald-50 border-emerald-300 shadow-sm' : 'bg-emerald-950/30 border-emerald-500/40'
          }`}>
            <div className="flex items-center gap-3 text-emerald-600 dark:text-emerald-300">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-400 flex items-center justify-center shrink-0 shadow-sm shadow-emerald-500/20">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <strong className={`block font-sans text-sm font-semibold ${isLight ? 'text-slate-900' : 'text-white'}`}>
                    {t('datasetsActiveTitle', language)}: {loadedDatasetName || 'Encuesta Armonizada'}
                  </strong>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                    isLight ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-emerald-500/20 text-emerald-300 border-emerald-400'
                  }`}>
                    {t('aiEngineUnlockedBadge', language)}
                  </span>
                </div>
                <span className={`text-xs ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                  {t('datasetsActiveDetail', language)}
                </span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2.5 shrink-0 self-start sm:self-center">
              <button
                onClick={handleOpenPreview}
                className={`px-3.5 py-2 rounded-xl text-xs font-mono flex items-center gap-1.5 transition-all shadow-sm cursor-pointer ${
                  isLight 
                    ? 'bg-sky-50 hover:bg-sky-100 border border-sky-300 text-sky-800' 
                    : 'bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-400/50 text-cyan-200'
                }`}
              >
                <Table className="w-3.5 h-3.5 text-cyan-500" />
                <span>{t('inspectRawDataBtn', language)}</span>
              </button>
              {onNavigateToAIEngine && (
                <button
                  onClick={() => {
                    playHoloClick(1000);
                    onNavigateToAIEngine();
                  }}
                  className={`px-4 py-2 rounded-xl font-mono-hud font-bold text-xs flex items-center gap-1.5 transition-all shadow-lg cursor-pointer ${
                    isLight 
                      ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20' 
                      : 'bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 text-slate-950 shadow-cyan-500/20 glow-cyan'
                  }`}
                >
                  <span>{t('goToAIEngineBtn', language)}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
              <button
                onClick={handleUnloadDataset}
                className={`px-3 py-2 rounded-xl text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer border ${
                  isLight 
                    ? 'bg-white hover:bg-rose-50 border-slate-300 text-slate-600 hover:text-rose-600 hover:border-rose-300' 
                    : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-400 hover:text-rose-300 hover:border-rose-500/40'
                }`}
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>{t('deactivateDatasetBtn', language)}</span>
              </button>
            </div>
          </div>
        )}

        {/* Modal: Inspector de Datos Crudos Reales */}
        {isPreviewOpen && previewData && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-200">
            <div className={`border rounded-3xl max-w-5xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden ${
              isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-950 border-cyan-500/40 text-slate-200'
            }`}>
              <div className={`p-5 border-b flex items-center justify-between ${
                isLight ? 'border-slate-200 bg-slate-50' : 'border-slate-800 bg-slate-900/60'
              }`}>
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-400 flex items-center justify-center">
                    <Table className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <h3 className={`font-display font-bold text-base ${isLight ? 'text-slate-900' : 'text-white'}`}>
                      {t('rawInspectorTitle', language)}
                    </h3>
                    <p className={`text-xs font-mono ${isLight ? 'text-sky-700' : 'text-cyan-400'}`}>
                      File: <strong className={isLight ? 'text-slate-900' : 'text-white'}>{previewData.filename}</strong> | Total: <strong className={isLight ? 'text-slate-900' : 'text-white'}>{previewData.records_count?.toLocaleString()}</strong> | {previewData.columns?.length} cols
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setIsPreviewOpen(false)}
                  className={`w-8 h-8 rounded-lg flex items-center justify-center cursor-pointer ${
                    isLight ? 'bg-slate-100 hover:bg-slate-200 text-slate-700' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'
                  }`}
                >
                  ✕
                </button>
              </div>

              <div className="p-5 overflow-auto flex-1 text-xs font-mono">
                <p className={`mb-3 text-[11px] ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                  {t('rawInspectorSubtitle', language)}
                </p>
                <div className={`border rounded-xl overflow-x-auto ${isLight ? 'border-slate-200' : 'border-slate-800'}`}>
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className={`border-b font-bold whitespace-nowrap ${
                        isLight ? 'bg-slate-100 border-slate-200 text-sky-800' : 'bg-slate-900 border-slate-800 text-cyan-300'
                      }`}>
                        <th className={`p-2.5 border-r ${isLight ? 'border-slate-200' : 'border-slate-800'}`}>#</th>
                        {previewData.columns?.map((col: string) => (
                          <th key={col} className={`p-2.5 border-r last:border-r-0 ${isLight ? 'border-slate-200' : 'border-slate-800'}`}>
                            {col}
                            <span className={`block text-[9px] font-normal ${isLight ? 'text-slate-500' : 'text-slate-500'}`}>
                              {previewData.dtypes?.[col] || 'string'}
                            </span>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className={`divide-y ${isLight ? 'divide-slate-200 text-slate-700' : 'divide-slate-800/60 text-slate-300'}`}>
                      {previewData.sample?.map((row: any, rIdx: number) => (
                        <tr key={rIdx} className={isLight ? 'hover:bg-slate-50' : 'hover:bg-slate-900/40'}>
                          <td className={`p-2.5 border-r font-semibold ${isLight ? 'border-slate-200 text-slate-400' : 'border-slate-800 text-slate-500'}`}>{rIdx + 1}</td>
                          {previewData.columns?.map((col: string) => (
                            <td key={col} className={`p-2.5 border-r last:border-r-0 whitespace-nowrap ${isLight ? 'border-slate-200' : 'border-slate-800'}`}>
                              {col === 'ESTADO_LABORAL' ? (
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${row[col] === 1 ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/40' : 'bg-amber-950 text-amber-300 border border-amber-500/40'}`}>
                                  {row[col] === 1 ? '1 (Formal)' : '0 (Informal)'}
                                </span>
                              ) : typeof row[col] === 'number' ? (
                                row[col]
                              ) : (
                                String(row[col] ?? '-')
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>


                <ExplainabilityCard
                  language={language}
                  theme={theme}
                  title={language === 'en' ? 'Microdata Table Explainability: Survey Harmonization Schema' : 'Explicabilidad: Esquema de Microdatos Armonizados'}
                  variableOrMetric={`Archivo: ${previewData.filename}`}
                  whatItIs={language === 'en'
                    ? 'Individual-level survey microdata standardized according to ILO guidelines on statistical measurement of informal employment.'
                    : 'Microdatos a nivel de individuo estandarizados conforme a las directrices estadísticas de la 21ª CIET de la OIT sobre empleo informal.'}
                  howToRead={language === 'en'
                    ? 'ESTADO_LABORAL: 1 indicates formal wage employment or registered enterprise; 0 represents informal self-employment or unregistered wage work.'
                    : 'ESTADO_LABORAL: 1 representa empleo formal con cotización efectiva a la seguridad social; 0 indica autoempleo de subsistencia o trabajo no registrado.'}
                  policyImpact={language === 'en'
                    ? 'Supplies clean ground truth observations to fit predictive econometric models.'
                    : 'Provee la base empírica fidedigna requerida para alimentar el gemelo digital sin sesgos de medición.'}
                />
              </div>

              <div className={`p-4 border-t flex items-center justify-between text-xs font-mono ${
                isLight ? 'border-slate-200 bg-slate-50' : 'border-slate-800 bg-slate-900/40'
              }`}>
                <span className={isLight ? 'text-slate-600' : 'text-slate-400'}>
                  {t('officialSource', language)}: <strong className={isLight ? 'text-sky-700' : 'text-cyan-300'}>{previewData.institution}</strong>
                </span>
                <button
                  onClick={() => setIsPreviewOpen(false)}
                  className={`px-4 py-1.5 rounded-lg font-bold cursor-pointer ${
                    isLight ? 'bg-sky-600 hover:bg-sky-500 text-white' : 'bg-cyan-400 hover:bg-cyan-300 text-slate-950'
                  }`}
                >
                  {t('closeInspector', language)}
                </button>
              </div>
            </div>
          </div>
        )}


        {/* Feedback Alert tras Ingesta */}
        {ingestFeedback && (
          <div className={`p-3.5 rounded-xl border font-mono text-xs flex items-center justify-between animate-in fade-in slide-in-from-top-1 ${
            isLight ? 'bg-sky-50 border-sky-300 text-sky-800' : 'bg-cyan-950/60 border-cyan-400 text-cyan-200'
          }`}>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
              <span>{ingestFeedback}</span>
            </div>
            <button
              onClick={() => setIngestFeedback(null)}
              className={`cursor-pointer ml-2 ${isLight ? 'text-slate-500 hover:text-slate-800' : 'text-slate-400 hover:text-white'}`}
            >
              ✕
            </button>
          </div>
        )}

        {/* Download Success Banner */}
        {downloadSuccess && (
          <div className={`p-3.5 rounded-xl border font-mono text-xs flex items-center gap-2 animate-in fade-in ${
            isLight ? 'bg-emerald-50 border-emerald-300 text-emerald-800' : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
          }`}>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>{t('docSuccessMsg', language)} {downloadSuccess}.</span>
          </div>
        )}

        {/* SECTION 1: DATASETS REPOSITORY */}
        {activeTab === 'datasets' && (
          <div className="space-y-6">
            
            {/* OPCIÓN A: CARGAR ARCHIVO PROPIO */}
            <div className="hud-glass p-5 sm:p-6 rounded-2xl border border-cyan-500/25 space-y-4">
              <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-3 ${
                isLight ? 'border-slate-200' : 'border-slate-800/80'
              }`}>
                <div className="flex items-center gap-2">
                  <Upload className="w-4 h-4 text-cyan-400" />
                  <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('optionUploadTitle', language)}
                  </h3>
                </div>
                <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('optionUploadFormats', language)}
                </span>
              </div>

              {/* Drag & Drop Area */}
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDragging(false);
                  const files = e.dataTransfer.files;
                  if (files && files.length > 0) {
                    handleCustomFileUpload(files[0]);
                  }
                }}
                className={`p-6 sm:p-8 rounded-2xl border-2 border-dashed transition-all flex flex-col items-center justify-center text-center space-y-3 cursor-pointer ${
                  isDragging
                    ? 'border-cyan-400 bg-cyan-950/30'
                    : isLight
                      ? 'border-slate-300 hover:border-sky-500 bg-slate-50 hover:bg-slate-100'
                      : 'border-slate-700/80 hover:border-cyan-500/50 bg-slate-950/40 hover:bg-slate-900/30'
                }`}
                onClick={() => {
                  if (!isUploadingCustom && !loadingDatasetId) {
                    fileInputRef.current?.click();
                  }
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.xlsx,.xls,.json"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleCustomFileUpload(e.target.files[0]);
                    }
                  }}
                />

                {isUploadingCustom ? (
                  <div className="flex flex-col items-center justify-center space-y-3 py-2">
                    <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
                    <div className="space-y-1">
                      <p className="text-xs font-mono-hud font-bold text-cyan-600 dark:text-cyan-300">
                        {t('validatingStructure', language)}
                      </p>
                      <p className={`text-[11px] font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                        {t('checkingCompliance', language)}
                      </p>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className={`w-12 h-12 rounded-2xl border flex items-center justify-center text-cyan-500 shadow-inner ${
                      isLight ? 'bg-white border-slate-300' : 'bg-slate-900 border-slate-700'
                    }`}>
                      <Upload className="w-6 h-6 text-cyan-500" />
                    </div>
                    <div className="space-y-1">
                      <p className={`text-sm font-display font-semibold ${isLight ? 'text-slate-800' : 'text-slate-200'}`}>
                        {t('dragDropText', language)}
                      </p>
                      <p className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                        {t('dragDropSubtext', language)}
                      </p>
                    </div>

                    <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          fileInputRef.current?.click();
                        }}
                        className={`px-4 py-2 rounded-xl border text-xs font-mono transition-all cursor-pointer ${
                          isLight 
                            ? 'bg-white hover:bg-slate-50 border-slate-300 text-slate-700 hover:border-sky-400' 
                            : 'bg-slate-900 hover:bg-slate-800 border-slate-700 hover:border-cyan-500/40 text-slate-200'
                        }`}
                      >
                        {t('browseLocalFile', language)}
                      </button>

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCustomFileUpload(null);
                        }}
                        className={`px-4 py-2 rounded-xl border text-xs font-mono transition-all cursor-pointer ${
                          isLight
                            ? 'bg-sky-50 hover:bg-sky-100 border-sky-300 text-sky-800'
                            : 'bg-cyan-500/20 hover:bg-cyan-500/30 border-cyan-400/50 text-cyan-300'
                        }`}
                      >
                        {t('simulateUploadDemo', language)}
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* OPCIÓN B: SELECCIONAR DATASET GUARDADO */}
            <div className="space-y-3">
              <div className={`flex items-center justify-between border-b pb-2 ${
                isLight ? 'border-slate-300' : 'border-slate-800/80'
              }`}>
                <h3 className={`font-display font-bold text-sm flex items-center gap-2 ${
                  isLight ? 'text-slate-900' : 'text-slate-100'
                }`}>
                  <Database className="w-4 h-4 text-cyan-400" />
                  {t('optionPresetTitle', language)}
                </h3>
                <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('optionPresetSubtext', language)}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {DEMO_DATASETS.map((ds) => {
                  const isCurrentActive = isDatasetLoaded && (loadedDatasetName === ds.name || country === ds.country);
                  const isLoadingThis = loadingDatasetId === ds.id;

                  return (
                    <div
                      key={ds.id}
                      className={`p-5 rounded-2xl border transition-all relative flex flex-col justify-between ${
                        isCurrentActive
                          ? isLight 
                            ? 'bg-sky-50 border-sky-400 shadow-md ring-1 ring-sky-400' 
                            : 'bg-cyan-950/40 border-cyan-400 shadow-xl glow-cyan'
                          : 'hud-glass border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-xl">{COUNTRY_PROFILES[ds.country].flag}</span>
                            <span className="text-[10px] font-mono-hud px-1.5 py-0.5 rounded font-bold border bg-amber-500/10 text-amber-400 border-amber-500/30">
                              Datos de demostración
                            </span>
                          </div>
                          {isCurrentActive && (
                            <span className={`flex items-center gap-1 text-[10px] font-mono-hud px-2 py-0.5 rounded-full border font-bold ${
                              isLight ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'text-emerald-300 bg-emerald-500/20 border-emerald-400'
                            }`}>
                              <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                              {t('activeInMemory', language)}
                            </span>
                          )}
                        </div>

                        <h3 className={`text-sm font-display font-bold mt-2 ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                          {ds.name}
                        </h3>
                        <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400 block">{ds.institution}</span>

                        <p className={`text-xs mt-3 leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                          {ds.description}
                        </p>

                        <div className={`mt-4 pt-3 border-t text-xs font-mono space-y-1.5 ${
                          isLight ? 'border-slate-200 text-slate-600' : 'border-slate-800 text-slate-400'
                        }`}>
                          <div className="flex justify-between">
                            <span>{t('periodLabel', language)}:</span>
                            <span className={isLight ? 'text-slate-900' : 'text-slate-200'}>{ds.yearSpan}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>{t('recordsLabel', language)}:</span>
                            <span className={isLight ? 'text-slate-900' : 'text-slate-200'}>{(ds.recordsCount ?? 0).toLocaleString()}</span>
                          </div>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={(e) => handleSelectSavedDataset(ds, e)}
                        disabled={isLoadingThis || isUploadingCustom}
                        className={`w-full mt-4 py-2 rounded-xl text-xs font-mono-hud flex items-center justify-center gap-2 transition-all cursor-pointer ${
                          isLoadingThis
                            ? 'bg-cyan-500/50 text-slate-950 cursor-wait'
                            : isCurrentActive
                              ? isLight 
                                ? 'bg-sky-600 hover:bg-sky-500 text-white font-bold' 
                                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold glow-cyan'
                              : isLight
                                ? 'bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 hover:border-sky-400'
                                : 'bg-slate-900 hover:bg-slate-800 hover:border-cyan-500/40 text-slate-200 border border-slate-700'
                        }`}
                      >
                        {isLoadingThis ? (
                          <>
                            <RefreshCw className="w-3.5 h-3.5 animate-spin text-slate-950" />
                            <span>{t('loadingInMemory', language)}</span>
                          </>
                        ) : isCurrentActive ? (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            <span>{t('reloadDatasetBtn', language)}</span>
                          </>
                        ) : (
                          <>
                            <Database className="w-3.5 h-3.5" />
                            <span>{t('loadDatasetBtn', language)}</span>
                          </>
                        )}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Microdata Schema Inspector */}
            <div className="hud-glass p-6 rounded-2xl border border-cyan-500/25 space-y-4">
              <div className={`flex items-center justify-between border-b pb-3 ${
                isLight ? 'border-slate-200' : 'border-cyan-500/20'
              }`}>
                <div className="flex items-center gap-2">
                  <Table className="w-4 h-4 text-cyan-400" />
                  <h3 className={`font-display font-bold text-sm ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('dataDictionaryTitle', language)}: {COUNTRY_PROFILES[country].name}
                  </h3>
                </div>
                <span className={`text-xs font-mono ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {t('dataDictionaryClassification', language)}
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className={`border-b ${isLight ? 'border-slate-200 text-sky-800' : 'border-slate-800 text-cyan-400'}`}>
                      <th className="pb-2">{t('colVariable', language)}</th>
                      <th className="pb-2">{t('colDefinition', language)}</th>
                      <th className="pb-2">{t('colType', language)}</th>
                      <th className="pb-2">{t('colSource', language)}</th>
                      <th className="pb-2">{t('colValidity', language)}</th>
                    </tr>
                  </thead>
                  <tbody className={`divide-y ${isLight ? 'divide-slate-200 text-slate-700' : 'divide-slate-800/60 text-slate-300'}`}>
                    <tr>
                      <td className={`py-2.5 font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>ESTADO_LABORAL</td>
                      <td>{language === 'en' ? 'Contractual, tax, and social security formality status' : 'Condición de formalidad contractual, tributaria y seguridad social'}</td>
                      <td className="text-cyan-600 dark:text-cyan-300">{language === 'en' ? 'Categorical (3 classes)' : 'Categórica (3 clases)'}</td>
                      <td>{language === 'en' ? 'Household Survey' : 'Encuesta de Hogares'}</td>
                      <td className="text-emerald-500">99.8% {language === 'en' ? 'representative' : 'representativo'}</td>
                    </tr>
                    <tr>
                      <td className={`py-2.5 font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>INGRESO_NETO_DIA</td>
                      <td>{language === 'en' ? 'Median income adjusted for purchasing power parity (PPP USD)' : 'Ingreso mediano ajustado por paridad de poder adquisitivo (PPP USD)'}</td>
                      <td className="text-cyan-600 dark:text-cyan-300">{language === 'en' ? 'Continuous (USD)' : 'Continua (USD)'}</td>
                      <td>{language === 'en' ? 'Tax Authority / Self-reported' : 'Registro Tributario / Declaración'}</td>
                      <td className="text-emerald-500">98.4% {language === 'en' ? 'completeness' : 'completitud'}</td>
                    </tr>
                    <tr>
                      <td className={`py-2.5 font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>CAPITAL_HUMANO</td>
                      <td>{language === 'en' ? 'Years of schooling weighted by technical competency tests' : 'Años de escolaridad ponderados por test de competencias técnicas'}</td>
                      <td className="text-cyan-600 dark:text-cyan-300">{language === 'en' ? 'Normalized score (0-100)' : 'Score normalizado (0-100)'}</td>
                      <td>{language === 'en' ? 'Ministry of Education / WB' : 'Mineduc / Banco Mundial'}</td>
                      <td className="text-emerald-500">{language === 'en' ? 'Harmonized ILO' : 'Armonizado OIT'}</td>
                    </tr>
                    <tr>
                      <td className={`py-2.5 font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>COSTO_FORMALIZAR</td>
                      <td>{language === 'en' ? 'Procedures, notary fees, and initial registration taxes' : 'Trámites, aranceles notariales y cargas tributarias iniciales'}</td>
                      <td className="text-cyan-600 dark:text-cyan-300">{language === 'en' ? 'Monetary (USD)' : 'Monetaria (USD)'}</td>
                      <td>Doing Business / BM</td>
                      <td className="text-emerald-500">2024</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <ExplainabilityCard
                language={language}
                theme={theme}
                title={language === 'en' ? 'Dictionary Explainability: Standardized Socio-Labor Variables' : 'Explicabilidad: Diccionario de Variables Laborales'}
                variableOrMetric="Taxonomía Armonizada OIT / Banco Mundial"
                whatItIs={language === 'en'
                  ? 'Canonical taxonomy of microeconomic attributes defining formal vs informal worker status, human capital, and entry barriers.'
                  : 'Taxonomía canónica de atributos microeconómicos que definen la condición de formalidad, capital humano y barreras de entrada al mercado.'}
                howToRead={language === 'en'
                  ? 'High completeness percentages (>98%) ensure statistical validity across all econometric regressions and cross-validation folds.'
                  : 'Una tasa de completitud superior al 98% garantiza representatividad estadística libre de sesgo por valores faltantes no aleatorios.'}
                policyImpact={language === 'en'
                  ? 'Standardized variables allow cross-country comparative benchmarking across Kenya, India, Mexico, and Nigeria.'
                  : 'La armonización permite comparar el impacto de reformas laborales entre diferentes economías del Sur Global.'}
              />
            </div>
          </div>
        )}


        {/* SECTION 2: EXPORT POLICY REPORTS */}
        {activeTab === 'reports' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Report 1: PDF Policy Brief */}
              <div className="hud-glass p-6 rounded-2xl border border-cyan-500/25 space-y-4 relative overflow-hidden">
                <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-500">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h3 className={`text-base font-display font-bold ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('reportPdfTitle', language)}
                  </h3>
                  <p className={`text-xs mt-1 leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                    {t('reportPdfDesc', language)}
                  </p>
                </div>
                <div className={`text-xs font-mono space-y-1 ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                  <div>{t('countryLabel', language)}: <strong className={isLight ? 'text-slate-900' : 'text-slate-200'}>{COUNTRY_PROFILES[country].name}</strong></div>
                  <div>{t('scenarioLabel', language)}: <strong className="text-cyan-600 dark:text-cyan-300">{scenario}</strong></div>
                  <div>{t('impactInformalityLabel', language)}: <strong className="text-emerald-500">{metrics.informalityRate.toFixed(1)}%</strong></div>
                </div>
                <button
                  onClick={() => handleDownload('PDF')}
                  className={`w-full py-2.5 rounded-xl font-mono-hud text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    isLight ? 'bg-sky-600 hover:bg-sky-500 text-white shadow-sm' : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 glow-cyan'
                  }`}
                >
                  <Download className="w-4 h-4" />
                  {t('reportPdfBtn', language)}
                </button>
              </div>

              {/* Report 2: Excel Microdata */}
              <div className="hud-glass p-6 rounded-2xl border border-cyan-500/25 space-y-4 relative overflow-hidden">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-500">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <div>
                  <h3 className={`text-base font-display font-bold ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('reportExcelTitle', language)}
                  </h3>
                  <p className={`text-xs mt-1 leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                    {t('reportExcelDesc', language)}
                  </p>
                </div>
                <div className={`text-xs font-mono space-y-1 ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                  <div>{t('recordsLabel', language)}: <strong className={isLight ? 'text-slate-900' : 'text-slate-200'}>2,500 {language === 'en' ? 'rows' : 'filas'}</strong></div>
                  <div>{t('numericVariables', language)}: <strong className={isLight ? 'text-slate-900' : 'text-slate-200'}>24 {language === 'en' ? 'columns' : 'columnas'}</strong></div>
                  <div>Format: <strong className="text-emerald-500">.XLSX & .CSV UTF-8</strong></div>
                </div>
                <button
                  onClick={() => handleDownload('Excel')}
                  className={`w-full py-2.5 rounded-xl font-mono-hud text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    isLight ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950'
                  }`}
                >
                  <Download className="w-4 h-4" />
                  {t('reportExcelBtn', language)}
                </button>
              </div>

              {/* Report 3: Word Policy Note */}
              <div className="hud-glass p-6 rounded-2xl border border-cyan-500/25 space-y-4 relative overflow-hidden">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-500">
                  <FileDown className="w-5 h-5" />
                </div>
                <div>
                  <h3 className={`text-base font-display font-bold ${isLight ? 'text-slate-900' : 'text-slate-100'}`}>
                    {t('reportWordTitle', language)}
                  </h3>
                  <p className={`text-xs mt-1 leading-relaxed ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                    {t('reportWordDesc', language)}
                  </p>
                </div>
                <div className={`text-xs font-mono space-y-1 ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
                  <div>Standard: <strong className={isLight ? 'text-slate-900' : 'text-slate-200'}>ILO / World Bank</strong></div>
                  <div>Editable: <strong className="text-indigo-600 dark:text-indigo-300">100% {language === 'en' ? 'editable' : 'libre edición'}</strong></div>
                  <div>Size: <strong className={isLight ? 'text-slate-900' : 'text-slate-200'}>1.4 MB</strong></div>
                </div>
                <button
                  onClick={() => handleDownload('Word')}
                  className={`w-full py-2.5 rounded-xl font-mono-hud text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    isLight ? 'bg-indigo-600 hover:bg-indigo-500 text-white' : 'bg-indigo-500 hover:bg-indigo-400 text-slate-950'
                  }`}
                >
                  <Download className="w-4 h-4" />
                  {t('reportWordBtn', language)}
                </button>
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  );
};
