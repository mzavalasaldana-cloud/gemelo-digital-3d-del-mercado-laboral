// Mock datasets for AI Engine & Algorithmic Audit module

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
  direction: 'Positiva Fuerte' | 'Negativa Fuerte';
  impact: string;
}

export const EDA_KPIS = {
  dataQuality: 99.2,
  totalRecords: 15420,
  totalVariables: 14,
  nullPercentage: 0.0,
  imputationMethod: 'Mediana / Moda (Demostración)',
  surveySource: 'Datos sintéticos de demostración; no son microdatos oficiales',
};

export const EDA_HISTOGRAMS: Record<string, { label: string; unit: string; data: EDAVariableDistribution[] }> = {
  salary: {
    label: 'Ingreso Salarial Mensual',
    unit: 'USD',
    data: [
      { range: '< $200', formalCount: 12000, informalCount: 145000, density: 0.18 },
      { range: '$200 - $350', formalCount: 45000, informalCount: 260000, density: 0.35 },
      { range: '$350 - $550', formalCount: 110000, informalCount: 195000, density: 0.28 },
      { range: '$550 - $800', formalCount: 195000, informalCount: 82000, density: 0.14 },
      { range: '$800 - $1200', formalCount: 140000, informalCount: 28000, density: 0.08 },
      { range: '> $1200', formalCount: 85000, informalCount: 9000, density: 0.04 },
    ],
  },
  hours: {
    label: 'Horas Trabajadas Semanales',
    unit: 'Horas',
    data: [
      { range: '< 20h', formalCount: 15000, informalCount: 88000, density: 0.12 },
      { range: '20 - 35h', formalCount: 38000, informalCount: 142000, density: 0.22 },
      { range: '36 - 40h', formalCount: 185000, informalCount: 110000, density: 0.31 },
      { range: '41 - 48h', formalCount: 220000, informalCount: 165000, density: 0.26 },
      { range: '49 - 60h', formalCount: 65000, informalCount: 135000, density: 0.16 },
      { range: '> 60h', formalCount: 18000, informalCount: 79000, density: 0.09 },
    ],
  },
  education: {
    label: 'Años de Educación Formal',
    unit: 'Años',
    data: [
      { range: '0 - 5 años (Primaria inc.)', formalCount: 12000, informalCount: 185000, density: 0.21 },
      { range: '6 - 9 años (Primaria comp.)', formalCount: 42000, informalCount: 240000, density: 0.32 },
      { range: '10 - 12 años (Secundaria)', formalCount: 165000, informalCount: 215000, density: 0.36 },
      { range: '13 - 16 años (Superior)', formalCount: 240000, informalCount: 72000, density: 0.18 },
      { range: '17+ años (Posgrado)', formalCount: 75000, informalCount: 7000, density: 0.06 },
    ],
  },
};

export const CORRELATION_VARIABLES = [
  'Formalidad',
  'Salario USD',
  'Años Educ.',
  'Tam. Empresa',
  'Aporte Seg. Soc.',
  'Tasa Inspecc.',
];

export const CORRELATION_MATRIX: number[][] = [
  [1.00, 0.68, 0.62, 0.74, 0.84, 0.58],
  [0.68, 1.00, 0.73, 0.65, 0.71, 0.44],
  [0.62, 0.73, 1.00, 0.51, 0.59, 0.38],
  [0.74, 0.65, 0.51, 1.00, 0.79, 0.63],
  [0.84, 0.71, 0.59, 0.79, 1.00, 0.61],
  [0.58, 0.44, 0.38, 0.63, 0.61, 1.00],
];

export const BOXPLOT_METRICS: BoxplotMetric[] = [
  {
    group: 'Empleo Formal',
    min: 240,
    q1: 520,
    median: 840,
    q3: 1320,
    max: 2400,
    outliers: [2800, 3400, 4200],
  },
  {
    group: 'Empleo Informal',
    min: 80,
    q1: 190,
    median: 310,
    q3: 480,
    max: 950,
    outliers: [1150, 1380, 1620],
  },
];

