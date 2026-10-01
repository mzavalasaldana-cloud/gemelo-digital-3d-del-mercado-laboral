import React, { useState, useEffect, useRef } from 'react';
import { UserRole, MLAlgorithmMetric } from '../../types';
import { 
  MOCK_ML_ALGORITHMS, 
  MOCK_COHORTS 
} from '../../data/mockData';
import { 
  X, 
  Cpu, 
  Trophy, 
  Target, 
  RefreshCw, 
  Terminal, 
  ScatterChart, 
  GitBranch, 
  Sliders, 
  Activity, 
  CheckCircle2, 
  AlertTriangle,
  Play,
  RotateCcw
} from 'lucide-react';
import { playHoloClick } from '../../utils/audioSynth';

interface AIEngineModalProps {
  isOpen: boolean;
  onClose: () => void;
  role: UserRole;
  onRetrainTriggered: () => void;
}

export const AIEngineModal: React.FC<AIEngineModalProps> = ({
  isOpen,
  onClose,
  role,
  onRetrainTriggered,
}) => {
  const [activeSection, setActiveSection] = useState<'compare' | 'cohorts' | 'eda' | 'kfolds' | 'hyperparams' | 'stats'>('compare');
  const [weightPrecision, setWeightPrecision] = useState(60); // 60% precision vs 40% interpretability
  const [isRetraining, setIsRetraining] = useState(false);
  const [trainingLogs, setTrainingLogs] = useState<string[]>([
    '[INIT] Cargando microdatos armonizados del mercado laboral...',
    '[TENSOR] Preprocesamiento de 1,245,900 registros completado.',
    '[MODEL] Inferencia distribuida XGBoost v3.4 activa.',
    '[STATUS] Convergencia alcanzada en época 42. Loss: 0.0841.',
  ]);
  const [selectedCohort, setSelectedCohort] = useState(MOCK_COHORTS[0]);
  const [activeFold, setActiveFold] = useState(2);
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Hyperparameters dial states
  const [hyperparams, setHyperparams] = useState({
    maxDepth: 6,
    learningRate: 0.045,
    nEstimators: 350,
    l2Reg: 0.012,
  });

  const canRetrain = role === 'ADMIN';

  // Calculate composite score based on user weighting
  const getRankedAlgorithms = () => {
    return [...MOCK_ML_ALGORITHMS].map((algo) => {
      const precisionScore = algo.f1Score * 100;
      const interpScore = algo.interpretability;
      const composite = (precisionScore * (weightPrecision / 100)) + (interpScore * ((100 - weightPrecision) / 100));
      return { ...algo, compositeScore: composite };
    }).sort((a, b) => b.compositeScore - a.compositeScore);
  };

  const rankedAlgos = getRankedAlgorithms();
  const bestAlgo = rankedAlgos[0];

  // Handle Retrain Simulation
  const handleRetrain = () => {
    if (!canRetrain || isRetraining) return;
    setIsRetraining(true);
    onRetrainTriggered();
    playHoloClick(1200);

    const steps = [
      '[RETRAIN] Pausando simulación física del gemelo digital...',
      '[TELEMETRY] Transfiriendo ráfagas de datos de 4 países al centro de cálculo...',
      '[KFOLD] Repartiendo datos en 5 folds estratificados...',
      '[EPOCH 10/50] Loss: 0.324 | ROC-AUC: 0.812 | Validando...',
      '[EPOCH 25/50] Loss: 0.165 | ROC-AUC: 0.894 | Optimizando gradientes...',
      '[EPOCH 40/50] Loss: 0.078 | ROC-AUC: 0.941 | Early stopping check...',
      '[EPOCH 50/50] Convergencia óptima: XGBoost F1-Score 0.924 | ROC-AUC 0.952!',
      '[DEPLOY] Pesos actualizados en el motor central. Reanudando gemelo.',
    ];

    steps.forEach((msg, idx) => {
      setTimeout(() => {
        setTrainingLogs((prev) => [...prev, msg]);
        if (logContainerRef.current) {
          logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
        if (idx === steps.length - 1) {
          setIsRetraining(false);
        }
      }, (idx + 1) * 600);
    });
  };

  // Auto-tune hyperparameters simulation
  const handleAutoTune = () => {
    playHoloClick(950);
    setHyperparams({
      maxDepth: Math.floor(Math.random() * 4) + 5,
      learningRate: Number((Math.random() * 0.05 + 0.02).toFixed(3)),
      nEstimators: Math.floor(Math.random() * 200) + 300,
      l2Reg: Number((Math.random() * 0.02 + 0.005).toFixed(3)),
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-xl animate-fadeIn">
      <div className="hud-glass-solid w-full max-w-5xl h-[88vh] rounded-3xl border border-cyan-500/40 shadow-2xl flex flex-col overflow-hidden holo-corner-tl">
        {/* Top Header */}
        <div className="px-6 py-4 border-b border-cyan-500/20 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-400 glow-cyan">
              <Cpu className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-display font-bold text-lg text-slate-100 tracking-wide">
                  MOTOR IA: CEREBRO ANALÍTICO DEL GEMELO DIGITAL
                </h2>
                <span className="text-[10px] font-mono-hud px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-700">
                  ML AUDIT CORE v4.2
                </span>
              </div>
              <p className="text-xs font-mono-hud text-slate-400">
                Auditoría econométrica y algoritmos de transición formal-informal
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {canRetrain ? (
              <button
                onClick={handleRetrain}
                disabled={isRetraining}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-600 hover:from-amber-400 hover:to-red-500 text-slate-950 font-bold font-mono-hud text-xs flex items-center gap-2 shadow-lg glow-amber transition-all disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${isRetraining ? 'animate-spin' : ''}`} />
                <span>{isRetraining ? 'REENTRENANDO MOTOR...' : 'REENTRENAR MODELO'}</span>
              </button>
            ) : (
              <div className="text-[11px] font-mono-hud text-slate-400 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                <span>Reentrenamiento restringido a Administrador</span>
              </div>
            )}

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
        </div>

        {/* Section Navigation Tabs */}
        <div className="px-6 py-2.5 border-b border-cyan-500/15 flex items-center gap-2 overflow-x-auto bg-slate-950/20 font-mono-hud text-xs">
          {[
            { id: 'compare', label: 'Comparativa de Algoritmos', icon: Trophy },
            { id: 'cohorts', label: 'Predicción por Cohortes', icon: Target },
            { id: 'eda', label: 'EDA: Correlaciones 3D', icon: ScatterChart },
            { id: 'kfolds', label: 'Validación Cruzada K-Fold', icon: GitBranch },
            { id: 'hyperparams', label: 'Optimización Hiperparámetros', icon: Sliders },
            { id: 'stats', label: 'Pruebas Estadísticas & P-Values', icon: Activity },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  playHoloClick(850);
                  setActiveSection(tab.id as typeof activeSection);
                }}
                className={`px-3 py-1.5 rounded-xl flex items-center gap-2 transition-all whitespace-nowrap ${
                  activeSection === tab.id
                    ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/50 glow-cyan'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className="w-3.5 h-3.5 text-cyan-400" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* SECTION 1: COMPARATIVA DE ALGORITMOS & PODIO */}
          {activeSection === 'compare' && (
            <div className="space-y-6">
              {/* Golden Podium Winner */}
              <div className="p-5 rounded-2xl bg-gradient-to-r from-amber-500/10 via-amber-400/5 to-transparent border border-amber-500/40 flex flex-col md:flex-row items-center justify-between gap-4 glow-amber">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-amber-500/20 border border-amber-400 flex items-center justify-center text-amber-300 shadow-xl">
                    <Trophy className="w-8 h-8 text-amber-400 animate-bounce" />
                  </div>
                  <div>
                    <div className="text-[10px] font-mono-hud text-amber-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                      PODIO LUMÍNICO: ALGORITMO GANADOR DESPLEGADO
                    </div>
                    <h3 className="font-display font-bold text-xl text-amber-200">
                      {bestAlgo.name}
                    </h3>
                    <p className="text-xs font-mono-hud text-slate-300">
                      Mayor equilibrio ponderado entre poder predictivo (ROC-AUC {bestAlgo.rocAuc}) e interpretabilidad SHAP ({bestAlgo.interpretability}%).
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 font-mono-hud text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-amber-500/30 text-center">
                    <div className="text-[10px] text-slate-400">Score Ponderado</div>
                    <div className="text-lg font-bold text-amber-300">
                      {bestAlgo.compositeScore?.toFixed(1)} /100
                    </div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-amber-500/30 text-center">
                    <div className="text-[10px] text-slate-400">Latencia Inferencia</div>
                    <div className="text-lg font-bold text-cyan-300">
                      {bestAlgo.latencyMs} ms
                    </div>
                  </div>
                </div>
              </div>

              {/* Slider de Ponderación Criterios: Interpretabilidad vs Precisión */}
              <div className="p-4 rounded-2xl bg-slate-900/50 border border-cyan-500/20 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono-hud">
                  <span className="text-slate-300">Criterio Ponderado: Interpretabilidad vs Precisión</span>
                  <div className="space-x-3 text-cyan-300 font-semibold">
                    <span>Precisión: {weightPrecision}%</span>
                    <span>•</span>
                    <span>Interpretabilidad: {100 - weightPrecision}%</span>
                  </div>
                </div>
                <input
                  type="range"
                  min={10}
                  max={90}
                  value={weightPrecision}
                  onChange={(e) => setWeightPrecision(Number(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                />
                <div className="flex justify-between text-[10px] font-mono-hud text-slate-500">
                  <span>← Priorizar Caja Blanca / Explicabilidad Política</span>
                  <span>Priorizar F1-Score Máximo / Deep Learning →</span>
                </div>
              </div>

              {/* Algoritmos en Tabla / Tarjetas Volumétricas */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {rankedAlgos.map((algo, rank) => (
                  <div
                    key={algo.id}
                    className={`p-4 rounded-2xl border transition-all font-mono-hud text-xs space-y-3 ${
                      rank === 0
                        ? 'bg-amber-500/10 border-amber-500/50 glow-amber'
                        : 'bg-slate-900/60 border-slate-800 hover:border-cyan-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] text-cyan-400 font-bold block">
                          RANK #{rank + 1}
                        </span>
                        <h4 className="font-bold text-slate-200 text-sm">{algo.name}</h4>
                      </div>
                      {algo.isDeployed && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700">
                          ACTIVO EN 3D
                        </span>
                      )}
                    </div>

                    <div className="space-y-2 pt-2 border-t border-slate-800">
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>F1-Score / Precisión:</span>
                          <span className="text-cyan-300 font-bold">{(algo.f1Score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-cyan-400 h-full rounded-full"
                            style={{ width: `${algo.f1Score * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>Área bajo la curva (ROC-AUC):</span>
                          <span className="text-indigo-300 font-bold">{algo.rocAuc.toFixed(3)}</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-indigo-400 h-full rounded-full"
                            style={{ width: `${algo.rocAuc * 100}%` }}
                          />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>Interpretabilidad SHAP:</span>
                          <span className="text-amber-300 font-bold">{algo.interpretability}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-amber-400 h-full rounded-full"
                            style={{ width: `${algo.interpretability}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION 2: PREDICCIÓN POR COHORTES */}
          {activeSection === 'cohorts' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Cohort Selector List */}
                <div className="space-y-2">
                  <h3 className="text-xs font-mono-hud text-cyan-400 uppercase tracking-wider font-semibold">
                    Seleccionar Clúster Vulnerable:
                  </h3>
                  {MOCK_COHORTS.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => {
                        playHoloClick(800);
                        setSelectedCohort(c);
                      }}
                      className={`w-full p-3 rounded-xl border text-left font-mono-hud text-xs transition-all ${
                        selectedCohort.id === c.id
                          ? 'bg-cyan-500/20 text-cyan-200 border-cyan-400 glow-cyan'
                          : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="font-semibold text-slate-200 text-sm mb-1">{c.label}</div>
                      <div className="text-[10px] text-slate-400">
                        Población estimada: {c.populationShare}% del mercado informal
                      </div>
                    </button>
                  ))}
                </div>

                {/* Cohort Horizon Projections (1, 3, 5 years) */}
                <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/60 border border-cyan-500/30 space-y-5">
                  <div>
                    <span className="text-[10px] font-mono-hud text-cyan-400 uppercase tracking-wider">
                      FOCALIZACIÓN DE POLÍTICA ACTIVA
                    </span>
                    <h3 className="font-display font-bold text-lg text-slate-100">
                      {selectedCohort.label}
                    </h3>
                  </div>

                  {/* Horizon Bar Cylinders */}
                  <div className="grid grid-cols-3 gap-4 text-center font-mono-hud">
                    <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block mb-1">Horizonte 1 Año</span>
                      <span className="text-2xl font-bold text-cyan-300 block mb-2">
                        {selectedCohort.prob1Year}%
                      </span>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-cyan-400 h-full"
                          style={{ width: `${selectedCohort.prob1Year}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-950/60 border border-cyan-500/40 glow-cyan">
                      <span className="text-[10px] text-cyan-400 block mb-1">Horizonte 3 Años</span>
                      <span className="text-3xl font-extrabold text-cyan-200 block mb-2">
                        {selectedCohort.prob3Year}%
                      </span>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-cyan-400 h-full"
                          style={{ width: `${selectedCohort.prob3Year}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block mb-1">Horizonte 5 Años</span>
                      <span className="text-2xl font-bold text-emerald-300 block mb-2">
                        {selectedCohort.prob5Year}%
                      </span>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-emerald-400 h-full"
                          style={{ width: `${selectedCohort.prob5Year}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* SHAP Factor Driver */}
                  <div className="p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/30 font-mono-hud text-xs flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-cyan-400 block uppercase">
                        Factor SHAP con Mayor Impacto Marginal:
                      </span>
                      <span className="font-bold text-slate-100 text-sm">
                        {selectedCohort.topDriver}
                      </span>
                    </div>
                    <span className="text-xs px-2.5 py-1 rounded bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/40">
                      +28.4% Probabilidad Neta
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 3: EDA NUBE DE PUNTOS CORRELACIÓN */}
          {activeSection === 'eda' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-display font-bold text-base text-slate-100">
                    Análisis Exploratorio de Datos (EDA Multidimensional)
                  </h3>
                  <p className="text-xs font-mono-hud text-slate-400">
                    Correlación entre Nivel de Educación, Edad y Rendimiento de Ingreso (Muestra representativa de 400 microdatos)
                  </p>
                </div>
              </div>

              {/* Interactive Scatter Canvas Simulation */}
              <div className="h-72 w-full rounded-2xl bg-slate-950/80 border border-cyan-500/30 p-4 relative overflow-hidden flex flex-col justify-between">
                <div className="flex items-center justify-between text-[11px] font-mono-hud text-slate-400">
                  <span>Y: Ingreso Diario USD ($0 a $60)</span>
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1.5 text-cyan-400">
                      <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Sector Formal
                    </span>
                    <span className="flex items-center gap-1.5 text-amber-400">
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Sector Informal
                    </span>
                  </div>
                </div>

                {/* Simulated Scatter Points SVG */}
                <svg className="w-full h-48">
                  {/* Grid lines */}
                  {[0.2, 0.4, 0.6, 0.8].map((ratio, i) => (
                    <line
                      key={i}
                      x1="0"
                      y1={`${ratio * 100}%`}
                      x2="100%"
                      y2={`${ratio * 100}%`}
                      stroke="rgba(0, 240, 255, 0.08)"
                      strokeDasharray="4 4"
                    />
                  ))}
                  {/* Formal points (higher income, higher education) */}
                  {Array.from({ length: 45 }).map((_, i) => {
                    const cx = `${35 + (i * 1.3) + Math.sin(i) * 8}%`;
                    const cy = `${20 + Math.cos(i * 2) * 18 + (45 - i) * 0.8}%`;
                    return (
                      <circle
                        key={`f-${i}`}
                        cx={cx}
                        cy={cy}
                        r="3.5"
                        fill="#00f0ff"
                        opacity="0.85"
                        className="hover:r-6 cursor-pointer transition-all"
                      />
                    );
                  })}
                  {/* Informal points (lower income, broad age distribution) */}
                  {Array.from({ length: 60 }).map((_, i) => {
                    const cx = `${15 + (i * 1.2) + Math.sin(i * 3) * 12}%`;
                    const cy = `${65 + Math.sin(i * 1.5) * 16}%`;
                    return (
                      <circle
                        key={`inf-${i}`}
                        cx={cx}
                        cy={cy}
                        r="3"
                        fill="#f59e0b"
                        opacity="0.75"
                        className="hover:r-6 cursor-pointer transition-all"
                      />
                    );
                  })}
                </svg>

                <div className="flex items-center justify-between text-[11px] font-mono-hud text-slate-400">
                  <span>X: Nivel Educativo & Años de Escolaridad (0 a 18 años)</span>
                  <span className="text-cyan-400 font-semibold">
                    R² = 0.684 (Fuerte gradiente de formalización a partir de 12 años)
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 4: VALIDACIÓN CRUZADA K-FOLD */}
          {activeSection === 'kfolds' && (
            <div className="space-y-4 font-mono-hud text-xs">
              <div>
                <h3 className="font-display font-bold text-base text-slate-100">
                  Validación Cruzada Estratificada (K=5 Folds)
                </h3>
                <p className="text-slate-400">
                  Bloque de datos fragmentándose e iluminándose secuencialmente para evitar sobreajuste (overfitting).
                </p>
              </div>

              <div className="grid grid-cols-5 gap-3">
                {[1, 2, 3, 4, 5].map((fold) => {
                  const isActive = activeFold === fold;
                  const f1Scores = [0.912, 0.928, 0.909, 0.919, 0.915];
                  return (
                    <button
                      key={fold}
                      onClick={() => {
                        playHoloClick(900);
                        setActiveFold(fold);
                      }}
                      className={`p-4 rounded-2xl border transition-all text-left space-y-2 ${
                        isActive
                          ? 'bg-cyan-500/20 border-cyan-400 glow-cyan'
                          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-200">FOLD #{fold}</span>
                        {isActive && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {isActive ? 'Validando Batch...' : '249,180 registros'}
                      </div>
                      <div className="pt-2 border-t border-slate-800">
                        <span className="text-[10px] text-slate-400 block">F1-Score:</span>
                        <span className="text-base font-bold text-cyan-300">
                          {f1Scores[fold - 1]}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/20 flex items-center justify-between">
                <span>Promedio General Validación Cruzada:</span>
                <span className="font-bold text-cyan-300 text-sm">
                  F1 Medio: 0.9166 ± 0.0068 (Modelo altamente robusto y generalizable)
                </span>
              </div>
            </div>
          )}

          {/* SECTION 5: OPTIMIZACIÓN DE HIPERPARÁMETROS */}
          {activeSection === 'hyperparams' && (
            <div className="space-y-4 font-mono-hud text-xs">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-display font-bold text-base text-slate-100">
                    Diales de Optimización Bayesiana & Grid Search
                  </h3>
                  <p className="text-slate-400">
                    Ajuste automático de hiperparámetros para balancear regularización y convergencia.
                  </p>
                </div>
                <button
                  onClick={handleAutoTune}
                  className="px-3 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 border border-cyan-400/40 flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Auto-Tune Bayesiano
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-slate-900/60 border border-cyan-500/30 text-center space-y-2">
                  <span className="text-[10px] text-slate-400 block">max_depth</span>
                  <div className="w-16 h-16 mx-auto rounded-full border-2 border-cyan-400 flex items-center justify-center font-bold text-xl text-cyan-300 glow-cyan">
                    {hyperparams.maxDepth}
                  </div>
                  <span className="text-[10px] text-slate-500">Profundidad árbol</span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-indigo-500/30 text-center space-y-2">
                  <span className="text-[10px] text-slate-400 block">learning_rate</span>
                  <div className="w-16 h-16 mx-auto rounded-full border-2 border-indigo-400 flex items-center justify-center font-bold text-lg text-indigo-300">
                    {hyperparams.learningRate}
                  </div>
                  <span className="text-[10px] text-slate-500">Tasa aprendizaje</span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-amber-500/30 text-center space-y-2">
                  <span className="text-[10px] text-slate-400 block">n_estimators</span>
                  <div className="w-16 h-16 mx-auto rounded-full border-2 border-amber-400 flex items-center justify-center font-bold text-xl text-amber-300 glow-amber">
                    {hyperparams.nEstimators}
                  </div>
                  <span className="text-[10px] text-slate-500">Número de árboles</span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-emerald-500/30 text-center space-y-2">
                  <span className="text-[10px] text-slate-400 block">l2_regularization</span>
                  <div className="w-16 h-16 mx-auto rounded-full border-2 border-emerald-400 flex items-center justify-center font-bold text-lg text-emerald-300">
                    {hyperparams.l2Reg}
                  </div>
                  <span className="text-[10px] text-slate-500">Penalización Ridge</span>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 6: PRUEBAS ESTADÍSTICAS & P-VALUES */}
          {activeSection === 'stats' && (
            <div className="space-y-4 font-mono-hud text-xs">
              <div>
                <h3 className="font-display font-bold text-base text-slate-100">
                  Pruebas de Hipótesis & Inferencia Causal
                </h3>
                <p className="text-slate-400">
                  Evaluación estadística de significancia de impacto en transición formal frente al grupo de control.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-slate-900/60 border border-emerald-500/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300 font-bold">T-Student Test</span>
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                  </div>
                  <div className="text-2xl font-bold text-emerald-400">
                    p &lt; 0.0001
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Significativo al 99.9%. Diferencia en ingreso salarial formal vs informal no atribuible al azar.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-emerald-500/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300 font-bold">Kolmogorov-Smirnov</span>
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                  </div>
                  <div className="text-2xl font-bold text-emerald-400">
                    D = 0.442
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Rechaza hipótesis nula de distribuciones idénticas de capital humano entre ambos sectores.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-cyan-500/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-300 font-bold">Odds Ratio Subsidio</span>
                    <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                  </div>
                  <div className="text-2xl font-bold text-cyan-300">
                    OR: 2.84x
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Un subsidio de $50/mes incrementa en 2.84 veces la razón de formalización empresarial.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Real-time Cascading Terminal Logs */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono-hud text-slate-400">
              <span className="flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                Terminal de Registro de Telemetría & Entrenamiento
              </span>
              <span className="text-[10px] text-emerald-400">STREAM CONECTADO</span>
            </div>

            <div
              ref={logContainerRef}
              className="h-32 rounded-2xl bg-slate-950 border border-slate-800 p-3 font-mono-hud text-[11px] text-cyan-300/80 overflow-y-auto space-y-1"
            >
              {trainingLogs.map((log, i) => (
                <div key={i} className="leading-relaxed">
                  <span className="text-slate-600 mr-2">&gt;</span>
                  <span className={log.includes('CONVERGENCIA') || log.includes('Óptima') ? 'text-emerald-400 font-bold' : ''}>
                    {log}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
