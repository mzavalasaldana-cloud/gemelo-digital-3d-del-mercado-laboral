import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    JSON,
    Text,
)
from pydantic import BaseModel, Field, ConfigDict
from .database import Base

# ==========================================
# 1. SQLALCHEMY ORM MODELS
# ==========================================

class DatasetModel(Base):
    __tablename__ = "datasets"

    id = Column(String(50), primary_key=True, default=lambda: f"ds-{uuid.uuid4().hex[:8]}")
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    records_count = Column(Integer, default=0)
    features_list = Column(JSON, default=list)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "records_count": self.records_count,
            "features_list": self.features_list or [],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SimulationRunModel(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(100), primary_key=True, default=lambda: f"RUN-{uuid.uuid4().hex[:6].upper()}")
    country = Column(String(50), nullable=False)
    scenario = Column(String(100), nullable=False)
    policy_params = Column(JSON, default=dict)
    final_metrics = Column(JSON, default=dict)
    duration_sec = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "country": self.country,
            "scenario": self.scenario,
            "policy_params": self.policy_params,
            "final_metrics": self.final_metrics,
            "duration_sec": self.duration_sec,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CopilotMessageModel(Base):
    __tablename__ = "copilot_chat_history"

    id = Column(String(50), primary_key=True, default=lambda: f"msg-{uuid.uuid4().hex[:10]}")
    session_id = Column(String(100), nullable=False, index=True, default="default-session")
    country = Column(String(50), nullable=True)
    scenario = Column(String(100), nullable=True)
    month = Column(Integer, nullable=True, default=0)
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    source = Column(String(50), default="langflow")
    flow_id = Column(String(100), nullable=True)
    verified_metrics = Column(JSON, default=dict)
    policy_params = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "country": self.country,
            "scenario": self.scenario,
            "month": self.month,
            "user_message": self.user_message,
            "assistant_response": self.assistant_response,
            "source": self.source,
            "flow_id": self.flow_id,
            "verified_metrics": self.verified_metrics or {},
            "policy_params": self.policy_params or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ==========================================
# 2. PYDANTIC V2 SCHEMAS (Matches TypeScript)
# ==========================================

class PolicyParameters(BaseModel):
    registrationCostReduction: float = Field(default=0.0, ge=0.0, le=100.0, description="Reducción costos de registro (0-100%)")
    smeSubsidyUSDMonth: float = Field(default=0.0, ge=0.0, le=150.0, description="Subsidio mensual PyMEs (0-150 USD)")
    skillsTrainingCoverage: float = Field(default=0.0, ge=0.0, le=100.0, description="Cobertura de capacitación técnica (0-100%)")
    socialProtectionTax: float = Field(default=15.0, ge=0.0, le=50.0, description="Tasa de contribución protección social (0-50%)")
    smartInspectionCoverage: float = Field(default=0.0, ge=0.0, le=100.0, description="Inspección inteligente satelital/digital (0-100%)")

    model_config = ConfigDict(from_attributes=True)


class StructuralMetrics(BaseModel):
    informalityRate: float = Field(..., description="Tasa de informalidad neta (%)")
    giniIndex: float = Field(..., description="Índice de desigualdad Gini (0-1)")
    formalWorkersCount: int = Field(..., description="Total agentes formales")
    informalWorkersCount: int = Field(..., description="Total agentes informales")
    unemployedCount: int = Field(..., description="Total agentes desempleados")
    avgFormalWageUSD: float = Field(..., description="Salario medio formal (USD/día)")
    avgInformalWageUSD: float = Field(..., description="Salario medio informal (USD/día)")
    fiscalRevenueMillionUSD: float = Field(..., description="Recaudación fiscal estimada (M$ USD)")
    policyCostMillionUSD: float = Field(..., description="Costo total de políticas activas (M$ USD)")
    decentWorkIndex: float = Field(..., description="Índice de Trabajo Decente OIT (0-100)")

    model_config = ConfigDict(from_attributes=True)


class SimulationRunCreate(BaseModel):
    country: str
    scenario: str
    policy_params: Dict[str, Any]
    final_metrics: Dict[str, Any]
    duration_sec: float = 0.0


class SimulationRunResponse(BaseModel):
    id: str
    country: str
    scenario: str
    policy_params: Dict[str, Any]
    final_metrics: Dict[str, Any]
    duration_sec: float
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 3. ML ANALYTICS SCHEMAS (EDA, CV, SHAP)
# ==========================================

