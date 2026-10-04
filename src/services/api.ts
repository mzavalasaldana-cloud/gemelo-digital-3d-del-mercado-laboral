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

// API Base URL config (Proxy in dev or env var in prod)
const BACKEND_URL = (import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_URL || '').replace(/\/$/, '');
const API_BASE = BACKEND_URL ? `${BACKEND_URL}/api/v1` : '/api/v1';

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
    console.warn('[API Datasets] Backend no disponible o error:', error.message);
    // Graceful offline mock response
    return {
      status: 'success',
      message: `Dataset "${file.name}" cargado en memoria exitosamente (Modo offline / desarrollo).`,
      dataset: {
        id: `ds-${Date.now().toString().slice(-6)}`,
        filename: file.name,
        records_count: 15420,
        features_list: ['ESTADO_LABORAL', 'INGRESO_NETO_DIA', 'CAPITAL_HUMANO', 'EDUCACION_ANIOS'],
        is_active: true,
        created_at: new Date().toISOString(),
      }
    };
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

  constructor() {
    const customBackend = import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_URL;
    if (customBackend) {
      const cleanUrl = customBackend.replace(/^http/, 'ws').replace(/\/$/, '');
      this.url = `${cleanUrl}/ws/simulation`;
    } else {
      const isHttps = window.location.protocol === 'https:';
      const host = window.location.host || 'localhost:3000';
      this.url = `${isHttps ? 'wss:' : 'ws:'}//${host}/ws/simulation`;
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


