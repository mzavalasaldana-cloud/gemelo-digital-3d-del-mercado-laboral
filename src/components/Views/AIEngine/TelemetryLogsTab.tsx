import React, { useState, useEffect, useRef } from 'react';
import { 
  Terminal, 
  Play, 
  Pause, 
  Trash2, 
  Download, 
  Copy, 
  Check, 
  Sparkles, 
  Wifi, 
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { playHoloClick } from '../../../utils/audioSynth';
import { Language, AppTheme } from '../../../types';
import { t } from '../../../utils/i18n';
import { ExplainabilityCard } from '../../Common/ExplainabilityCard';

interface TelemetryLogsTabProps {
  language?: Language;
  theme?: AppTheme;
}

const INITIAL_LOGS_ES = [
  '[2026-09-05 09:30:01] [INIT] Inicializando entorno de inferencia distribuida XGBoost v3.4 en clúster GPU NVIDIA H100...',
  '[2026-09-05 09:30:02] [DATA] Ingestando 15,420 registros sintéticos calibrados (demostración)...',
  '[2026-09-05 09:30:03] [DATA] Validación sintáctica OK. Imputación mediana/moda completada (tasa nulos: 0.8%).',
  '[2026-09-05 09:30:04] [SPLIT] Particionando datos: 80% Train (12,336) | 20% Test (3,084) con K-Fold Estratificado.',
  '[2026-09-05 09:30:06] [GPU] CUDA context creado. 8 hilos GPU asignados. Batch size: 4096.',
  '[2026-09-05 09:30:08] [EPOCH 01/50] Train Loss: 0.4820 | Val Loss: 0.4912 | ROC-AUC: 0.784 | F1: 0.742',
  '[2026-09-05 09:30:11] [EPOCH 10/50] Train Loss: 0.2814 | Val Loss: 0.2940 | ROC-AUC: 0.865 | F1: 0.820',
  '[2026-09-05 09:30:14] [EPOCH 25/50] Train Loss: 0.1650 | Val Loss: 0.1782 | ROC-AUC: 0.918 | F1: 0.884',
  '[2026-09-05 09:30:17] [EPOCH 40/50] Train Loss: 0.1142 | Val Loss: 0.1290 | ROC-AUC: 0.941 | F1: 0.905',
  '[2026-09-05 09:30:20] [EPOCH 50/50] Train Loss: 0.0924 | Val Loss: 0.1085 | ROC-AUC: 0.948 | F1: 0.912',
  '[2026-09-05 09:30:22] [CONVERGENCE] Criterio de parada temprana alcanzado (Early Stopping delta < 1e-4).',
  '[2026-09-05 09:30:23] [SHAP] Calculando valores TreeSHAP para 42 variables sociolaborales...',
  '[2026-09-05 09:30:25] [SHAP] Top driver validado: Aporte a Seguridad Social (Mean |SHAP| = +0.38).',
  '[2026-09-05 09:30:26] [AUDIT] Ejecutando Fairlearn Disparate Impact Ratio en subgrupos de género y edad...',
  '[2026-09-05 09:30:27] [AUDIT] Paridad demográfica: 0.962 (Umbral reglamentario OIT > 0.80 superado. SIN SESGO DETECTADO).',
  '[2026-09-05 09:30:28] [DEPLOY] Pesos serializados en /models/xgboost_prod_v3.4.ubj (Checksum: SHA256:8f4c2e...).',
  '[2026-09-05 09:30:29] [ACTIVE] Servicio gRPC listo para inferencia en tiempo real en puerto 50051.',
];

const INITIAL_LOGS_EN = [
  '[2026-09-05 09:30:01] [INIT] Initializing distributed inference environment XGBoost v3.4 on NVIDIA H100 GPU cluster...',
  '[2026-09-05 09:30:02] [DATA] Ingesting 15,420 synthetic calibrated records (demonstration)...',
  '[2026-09-05 09:30:03] [DATA] Syntactic validation OK. Median/mode imputation complete (null rate: 0.8%).',
  '[2026-09-05 09:30:04] [SPLIT] Splitting data: 80% Train (12,336) | 20% Test (3,084) with Stratified K-Fold.',
  '[2026-09-05 09:30:06] [GPU] CUDA context created. 8 GPU threads allocated. Batch size: 4096.',
  '[2026-09-05 09:30:08] [EPOCH 01/50] Train Loss: 0.4820 | Val Loss: 0.4912 | ROC-AUC: 0.784 | F1: 0.742',
  '[2026-09-05 09:30:11] [EPOCH 10/50] Train Loss: 0.2814 | Val Loss: 0.2940 | ROC-AUC: 0.865 | F1: 0.820',
  '[2026-09-05 09:30:14] [EPOCH 25/50] Train Loss: 0.1650 | Val Loss: 0.1782 | ROC-AUC: 0.918 | F1: 0.884',
  '[2026-09-05 09:30:17] [EPOCH 40/50] Train Loss: 0.1142 | Val Loss: 0.1290 | ROC-AUC: 0.941 | F1: 0.905',
  '[2026-09-05 09:30:20] [EPOCH 50/50] Train Loss: 0.0924 | Val Loss: 0.1085 | ROC-AUC: 0.948 | F1: 0.912',
  '[2026-09-05 09:30:22] [CONVERGENCE] Early stopping criteria met (delta < 1e-4).',
  '[2026-09-05 09:30:23] [SHAP] Computing TreeSHAP values for 42 socio-labor variables...',
  '[2026-09-05 09:30:25] [SHAP] Top driver validated: Social Security Contribution (Mean |SHAP| = +0.38).',
  '[2026-09-05 09:30:26] [AUDIT] Running Fairlearn Disparate Impact Ratio across gender and age subgroups...',
  '[2026-09-05 09:30:27] [AUDIT] Demographic parity: 0.962 (ILO statutory threshold > 0.80 passed. NO BIAS DETECTED).',
  '[2026-09-05 09:30:28] [DEPLOY] Weights serialized to /models/xgboost_prod_v3.4.ubj (Checksum: SHA256:8f4c2e...).',
  '[2026-09-05 09:30:29] [ACTIVE] gRPC service ready for real-time inference on port 50051.',
];

export const TelemetryLogsTab: React.FC<TelemetryLogsTabProps> = ({
  language = 'es',
  theme = 'dark',
}) => {
  const initialLogs = language === 'en' ? INITIAL_LOGS_EN : INITIAL_LOGS_ES;
  const [logs, setLogs] = useState<string[]>(initialLogs);
  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const [copied, setCopied] = useState<boolean>(false);
  const terminalBodyRef = useRef<HTMLDivElement>(null);

  const isLight = theme === 'light';

  // Auto-scroll when new logs arrive
  useEffect(() => {
    if (terminalBodyRef.current) {
      terminalBodyRef.current.scrollTop = terminalBodyRef.current.scrollHeight;
    }
  }, [logs]);

  // Periodic telemetry heartbeat stream
  useEffect(() => {
    if (!isStreaming) return;

    const interval = setInterval(() => {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      const randomLatency = (3.2 + Math.random() * 1.8).toFixed(1);
      const randomQPS = Math.floor(180 + Math.random() * 75);
      const heartbeatMsg = language === 'en'
        ? `[${now.toISOString().split('T')[0]} ${timeStr}] [TELEMETRY] Live inference: ${randomQPS} QPS | Mean Latency: ${randomLatency} ms | GPU Mem: 34.2% | VRAM Temp: 48°C`
        : `[${now.toISOString().split('T')[0]} ${timeStr}] [TELEMETRY] Inferencia live: ${randomQPS} QPS | Latencia media: ${randomLatency} ms | GPU Mem: 34.2% | VRAM Temp: 48°C`;

      setLogs((prev) => [...prev.slice(-40), heartbeatMsg]);
    }, 4000);

    return () => clearInterval(interval);
  }, [isStreaming, language]);

  const handleCopyLogs = () => {
    playHoloClick(1000);
    navigator.clipboard.writeText(logs.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClearLogs = () => {
    playHoloClick(600);
    setLogs([]);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* 1. TOP HEADER & METRICS BAR */}
      <div className={`hud-glass p-5 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
        isLight ? 'border-slate-300 shadow-sm' : 'border-cyan-500/25'
      }`}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono-hud text-cyan-600 dark:text-cyan-400 font-bold uppercase tracking-wider">
              {t('telemetryTitle', language)}
            </span>
            <span className="flex items-center gap-1 px-2 py-0.5 text-[10px] font-mono rounded bg-emerald-500/20 border border-emerald-400 text-emerald-500 font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              {t('liveStream', language)}
            </span>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-amber-500/20 border border-amber-400 text-amber-500 font-bold">
              Demostración
            </span>
          </div>
          <p className={`text-xs ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
            {t('telemetrySubtitle', language)}
          </p>
        </div>

        {/* Live Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              playHoloClick(800);
              setIsStreaming(!isStreaming);
            }}
            className={`px-3.5 py-1.5 rounded-xl border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              isStreaming
                ? isLight 
                  ? 'bg-amber-50 border-amber-300 text-amber-800' 
                  : 'bg-amber-500/20 border-amber-400 text-amber-300'
                : isLight 
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-800' 
                  : 'bg-emerald-500/20 border-emerald-400 text-emerald-300'
            }`}
          >
            {isStreaming ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isStreaming ? t('pauseStream', language) : t('resumeStream', language)}</span>
          </button>

          <button
            onClick={handleCopyLogs}
            className={`px-3 py-1.5 rounded-xl border text-xs font-mono flex items-center gap-1.5 transition-all cursor-pointer ${
              isLight 
                ? 'bg-white hover:bg-slate-50 border-slate-300 text-slate-700' 
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300'
            }`}
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? t('copied', language) : 'Copy'}</span>
          </button>

          <button
            onClick={handleClearLogs}
            className={`p-2 rounded-xl border transition-all cursor-pointer ${
              isLight 
                ? 'bg-white hover:bg-rose-50 border-slate-300 text-slate-600 hover:text-rose-600' 
                : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-400 hover:text-rose-400'
            }`}
            title={t('clearLogs', language)}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. TELEMETRY STATS CHIPS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
        <div className={`p-3 rounded-xl border ${
          isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900/60 border-slate-800 text-slate-200'
        }`}>
          <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{t('inferenceQPS', language)}</span>
          <span className="text-lg font-bold text-cyan-600 dark:text-cyan-400">234 QPS</span>
        </div>

        <div className={`p-3 rounded-xl border ${
          isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900/60 border-slate-800 text-slate-200'
        }`}>
          <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{t('avgLatency', language)}</span>
          <span className="text-lg font-bold text-emerald-500">3.8 ms</span>
        </div>

        <div className={`p-3 rounded-xl border ${
          isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900/60 border-slate-800 text-slate-200'
        }`}>
          <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{t('gpuUsage', language)}</span>
          <span className="text-lg font-bold text-indigo-500">34.2% VRAM</span>
        </div>

        <div className={`p-3 rounded-xl border ${
          isLight ? 'bg-white border-slate-300 text-slate-800' : 'bg-slate-900/60 border-slate-800 text-slate-200'
        }`}>
          <span className={`text-[10px] block ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>{t('activeCluster', language)}</span>
          <span className={`text-xs font-bold ${isLight ? 'text-slate-900' : 'text-white'}`}>gRPC :50051</span>
        </div>
      </div>

      {/* 3. TERMINAL STREAM CONTAINER */}
      <div className={`rounded-2xl border shadow-2xl overflow-hidden font-mono text-xs ${
        isLight ? 'bg-slate-900 border-slate-800 text-slate-100 shadow-slate-300/30' : 'bg-[#020408] border-cyan-500/30 text-slate-200'
      }`}>
        <div className="px-4 py-2.5 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-rose-500/80" />
            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            <span className="text-xs text-slate-400 font-mono ml-2">stdout / inference.log (Follow mode)</span>
          </div>
          <span className="text-[10px] text-cyan-400 font-mono">UTF-8 / TLS 1.3</span>
        </div>

        <div
          ref={terminalBodyRef}
          className="p-5 h-96 overflow-y-auto space-y-1.5 leading-relaxed selection:bg-cyan-500 selection:text-slate-950"
        >
          {logs.map((line, idx) => {
            const isError = line.includes('ERR') || line.includes('Error');
            const isWarn = line.includes('WARN') || line.includes('Alert');
            const isSuccess = line.includes('OK') || line.includes('Converged') || line.includes('EXITO') || line.includes('passed');

            return (
              <div
                key={idx}
                className={`font-mono text-[11px] ${
                  isError
                    ? 'text-rose-400 font-semibold'
                    : isWarn
                      ? 'text-amber-300'
                      : isSuccess
                        ? 'text-emerald-400 font-semibold'
                        : line.includes('TELEMETRY')
                          ? 'text-cyan-400/90'
                          : 'text-slate-300'
                }`}
              >
                {line}
              </div>
            );
          })}
        </div>
      </div>

      <ExplainabilityCard
        language={language}
        theme={theme}
        title={language === 'en' ? 'Telemetry Explainability: MLOps Real-time Inference & Ethical AI Audit' : 'Explicabilidad: Telemetría MLOps y Auditoría Ética de Sesgo'}
        variableOrMetric="GPU Inferencia (3.8ms) & Fairlearn Audit"
        whatItIs={language === 'en'
          ? 'Live observability terminal streaming distributed GPU inference metrics (QPS, VRAM, latency) and algorithmic fairness checks (Demographic Parity).'
          : 'Terminal de observabilidad en tiempo real que transmite métricas de inferencia GPU y auditorías continuas de equidad algorítmica y paridad demográfica.'}
        howToRead={language === 'en'
          ? 'Demographic parity ratio of 0.962 exceeds statutory thresholds (>0.80), mathematically certifying the model does not discriminate by gender or age.'
          : 'El ratio de paridad demográfica de 0.962 supera el umbral regulatorio (>0.80), certificando que la IA no discrimina a colectivos vulnerables.'}
        policyImpact={language === 'en'
          ? 'Provides full compliance with OECD and UNESCO guidelines on trustworthy artificial intelligence.'
          : 'Garantiza el cumplimiento normativo con las directrices de la OCDE y la UNESCO sobre Inteligencia Artificial Confiable y Ética.'}
        formulaOrMethod="Fairlearn Disparate Impact Ratio = P(Ŷ=1|Grupo Protegido) / P(Ŷ=1|Grupo Referencia)"
        benchmarksOrAlerts="Paridad Demográfica > 0.80 requerida por normativa internacional"
      />

    </div>
  );
};