export const HIGH_CORRELATIONS_TABLE: HighCorrelationItem[] = [
  {
    varA: 'Aporte Continuo a Seguridad Social',
    varB: 'Probabilidad de Formalidad Laboral',
    r: 0.84,
    pValue: '< 0.0001',
    direction: 'Positiva Fuerte',
    impact: 'El registro a pensiones y salud es el predictor determinante más directo de estabilidad formal.',
  },
  {
    varA: 'Tamaño de la Unidad Productiva (Personal)',
    varB: 'Aporte a Seguridad Social Colectivo',
    r: 0.79,
    pValue: '< 0.0001',
    direction: 'Positiva Fuerte',
    impact: 'Empresas con más de 10 trabajadores muestran elasticidad formal superior a 80%.',
  },
  {
    varA: 'Registro Tributario / RUC / Licencia',
    varB: 'Acceso a Crédito en Sistema Bancario',
    r: 0.78,
    pValue: '< 0.0001',
    direction: 'Positiva Fuerte',
    impact: 'La bancarización formal reduce los incentivos de ocultamiento transaccional.',
  },
  {
    varA: 'Nivel Educativo Universitario / Técnico',
    varB: 'Ingreso Salarial Formal',
    r: 0.73,
    pValue: '< 0.0001',
    direction: 'Positiva Fuerte',
    impact: 'Retorno salarial adicional del 11.4% por año de educación terciaria acreditada.',
  },
  {
    varA: 'Uso de Medios de Pago Digitales (QR/M-Pesa)',
    varB: 'Transparencia de Facturación',
    r: 0.71,
    pValue: '< 0.0001',
    direction: 'Positiva Fuerte',
    impact: 'La huella digital de transacciones desincentiva la economía sumergida en efectivo.',
  },
];

// Cross-Validation Mock Data
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

export const CV_PRESET_RESULTS: Record<string, CVMockResult> = {
  xgboost: {
    algorithm: 'XGBoost Classifier v3.4',
    kFolds: 5,
    strategy: 'K-Fold Estratificado (StratifiedKFold)',
    metricsTrainVsTest: [
      { metric: 'Accuracy', Train: 95.8, Test: 92.6 },
      { metric: 'Precision', Train: 95.1, Test: 92.4 },
      { metric: 'Recall', Train: 93.9, Test: 90.1 },
      { metric: 'F1-Score', Train: 94.5, Test: 91.2 },
      { metric: 'ROC_AUC', Train: 97.6, Test: 94.8 },
    ],
    foldsF1: [
      { fold: 'Fold 1', f1Score: 91.1, rocAuc: 94.7, accuracy: 92.4 },
      { fold: 'Fold 2', f1Score: 91.8, rocAuc: 95.1, accuracy: 92.9 },
      { fold: 'Fold 3', f1Score: 90.9, rocAuc: 94.5, accuracy: 92.3 },
      { fold: 'Fold 4', f1Score: 91.6, rocAuc: 95.0, accuracy: 92.8 },
      { fold: 'Fold 5', f1Score: 90.7, rocAuc: 94.6, accuracy: 92.5 },
    ],
    confusionMatrix: {
      tp: 48250,
      fp: 4680,
      fn: 3950,
      tn: 48520,
      tpPct: 92.4,
      fpPct: 8.8,
      fnPct: 7.6,
      tnPct: 91.2,
    },
    summary: {
      meanF1: 91.2,
      stdF1: 0.44,
      meanRocAuc: 94.8,
      stdRocAuc: 0.25,
    },
  },
  lightgbm: {
    algorithm: 'LightGBM Gradient Booster',
    kFolds: 5,
    strategy: 'K-Fold Estratificado (StratifiedKFold)',
    metricsTrainVsTest: [
      { metric: 'Accuracy', Train: 94.9, Test: 91.8 },
      { metric: 'Precision', Train: 94.2, Test: 91.1 },
      { metric: 'Recall', Train: 92.8, Test: 89.2 },
      { metric: 'F1-Score', Train: 93.5, Test: 90.1 },
      { metric: 'ROC_AUC', Train: 96.9, Test: 93.9 },
    ],
    foldsF1: [
      { fold: 'Fold 1', f1Score: 90.0, rocAuc: 93.7, accuracy: 91.6 },
      { fold: 'Fold 2', f1Score: 90.5, rocAuc: 94.2, accuracy: 92.1 },
      { fold: 'Fold 3', f1Score: 89.8, rocAuc: 93.6, accuracy: 91.5 },
      { fold: 'Fold 4', f1Score: 90.4, rocAuc: 94.1, accuracy: 92.0 },
      { fold: 'Fold 5', f1Score: 89.9, rocAuc: 93.8, accuracy: 91.7 },
    ],
    confusionMatrix: {
      tp: 46800,
      fp: 5200,
      fn: 4400,
      tn: 47900,
      tpPct: 91.4,
      fpPct: 9.8,
      fnPct: 8.6,
      tnPct: 90.2,
    },
    summary: {
      meanF1: 90.1,
      stdF1: 0.31,
      meanRocAuc: 93.9,
      stdRocAuc: 0.28,
    },
  },
  random_forest: {
    algorithm: 'Random Forest Ensemble (500 Trees)',
    kFolds: 5,
    strategy: 'K-Fold Estratificado (StratifiedKFold)',
    metricsTrainVsTest: [
      { metric: 'Accuracy', Train: 93.4, Test: 89.8 },
      { metric: 'Precision', Train: 92.8, Test: 88.9 },
      { metric: 'Recall', Train: 91.1, Test: 87.2 },
      { metric: 'F1-Score', Train: 91.9, Test: 88.0 },
      { metric: 'ROC_AUC', Train: 95.4, Test: 92.1 },
    ],
    foldsF1: [
      { fold: 'Fold 1', f1Score: 87.8, rocAuc: 91.9, accuracy: 89.6 },
      { fold: 'Fold 2', f1Score: 88.4, rocAuc: 92.3, accuracy: 90.1 },
      { fold: 'Fold 3', f1Score: 87.7, rocAuc: 91.8, accuracy: 89.5 },
      { fold: 'Fold 4', f1Score: 88.2, rocAuc: 92.2, accuracy: 89.9 },
      { fold: 'Fold 5', f1Score: 88.0, rocAuc: 92.1, accuracy: 89.8 },
    ],
    confusionMatrix: {
      tp: 44900,
      fp: 6100,
      fn: 5300,
      tn: 46200,
      tpPct: 89.4,
      fpPct: 11.7,
      fnPct: 10.6,
      tnPct: 88.3,
    },
    summary: {
      meanF1: 88.0,
      stdF1: 0.29,
      meanRocAuc: 92.1,
      stdRocAuc: 0.21,
    },
  },
};

