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
  population: string;
  baseInformalityRate: number; // %
  baseGini: number;
  terrainProfile: {
    peakFrequency: number;
    valleyDepth: number;
    terrainRoughness: number;
    colorTint: string;
  };
  keyClusters: string[];
  contextDescription: string;
}

export const COUNTRY_PROFILES: Record<CountryCode, CountryProfile> = {
  KENYA: {
    code: 'KENYA',
    name: 'Kenia (KNBS-ILFS)',
    flag: '🇰🇪',
    currency: 'KES',
    population: '54.0M',
    baseInformalityRate: 83.2,
    baseGini: 0.408,
    terrainProfile: {
      peakFrequency: 2.2,
      valleyDepth: 1.8,
      terrainRoughness: 1.4,
      colorTint: '#00f0ff',
    },
    keyClusters: ['Nairobi Silicon Savannah', 'Mombasa Port Hub', 'Jua Kali Artisan Basins', 'Eldoret Agri-Valley'],
    contextDescription: 'Alta prevalencia del sector informal "Jua Kali", microfinanzas móviles M-Pesa y polo tecnológico en Nairobi.',
  },
  NIGERIA: {
    code: 'NIGERIA',
    name: 'Nigeria (NBS-NLFS)',
    flag: '🇳🇬',
    currency: 'NGN',
    population: '223.8M',
    baseInformalityRate: 88.5,
    baseGini: 0.351,
    terrainProfile: {
      peakFrequency: 1.8,
      valleyDepth: 2.4,
      terrainRoughness: 1.6,
      colorTint: '#10b981',
    },
    keyClusters: ['Lagos Financial Island', 'Kano Commercial Axis', 'Onitsha Market Hub', 'Niger Delta Energy'],
    contextDescription: 'Mercados urbanos densos, comercio informal masivo en Lagos y brechas significativas entre el sector formal corporativo y microtalleres.',
  },
  INDIA: {
    code: 'INDIA',
    name: 'India (PLFS MoSPI)',
    flag: '🇮🇳',
    currency: 'INR',
    population: '1.428B',
    baseInformalityRate: 81.4,
    baseGini: 0.357,
    terrainProfile: {
      peakFrequency: 3.0,
      valleyDepth: 2.0,
      terrainRoughness: 1.8,
      colorTint: '#38bdf8',
    },
    keyClusters: ['Bengaluru Tech Triangle', 'Maharashtra Manufacturing', 'Ganga Rural Basin', 'Surat Textile Clusters'],
    contextDescription: 'Enorme sector "unorganized", transición de manufactura semi-formal y rápido crecimiento de plataformas gig de servicios.',
  },
  BANGLADESH: {
    code: 'BANGLADESH',
    name: 'Bangladesh (BBS-LFS)',
    flag: '🇧🇩',
    currency: 'BDT',
    population: '171.2M',
    baseInformalityRate: 84.9,
    baseGini: 0.399,
    terrainProfile: {
      peakFrequency: 1.6,
      valleyDepth: 2.2,
      terrainRoughness: 1.2,
      colorTint: '#06b6d4',
    },
    keyClusters: ['Dhaka RMG Ready-Made Garments', 'Chittagong Maritime Corridor', 'Sylhet Plantation Lowlands', 'Khulna Delta Crafts'],
    contextDescription: 'Exportación textil masiva con encadenamientos de talleres informales subcontratados y microcréditos rurales.',
  },
};

export const INITIAL_POLICY_STATE: PolicyParameters = {
  registrationCostReduction: 30, // 30% reduction
  smeSubsidyUSDMonth: 50, // $50/month
  skillsTrainingCoverage: 25, // 25% coverage
  socialProtectionTax: 12, // 12% tax/contribution
  smartInspectionCoverage: 20, // 20% inspection
};

