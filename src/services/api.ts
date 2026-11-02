import { 
  PolicyParameters, 
  StructuralMetrics, 
  SimulationRun, 
  CountryCode, 
  ScenarioPreset 
} from '../types';
import { 
  EDA_KPIS, 
  EDA_HISTOGRAMS, 
  CORRELATION_VARIABLES, 
  CORRELATION_MATRIX, 
  BOXPLOT_METRICS, 
  HIGH_CORRELATIONS_TABLE,
  CV_PRESET_RESULTS,
  EXTENDED_COHORTS,
  CVMockResult,
  ExtendedCohortData
} from '../data/aiEngineMockData';

// API Base URL config (parametrizado con VITE_API_URL, por defecto http://localhost:8000)
export const BACKEND_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export const API_BASE = `${BACKEND_URL}/api/v1`;

// Derivación de URL WebSocket: cambiar https por wss y http por ws
export const WS_BASE_URL = BACKEND_URL.replace(/^https:/i, 'wss:').replace(/^http:/i, 'ws:');

// Model ID in-memory / local storage persistence
const MODEL_STORAGE_KEY = 'labortwin_active_model_id';

export const getActiveModelId = (): string => {
  return localStorage.getItem(MODEL_STORAGE_KEY) || 'model-xgboost-prod-opt';
};

export const setActiveModelId = (modelId: string): void => {
  localStorage.setItem(MODEL_STORAGE_KEY, modelId);
};

// ==========================================
// 1. DATASET SERVICES
// ==========================================

export interface DatasetUploadResponse {
  status: string;
  message: string;
  dataset: {
    id: string;
    filename: string;
    records_count: number;
    features_list: string[];
    is_active: boolean;
    created_at: string;
  };
}

export const uploadDatasetFile = async (file: File): Promise<DatasetUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/datasets/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al subir dataset' }));
      throw new Error(err.detail || 'Fallo en la carga del dataset');
    }

    return await res.json();
  } catch (error: any) {
    console.error('[API Datasets] Backend no disponible o error:', error.message);
    throw new Error(error.message || 'Error de conexión con el backend al subir dataset');
  }
};

export const selectPresetDataset = async (datasetId: string) => {
  try {
    const res = await fetch(`${API_BASE}/datasets/select-preset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset_id: datasetId }),
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('[API Datasets] Error al seleccionar preset en backend:', err);
  }
  return null;
};

export const fetchDatasetPreview = async () => {
  try {
    const res = await fetch(`${API_BASE}/datasets/preview`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    // offline
  }
  return null;
};

export const fetchActiveDataset = async () => {
  const res = await fetch(`${API_BASE}/datasets/active`);
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  return await res.json();
};

export const fetchDatasetsListApi = async (): Promise<{ datasets: any[]; active_id: string }> => {
  const res = await fetch(`${API_BASE}/datasets/list`);
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  return await res.json();
};

// ==========================================
// 2. ML ENGINE SERVICES (EDA, CV, SHAP)
// ==========================================

export interface EDAApiResponse {
  kpis: typeof EDA_KPIS;
  histograms: typeof EDA_HISTOGRAMS;
  correlationVariables: string[];
  correlationMatrix: number[][];
  highCorrelations: typeof HIGH_CORRELATIONS_TABLE;
  boxplots: typeof BOXPLOT_METRICS;
}

export const fetchEDAAnalytics = async (): Promise<EDAApiResponse> => {
  const res = await fetch(`${API_BASE}/ml/eda`);
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  return await res.json();
};

export const runCrossValidationApi = async (
  nFolds: number = 5,
  algorithm: string = 'xgboost',
  targetCol: string = 'ESTADO_LABORAL'
): Promise<CVMockResult & { model_id?: string }> => {
  const res = await fetch(`${API_BASE}/ml/cross-validation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ n_folds: nFolds, algorithm, target_col: targetCol }),
  });

  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  const data = await res.json();
  if (data.model_id) {
    setActiveModelId(data.model_id);
  }
  return data;
};

export const fetchCohortProjectionsApi = async (
  policyParams: PolicyParameters,
  cohortFilters: Record<string, any> = {}
): Promise<{ model_id: string; cohorts: ExtendedCohortData[] }> => {
  const modelId = getActiveModelId();
  const res = await fetch(`${API_BASE}/ml/proyeccion-cohorte`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model_id: modelId,
      cohort_filters: cohortFilters,
      policy_params: policyParams,
    }),
  });

  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  return await res.json();
};

