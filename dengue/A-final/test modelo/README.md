# Test Modelo - Predicción de casos t+1 por departamento

Estructura del pipeline:

- 01_prepare_data.py: prepara panel semanal por `id_uta` (semanas 1–52, faltantes a 0).
- 02_build_features.py: genera variables (lags, medias móviles, estacionalidad, provincia/población) sin fuga temporal.
- 03_train_baselines.py: modelos baseline (naive y promedio móvil) para referencia.
- 04_train_random_forest.py: entrena Random Forest para t+1 y guarda modelo.
- 05_evaluate.py: evalúa MAE/RMSLE global y por provincia/deciles de población; guarda reportes.

Entradas/salidas:

- Entrada: `../../dengue-final.csv`.
- Salidas:
  - `data/panel.parquet`, `data/features.parquet`.
  - `models/random_forest.pkl` y `models/feature_columns.json`.
  - `reports/metrics_global.json`, `reports/metrics_by_province.csv`, `reports/metrics_by_pop_decile.csv`, `reports/rf_metrics.json`.

Partición temporal:
- Train: 2018–2023
- Validación: 2024
- Test: 2025

Métricas:
- MAE y RMSLE en casos.

Notas:
- No se usan columnas de edad. El objetivo es casos t+1 por `id_uta`.

Resultados actuales (RF rápido):
- Validación (2024): ver `reports/rf_metrics.json` (MAE ~16.71; RMSLE ~0.61)
- Test (2025): ver `reports/rf_metrics.json` (MAE ~0.58; RMSLE ~0.25)
- Baselines: `reports/baselines_metrics.json`
