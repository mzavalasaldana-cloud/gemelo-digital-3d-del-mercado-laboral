export type UserRole = 'ADMIN' | 'POLICY_ANALYST' | 'RESEARCHER';

export type Language = 'es' | 'en';
export type AppTheme = 'dark' | 'light';

export type MainView = 'dashboard' | 'digital_twin_3d' | 'ai_engine' | 'datasets_reports';

export type CountryCode = 'KENYA' | 'NIGERIA' | 'INDIA' | 'BANGLADESH';

export type WorkerSector = 'formal' | 'informal' | 'unemployed';

export interface WorkerAgent {
  id: string;
  code: string;
  x: number;
  y: number;
  z: number;
  baseX: number;
  baseZ: number;
  vx: number;
  vz: number;
  sector: WorkerSector;
  humanCapital: number; // 0-100 (size)
  incomeUSDDay: number; // income (brightness)
  socialCapital: number; // 0-100
  riskTolerance: number; // 0-100
  flexibilityPref: number; // 0-100
  firmId: string | null;
  orbitRadius: number;
  orbitSpeed: number;
  orbitAngle: number;
  age: number;
  gender: 'Femenino' | 'Masculino' | 'No binario';
  education: 'Primaria' | 'Secundaria' | 'Técnica' | 'Universitaria';
  subSector: string;
  formalizationProb: number; // 0-100%
  inTransition?: boolean;
  formalizationMonth: number; // Month (0-120) when this worker transitions
  currentProgress?: number; // 0 (informal) to 1 (formal)
  informalX?: number;
  informalZ?: number;
}

export interface StructuralFirm {
  id: string;
  name: string;
  type: 'formal' | 'informal_mycelium';
  x: number;
  z: number;
  sizeEmployees: number;
  height: number;
  sectorCategory: 'Manufactura' | 'Tecnología' | 'Comercio & Retail' | 'Logística' | 'Servicios Personales' | 'Agroindustria';
  productivityScore: number; // 0-100
  formalizationCostUSD: number;
  taxComplianceRate: number; // %
  baseEmployees: number;
  isFormalizedScenario?: boolean;
  shockwaveActive?: boolean;
  emergenceMonth?: number; // Month (0-120) when this firm sprouts from the ground
  growthSpanMonths?: number;
}

export interface PolicyParameters {
  registrationCostReduction: number; // 0 to 100%
  smeSubsidyUSDMonth: number; // 0 to 150 USD/month
  skillsTrainingCoverage: number; // 0 to 100%
  socialProtectionTax: number; // 0 to 50%
  smartInspectionCoverage: number; // 0 to 100%
}

export type ScenarioPreset = 
  | 'BASELINE'
  | 'SCENARIO_A_REGISTRATION'
  | 'SCENARIO_B_WORKER_SUBSIDY'
  | 'SCENARIO_E_AUTOMATION_SHOCK'
  | 'CUSTOM';

export interface StructuralMetrics {
  informalityRate: number; // %
  giniIndex: number; // 0 to 1 (e.g. 0.46)
  formalWorkersCount: number;
  informalWorkersCount: number;
  unemployedCount: number;
  avgFormalWageUSD: number;
  avgInformalWageUSD: number;
  fiscalRevenueMillionUSD: number;
  policyCostMillionUSD: number;
  decentWorkIndex: number; // 0 to 100
}

export interface MLAlgorithmMetric {
  id: string;
  name: string;
  f1Score: number;
  rocAuc: number;
  latencyMs: number;
  interpretability: number; // 0-100
  accuracy: number;
  isDeployed: boolean;
}

export interface CohortPrediction {
  id: string;
  label: string;
  populationShare: number; // %
  prob1Year: number; // %
  prob3Year: number; // %
  prob5Year: number; // %
  topDriver: string;
}

export interface SimulationRun {
  id: string;
  name: string;
  timestamp: string;
  country: CountryCode;
  scenario: string;
  status: 'completada' | 'en_ejecucion' | 'error';
  informalityChange: number; // e.g. -4.2%
  executionTimeSec: number;
}

export interface DatasetEntry {
  id: string;
  name: string;
  country: CountryCode;
  yearSpan: string;
  sampleSize: string;
  recordsCount: number;
  institution: string;
  variables: string[];
  verified: boolean;
  active: boolean;
  description: string;
}

export interface UserAccount {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department: string;
  lastActive: string;
  permissions: {
    editPolicies: boolean;
    retrainAI: boolean;
    manageDatasets: boolean;
    manageUsers: boolean;
    exportReports: boolean;
  };
}