export const fetchMLModelsApi = async (): Promise<{ models: any[]; active_model_id: string; active_model: any } | null> => {
  const res = await fetch(`${API_BASE}/ml/models`);
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  return await res.json();
};

export const fetchActiveMLModelApi = async (): Promise<any | null> => {
  const res = await fetch(`${API_BASE}/ml/active-model`);
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  const data = await res.json();
  return data.active_model;
};

export const deployMLModelApi = async (modelId: string, deployedBy: string = 'Digital Twin Web UI'): Promise<any | null> => {
  try {
    const res = await fetch(`${API_BASE}/ml/deploy-model`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, deployed_by: deployedBy }),
    });
    if (res.ok) {
      const data = await res.json();
      return data.active_model;
    }
  } catch (err) {
    console.warn('[API ML] deployMLModelApi offline.');
  }
  return null;
};

// ==========================================
// 3. SIMULATION RUNS & METRICS SERVICES
// ==========================================

export const fetchSimulationScenariosApi = async (): Promise<any> => {
  const res = await fetch(`${API_BASE}/simulation/scenarios`);
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  return await res.json();
};

export const fetchStructuralMetricsApi = async (
  country: string,
  scenario: string,
  month: number
): Promise<StructuralMetrics> => {
  const res = await fetch(
    `${API_BASE}/simulation/metrics?country=${encodeURIComponent(country)}&scenario=${encodeURIComponent(scenario)}&month=${month}`
  );
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  return await res.json();
};

export const fetchSimulationHistory = async (): Promise<SimulationRun[]> => {
  const res = await fetch(`${API_BASE}/simulations/history`);
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
  const data = await res.json();
  return data.runs || [];
};

export const saveSimulationRunApi = async (run: Record<string, any>): Promise<void> => {
  const res = await fetch(`${API_BASE}/simulations/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(run),
  });
  if (!res.ok) {
    throw new Error('Backend no disponible');
  }
};

// ==========================================
// 4. WEBSOCKET REAL-TIME SIMULATION CLIENT
// ==========================================

export type CompactWorkerTuple = [
  id_num: number,
  x: number,
  y: number,
  z: number,
  progress: number
];

export interface SimulationFramePayload {
  month: number;
  year: number;
  metrics: StructuralMetrics;
  workers: CompactWorkerTuple[];
}

export class SimulationWebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectTimer: any = null;
  private onFrameCallback: ((frame: SimulationFramePayload) => void) | null = null;
  private onStatusCallback: ((isConnected: boolean) => void) | null = null;
  private isExplicitlyClosed = false;

  constructor(customUrl?: string) {
    if (customUrl) {
      this.url = customUrl;
    } else {
      this.url = `${WS_BASE_URL}/ws/simulation`;
    }
  }

  public connect(
    onFrame: (frame: SimulationFramePayload) => void,
    onStatus?: (isConnected: boolean) => void
  ) {
    this.onFrameCallback = onFrame;
    this.onStatusCallback = onStatus || null;
    this.isExplicitlyClosed = false;
    this.initSocket();
  }

  private initSocket() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        if (this.onStatusCallback) this.onStatusCallback(true);
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as SimulationFramePayload;
          if (this.onFrameCallback && payload.workers) {
            this.onFrameCallback(payload);
          }
        } catch (e) {
          console.error('[WS Parse Error]', e);
        }
      };

      this.ws.onclose = () => {
        if (this.onStatusCallback) this.onStatusCallback(false);
        if (!this.isExplicitlyClosed) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = setTimeout(() => this.initSocket(), 3000);
        }
      };

      this.ws.onerror = () => {
        if (this.onStatusCallback) this.onStatusCallback(false);
      };
    } catch (err) {
      if (this.onStatusCallback) this.onStatusCallback(false);
    }
  }

  public sendAction(actionObj: Record<string, any>) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(actionObj));
    }
  }

  public disconnect() {
    this.isExplicitlyClosed = true;
    clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.onStatusCallback) this.onStatusCallback(false);
  }
}

// ==========================================
// 5. COPILOT IA SERVICE (LANGFLOW V1)
// ==========================================

export interface CopilotChatRequestPayload {
  message: string;
  session_id?: string;
  country?: string;
  scenario?: string;
  month?: number;
  policy_params?: Record<string, any>;
}

export interface CopilotChatResponsePayload {
  response: string;
  session_id: string;
  source: string;
  flow_id?: string;
  verified_metrics?: Record<string, any>;
}

export interface CopilotHistoryItem {
  id: string;
  session_id: string;
  country?: string;
  scenario?: string;
  month?: number;
  user_message: string;
  assistant_response: string;
  source: string;
  flow_id?: string;
  verified_metrics?: Record<string, any>;
  policy_params?: Record<string, any>;
  created_at: string;
}

export const sendCopilotMessageApi = async (
  payload: CopilotChatRequestPayload
): Promise<CopilotChatResponsePayload> => {
  const res = await fetch(`${API_BASE}/copilot/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Error de comunicación con el Copiloto IA' }));
    throw new Error(errorData.detail || `Error del Copiloto (HTTP ${res.status})`);
  }

  return await res.json();
};