// EMPRESAS FICTICIAS DE DEMOSTRACIÓN (No representan entidades corporativas reales)
export const MOCK_FIRMS: StructuralFirm[] = [
  // Formal hexagonal crystal enterprises with emergence timeline
  {
    id: 'firm-f-01',
    name: 'Apex Synth & Tech Corp',
    type: 'formal',
    x: -8,
    z: -6,
    sizeEmployees: 1420,
    height: 6.5,
    sectorCategory: 'Tecnología',
    productivityScore: 92,
    formalizationCostUSD: 2400,
    taxComplianceRate: 98,
    baseEmployees: 1420,
    emergenceMonth: 0, // Present at baseline month 0
    growthSpanMonths: 1,
  },
  {
    id: 'firm-f-02',
    name: 'Metropolis Port Logistics Ltd',
    type: 'formal',
    x: 7,
    z: -7,
    sizeEmployees: 980,
    height: 5.2,
    sectorCategory: 'Logística',
    productivityScore: 84,
    formalizationCostUSD: 1800,
    taxComplianceRate: 95,
    baseEmployees: 980,
    emergenceMonth: 0, // Present at baseline month 0
    growthSpanMonths: 1,
  },
  {
    id: 'firm-f-03',
    name: 'Vanguard Industrial Textiles',
    type: 'formal',
    x: 0,
    z: -10,
    sizeEmployees: 2150,
    height: 7.8,
    sectorCategory: 'Manufactura',
    productivityScore: 88,
    formalizationCostUSD: 3100,
    taxComplianceRate: 99,
    baseEmployees: 2150,
    emergenceMonth: 20, // Emerges as formalization takes off (Year 2)
    growthSpanMonths: 10,
  },
  {
    id: 'firm-f-04',
    name: 'Equator Agro-Bio Processing',
    type: 'formal',
    x: -11,
    z: 5,
    sizeEmployees: 640,
    height: 4.5,
    sectorCategory: 'Agroindustria',
    productivityScore: 76,
    formalizationCostUSD: 1400,
    taxComplianceRate: 92,
    baseEmployees: 640,
    emergenceMonth: 42, // Emerges at Month 42 (mid-Year 4)
    growthSpanMonths: 10,
  },
  {
    id: 'firm-f-05',
    name: 'Nova Pharma Labs',
    type: 'formal',
    x: 10,
    z: 4,
    sizeEmployees: 510,
    height: 4.2,
    sectorCategory: 'Tecnología',
    productivityScore: 89,
    formalizationCostUSD: 2800,
    taxComplianceRate: 97,
    baseEmployees: 510,
    emergenceMonth: 65, // Emerges at Month 65 (Year 5)
    growthSpanMonths: 12,
  },
  {
    id: 'firm-f-06',
    name: 'Solar Grid Micro-Dynamics',
    type: 'formal',
    x: -4,
    z: -4,
    sizeEmployees: 890,
    height: 5.6,
    sectorCategory: 'Tecnología',
    productivityScore: 91,
    formalizationCostUSD: 2100,
    taxComplianceRate: 96,
    baseEmployees: 890,
    emergenceMonth: 85, // Emerges at Month 85 (Year 7)
    growthSpanMonths: 12,
  },
  {
    id: 'firm-f-07',
    name: 'Trans-Corridor Cargo Hub',
    type: 'formal',
    x: 4,
    z: -3,
    sizeEmployees: 1120,
    height: 6.0,
    sectorCategory: 'Logística',
    productivityScore: 87,
    formalizationCostUSD: 2600,
    taxComplianceRate: 94,
    baseEmployees: 1120,
    emergenceMonth: 102, // Emerges at Month 102 (Year 9)
    growthSpanMonths: 12,
  },

  // Informal mycelium clusters
  {
    id: 'firm-inf-01',
    name: 'Enjambre Micro-Talleres Jua Kali',
    type: 'informal_mycelium',
    x: -4,
    z: 4,
    sizeEmployees: 185,
    height: 0.6,
    sectorCategory: 'Manufactura',
    productivityScore: 38,
    formalizationCostUSD: 850,
    taxComplianceRate: 5,
    baseEmployees: 185,
  },
  {
    id: 'firm-inf-02',
    name: 'Red Mercaderes Callejeros del Valle',
    type: 'informal_mycelium',
    x: 3,
    z: 8,
    sizeEmployees: 320,
    height: 0.5,
    sectorCategory: 'Comercio & Retail',
    productivityScore: 29,
    formalizationCostUSD: 620,
    taxComplianceRate: 2,
    baseEmployees: 320,
  },
  {
    id: 'firm-inf-03',
    name: 'Nodo Micelio Transporte Boda/Rikshaw',
    type: 'informal_mycelium',
    x: 6,
    z: 0,
    sizeEmployees: 240,
    height: 0.6,
    sectorCategory: 'Logística',
    productivityScore: 33,
    formalizationCostUSD: 740,
    taxComplianceRate: 4,
    baseEmployees: 240,
  },
  {
    id: 'firm-inf-04',
    name: 'Taller Confección Subcontratada',
    type: 'informal_mycelium',
    x: -6,
    z: 9,
    sizeEmployees: 160,
    height: 0.5,
    sectorCategory: 'Servicios Personales',
    productivityScore: 41,
    formalizationCostUSD: 910,
    taxComplianceRate: 6,
    baseEmployees: 160,
  },
];

