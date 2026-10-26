import { 
  CountryCode, 
  StructuralFirm, 
  MLAlgorithmMetric, 
  CohortPrediction, 
  SimulationRun, 
  DatasetEntry, 
  UserAccount,
  PolicyParameters,
  ScenarioPreset
} from '../types';
import trayectoriasData from '@/outputs/trayectorias_mensuales.json';
import ilostatCalibracionFuentes from './ilostat_calibracion_fuentes.json';

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
}

export const COUNTRY_PROFILES: Record<CountryCode, CountryProfile> = {
  KENYA: {
    code: 'KENYA',
    name: ilostatCalibracionFuentes.KENYA.label,
    flag: '🇰🇪',
    currency: 'KES',
    baseInformalityRate: 86.49, // ILOSTAT EMP_NIFL_SEX_RT 2019 (data/ilostat_series_historicas.csv)
    baseGini: 0.288, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: ilostatCalibracionFuentes.KENYA.full_source,
    terrainProfile: {
      peakFrequency: 2.2,
      valleyDepth: 1.8,
      terrainRoughness: 1.4,
      colorTint: '#00f0ff',
    },
  },
  NIGERIA: {
    code: 'NIGERIA',
    name: ilostatCalibracionFuentes.NIGERIA.label,
    flag: '🇳🇬',
    currency: 'NGN',
    baseInformalityRate: 93.14, // ILOSTAT EMP_NIFL_SEX_RT 2024 (data/ilostat_calibracion.csv)
    baseGini: 0.285, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: ilostatCalibracionFuentes.NIGERIA.full_source,
    terrainProfile: {
      peakFrequency: 1.8,
      valleyDepth: 2.4,
      terrainRoughness: 1.6,
      colorTint: '#10b981',
    },
  },
  INDIA: {
    code: 'INDIA',
    name: ilostatCalibracionFuentes.INDIA.label,
    flag: '🇮🇳',
    currency: 'INR',
    baseInformalityRate: 88.13, // ILOSTAT EMP_NIFL_SEX_RT 2024 (data/ilostat_calibracion.csv)
    baseGini: 0.292, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: ilostatCalibracionFuentes.INDIA.full_source,
    terrainProfile: {
      peakFrequency: 3.0,
      valleyDepth: 2.0,
      terrainRoughness: 1.8,
      colorTint: '#38bdf8',
    },
  },
  BANGLADESH: {
    code: 'BANGLADESH',
    name: ilostatCalibracionFuentes.BANGLADESH.label,
    flag: '🇧🇩',
    currency: 'BDT',
    baseInformalityRate: 84.14, // ILOSTAT EMP_NIFL_SEX_RT 2023 (data/ilostat_calibracion.csv)
    baseGini: 0.288, // Gini del modelo ITDT calibrado (Escenario A, mes 0 / post-burn-in)
    giniSource: 'Gini del modelo ITDT calibrado (Escenario A, mes 0)',
    informalitySource: ilostatCalibracionFuentes.BANGLADESH.full_source,
    terrainProfile: {
      peakFrequency: 1.6,
      valleyDepth: 2.2,
      terrainRoughness: 1.2,
      colorTint: '#06b6d4',
    },
  },
};

export const INITIAL_POLICY_STATE: PolicyParameters = {
  scenario: 'A',
};

// GENERADOR DINÁMICO DE EMPRESAS SEGÚN LA PROPORCIÓN REAL DE FIRMAS FORMALES DE ITDTModel
export function getModelFirms(
  country: CountryCode = 'KENYA',
  scenario: ScenarioPreset = 'A',
  month: number = 0
): StructuralFirm[] {
  const cClean = (country || 'KENYA').toUpperCase();
  const scClean = (scenario || 'A').toUpperCase().replace('SCENARIO_', '').split('_')[0] || 'A';
  
  const cData = (trayectoriasData as any)[cClean] || (trayectoriasData as any)['KENYA'];
  const scData = cData?.[scClean] || cData?.['A'] || [];
  
  const clampedMonth = Math.max(1, Math.min(120, month > 0 ? month : 1));
  const monthItem = scData[clampedMonth - 1] || {};
  const formalRatio = monthItem.formal_firms_ratio ?? 0.05;

  let numFormal = Math.round(10 * formalRatio);
  if (formalRatio > 0.005 && numFormal === 0) {
    numFormal = 1;
  }
  numFormal = Math.min(10, Math.max(0, numFormal));

  const firms: StructuralFirm[] = [];
  for (let slot = 0; slot < 10; slot++) {
    const angle = (slot / 10.0) * Math.PI * 2 + 0.3;
    const isFormal = slot < numFormal;
    const radius = isFormal ? 8.5 : 5.2;
    const x = Number((Math.cos(angle) * radius).toFixed(2));
    const z = Number((Math.sin(angle) * radius).toFixed(2));
    const fid = isFormal ? `UP-F-${slot + 1}` : `UP-INF-${slot + 1 - numFormal}`;

    if (isFormal) {
      firms.push({
        id: fid,
        name: fid,
        type: 'formal',
        x,
        z,
        height: 8.5,
        L_j: 35.0,
        Y_j: 120.0,
        A_j: 1.5,
        emergenceMonth: 0,
        growthSpanMonths: 1,
      });
    } else {
      firms.push({
        id: fid,
        name: fid,
        type: 'informal_mycelium',
        x,
        z,
        height: 2.2,
        L_j: 3.0,
        Y_j: 15.0,
        A_j: 0.8,
        emergenceMonth: 0,
        growthSpanMonths: 1,
      });
    }
  }
  return firms;
}

export const DEMO_FIRMS: StructuralFirm[] = getModelFirms('KENYA', 'A', 0);
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

export const DEMO_SIM_RUNS: SimulationRun[] = [];
export const MOCK_SIM_RUNS = DEMO_SIM_RUNS;