export const fetchCopilotHistoryApi = async (
  sessionId: string,
  limit: number = 40
): Promise<CopilotHistoryItem[]> => {
  const res = await fetch(`${API_BASE}/copilot/history?session_id=${encodeURIComponent(sessionId)}&limit=${limit}`);
  if (!res.ok) {
    throw new Error(`Error al recuperar historial desde PostgreSQL (HTTP ${res.status})`);
  }
  return await res.json();
};

export const clearCopilotHistoryApi = async (
  sessionId: string
): Promise<{ status: string; deleted_rows: number }> => {
  const res = await fetch(`${API_BASE}/copilot/history?session_id=${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`Error al limpiar historial en PostgreSQL (HTTP ${res.status})`);
  }
  return await res.json();
};

// ==========================================
// 6. OUTPUTS SCIENTIFIC FIGURES & IMAGES API
// ==========================================

export interface OutputImageItem {
  filename: string;
  relativePath: string;
  category: 'paper_figures' | 'capturas_hd' | 'reproduce' | string;
  categoryLabel: string;
  title: string;
  description: string;
  sizeBytes: number;
  sizeFormatted: string;
  extension: string;
  lastModified?: string;
  downloadUrl: string;
  previewUrl: string;
}

export interface OutputImagesCatalogResponse {
  status: string;
  total: number;
  categories: Array<{ id: string; label: string; count: number }>;
  images: OutputImageItem[];
}

export const FALLBACK_OUTPUT_IMAGES: OutputImageItem[] = [
  {
    filename: 'figure4_calibration.png',
    relativePath: 'figure4_calibration.png',
    category: 'paper_figures',
    categoryLabel: 'Figuras del Paper',
    title: 'Figura 4: Calibración SMM del Modelo ITDT',
    description: 'Momentos simulados vs. momentos observados de ILOSTAT para informalidad laboral y dispersión salarial.',
    sizeBytes: 208420,
    sizeFormatted: '208 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=figure4_calibration.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=figure4_calibration.png`,
  },
  {
    filename: 'figure5_sanctions_sweep.png',
    relativePath: 'figure5_sanctions_sweep.png',
    category: 'paper_figures',
    categoryLabel: 'Figuras del Paper',
    title: 'Figura 5: Barrido de Sanciones e Intensidad GovTech',
    description: 'Elasticidad de la informalidad ante variaciones de 1× a 5× en sanciones (μ0, μ1) y fiscalización digital.',
    sizeBytes: 280969,
    sizeFormatted: '281 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=figure5_sanctions_sweep.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=figure5_sanctions_sweep.png`,
  },
  {
    filename: 'figure6_trajectories.png',
    relativePath: 'figure6_trajectories.png',
    category: 'paper_figures',
    categoryLabel: 'Figuras del Paper',
    title: 'Figura 6: Trayectorias Dinámicas de Transición (Meses 1-120)',
    description: 'Evolución mensual continua de la informalidad y brecha de género por escenario canónico (A, B1, B2, C, D).',
    sizeBytes: 720939,
    sizeFormatted: '721 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=figure6_trajectories.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=figure6_trajectories.png`,
  },
  {
    filename: 'figure7_policy_effects.png',
    relativePath: 'figure7_policy_effects.png',
    category: 'paper_figures',
    categoryLabel: 'Figuras del Paper',
    title: 'Figura 7: Efectos Netos y Contrastes Estructurales',
    description: 'Comparativa de largo plazo del impacto macroeconómico, recaudación fiscal y equidad de género.',
    sizeBytes: 173164,
    sizeFormatted: '173 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=figure7_policy_effects.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=figure7_policy_effects.png`,
  },
  {
    filename: 'fig_dashboard_kenia_escenarioA.png',
    relativePath: 'capturas/fig_dashboard_kenia_escenarioA.png',
    category: 'capturas_hd',
    categoryLabel: 'Capturas HD (4800×2700 px)',
    title: 'Captura HD: Tablero Ejecutivo - Escenario A (Status Quo)',
    description: 'Tablero ejecutivo en ultra-alta resolución al mes 120 de la política en Kenia.',
    sizeBytes: 812396,
    sizeFormatted: '812 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=capturas/fig_dashboard_kenia_escenarioA.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=capturas/fig_dashboard_kenia_escenarioA.png`,
  },
  {
    filename: 'fig_dashboard_kenia_escenarioD.png',
    relativePath: 'capturas/fig_dashboard_kenia_escenarioD.png',
    category: 'capturas_hd',
    categoryLabel: 'Capturas HD (4800×2700 px)',
    title: 'Captura HD: Tablero Ejecutivo - Escenario D (Integrado)',
    description: 'Tablero ejecutivo con paquete integrado de GovTech y Cuidados.',
    sizeBytes: 808615,
    sizeFormatted: '809 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=capturas/fig_dashboard_kenia_escenarioD.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=capturas/fig_dashboard_kenia_escenarioD.png`,
  },
  {
    filename: 'fig_gemelo3d_kenia_escenarioA.png',
    relativePath: 'capturas/fig_gemelo3d_kenia_escenarioA.png',
    category: 'capturas_hd',
    categoryLabel: 'Capturas HD (4800×2700 px)',
    title: 'Captura HD: Gemelo Digital 3D - Escenario A (Mes 120)',
    description: 'Render espacial 3D con proporción real de empresas formales e informales al mes 120.',
    sizeBytes: 4030597,
    sizeFormatted: '3.8 MB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=capturas/fig_gemelo3d_kenia_escenarioA.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=capturas/fig_gemelo3d_kenia_escenarioA.png`,
  },
  {
    filename: 'fig_gemelo3d_kenia_escenarioA_m60.png',
    relativePath: 'capturas/fig_gemelo3d_kenia_escenarioA_m60.png',
    category: 'capturas_hd',
    categoryLabel: 'Capturas HD (4800×2700 px)',
    title: 'Captura HD: Gemelo Digital 3D - Escenario A (Mes 60)',
    description: 'Estado de transición a mitad de ciclo (mes 60) del régimen inercial.',
    sizeBytes: 3964514,
    sizeFormatted: '3.8 MB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=capturas/fig_gemelo3d_kenia_escenarioA_m60.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=capturas/fig_gemelo3d_kenia_escenarioA_m60.png`,
  },
  {
    filename: 'fig_gemelo3d_kenia_escenarioB2.png',
    relativePath: 'capturas/fig_gemelo3d_kenia_escenarioB2.png',
    category: 'capturas_hd',
    categoryLabel: 'Capturas HD (4800×2700 px)',
    title: 'Captura HD: Gemelo Digital 3D - Escenario B2 (GovTech 3×, Mes 120)',
    description: 'Visualización 3D con sanciones triplicadas y fiscalización algorítmica intensiva al mes 120.',
    sizeBytes: 3487788,
    sizeFormatted: '3.3 MB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=capturas/fig_gemelo3d_kenia_escenarioB2.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=capturas/fig_gemelo3d_kenia_escenarioB2.png`,
  },
  {
    filename: 'fig_gemelo3d_kenia_escenarioB2_m60.png',
    relativePath: 'capturas/fig_gemelo3d_kenia_escenarioB2_m60.png',
    category: 'capturas_hd',
    categoryLabel: 'Capturas HD (4800×2700 px)',
    title: 'Captura HD: Gemelo Digital 3D - Escenario B2 (GovTech 3×, Mes 60)',
    description: 'Estado intermedio en el mes 60 bajo régimen de sanciones 3×.',
    sizeBytes: 3655948,
    sizeFormatted: '3.5 MB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=capturas/fig_gemelo3d_kenia_escenarioB2_m60.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=capturas/fig_gemelo3d_kenia_escenarioB2_m60.png`,
  },
  {
    filename: 'figura5_intensidad_sanciones.png',
    relativePath: 'reproduce/figura5_intensidad_sanciones.png',
    category: 'reproduce',
    categoryLabel: 'Figuras de Replicación',
    title: 'Figura 5 (Replicación): Intensidad de Sanciones',
    description: 'Gráfico generado por el pipeline de reproducción científica del artículo para barrido de sanciones.',
    sizeBytes: 399060,
    sizeFormatted: '390 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=reproduce/figura5_intensidad_sanciones.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=reproduce/figura5_intensidad_sanciones.png`,
  },
  {
    filename: 'figura6_informalidad_sexo.png',
    relativePath: 'reproduce/figura6_informalidad_sexo.png',
    category: 'reproduce',
    categoryLabel: 'Figuras de Replicación',
    title: 'Figura 6 (Replicación): Informalidad por Sexo',
    description: 'Gráfico de replicación directa con trayectorias de informalidad desagregadas para hombres y mujeres.',
    sizeBytes: 225741,
    sizeFormatted: '220 KB',
    extension: 'png',
    downloadUrl: `${API_BASE}/outputs/download-image?path=reproduce/figura6_informalidad_sexo.png`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=reproduce/figura6_informalidad_sexo.png`,
  },
  {
    filename: 'figura5_intensidad_sanciones.pdf',
    relativePath: 'reproduce/figura5_intensidad_sanciones.pdf',
    category: 'reproduce',
    categoryLabel: 'Figuras de Replicación',
    title: 'Figura 5 Vectorial (PDF): Intensidad de Sanciones',
    description: 'Gráfico vectorial de alta fidelidad listo para imprenta o publicación académica.',
    sizeBytes: 44893,
    sizeFormatted: '44 KB',
    extension: 'pdf',
    downloadUrl: `${API_BASE}/outputs/download-image?path=reproduce/figura5_intensidad_sanciones.pdf`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=reproduce/figura5_intensidad_sanciones.pdf`,
  },
  {
    filename: 'figura6_informalidad_sexo.pdf',
    relativePath: 'reproduce/figura6_informalidad_sexo.pdf',
    category: 'reproduce',
    categoryLabel: 'Figuras de Replicación',
    title: 'Figura 6 Vectorial (PDF): Informalidad por Sexo',
    description: 'Gráfico vectorial de alta fidelidad listo para imprenta o publicación académica.',
    sizeBytes: 36924,
    sizeFormatted: '36 KB',
    extension: 'pdf',
    downloadUrl: `${API_BASE}/outputs/download-image?path=reproduce/figura6_informalidad_sexo.pdf`,
    previewUrl: `${API_BASE}/outputs/preview-image?path=reproduce/figura6_informalidad_sexo.pdf`,
  },
];