export const MOCK_ML_ALGORITHMS: MLAlgorithmMetric[] = [
  {
    id: 'algo-xgboost',
    name: 'XGBoost Gradient Boosted Trees v3.4',
    f1Score: 0.914,
    rocAuc: 0.948,
    latencyMs: 1.8,
    interpretability: 82,
    accuracy: 92.6,
    isDeployed: true,
  },
  {
    id: 'algo-rf',
    name: 'Random Forest Ensemble (500 Trees)',
    f1Score: 0.887,
    rocAuc: 0.921,
    latencyMs: 3.4,
    interpretability: 89,
    accuracy: 89.8,
    isDeployed: false,
  },
  {
    id: 'algo-deepnn',
    name: 'Deep Residual Network (Embedding PyTorch)',
    f1Score: 0.928,
    rocAuc: 0.961,
    latencyMs: 7.2,
    interpretability: 44,
    accuracy: 93.9,
    isDeployed: false,
  },
  {
    id: 'algo-svm',
    name: 'Support Vector Classifier (RBF Kernel)',
    f1Score: 0.832,
    rocAuc: 0.865,
    latencyMs: 14.6,
    interpretability: 68,
    accuracy: 84.1,
    isDeployed: false,
  },
  {
    id: 'algo-survival',
    name: 'Cox Proportional Hazards (Supervivencia)',
    f1Score: 0.854,
    rocAuc: 0.893,
    latencyMs: 2.1,
    interpretability: 95,
    accuracy: 86.7,
    isDeployed: false,
  },
];

export const MOCK_COHORTS: CohortPrediction[] = [
  {
    id: 'cohort-01',
    label: 'Mujeres jóvenes en comercio informal urbano',
    populationShare: 24.8,
    prob1Year: 18.4,
    prob3Year: 42.1,
    prob5Year: 67.8,
    topDriver: 'Subsidio Guardería & Costo Registro Cero',
  },
  {
    id: 'cohort-02',
    label: 'Varones adultos en manufactura/talleres Jua Kali',
    populationShare: 19.5,
    prob1Year: 22.0,
    prob3Year: 51.3,
    prob5Year: 74.2,
    topDriver: 'Crédito $50/mes + Certificación de Oficio',
  },
  {
    id: 'cohort-03',
    label: 'Trabajadores agrícolas de subsistencia',
    populationShare: 31.2,
    prob1Year: 6.8,
    prob3Year: 19.4,
    prob5Year: 38.0,
    topDriver: 'Extensión Cooperativa & Encadenamiento Agro',
  },
  {
    id: 'cohort-04',
    label: 'Jóvenes técnicos de servicios y plataformas gig',
    populationShare: 15.6,
    prob1Year: 34.5,
    prob3Year: 63.8,
    prob5Year: 82.5,
    topDriver: 'Régimen Simplificado Monotributo Digital',
  },
];

