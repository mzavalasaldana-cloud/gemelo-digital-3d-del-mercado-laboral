# Tabla de Desempeño Comparativo: Modelos de Inteligencia Artificial sobre Microdatos Reales

**Fecha de Entrenamiento:** 2026-10-24 06:33:51 UTC
**Metodología:** StratifiedGroupKFold (5 Folds por hogar) con ponderadores de encuesta oficiales OIT.

| País                   | Modelo                         |   AUC-ROC (%) |   F1-Score (%) |   Accuracy (%) |   Precision (%) |   Recall (%) |   Brier Score |   F1 Mujeres (%) |   AUC Mujeres (%) |   F1 Hombres (%) |   AUC Hombres (%) |   Latencia (ms) |
|:-----------------------|:-------------------------------|--------------:|---------------:|---------------:|----------------:|-------------:|--------------:|-----------------:|------------------:|-----------------:|------------------:|----------------:|
| India (PLFS 2024)      | Regresión Logística L2         |         89.62 |          94.44 |          89.98 |           92.3  |        96.69 |        0.0698 |            95.37 |             89.48 |            94.08 |             89.51 |         0.0001  |
| India (PLFS 2024)      | Random Forest (100 Trees)      |         91.87 |          95.33 |          91.58 |           93.29 |        97.46 |        0.0617 |            96.18 |             93.36 |            94.99 |             91.26 |         0.00315 |
| India (PLFS 2024)      | HistGradientBoosting (Campeón) |         93.05 |          95.63 |          92.21 |           94.58 |        96.71 |        0.0573 |            96.29 |             93.71 |            95.37 |             92.77 |         0.00093 |
| India (PLFS 2024)      | XGBoost Classifier v3.4        |         92.97 |          95.57 |          92.1  |           94.46 |        96.7  |        0.0577 |            96.22 |             93.76 |            95.31 |             92.65 |         0.00092 |
| India (PLFS 2024)      | CatBoost Classifier            |         90.41 |          95.02 |          91.01 |           92.72 |        97.44 |        0.0655 |            96.09 |             91.81 |            94.6  |             89.82 |         0.00041 |
| India (PLFS 2024)      | MLP Neural Net                 |         91.93 |          95.31 |          91.59 |           93.77 |        96.89 |        0.0625 |            96.2  |             93.55 |            94.95 |             91.2  |         0.00037 |
| Nigeria (NLFS 2023 Q3) | Regresión Logística L2         |         88.66 |          96.1  |          92.64 |           94.15 |        98.13 |        0.0547 |            98.37 |             91.58 |            93.84 |             84.73 |         0.0004  |
| Nigeria (NLFS 2023 Q3) | Random Forest (100 Trees)      |         88.35 |          96.23 |          92.87 |           94.11 |        98.45 |        0.0537 |            98.29 |             91.13 |            94.2  |             84.03 |         0.00679 |
| Nigeria (NLFS 2023 Q3) | HistGradientBoosting (Campeón) |         88.62 |          96.39 |          93.17 |           94.27 |        98.6  |        0.0539 |            98.3  |             92.58 |            94.51 |             83.88 |         0.00094 |
| Nigeria (NLFS 2023 Q3) | XGBoost Classifier v3.4        |         87.99 |          96.26 |          92.95 |           94.34 |        98.26 |        0.0551 |            98.22 |             92.17 |            94.32 |             83.11 |         0.00137 |
| Nigeria (NLFS 2023 Q3) | CatBoost Classifier            |         88.62 |          96.37 |          93.13 |           94.23 |        98.61 |        0.0535 |            98.5  |             91.69 |            94.27 |             84.05 |         0.0009  |
| Nigeria (NLFS 2023 Q3) | MLP Neural Net                 |         88.74 |          96.33 |          93.05 |           94    |        98.78 |        0.0536 |            98.27 |             92.36 |            94.42 |             84.55 |         0.00058 |

*Nota Metodológica:* Se garantiza ausencia de fuga de información excluyendo variables directas del objetivo laboral. Los factores de expansión se utilizan tanto en ajuste como en métricas de evaluación.
