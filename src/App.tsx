import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  CountryCode, 
  UserRole, 
  ScenarioPreset, 
  PolicyParameters, 
  WorkerAgent, 
  StructuralFirm, 
  StructuralMetrics,
  SimulationRun,
  MainView,
  Language,
  AppTheme,
  UserAccount
} from './types';
import { 
  COUNTRY_PROFILES, 
  INITIAL_POLICY_STATE, 
  DEMO_FIRMS, 
  DEMO_USERS
} from './data/mockData';
import { TopNavigationBar } from './components/HUD/TopNavigationBar';
import { DashboardView } from './components/Views/DashboardView';
const DigitalTwin3DView = React.lazy(() => 
  import('./components/Views/DigitalTwin3DView').then(m => ({ default: m.DigitalTwin3DView }))
);
import { AIEngineView } from './components/Views/AIEngineView';
import { DatasetsReportsView } from './components/Views/DatasetsReportsView';
import { UserManagementModal } from './components/Modals/UserManagementModal';
import { ILODecentWorkModal } from './components/Modals/ILODecentWorkModal';
import { AIChatbotModal } from './components/HUD/AIChatbotModal';
import { 
  playPolicyWaveSound, 
  playShockwaveSound, 
  playCrystallizeSound, 
  playHoloClick 
} from './utils/audioSynth';
import { 
  SimulationWebSocketClient, 
  SimulationFramePayload,
  fetchActiveDataset,
  fetchSimulationHistory,
  saveSimulationRunApi
} from './services/api';

// Helper: Generate Worker Particles Population (2,500 boids with formalization schedules)
export function createWorkersPopulation(
  countryCode: CountryCode, 
  informalityRate: number,
  firmList: StructuralFirm[]
): WorkerAgent[] {
  const totalWorkers = 2500;
  const formalFirms = firmList.filter((f) => f.type === 'formal');
  const newWorkers: WorkerAgent[] = [];

  const informalRatio = informalityRate / 100;
  const formalRatio = (1 - informalRatio) * 0.92;

  const numFormal = Math.round(totalWorkers * formalRatio);
  const numInformal = Math.round(totalWorkers * informalRatio);
  const numUnemployed = totalWorkers - numFormal - numInformal;

  const educations: WorkerAgent['education'][] = ['Primaria', 'Secundaria', 'Técnica', 'Universitaria'];
  const genders: WorkerAgent['gender'][] = ['Femenino', 'Masculino', 'No binario'];

  // Formal workers (Anchored from month 0)
  for (let i = 0; i < numFormal; i++) {
    const hostFirm = formalFirms[i % formalFirms.length] || firmList[0];
    const orbitRadius = 1.4 + Math.random() * 2.6;
    const orbitSpeed = 0.012 + Math.random() * 0.016;
    const orbitAngle = Math.random() * Math.PI * 2;
    const humanCapital = Math.floor(65 + Math.random() * 35);
    const income = Number((24 + (humanCapital / 100) * 32 + Math.random() * 8).toFixed(1));

    newWorkers.push({
      id: `w-formal-${i}`,
      code: `F-${1000 + i}`,
      x: (hostFirm?.x ?? 0) + Math.cos(orbitAngle) * orbitRadius,
      y: 2,
      z: (hostFirm?.z ?? 0) + Math.sin(orbitAngle) * orbitRadius,
      baseX: hostFirm?.x ?? 0,
      baseZ: hostFirm?.z ?? 0,
      vx: 0,
      vz: 0,
      sector: 'formal',
      humanCapital,
      incomeUSDDay: income,
      socialCapital: Math.floor(40 + Math.random() * 50),
      riskTolerance: Math.floor(20 + Math.random() * 40),
      flexibilityPref: Math.floor(20 + Math.random() * 50),
      firmId: hostFirm?.id ?? null,
      orbitRadius,
      orbitSpeed,
      orbitAngle,
      age: 22 + Math.floor(Math.random() * 40),
      gender: genders[i % 3],
      education: educations[Math.min(3, Math.floor(humanCapital / 28))],
      subSector: hostFirm?.sectorCategory ?? 'Manufactura',
      formalizationProb: 95,
      formalizationMonth: 0, // already formal at baseline
      currentProgress: 1.0,
    });
  }

  // Informal workers (with distributed formalization months)
  for (let i = 0; i < numInformal; i++) {
    const x = (Math.random() - 0.5) * 36;
    const z = 2 + (Math.random() - 0.2) * 22;
    const humanCapital = Math.floor(20 + Math.random() * 55);
    const income = Number((4.5 + (humanCapital / 100) * 14 + Math.random() * 4).toFixed(1));
    const baseMonth = Math.round(18 + (100 - humanCapital) * 1.1 + (Math.random() - 0.5) * 16);

    newWorkers.push({
      id: `w-informal-${i}`,
      code: `INF-${2000 + i}`,
      x,
      y: 0.5,
      z,
      baseX: x,
      baseZ: z,
      vx: (Math.random() - 0.5) * 0.04,
      vz: (Math.random() - 0.5) * 0.04,
      sector: 'informal',
      humanCapital,
      incomeUSDDay: income,
      socialCapital: Math.floor(60 + Math.random() * 40),
      riskTolerance: Math.floor(50 + Math.random() * 50),
      flexibilityPref: Math.floor(60 + Math.random() * 40),
      firmId: null,
      orbitRadius: 0,
      orbitSpeed: 0,
      orbitAngle: 0,
      age: 18 + Math.floor(Math.random() * 48),
      gender: genders[i % 3],
      education: educations[Math.min(2, Math.floor(humanCapital / 35))],
      subSector: 'Comercio Ambulante / Taller',
      formalizationProb: Math.floor(15 + (humanCapital / 100) * 45),
      formalizationMonth: baseMonth,
      currentProgress: 0.0,
      informalX: x,
      informalZ: z,
    });
  }

  // Unemployed workers
  for (let i = 0; i < numUnemployed; i++) {
    const x = (Math.random() - 0.5) * 40;
    const z = (Math.random() - 0.5) * 40;
    newWorkers.push({
      id: `w-unemp-${i}`,
      code: `U-${3000 + i}`,
      x,
      y: 0.2,
      z,
      baseX: x,
      baseZ: z,
      vx: (Math.random() - 0.5) * 0.015,
      vz: (Math.random() - 0.5) * 0.015,
      sector: 'unemployed',
      humanCapital: Math.floor(15 + Math.random() * 40),
      incomeUSDDay: 1.2,
      socialCapital: Math.floor(30 + Math.random() * 40),
      riskTolerance: Math.floor(30 + Math.random() * 40),
      flexibilityPref: 50,
      firmId: null,
      orbitRadius: 0,
      orbitSpeed: 0,
      orbitAngle: 0,
      age: 18 + Math.floor(Math.random() * 45),
      gender: genders[i % 3],
      education: educations[0],
      subSector: 'Búsqueda Activa',
      formalizationProb: 12,
      formalizationMonth: 999,
      currentProgress: 0.0,
      informalX: x,
      informalZ: z,
    });
  }

  return newWorkers;
}

