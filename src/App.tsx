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
  getModelFirms, 
  DEMO_USERS
} from './data/mockData';
import trayectoriasData from '@/outputs/trayectorias_mensuales.json';
import muestraTrabajadores from './data/muestra_trabajadores.json';
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
  saveSimulationRunApi,
  fetchStructuralMetricsApi,
  BACKEND_URL
} from './services/api';

// Helper: Generate Worker Particles Population (2,500 boids with formalization schedules from ITDT real sample)
export function createWorkersPopulation(
  countryCode: CountryCode, 
  informalityRate: number,
  firmList: StructuralFirm[]
): WorkerAgent[] {
  const totalWorkers = 2500;
  const formalFirms = firmList.filter((f) => f.type === 'formal');
  const newWorkers: WorkerAgent[] = [];

  const informalRatio = informalityRate / 100;
  const formalRatio = 1 - informalRatio;

  const numFormal = Math.round(totalWorkers * formalRatio);
  const numInformal = totalWorkers - numFormal;

  const sampleLen = (muestraTrabajadores as any[]).length || 2500;

  // Formal workers (Anchored from month 0)
  for (let i = 0; i < numFormal; i++) {
    const hostFirm = formalFirms[i % formalFirms.length] || firmList[0];
    const profile = (muestraTrabajadores as any[])[i % sampleLen];
    const orbitRadius = 1.4 + ((i % 10) / 10) * 2.6;
    const orbitSpeed = 0.012 + ((i % 8) / 8) * 0.016;
    const orbitAngle = ((i * 137.5) * Math.PI) / 180;

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
      gender: profile.sexo as 'Femenino' | 'Masculino',
      education: profile.educacion,
      ruralZone: profile.zona as 'Rural' | 'Urbana',
      productivityH: profile.productividad_h,
      careHours: profile.horas_cuidado,
      digitalLit: profile.alfabetizacion_digital,
      firmId: hostFirm?.id ?? null,
      orbitRadius,
      orbitSpeed,
      orbitAngle,
      subSector: hostFirm?.sectorCategory ?? 'Manufactura',
      formalizationMonth: 0,
      currentProgress: 1.0,
    });
  }

  // Informal workers (with distributed formalization months based on productivity)
  for (let i = 0; i < numInformal; i++) {
    const workerIndex = numFormal + i;
    const profile = (muestraTrabajadores as any[])[workerIndex % sampleLen];
    const angle = ((i * 137.5) * Math.PI) / 180;
    const dist = 3 + Math.sqrt(i / (numInformal || 1)) * 16;
    const x = Math.cos(angle) * dist;
    const z = Math.sin(angle) * dist;
    const baseMonth = Math.round(12 + (2.0 - Math.min(2.0, profile.productividad_h)) * 45);

    newWorkers.push({
      id: `w-informal-${i}`,
      code: `INF-${2000 + i}`,
      x,
      y: 0.5,
      z,
      baseX: x,
      baseZ: z,
      vx: ((i % 7) - 3) * 0.008,
      vz: ((i % 5) - 2) * 0.008,
      sector: 'informal',
      gender: profile.sexo as 'Femenino' | 'Masculino',
      education: profile.educacion,
      ruralZone: profile.zona as 'Rural' | 'Urbana',
      productivityH: profile.productividad_h,
      careHours: profile.horas_cuidado,
      digitalLit: profile.alfabetizacion_digital,
      firmId: null,
      orbitRadius: 0,
      orbitSpeed: 0,
      orbitAngle: 0,
      subSector: profile.zona === 'Rural' ? 'Agricultura Familiar' : 'Comercio Ambulante / Taller',
      formalizationMonth: baseMonth,
      currentProgress: 0.0,
      informalX: x,
      informalZ: z,
    });
  }

  return newWorkers;
}

