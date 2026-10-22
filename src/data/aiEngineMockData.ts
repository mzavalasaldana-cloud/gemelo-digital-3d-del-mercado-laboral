// Estructuras de tipos para el Motor IA & Auditoría Algorítmica.
// Conforme a la regla de integridad: SIN DATOS SINTÉTICOS NI INVENTADOS.
// Los datos reales deben ser provistos vía backend desde data/microdatos_reales/<pais>/.

export interface EDAVariableDistribution {
  range: string;
  formalCount: number;
  informalCount: number;
  density: number;
}

export interface CorrelationCell {
  varA: string;
  varB: string;
  val: number;
}

export interface BoxplotMetric {
  group: string;
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  outliers: number[];
}

export interface HighCorrelationItem {
  varA: string;
  varB: string;
  r: number;
  pValue: string;
  direction: string;
  impact: string;
}

// Valores vacíos por defecto: Si no hay microdatos reales cargados, no se muestran valores inventados.
export const EDA_KPIS = null;
export const DEMO_EDA_KPIS = null;

export const EDA_HISTOGRAMS: Record<string, { label: string; unit: string; data: EDAVariableDistribution[] }> = {};
export const DEMO_EDA_HISTOGRAMS = EDA_HISTOGRAMS;

export const CORRELATION_VARIABLES: string[] = [];
export const DEMO_CORRELATION_VARIABLES = CORRELATION_VARIABLES;

export const CORRELATION_MATRIX: number[][] = [];
export const DEMO_CORRELATION_MATRIX = CORRELATION_MATRIX;

export const BOXPLOT_METRICS: BoxplotMetric[] = [];
export const DEMO_BOXPLOT_METRICS = BOXPLOT_METRICS;

export const HIGH_CORRELATIONS_TABLE: HighCorrelationItem[] = [];
export const DEMO_HIGH_CORRELATIONS_TABLE = HIGH_CORRELATIONS_TABLE;

export interface CVMockResult {
  algorithm: string;
  kFolds: number;
  strategy: string;
  metricsTrainVsTest: {
    metric: string;
    Train: number;
    Test: number;
  }[];
  foldsF1: {
    fold: string;
    f1Score: number;
    rocAuc: number;
    accuracy: number;
  }[];
  confusionMatrix: {
    tp: number;
    fp: number;
    fn: number;
    tn: number;
    tpPct: number;
    fpPct: number;
    fnPct: number;
    tnPct: number;
  };
  summary: {
    meanF1: number;
    stdF1: number;
    meanRocAuc: number;
    stdRocAuc: number;
  };
}

export const CV_PRESET_RESULTS: Record<string, CVMockResult> = {};
export const DEMO_CV_PRESET_RESULTS = CV_PRESET_RESULTS;

export interface ExtendedCohortData {
  id: string;
  label: string;
  populationShare: number;
  probability: number;
  estimatedMonths: number;
  topDrivers: {
    feature: string;
    importance: number;
    shapValue: string;
  }[];
  policyIntervention: string;
  barrier: string;
}

export const EXTENDED_COHORTS: ExtendedCohortData[] = [];
export const DEMO_EXTENDED_COHORTS = EXTENDED_COHORTS;

export const OPTIMAL_HYPERPARAMS_JSON: any = null;

export interface StatisticalTestRow {
  testName: string;
  variable: string;
  statistic: string;
  pValue: string;
  criticalValue: string;
  conclusion: string;
  status: 'passed' | 'warning' | 'failed';
}

export const STATISTICAL_TESTS_RESULTS: StatisticalTestRow[] = [];
export const DEMO_STATISTICAL_TESTS_RESULTS = STATISTICAL_TESTS_RESULTS;