class EDADistributionBin(BaseModel):
    range: str
    formalCount: int
    informalCount: int
    density: float


class EDAHistogramGroup(BaseModel):
    label: str
    unit: str
    data: List[EDADistributionBin]


class HighCorrelationItem(BaseModel):
    varA: str
    varB: str
    r: float
    pValue: str
    direction: str
    impact: str


class BoxplotMetricItem(BaseModel):
    group: str
    min: float
    q1: float
    median: float
    q3: float
    max: float
    outliers: List[float]


class EDAKPIS(BaseModel):
    dataQuality: float
    totalRecords: int
    totalVariables: int
    nullPercentage: float
    imputationMethod: str
    surveySource: str


class EDADataResponse(BaseModel):
    kpis: EDAKPIS
    histograms: Dict[str, EDAHistogramGroup]
    correlationVariables: List[str]
    correlationMatrix: List[List[float]]
    highCorrelations: List[HighCorrelationItem]
    boxplots: List[BoxplotMetricItem]


class CrossValidationRequest(BaseModel):
    n_folds: int = Field(default=5, ge=2, le=10)
    target_col: str = "ESTADO_LABORAL"
    algorithm: str = "xgboost"


class CVFoldMetric(BaseModel):
    fold: str
    f1Score: float
    rocAuc: float
    accuracy: float


class CVTrainVsTestMetric(BaseModel):
    metric: str
    Train: float
    Test: float


class CVConfusionMatrix(BaseModel):
    tp: int
    fp: int
    fn: int
    tn: int
    tpPct: float
    fpPct: float
    fnPct: float
    tnPct: float


class CVSummary(BaseModel):
    meanF1: float
    stdF1: float
    meanRocAuc: float
    stdRocAuc: float


class CrossValidationResponse(BaseModel):
    model_id: str
    algorithm: str
    kFolds: int
    strategy: str
    metricsTrainVsTest: List[CVTrainVsTestMetric]
    foldsF1: List[CVFoldMetric]
    confusionMatrix: CVConfusionMatrix
    summary: CVSummary


class SHAPDriver(BaseModel):
    feature: str
    importance: float
    shapValue: str


class CohortFilterRequest(BaseModel):
    model_id: Optional[str] = None
    cohort_filters: Dict[str, Any] = Field(default_factory=dict)
    policy_params: Dict[str, Any] = Field(default_factory=dict)


class CohortProjectionItem(BaseModel):
    id: str
    label: str
    populationShare: float
    prob1Year: float
    prob3Year: float
    prob5Year: float
    estimatedMonths: int
    topDrivers: List[SHAPDriver]
    policyIntervention: str
    barrier: str


class CohortProjectionResponse(BaseModel):
    model_id: str
    cohorts: List[CohortProjectionItem]


# ==========================================
# 4. WEBSOCKET STREAMING SCHEMAS
# ==========================================

class SimulationControlMessage(BaseModel):
    action: str  # "play", "pause", "seek", "set_speed", "set_policy", "set_country", "reset"
    speed: Optional[float] = None
    month: Optional[int] = None
    country: Optional[str] = None
    policy_params: Optional[PolicyParameters] = None
    scenario: Optional[str] = None


# ==========================================
# 5. COPILOT IA SCHEMAS (V1)
# ==========================================

class CopilotChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta o consulta del usuario")
    session_id: Optional[str] = Field(default="default-session", description="Identificador de sesión")
    country: Optional[str] = Field(default="KENYA", description="Código del país objetivo")
    scenario: Optional[str] = Field(default="BASELINE", description="Escenario de política activa")
    month: Optional[int] = Field(default=0, ge=0, le=120, description="Mes de la simulación")
    policy_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parámetros de política activos")
    simulation_id: Optional[str] = Field(default=None, description="ID opcional de corrida histórica")


class CopilotChatResponse(BaseModel):
    response: str = Field(..., description="Respuesta contextual generada por el agente")
    session_id: str = Field(..., description="ID de sesión")
    source: str = Field(default="langflow", description="Origen de la respuesta")
    flow_id: Optional[str] = Field(default=None, description="ID del flujo ejecutado")
    verified_metrics: Optional[Dict[str, Any]] = Field(default=None, description="Métricas de simulación utilizadas")

