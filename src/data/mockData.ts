import { 
  CountryCode, 
  StructuralFirm, 
  MLAlgorithmMetric, 
  CohortPrediction, 
  SimulationRun, 
  DatasetEntry, 
  UserAccount,
  PolicyParameters
} from '../types';

export interface CountryProfile {
  code: CountryCode;
  name: string;
  flag: string;
  currency: string;
  baseInformalityRate: number; // % ILOSTAT EMP_NIFL_SEX_RT
  baseGini: number; // Gini del modelo ITDT calibrado (Escenario A, mes 0)
  giniSource: string;
  informalitySource: string;
  terrainProfile: {
    peakFrequency: number;
    valleyDepth: number;
    terrainRoughness: number;
    colorTint: string;
  };
  contextDescription: string;
}

export const COUNTRY_PROFILES: Record<CountryCode, CountryProfile> = {
  KENYA: {
    code: 'KENYA',
    name: 'Kenia (KNBS-ILFS 2019)',
    flag: '🇰🇪',
    currency: 'KES',
    baseInformalityRate: 86.49, // ILOSTAT EMP_NIFL_SEX_RT 2019 (data/ilostat_series_historicas.csv)
    baseGini: 0.288, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: 'ILOSTAT EMP_NIFL_SEX_RT (KNBS 2019)',
    terrainProfile: {
      peakFrequency: 2.2,
      valleyDepth: 1.8,
      terrainRoughness: 1.4,
      colorTint: '#00f0ff',
    },
    contextDescription: 'Alta prevalencia del sector informal "Jua Kali", microfinanzas móviles M-Pesa y polo tecnológico en Nairobi.',
  },
  NIGERIA: {
    code: 'NIGERIA',
    name: 'Nigeria (NBS-NLFS 2024)',
    flag: '🇳🇬',
    currency: 'NGN',
    baseInformalityRate: 93.18, // ILOSTAT EMP_NIFL_SEX_RT 2024 (data/ilostat_series_historicas.csv)
    baseGini: 0.285, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: 'ILOSTAT EMP_NIFL_SEX_RT (NBS 2024)',
    terrainProfile: {
      peakFrequency: 1.8,
      valleyDepth: 2.4,
      terrainRoughness: 1.6,
      colorTint: '#10b981',
    },
    contextDescription: 'Mercados urbanos densos, comercio informal masivo en Lagos y brechas significativas entre el sector formal corporativo y microtalleres.',
  },
  INDIA: {
    code: 'INDIA',
    name: 'India (PLFS MoSPI 2024)',
    flag: '🇮🇳',
    currency: 'INR',
    baseInformalityRate: 88.36, // ILOSTAT EMP_NIFL_SEX_RT 2024 (data/ilostat_series_historicas.csv)
    baseGini: 0.292, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: 'ILOSTAT EMP_NIFL_SEX_RT (MoSPI 2024)',
    terrainProfile: {
      peakFrequency: 3.0,
      valleyDepth: 2.0,
      terrainRoughness: 1.8,
      colorTint: '#38bdf8',
    },
    contextDescription: 'Enorme sector informal "unorganized", transición de manufactura semi-formal y plataformas gig de servicios.',
  },
  BANGLADESH: {
    code: 'BANGLADESH',
    name: 'Bangladés (BBS-LFS 2023)',
    flag: '🇧🇩',
    currency: 'BDT',
    baseInformalityRate: 84.19, // ILOSTAT EMP_NIFL_SEX_RT 2023 (data/ilostat_series_historicas.csv)
    baseGini: 0.288, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: 'ILOSTAT EMP_NIFL_SEX_RT (BBS 2023)',
    terrainProfile: {
      peakFrequency: 1.6,
      valleyDepth: 2.2,
      terrainRoughness: 1.2,
      colorTint: '#06b6d4',
    },
    contextDescription: 'Exportación textil con encadenamientos de talleres subcontratados y microcréditos rurales.',
  },
};