// Cohort Projections Mock Data
export interface ExtendedCohortData {
  id: string;
  label: string;
  populationShare: number;
  probability: number;
  estimatedMonths: number;
  topDrivers: {
    feature: string;
    importance: number; // 0 to 100
    shapValue: string;
  }[];
  policyIntervention: string;
  barrier: string;
}

export const EXTENDED_COHORTS: ExtendedCohortData[] = [
  {
    id: 'cohort-01',
    label: 'Jóvenes (18-24) en comercio informal urbano',
    populationShare: 24.8,
    probability: 68.5,
    estimatedMonths: 14,
    topDrivers: [
      { feature: 'Subsidio Guardería & Costo Cero RUC', importance: 88, shapValue: '+0.34' },
      { feature: 'Capacitación en Habilidades Digitales / E-commerce', importance: 74, shapValue: '+0.27' },
      { feature: 'Microcrédito Bonificado con Monotributo', importance: 62, shapValue: '+0.21' },
    ],
    policyIntervention: 'Ventanilla única digital móvil con exención del 100% de aportes en el año 1 y créditos productivos vinculados a facturación electrónica.',
    barrier: 'Altos costos fijos de entrada inicial y falta de historial crediticio en banca comercial.',
  },
  {
    id: 'cohort-02',
    label: 'Mujeres jefas de hogar en microcomercio y servicios',
    populationShare: 21.2,
    probability: 61.4,
    estimatedMonths: 18,
    topDrivers: [
      { feature: 'Red de Cuidado Infantil Comunitario', importance: 92, shapValue: '+0.41' },
      { feature: 'Seguro Social No Contributivo Transitorio', importance: 79, shapValue: '+0.31' },
      { feature: 'Acceso a Terminales de Cobro Digital POS', importance: 58, shapValue: '+0.19' },
    ],
    policyIntervention: 'Políticas integradas de economía del cuidado que liberan 18h semanales para gestión formal y formalización asociativa cooperativa.',
    barrier: 'Pobreza de tiempo por sobrecarga de labores domésticas no remuneradas y precariedad de ingresos.',
  },
  {
    id: 'cohort-03',
    label: 'Trabajadores agrarios y rurales estacionales',
    populationShare: 18.6,
    probability: 47.2,
    estimatedMonths: 26,
    topDrivers: [
      { feature: 'Régimen Laboral Agrario Discontinuo / Por Cosecha', importance: 85, shapValue: '+0.38' },
      { feature: 'Seguro Catastrófico Climático Estatal', importance: 69, shapValue: '+0.26' },
      { feature: 'Asociatividad Cooperativa de Productores', importance: 64, shapValue: '+0.22' },
    ],
    policyIntervention: 'Contratos agropecuarios temporales con cotización proporcional acumulable por jornales sin pérdida de programas sociales.',
    barrier: 'Intermitencia de ingresos por ciclos climáticos y dispersión geográfica de las inspecciones laborales.',
  },
  {
    id: 'cohort-04',
    label: 'Microemprendedores de talleres y manufactura (Jua Kali)',
    populationShare: 19.5,
    probability: 73.8,
    estimatedMonths: 11,
    topDrivers: [
      { feature: 'Conexión a Red Eléctrica Industrial Tarifa Social', importance: 90, shapValue: '+0.43' },
      { feature: 'Compras Públicas Reservadas a Microempresas (20%)', importance: 81, shapValue: '+0.33' },
      { feature: 'Certificación de Competencias Laborales', importance: 56, shapValue: '+0.18' },
    ],
    policyIntervention: 'Parques industriales ligeros con infraestructura compartida, maquinaria en alquiler y titulación acelerada de locales comerciales.',
    barrier: 'Inseguridad jurídica sobre locales y costos exorbitantes de servicios básicos monofásicos.',
  },
  {
    id: 'cohort-05',
    label: 'Trabajadores de plataformas digitales y Gig Economy',
    populationShare: 15.9,
    probability: 79.4,
    estimatedMonths: 8,
    topDrivers: [
      { feature: 'Aporte Automático en Fuente por Algoritmo de App', importance: 95, shapValue: '+0.49' },
      { feature: 'Portabilidad de Beneficios Sociales Inter-Apps', importance: 83, shapValue: '+0.35' },
      { feature: 'Seguro contra Accidentes de Tránsito Cubierto por App', importance: 71, shapValue: '+0.24' },
    ],
    policyIntervention: 'Obligación a plataformas digitales de retener el 4% para fondo mutuo de pensiones y salud sin tipificación de relación de dependencia estricta.',
    barrier: 'Vacío regulatorio internacional y asimetría de poder en la fijación de tarifas dinámicas por algoritmo.',
  },
];