export default function App() {
  // 1. Core UX Navigation Route (Default: dashboard as mandated)
  const [currentView, setCurrentView] = useState<MainView>('dashboard');

  // 2. Core Simulation State
  const [country, setCountry] = useState<CountryCode>('KENYA');
  const [month, setMonth] = useState<number>(0); // 0 to 120 continuous months (10 years)
  const [role, setRole] = useState<UserRole>('ADMIN');
  const [scenario, setScenario] = useState<ScenarioPreset>('BASELINE');
  const [policyParams, setPolicyParams] = useState<PolicyParameters>(INITIAL_POLICY_STATE);

  // 3. Accessibility, Theme & I18n State
  const [language, setLanguage] = useState<Language>('es');
  const [theme, setTheme] = useState<AppTheme>('dark');
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  // 4. WebSocket Bridge State
  const wsClientRef = useRef<SimulationWebSocketClient | null>(null);
  const [isWsConnected, setIsWsConnected] = useState<boolean>(false);
  const [streamMetrics, setStreamMetrics] = useState<StructuralMetrics | null>(null);

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light');
      document.documentElement.classList.remove('dark');
    } else {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    }
  }, [theme]);

  // Derived Year (e.g. Month 0 -> 2024, Month 42 -> 2027)
  const year = 2024 + Math.floor(month / 12);

  // 5. 3D Scene Controls & Timeline State
  const [policyWaveTrigger, setPolicyWaveTrigger] = useState<number>(0);
  const [isPlayingTimeline, setIsPlayingTimeline] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  // 6. Entity Collections & Selection (Initialized synchronously)
  const [firms, setFirms] = useState<StructuralFirm[]>(DEMO_FIRMS);
  const [workers, setWorkers] = useState<WorkerAgent[]>(() => 
    createWorkersPopulation('KENYA', COUNTRY_PROFILES['KENYA'].baseInformalityRate, DEMO_FIRMS)
  );
  const [selectedWorker, setSelectedWorker] = useState<WorkerAgent | null>(null);
  const [selectedFirm, setSelectedFirm] = useState<StructuralFirm | null>(null);
  const [simRuns, setSimRuns] = useState<SimulationRun[]>([]);
  const [backendOffline, setBackendOffline] = useState<boolean>(false);

  // 7. Global Utilities Modals & RBAC Users State
  const [users, setUsers] = useState<UserAccount[]>(DEMO_USERS);
  const [isUsersOpen, setIsUsersOpen] = useState(false);
  const [isILOOpen, setIsILOOpen] = useState(false);

  // 8. Global Dataset Ingestion & AI Engine Lock Dependency State
  const [isDatasetLoaded, setIsDatasetLoaded] = useState<boolean>(true);
  const [loadedDatasetName, setLoadedDatasetName] = useState<string | null>('PLFS India Periodic Labour Force Survey 2023-24');

  // Hydrate active dataset & simulation history on mount from real API
  useEffect(() => {
    fetchActiveDataset()
      .then((ds) => {
        if (ds && ds.is_loaded) {
          setIsDatasetLoaded(true);
          setLoadedDatasetName(ds.filename);
        }
      })
      .catch((err) => {
        console.warn('Backend active dataset unavailable:', err);
        setBackendOffline(true);
      });

    fetchSimulationHistory()
      .then((history) => {
        if (history && history.length > 0) {
          setSimRuns(history);
        }
      })
      .catch((err) => {
        console.warn('Backend simulation history unavailable:', err);
        setBackendOffline(true);
      });
  }, []);

  // Initialize and connect WebSocket
  useEffect(() => {
    const ws = new SimulationWebSocketClient();
    wsClientRef.current = ws;

    ws.connect(
      (frame: SimulationFramePayload) => {
        if (frame.month !== undefined) {
          setMonth(frame.month);
        }
        if (frame.metrics) {
          setStreamMetrics(frame.metrics);
        }
        if (frame.workers && frame.workers.length > 0) {
          setWorkers((prevWorkers) => {
            if (prevWorkers.length === 0) return prevWorkers;
            const updated = [...prevWorkers];
            for (const [idNum, x, y, z, progress] of frame.workers) {
              if (updated[idNum]) {
                updated[idNum] = {
                  ...updated[idNum],
                  x,
                  y,
                  z,
                  currentProgress: progress,
                };
              }
            }
            return updated;
          });
        }
      },
      (connected: boolean) => {
        setIsWsConnected(connected);
      }
    );

    return () => {
      ws.disconnect();
    };
  }, []);

  // Broadcast user actions to WebSocket
  useEffect(() => {
    if (wsClientRef.current) {
      wsClientRef.current.sendAction({
        action: isPlayingTimeline ? 'play' : 'pause',
        speed: playbackSpeed,
      });
    }
  }, [isPlayingTimeline, playbackSpeed]);

  useEffect(() => {
    if (wsClientRef.current) {
      wsClientRef.current.sendAction({
        action: 'set_country',
        country,
      });
    }
  }, [country]);

  useEffect(() => {
    if (wsClientRef.current) {
      wsClientRef.current.sendAction({
        action: 'set_policy',
        policy_params: policyParams,
      });
    }
  }, [policyParams]);

  useEffect(() => {
    if (wsClientRef.current) {
      wsClientRef.current.sendAction({
        action: 'set_scenario',
        scenario,
      });
    }
  }, [scenario]);

  // Fallback local month-by-month ticker when WebSocket is offline
  useEffect(() => {
    if (!isPlayingTimeline || isWsConnected) return;
    const intervalMs = Math.max(80, Math.round(750 / playbackSpeed));
    const interval = setInterval(() => {
      setMonth((prev) => {
        if (prev >= 120) return 0;
        return prev + 1;
      });
    }, intervalMs);

    return () => clearInterval(interval);
  }, [isPlayingTimeline, playbackSpeed, isWsConnected]);

  // Initialize workers when country changes
  useEffect(() => {
    const baseInformality = COUNTRY_PROFILES[country].baseInformalityRate;
    const initialWorkers = createWorkersPopulation(country, baseInformality, firms);
    setWorkers(initialWorkers);
    setSelectedWorker(null);
    setSelectedFirm(null);
  }, [country, firms]);

  // Compute live Structural Metrics dynamically based on policies, scenarios and continuous month
  const calculateMetrics = (): StructuralMetrics => {
    const baseInformality = COUNTRY_PROFILES[country].baseInformalityRate;
    const baseGini = COUNTRY_PROFILES[country].baseGini;

    // Temporal realization factor: 0.0 at month 0 (baseline), up to 1.0 at month 120 (10 years)
    const phaseProgress = Math.min(1.0, Math.pow(month / 120, 0.75));

    // Policy impacts scaled by time progression:
    const regImpact = ((policyParams.registrationCostReduction / 100) * 8.5) * phaseProgress;
    const subImpact = ((policyParams.smeSubsidyUSDMonth / 150) * 11.0) * phaseProgress;
    const trainImpact = ((policyParams.skillsTrainingCoverage / 100) * 6.5) * phaseProgress;
    const inspImpact = ((policyParams.smartInspectionCoverage / 100) * 4.5) * phaseProgress;
    const taxBurden = policyParams.socialProtectionTax > 25 ? ((policyParams.socialProtectionTax - 25) * 0.35 * phaseProgress) : 0;

    // Scenario specific shocks scaled with temporal maturity:
    let scenarioShift = 0;
    if (scenario === 'SCENARIO_A_REGISTRATION') {
      scenarioShift = -14.0 * phaseProgress;
    } else if (scenario === 'SCENARIO_B_WORKER_SUBSIDY') {
      scenarioShift = -18.5 * phaseProgress;
    } else if (scenario === 'SCENARIO_E_AUTOMATION_SHOCK') {
      // Tech disruption takes effect after month 20
      scenarioShift = (month >= 20 ? +10.5 : 0) * phaseProgress;
    }

    const netInformality = Math.max(
      32.0,
      Math.min(96.0, baseInformality - regImpact - subImpact - trainImpact - inspImpact + taxBurden + scenarioShift)
    );

    const netGini = Math.max(
      0.27,
      Math.min(0.55, baseGini - (100 - netInformality) * 0.0014)
    );

    const formalCount = Math.round(2500 * (1 - netInformality / 100) * 0.92);
    const informalCount = Math.round(2500 * (netInformality / 100));
    const unemployedCount = 2500 - formalCount - informalCount;

    const avgFormalWage = 28.5 + (policyParams.skillsTrainingCoverage / 100) * 6.0 + phaseProgress * 9.0;
    const avgInformalWage = 8.2 + (policyParams.smeSubsidyUSDMonth / 150) * 3.5 + phaseProgress * 3.0;

    // Fiscal balance
    const fiscalRevenue = (formalCount * 0.18 * 30) / 10;
    const policyCost = (policyParams.smeSubsidyUSDMonth * 1200 + policyParams.skillsTrainingCoverage * 800) / 10000;

    return {
      informalityRate: netInformality,
      giniIndex: netGini,
      formalWorkersCount: formalCount,
      informalWorkersCount: informalCount,
      unemployedCount,
      avgFormalWageUSD: avgFormalWage,
      avgInformalWageUSD: avgInformalWage,
      fiscalRevenueMillionUSD: fiscalRevenue,
      policyCostMillionUSD: policyCost,
      decentWorkIndex: Math.round(55 + (100 - netInformality) * 0.4),
    };
  };

  const currentMetrics = streamMetrics || calculateMetrics();

  // Scenario Switcher with Transitions
  const handleSelectScenario = (newScenario: ScenarioPreset) => {
    setScenario(newScenario);
    setPolicyWaveTrigger((prev) => prev + 1);

    if (newScenario === 'SCENARIO_A_REGISTRATION') {
      playCrystallizeSound();
      setPolicyParams({
        ...policyParams,
        registrationCostReduction: 80,
        smeSubsidyUSDMonth: 40,
      });
      setFirms((prev) =>
        prev.map((f) => (f.id === 'firm-inf-01' ? { ...f, isFormalizedScenario: true, type: 'formal', emergenceMonth: 12 } : f))
      );
      setWorkers((prev) =>
        prev.map((w) => {
          if (w.sector === 'informal') {
            return {
              ...w,
              formalizationMonth: Math.max(8, w.formalizationMonth - 28),
            };
          }
          return w;
        })
      );
    } else if (newScenario === 'SCENARIO_B_WORKER_SUBSIDY') {
      playCrystallizeSound();
      setPolicyParams({
        ...policyParams,
        smeSubsidyUSDMonth: 75,
        skillsTrainingCoverage: 60,
      });
      setWorkers((prev) =>
        prev.map((w) => {
          if (w.sector === 'informal') {
            return {
              ...w,
              formalizationMonth: Math.max(6, w.formalizationMonth - 38),
            };
          }
          return w;
        })
      );
    } else if (newScenario === 'SCENARIO_E_AUTOMATION_SHOCK') {
      playShockwaveSound();
      setFirms((prev) =>
        prev.map((f) => (f.id === 'firm-f-01' ? { ...f, shockwaveActive: true } : f))
      );
      setWorkers((prev) =>
        prev.map((w, i) => {
          // Automation displaces workers at Month 36
          if (w.sector === 'formal' && w.firmId === 'firm-f-01' && i % 3 === 0) {
            return {
              ...w,
              formalizationMonth: 999, // pushed out of formality
            };
          }
          return w;
        })
      );
    } else if (newScenario === 'BASELINE') {
      playHoloClick(800);
      setPolicyParams(INITIAL_POLICY_STATE);
      setFirms(DEMO_FIRMS);
      const baseInf = COUNTRY_PROFILES[country].baseInformalityRate;
      setWorkers(createWorkersPopulation(country, baseInf, DEMO_FIRMS));
    }
  };

  // Trigger New Simulation Run
  const handleTriggerNewSimulation = () => {
    playHoloClick(1000);
    const newRun: SimulationRun = {
      id: `RUN-${Date.now().toString().slice(-4)}`,
      name: `${country}: Corrida ${scenario}`,
      timestamp: 'Justo ahora',
      country,
      scenario: `Simulación ${year}`,
      status: 'completada',
      informalityChange: Number((currentMetrics.informalityRate - COUNTRY_PROFILES[country].baseInformalityRate).toFixed(1)),
      executionTimeSec: 4.2,
    };
    setSimRuns([newRun, ...simRuns]);
    setPolicyWaveTrigger((prev) => prev + 1);

    // Persist to backend database
    saveSimulationRunApi({
      country,
      scenario,
      policy_params: policyParams,
      final_metrics: currentMetrics,
      duration_sec: 4.2,
    });
  };

  return (
    <main className={`relative w-screen h-screen overflow-hidden select-none flex flex-col transition-colors duration-200 ${
      theme === 'light' ? 'bg-slate-100 text-slate-800' : 'bg-[#05070c] text-slate-100'
    }`}>
      {/* Top Holographic Navigation Bar with 4 primary routes */}
      <TopNavigationBar
        currentView={currentView}
        onChangeView={setCurrentView}
        country={country}
        onSelectCountry={(c) => {
          setCountry(c);
          setScenario('BASELINE');
        }}
        role={role}
        onChangeRole={setRole}
        scenario={scenario}
        onSelectScenario={handleSelectScenario}
        onOpenILO={() => setIsILOOpen(true)}
        onOpenUsers={() => setIsUsersOpen(true)}
        language={language}
        onChangeLanguage={setLanguage}
        theme={theme}
        onChangeTheme={setTheme}
        onOpenChatbot={() => setIsChatbotOpen(true)}
        isDatasetLoaded={isDatasetLoaded}
      />

      {/* Backend Availability Alert Banner */}
      {backendOffline && (
        <div className="bg-amber-500/15 border-b border-amber-500/30 text-amber-300 text-xs px-4 py-1.5 flex items-center justify-between z-30 shrink-0">
          <div className="flex items-center gap-2 font-mono">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            <span>Aviso: Backend no disponible. La API FastAPI en http://localhost:8000 no responde; los datos en tiempo real requieren la API.</span>
          </div>
          <button
            onClick={() => setBackendOffline(false)}
            className="text-amber-400 hover:text-amber-200 font-bold px-1 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* Primary Dynamic View Routing */}
      <div className="flex-1 w-full h-full relative overflow-hidden">
        {/* ROUTE 1: 📊 DASHBOARD PRINCIPAL (Default 2D view, NO 3D canvas mounted) */}
        {currentView === 'dashboard' && (
          <DashboardView
            country={country}
            scenario={scenario}
            onSelectScenario={handleSelectScenario}
            policyParams={policyParams}
            onChangePolicy={setPolicyParams}
            metrics={currentMetrics}
            onNavigateTo3D={() => setCurrentView('digital_twin_3d')}
            onTriggerSimulation={handleTriggerNewSimulation}
            simRuns={simRuns}
            role={role}
            language={language}
            theme={theme}
          />
        )}

        {/* ROUTE 2: 🌐 GEMELO DIGITAL 3D (Dedicated 100% spatial viewport with minimal floating HUD, loaded lazily) */}
        {currentView === 'digital_twin_3d' && (
          <React.Suspense
            fallback={
              <div className="flex flex-col items-center justify-center h-full w-full bg-[#05070c] text-cyan-400 gap-4">
                <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
                <div className="text-sm font-mono-hud tracking-wider text-slate-300">
                  Cargando Gemelo Digital 3D & Three.js...
                </div>
              </div>
            }
          >
            <DigitalTwin3DView
              country={country}
              month={month}
              onMonthChange={setMonth}
              year={year}
              scenario={scenario}
              onSelectScenario={handleSelectScenario}
              policyParams={policyParams}
              onChangePolicy={setPolicyParams}
              workers={workers}
              firms={firms}
              selectedWorker={selectedWorker}
              selectedFirm={selectedFirm}
              onSelectWorker={setSelectedWorker}
              onSelectFirm={setSelectedFirm}
              metrics={currentMetrics}
              policyWaveTrigger={policyWaveTrigger}
              onTriggerPolicyWave={() => {
                playPolicyWaveSound();
                setPolicyWaveTrigger((prev) => prev + 1);
              }}
              isPlayingTimeline={isPlayingTimeline}
              onTogglePlay={() => setIsPlayingTimeline(!isPlayingTimeline)}
              playbackSpeed={playbackSpeed}
              onChangeSpeed={setPlaybackSpeed}
              language={language}
              theme={theme}
            />
          </React.Suspense>
        )}

        {/* ROUTE 3: 🧠 MOTOR IA (Dedicated algorithm audit & explainability) */}
        {currentView === 'ai_engine' && (
          <AIEngineView
            role={role}
            isDatasetLoaded={isDatasetLoaded}
            onNavigateToDatasets={() => setCurrentView('datasets_reports')}
            loadedDatasetName={loadedDatasetName}
            onRetrainTriggered={() => {
              setPolicyWaveTrigger((prev) => prev + 1);
            }}
            language={language}
            theme={theme}
          />
        )}

        {/* ROUTE 4: 📁 DATASETS & REPORTES (Surveys microdata & export brief) */}
        {currentView === 'datasets_reports' && (
          <DatasetsReportsView
            country={country}
            onSelectCountry={(c) => {
              setCountry(c);
              setScenario('BASELINE');
            }}
            scenario={scenario}
            metrics={currentMetrics}
            isDatasetLoaded={isDatasetLoaded}
            setIsDatasetLoaded={setIsDatasetLoaded}
            loadedDatasetName={loadedDatasetName}
            setLoadedDatasetName={setLoadedDatasetName}
            onNavigateToAIEngine={() => setCurrentView('ai_engine')}
            language={language}
            theme={theme}
          />
        )}
      </div>

      {/* Labor Economics AI Copilot Floating Modal */}
      <AIChatbotModal
        country={country}
        month={month}
        metrics={currentMetrics}
        policyParams={policyParams}
        scenario={scenario}
        onSelectScenario={handleSelectScenario}
        language={language}
        theme={theme}
        isOpen={isChatbotOpen}
        onOpen={() => setIsChatbotOpen(true)}
        onClose={() => setIsChatbotOpen(false)}
      />

      {/* Global Utilities Modals */}
      <UserManagementModal
        isOpen={isUsersOpen}
        onClose={() => setIsUsersOpen(false)}
        currentRole={role}
        onChangeRole={setRole}
        users={users}
        setUsers={setUsers}
        theme={theme}
        language={language}
      />

      <ILODecentWorkModal
        isOpen={isILOOpen}
        onClose={() => setIsILOOpen(false)}
        country={country}
        metrics={currentMetrics}
        language={language}
        theme={theme}
      />
    </main>
  );
}