export const INITIAL_POLICY_STATE: PolicyParameters = {
  registrationCostReduction: 30, // 30% reduction
  smeSubsidyUSDMonth: 50, // $50/month
  skillsTrainingCoverage: 25, // 25% coverage
  socialProtectionTax: 12, // 12% tax/contribution
  smartInspectionCoverage: 20, // 20% inspection
};

// EMPRESAS DERIVADAS DIRECTAMENTE DE ITDTModel (N_F = 600, muestra representativa para visualización 3D)
// Sin nombres comerciales ficticios, sin sectores inventados ni costos USD arbitrarios.
export const DEMO_FIRMS: StructuralFirm[] = [
  {
    id: 'firm-f-018',
    name: 'Unidad Productiva Formal #19',
    type: 'formal',
    x: 7.64,
    z: 2.36,
    sizeEmployees: 40,
    baseEmployees: 40,
    height: 8.5,
    productivityScore: 55.2,
    taxComplianceRate: 100,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-f-030',
    name: 'Unidad Productiva Formal #31',
    type: 'formal',
    x: 1.77,
    z: 7.8,
    sizeEmployees: 37,
    baseEmployees: 37,
    height: 8.5,
    productivityScore: 51.1,
    taxComplianceRate: 100,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-f-031',
    name: 'Unidad Productiva Formal #32',
    type: 'formal',
    x: -5.87,
    z: 5.44,
    sizeEmployees: 34,
    baseEmployees: 34,
    height: 8.5,
    productivityScore: 60.4,
    taxComplianceRate: 100,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-f-042',
    name: 'Unidad Productiva Formal #43',
    type: 'formal',
    x: -7.64,
    z: -2.36,
    sizeEmployees: 40,
    baseEmployees: 40,
    height: 8.5,
    productivityScore: 84.1,
    taxComplianceRate: 100,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-f-055',
    name: 'Unidad Productiva Formal #56',
    type: 'formal',
    x: -1.77,
    z: -7.8,
    sizeEmployees: 40,
    baseEmployees: 40,
    height: 8.5,
    productivityScore: 67.0,
    taxComplianceRate: 100,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-f-151',
    name: 'Unidad Productiva Formal #152',
    type: 'formal',
    x: 5.87,
    z: -5.44,
    sizeEmployees: 40,
    baseEmployees: 40,
    height: 8.5,
    productivityScore: 84.0,
    taxComplianceRate: 100,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-inf-000',
    name: 'Unidad Productiva Informal #1',
    type: 'informal_mycelium',
    x: 3.14,
    z: 3.23,
    sizeEmployees: 1,
    baseEmployees: 1,
    height: 1.8,
    productivityScore: 10.7,
    taxComplianceRate: 0,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-inf-001',
    name: 'Unidad Productiva Informal #2',
    type: 'informal_mycelium',
    x: -3.23,
    z: 3.14,
    sizeEmployees: 10,
    baseEmployees: 10,
    height: 4.0,
    productivityScore: 31.4,
    taxComplianceRate: 0,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-inf-002',
    name: 'Unidad Productiva Informal #3',
    type: 'informal_mycelium',
    x: -3.14,
    z: -3.23,
    sizeEmployees: 1,
    baseEmployees: 1,
    height: 1.8,
    productivityScore: 9.4,
    taxComplianceRate: 0,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
  {
    id: 'firm-inf-003',
    name: 'Unidad Productiva Informal #4',
    type: 'informal_mycelium',
    x: 3.23,
    z: -3.14,
    sizeEmployees: 2,
    baseEmployees: 2,
    height: 1.8,
    productivityScore: 15.8,
    taxComplianceRate: 0,
    emergenceMonth: 0,
    growthSpanMonths: 1,
  },
];
export const MODEL_FIRMS = DEMO_FIRMS;
export const MOCK_FIRMS = DEMO_FIRMS;

export const DEMO_ML_ALGORITHMS: MLAlgorithmMetric[] = [];
export const MOCK_ML_ALGORITHMS = DEMO_ML_ALGORITHMS;

export const DEMO_COHORTS: CohortPrediction[] = [];
export const MOCK_COHORTS = DEMO_COHORTS;

// MICRODATOS REALES (Vacío hasta que se carguen microdatos oficiales en data/microdatos_reales/)
export const DEMO_DATASETS: DatasetEntry[] = [];
export const MOCK_DATASETS = DEMO_DATASETS;

// USUARIOS FICTICIOS DE DEMOSTRACIÓN (Dominios cambiados a example.org)
export const DEMO_USERS: UserAccount[] = [
  {
    id: 'usr-01',
    name: 'Dra. Amina Diallo (Ficticia)',
    email: 'a.diallo@example.org',
    role: 'ADMIN',
    department: 'Dirección de Modelado & Demostración',
    lastActive: 'En línea ahora',
    permissions: {
      editPolicies: true,
      retrainAI: true,
      manageDatasets: true,
      manageUsers: true,
      exportReports: true,
    },
  },
  {
    id: 'usr-02',
    name: 'Lic. Mateo Rossi (Ficticio)',
    email: 'm.rossi@example.org',
    role: 'POLICY_ANALYST',
    department: 'Análisis de Políticas (Demostración)',
    lastActive: 'Hace 14 min',
    permissions: {
      editPolicies: true,
      retrainAI: false,
      manageDatasets: true,
      manageUsers: false,
      exportReports: true,
    },
  },
  {
    id: 'usr-03',
    name: 'Prof. Rajesh K. Patel (Ficticio)',
    email: 'r.patel@example.org',
    role: 'RESEARCHER',
    department: 'Investigación Laboral (Demostración)',
    lastActive: 'Hace 2 horas',
    permissions: {
      editPolicies: false,
      retrainAI: false,
      manageDatasets: false,
      manageUsers: false,
      exportReports: true,
    },
  },
];
export const MOCK_USERS = DEMO_USERS;

export const DEMO_SIM_RUNS: SimulationRun[] = [
  {
    id: 'RUN-2034-098',
    name: 'Kenia: Reducción Barreras Registro + Subsidio $50',
    timestamp: 'Hoy, 22:45',
    country: 'KENYA',
    scenario: 'Escenario A + B Combinado',
    status: 'completada',
    informalityChange: -12.4,
    executionTimeSec: 4.8,
  },
  {
    id: 'RUN-2034-097',
    name: 'India: Shock de Automatización en Ensamblaje',
    timestamp: 'Hoy, 21:12',
    country: 'INDIA',
    scenario: 'Escenario E Automatización',
    status: 'completada',
    informalityChange: +6.1,
    executionTimeSec: 5.2,
  },
  {
    id: 'RUN-2034-096',
    name: 'Nigeria: Programa Masivo Capacitación Técnica',
    timestamp: 'Ayer, 18:30',
    country: 'NIGERIA',
    scenario: 'Política de Capital Humano',
    status: 'completada',
    informalityChange: -7.8,
    executionTimeSec: 6.1,
  },
  {
    id: 'RUN-2034-095',
    name: 'Bangladesh: Subsidio RMG vs Informalidad Rural',
    timestamp: 'Ayer, 14:05',
    country: 'BANGLADESH',
    scenario: 'Transición Estructural',
    status: 'completada',
    informalityChange: -9.2,
    executionTimeSec: 4.5,
  },
  {
    id: 'RUN-2034-094',
    name: 'Stress Test: Hiper-inspección Punitiva',
    timestamp: 'Hace 2 días',
    country: 'KENYA',
    scenario: 'Fiscalización Estricta 80%',
    status: 'error',
    informalityChange: +3.2,
    executionTimeSec: 8.9,
  },
];
export const MOCK_SIM_RUNS = DEMO_SIM_RUNS;