export default function App() {
  // 1. Core UX Navigation Route (Default: dashboard as mandated)
  const [currentView, setCurrentView] = useState<MainView>(() => {
    const params = new URLSearchParams(window.location.search);
    const v = params.get('view') as MainView;
    return (v === 'dashboard' || v === 'digital_twin_3d' || v === 'ai_engine' || v === 'datasets_reports') ? v : 'dashboard';
  });

  // 2. Core Simulation State
  const [country, setCountry] = useState<CountryCode>(() => {
    const params = new URLSearchParams(window.location.search);
    const c = params.get('country') as CountryCode;
    return (c === 'KENYA' || c === 'NIGERIA' || c === 'INDIA' || c === 'BANGLADESH') ? c : 'KENYA';
  });
  const [month, setMonth] = useState<number>(() => {
    const params = new URLSearchParams(window.location.search);
    const m = params.get('month');
    return m !== null ? parseInt(m, 10) : 0;
  });
  const [role, setRole] = useState<UserRole>('ADMIN');
  const [scenario, setScenario] = useState<ScenarioPreset>(() => {
    const params = new URLSearchParams(window.location.search);
    const s = params.get('scenario') as ScenarioPreset;
    return s || 'A';
  });
  const [policyParams, setPolicyParams] = useState<PolicyParameters>(INITIAL_POLICY_STATE);

  // 3. Accessibility, Theme & I18n State
  const [language, setLanguage] = useState<Language>('es');
  const [theme, setTheme] = useState<AppTheme>(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get('theme') as AppTheme;
    return (t === 'light' || t === 'dark') ? t : 'light';
  });
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

  // 6. Entity Collections & Selection (Initialized synchronously with dynamic model firms)
  const [firms, setFirms] = useState<StructuralFirm[]>(() => getModelFirms('KENYA', 'A', 0));
  const [workers, setWorkers] = useState<WorkerAgent[]>(() => 
    createWorkersPopulation('KENYA', COUNTRY_PROFILES['KENYA'].baseInformalityRate, getModelFirms('KENYA', 'A', 0))
  );
  const [selectedWorker, setSelectedWorker] = useState<WorkerAgent | null>(null);
  const [selectedFirm, setSelectedFirm] = useState<StructuralFirm | null>(null);
  const [simRuns, setSimRuns] = useState<SimulationRun[]>([]);
  const [backendOffline, setBackendOffline] = useState<boolean>(false);
  const [apiMetrics, setApiMetrics] = useState<StructuralMetrics | null>(null);

  // 7. Global Utilities Modals & RBAC Users State
  const [users, setUsers] = useState<UserAccount[]>(DEMO_USERS);
  const [isUsersOpen, setIsUsersOpen] = useState(false);
  const [isILOOpen, setIsILOOpen] = useState(false);

  // 8. Global Dataset Ingestion & AI Engine Lock Dependency State
  const [isDatasetLoaded, setIsDatasetLoaded] = useState<boolean>(false);
  const [loadedDatasetName, setLoadedDatasetName] = useState<string | null>(null);

  // Hydrate active dataset & simulation history on mount from real API
  useEffect(() => {
    fetchActiveDataset()
      .then((ds) => {
        if (ds && ds.is_loaded) {
          setIsDatasetLoaded(true);
          setLoadedDatasetName(ds.filename);
        } else {
          setIsDatasetLoaded(false);
          setLoadedDatasetName(null);
        }
      })
      .catch((err) => {
        setIsDatasetLoaded(false);
        setLoadedDatasetName(null);
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

  // Ref to always track latest simulation playback state
  const isPlayingRef = useRef(isPlayingTimeline);
  useEffect(() => {
    isPlayingRef.current = isPlayingTimeline;
  }, [isPlayingTimeline]);

  const monthRef = useRef(month);
  useEffect(() => {
    monthRef.current = month;
  }, [month]);

  const countryRef = useRef(country);
  useEffect(() => {
    countryRef.current = country;
  }, [country]);

  const scenarioRef = useRef(scenario);
  useEffect(() => {
    scenarioRef.current = scenario;
  }, [scenario]);

  // Initialize and connect WebSocket
  useEffect(() => {
    const ws = new SimulationWebSocketClient();
    wsClientRef.current = ws;

    ws.connect(
      (frame: SimulationFramePayload) => {
        if (isPlayingRef.current) {
          if (frame.month !== undefined) {
            setMonth(frame.month);
          }
          if (frame.metrics) {
            setStreamMetrics(frame.metrics);
          }
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
        if (connected && wsClientRef.current) {
          wsClientRef.current.sendAction({ action: 'set_country', country: countryRef.current });
          wsClientRef.current.sendAction({ action: 'set_scenario', scenario: scenarioRef.current });
          wsClientRef.current.sendAction({ action: 'seek', month: monthRef.current });
        }
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
    if (wsClientRef.current && isWsConnected) {
      wsClientRef.current.sendAction({
        action: 'seek',
        month,
      });
    }
  }, [month, isWsConnected]);

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

  // Fetch structural metrics from backend FastAPI when country, scenario or month changes
  useEffect(() => {
    let isMounted = true;
    fetchStructuralMetricsApi(country, scenario, month)
      .then((m) => {
        if (isMounted) {
          setApiMetrics(m);
          setBackendOffline(false);
        }
      })
      .catch((err) => {
        console.warn('Backend metrics fetch failed:', err);
        setBackendOffline(true);
      });
    return () => {
      isMounted = false;
    };
  }, [country, scenario, month]);

  // Fetch real model firms from backend FastAPI (with dynamic fallback to model proportions)
  useEffect(() => {
    const scClean = scenario.toUpperCase().replace('SCENARIO_', '').split('_')[0] || 'A';
    fetch(`${BACKEND_URL}/api/v1/simulation/firms?country=${encodeURIComponent(country)}&scenario=${encodeURIComponent(scClean)}&month=${month}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && Array.isArray(data) && data.length > 0) {
          setFirms(data);
        } else {
          setFirms(getModelFirms(country, scenario, month));
        }
      })
      .catch(() => {
        setFirms(getModelFirms(country, scenario, month));
      });
  }, [country, scenario, month]);

  // Compute live Structural Metrics dynamically from outputs/trayectorias_mensuales.json
  const calculateMetrics = (): StructuralMetrics => {
    const baseInformality = COUNTRY_PROFILES[country]?.baseInformalityRate ?? 86.49;
    const baseGini = COUNTRY_PROFILES[country]?.baseGini ?? 0.288;
    const cClean = (country || 'KENYA').toUpperCase();
    const scClean = scenario.toUpperCase().replace('SCENARIO_', '').split('_')[0] || 'A';
    const cData = (trayectoriasData as any)[cClean] || (trayectoriasData as any)['KENYA'];
    const scData = cData?.[scClean] || cData?.['A'] || [];

    if (month > 0 && scData.length >= month) {
      const mItem = scData[month - 1];
      const netInf = mItem.informality_total;
      const netFem = mItem.informality_female;
      const netMasc = mItem.informality_male;
      const netGap = mItem.gender_gap;
      const netGini = mItem.gini_index ?? 0.288;
      const netRev = mItem.fiscal_revenue ?? 1381.05;
      const netExit = mItem.annual_exit_rate ?? 0.05;
      const corpTax = mItem.corporate_tax_revenue ?? Number((netRev * 0.865).toFixed(2));
      const laborTax = Number((netRev - corpTax).toFixed(2));
      const formalCount = Math.round(2500 * (1 - netInf / 100));
      const informalCount = 2500 - formalCount;

      return {
        informalityRate: netInf,
        informalityFemale: netFem,
        informalityMale: netMasc,
        genderGap: netGap,
        giniIndex: netGini,
        formalWorkersCount: formalCount,
        informalWorkersCount: informalCount,
        unemployedCount: 0,
        fiscalRevenueModelUnits: netRev,
        fiscalRevenue: netRev,
        corporateTaxRevenueModelUnits: corpTax,
        corporateTaxRevenue: corpTax,
        laborContributionsModelUnits: laborTax,
        laborContributionsRevenue: laborTax,
        annualExitRate: netExit,
        isRealData: true,
        source: 'Modelo ITDT (outputs/trayectorias_mensuales.json)',
      };
    }

    // Mes 0 (Línea base pre-política del país)
    const m0 = scData[0] || {};
    const baseFem = country === 'KENYA' ? 90.19 : country === 'NIGERIA' ? 96.39 : country === 'INDIA' ? 91.93 : 95.77;
    const baseMasc = country === 'KENYA' ? 83.13 : country === 'NIGERIA' ? 89.92 : country === 'INDIA' ? 86.76 : 78.08;
    const netGap = Number((baseFem - baseMasc).toFixed(2));
    const netRev = m0.fiscal_revenue ?? 1381.05;
    const corpTax = m0.corporate_tax_revenue ?? Number((netRev * 0.865).toFixed(2));
    const laborTax = Number((netRev - corpTax).toFixed(2));
    const formalCount = Math.round(2500 * (1 - baseInformality / 100));
    const informalCount = 2500 - formalCount;

    return {
      informalityRate: baseInformality,
      informalityFemale: baseFem,
      informalityMale: baseMasc,
      genderGap: netGap,
      giniIndex: baseGini,
      formalWorkersCount: formalCount,
      informalWorkersCount: informalCount,
      unemployedCount: 0,
      fiscalRevenueModelUnits: netRev,
      fiscalRevenue: netRev,
      corporateTaxRevenueModelUnits: corpTax,
      corporateTaxRevenue: corpTax,
      laborContributionsModelUnits: laborTax,
      laborContributionsRevenue: laborTax,
      annualExitRate: 0.05,
      isRealData: true,
      source: 'Modelo ITDT (Línea Base)',
    };
  };

  const currentMetrics = isPlayingTimeline 
    ? (streamMetrics || apiMetrics || calculateMetrics())
    : (apiMetrics || streamMetrics || calculateMetrics());

  // Objeto de depuración window.__itdtDebug expuesto globalmente
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const formalTowers = firms.filter((f) => f.type === 'formal' || f.isFormalizedScenario).length;
      const informalTowers = firms.length - formalTowers;
      (window as any).__itdtDebug = {
        ...((window as any).__itdtDebug || {}),
        country,
        scenario: scenario.toUpperCase().replace('SCENARIO_', '').split('_')[0] || 'A',
        month,
        formalParticles: currentMetrics.formalWorkersCount,
        informalParticles: currentMetrics.informalWorkersCount,
        formalTowers,
        informalTowers,
        informalityRate: currentMetrics.informalityRate,
        totalParticles: 2500,
        totalTowers: firms.length,
        timestamp: new Date().toISOString(),
      };
    }
  }, [country, scenario, month, currentMetrics, firms]);

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
    } else if (newScenario === 'BASELINE' || newScenario === 'A') {
      playHoloClick(800);
      setPolicyParams(INITIAL_POLICY_STATE);
      const dynamicFirms = getModelFirms(country, 'A', month);
      setFirms(dynamicFirms);
      const baseInf = COUNTRY_PROFILES[country].baseInformalityRate;
      setWorkers(createWorkersPopulation(country, baseInf, dynamicFirms));
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
      informalityChange: Number(((currentMetrics?.informalityRate ?? 0) - COUNTRY_PROFILES[country].baseInformalityRate).toFixed(1)),
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
            <span>Aviso: Backend no disponible. La API FastAPI en {BACKEND_URL} no responde; los datos en tiempo real requieren la API.</span>
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