// Hyperparameters & Statistical Tests Data (Demostración)
export const OPTIMAL_HYPERPARAMS_JSON = {
  model_id: 'xgboost-demo-opt-v3.4',
  framework: 'XGBoost 3.4.0 (Demostración)',
  objective: 'binary:logistic',
  eval_metric: 'aucpr',
  tree_method: 'hist',
  device: 'cpu',
  best_params: {
    max_depth: 6,
    learning_rate: 0.042,
    n_estimators: 420,
    min_child_weight: 3.5,
    subsample: 0.85,
    colsample_bytree: 0.80,
    reg_alpha: 0.05,
    reg_lambda: 1.35,
    gamma: 0.15,
    scale_pos_weight: 1.18,
  },
  optimization_metrics: {
    roc_auc_baseline: 0.924,
    roc_auc_optimized: 0.948,
    delta_roc_auc: '+0.024 (+2.6%)',
    f1_score_optimized: 0.912,
    trials_evaluated: 120,
    search_strategy: 'Optuna TPE (Demostración)',
    execution_time_seconds: 4.8,
  },
  fairness_constraints: {
    demographic_parity_ratio: 0.962,
    equalized_odds_difference: 0.028,
    status: 'Demostración de auditoría de sesgo (Fairness Audit)',
  },
};

export interface StatisticalTestRow {
  testName: string;
  variable: string;
  statistic: string;
  pValue: string;
  criticalValue: string;
  conclusion: string;
  status: 'passed' | 'warning' | 'failed';
}

export const STATISTICAL_TESTS_RESULTS: StatisticalTestRow[] = [
  {
    testName: 'Kolmogorov-Smirnov (Demostración)',
    variable: 'Salario Formal vs Salario Informal',
    statistic: 'D = 0.482',
    pValue: '< 0.00001',
    criticalValue: 'D_crit = 0.018',
    conclusion: '[Demostración] Distribuciones calculadas sobre muestra sintética.',
    status: 'passed',
  },
  {
    testName: 'Kolmogorov-Smirnov (Demostración)',
    variable: 'Horas Semanales (Hombres vs Mujeres)',
    statistic: 'D = 0.314',
    pValue: '< 0.0001',
    criticalValue: 'D_crit = 0.018',
    conclusion: '[Demostración] Brecha de horas estimada sobre muestra sintética.',
    status: 'passed',
  },
  {
    testName: 'Test Shapiro-Wilk (Demostración)',
    variable: 'Logaritmo de Productividad por Empleado',
    statistic: 'W = 0.988',
    pValue: '0.042',
    criticalValue: 'W_crit = 0.985',
    conclusion: '[Demostración] Aproximación log-normal sobre muestra sintética.',
    status: 'passed',
  },
  {
    testName: 'Factor Inflación Varianza VIF (Demostración)',
    variable: 'Educación x Edad x Experiencia',
    statistic: 'Max VIF = 2.84',
    pValue: 'N/A',
    criticalValue: 'Umbral VIF < 5.0',
    conclusion: '[Demostración] Ausencia de multicolinealidad severa en muestra sintética.',
    status: 'passed',
  },
  {
    testName: 'Paridad Demográfica (Demostración)',
    variable: 'Tasa de Selección Formal por Género',
    statistic: 'Ratio = 0.962',
    pValue: '0.68',
    criticalValue: 'Regla del 80% (Ratio > 0.80)',
    conclusion: '[Demostración] Simulación de auditoría algorítmica sin sesgo adverso.',
    status: 'passed',
  },
];