export const fetchOutputImagesList = async (): Promise<OutputImagesCatalogResponse> => {
  try {
    const res = await fetch(`${API_BASE}/outputs/images`);
    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.images) && data.images.length > 0) {
        return data;
      }
    }
  } catch (err) {
    console.warn('[API Outputs] Backend no disponible, usando catálogo integrado:', err);
  }

  // Fallback con datos auténticos precalculados
  return {
    status: 'fallback',
    total: FALLBACK_OUTPUT_IMAGES.length,
    categories: [
      { id: 'all', label: 'Todas las Figuras', count: FALLBACK_OUTPUT_IMAGES.length },
      { id: 'paper_figures', label: 'Figuras del Paper (Fig. 4-7)', count: 4 },
      { id: 'capturas_hd', label: 'Capturas HD (Gemelo 3D & Tablero)', count: 6 },
      { id: 'reproduce', label: 'Figuras de Replicación', count: 4 },
    ],
    images: FALLBACK_OUTPUT_IMAGES,
  };
};

export const getOutputImageDownloadUrl = (relativePath: string): string => {
  return `${API_BASE}/outputs/download-image?path=${encodeURIComponent(relativePath)}`;
};

export const getOutputImagePreviewUrl = (relativePath: string): string => {
  return `${API_BASE}/outputs/preview-image?path=${encodeURIComponent(relativePath)}`;
};

export const getOutputsZipDownloadUrl = (category: string = 'all'): string => {
  return `${API_BASE}/outputs/download-all-zip${category && category !== 'all' ? `?category=${encodeURIComponent(category)}` : ''}`;
};

export const triggerBrowserDownload = (url: string, filename?: string) => {
  const link = document.createElement('a');
  link.href = url;
  if (filename) {
    link.download = filename;
  }
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};