// DATASETS SINTÉTICOS DE DEMOSTRACIÓN (No son microdatos oficiales)
export const MOCK_DATASETS: DatasetEntry[] = [
  {
    id: 'ds-plfs-ind',
    name: 'SINTETICO_calibrado_PLFS_India.csv',
    country: 'INDIA',
    yearSpan: '2023-2024',
    sampleSize: '48,500 registros sintéticos',
    recordsCount: 48500,
    institution: 'Generador sintético calibrado (Demostración)',
    variables: ['ESTADO_LABORAL', 'INGRESO_NETO_DIA', 'CAPITAL_HUMANO', 'EDAD', 'EDUCACION_ANIOS', 'APORTE_SEG_SOC', 'TAM_EMPRESA'],
    verified: false,
    active: true,
    description: 'Datos sintéticos de demostración; no son microdatos oficiales. El artículo no usa microdatos: usa solo tasas agregadas de ILOSTAT.',
  },
  {
    id: 'ds-knbs-ken',
    name: 'SINTETICO_calibrado_KNBS_Kenya.csv',
    country: 'KENYA',
    yearSpan: '2024',
    sampleSize: '38,000 registros sintéticos',
    recordsCount: 38000,
    institution: 'Generador sintético calibrado (Demostración)',
    variables: ['ESTADO_LABORAL', 'INGRESO_NETO_DIA', 'CAPITAL_HUMANO', 'EDAD', 'EDUCACION_ANIOS', 'APORTE_SEG_SOC', 'TAM_EMPRESA'],
    verified: false,
    active: true,
    description: 'Datos sintéticos de demostración; no son microdatos oficiales. El artículo no usa microdatos: usa solo tasas agregadas de ILOSTAT.',
  },
  {
    id: 'ds-nbs-nga',
    name: 'SINTETICO_calibrado_NBS_Nigeria.csv',
    country: 'NIGERIA',
    yearSpan: '2023',
    sampleSize: '42,000 registros sintéticos',
    recordsCount: 42000,
    institution: 'Generador sintético calibrado (Demostración)',
    variables: ['ESTADO_LABORAL', 'INGRESO_NETO_DIA', 'CAPITAL_HUMANO', 'EDAD', 'EDUCACION_ANIOS', 'APORTE_SEG_SOC', 'TAM_EMPRESA'],
    verified: false,
    active: true,
    description: 'Datos sintéticos de demostración; no son microdatos oficiales. El artículo no usa microdatos: usa solo tasas agregadas de ILOSTAT.',
  },
  {
    id: 'ds-bbs-bgd',
    name: 'SINTETICO_calibrado_BBS_Bangladesh.csv',
    country: 'BANGLADESH',
    yearSpan: '2023-2024',
    sampleSize: '36,000 registros sintéticos',
    recordsCount: 36000,
    institution: 'Generador sintético calibrado (Demostración)',
    variables: ['ESTADO_LABORAL', 'INGRESO_NETO_DIA', 'CAPITAL_HUMANO', 'EDAD', 'EDUCACION_ANIOS', 'APORTE_SEG_SOC', 'TAM_EMPRESA'],
    verified: false,
    active: true,
    description: 'Datos sintéticos de demostración; no son microdatos oficiales. El artículo no usa microdatos: usa solo tasas agregadas de ILOSTAT.',
  },
];

// USUARIOS FICTICIOS DE DEMOSTRACIÓN (Dominios cambiados a example.org)
export const MOCK_USERS: UserAccount[] = [
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

export const MOCK_SIM_RUNS: SimulationRun[] = [
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
