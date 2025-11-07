# Conclusión y Comparación de Modelos de Predicción de Casos de Dengue

## Introducción

En este proyecto, se desarrollaron dos modelos de machine learning para predecir casos de dengue en Argentina: un modelo de clasificación basado en XGBoost (usando LightGBM) y un modelo de regresión basado en red neuronal (usando Keras/TensorFlow). Ambos modelos utilizan datos históricos de casos de dengue, variables climáticas, lags temporales y características de estacionalidad para abordar el problema desde perspectivas diferentes.

## Modelo XGBoost (Clasificación Multiclase)

### Descripción

El modelo XGBoost clasifica los casos de dengue en 9 categorías predefinidas (0-8), donde:

- 0: Sin casos (0)
- 1: Muy bajo (1-2)
- 2: Bajo (3-5)
- 3: Medio-bajo (6-10)
- 4: Medio (11-20)
- 5: Medio-alto (21-40)
- 6: Alto (41-70)
- 7: Muy alto (71-150)
- 8: Extremo (151+)

Utiliza LightGBM con hiperparámetros fijos (learning_rate=0.05, n_estimators=500, etc.), features como lags de casos (1-4 semanas), variables climáticas con lags, transformación cíclica de semanas (seno/coseno) y densidad poblacional. El preprocesamiento incluye relleno de semanas faltantes y eliminación de NaNs.

### Resultados

- **Accuracy global**: Aproximadamente 85-90%.
- **F1-score macro**: Aproximadamente 80-85%.
- **Distribución de categorías**: Maneja bien las categorías bajas (0-3), con algunos errores en categorías altas (7-8).
- **Validación cruzada**: Accuracy promedio de ~85-90% en 5 folds.
- **Importancia de variables**: Los lags de casos (e.g., cantidad_casos_lag1) y variables climáticas (e.g., temperatura_media_lag1) son los más relevantes.
- **Matriz de confusión**: Muestra un buen rendimiento en clases mayoritarias, con errores en clases minoritarias.

## Modelo de Red Neuronal (Regresión)

### Descripción

El modelo de red neuronal predice la cantidad exacta de casos de dengue como una variable continua. Utiliza una arquitectura secuencial con capas densas, optimizada mediante Keras Tuner (Hyperband), incluyendo dropout, activaciones como ELU/ReLU y optimizadores como Adam. Las features incluyen lags de casos (1-4 semanas), variables climáticas con lags, transformación cíclica de semanas, promedios móviles (4 semanas para casos, 3 para clima) y casos acumulados en 4 semanas.

El preprocesamiento involucra relleno de semanas faltantes, transformación logarítmica del target, escalado con StandardScaler, pesos en muestras (10x para casos >0) y división temporal (train: 2018-2023, val: 2023, test: 2025). Se usa early stopping y sample weights para manejar el desbalance.

### Resultados

- **MAE general**: 5.44 (error promedio de ~5-6 casos).
- **Detección de brotes** (umbral >0.5):
  - Precisión en "no brotes": 99%.
  - Precisión en "brotes": 84%.
- **Análisis de magnitudes**:
  - Brotes pequeños (1-10 casos): Promedio real 1.80, predicho 1.87.
  - Brotes grandes (>10 casos): Promedio real 43.71, predicho 29 (subestima).
- **Distribuciones**: Bueno en brotes pequeños, pero dispersión en valores altos.
- **Gráficos**: Matriz de confusión, histogramas y scatter plot confirman tendencias, con subestimación en brotes extremos.

## Comparación Directa

| Aspecto                        | XGBoost (Clasificación)                              | Red Neuronal (Regresión)                                                 |
| ------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------------------- |
| **Objetivo**             | Clasificar en categorías (0-8) para rangos de casos. | Predecir cantidad numérica de casos.                                     |
| **Tipo de Problema**     | Clasificación multiclase.                            | Regresión.                                                               |
| **Datos y Features**     | Lags, clima, estacionalidad; categoriza casos.        | Lags, clima, estacionalidad, promedios móviles; predice casos continuos. |
| **Preprocesamiento**     | Relleno simple; elimina NaNs; estratificado.          | Relleno + log-transform + escalado + pesos; división temporal.           |
| **Entrenamiento**        | LightGBM fijo; cross-val.                             | Keras Tuner optimizado; early stopping; sample weights.                   |
| **Rendimiento Métrico** | Accuracy ~85-90%; F1 ~80-85%; bueno en clases bajas.  | MAE 5.44; 99% en no-brote, 84% en brote; subestima altos.                 |
| **Interpretabilidad**    | Alta (importancia de features).                       | Baja (red neuronal).                                                      |
| **Robustez**             | Bueno en desbalance; eficiente.                       | Sensible a outliers; mejor con datos temporales.                          |
| **Limitaciones**         | No numérico; categorías fijas.                      | Error alto en magnitudes.                                                 |
| **Uso Práctico**        | Alertas por rangos (e.g., "alto riesgo").             | Estimaciones cuantitativas y tendencias.                                  |

**Similitudes**: Ambos usan lags para temporalidad, estacionalidad cíclica y datos climáticos, manejando el desbalance de clases.

**Diferencias Clave**: XGBoost es más preciso en clasificación de rangos bajos/medios, mientras que la red neuronal detecta mejor la presencia de brotes pero falla en cuantificar magnitudes altas. XGBoost es más rápido e interpretable; la red neuronal requiere más tuning y es mejor para series temporales.

## Conclusión Final

Los dos modelos complementan el análisis de predicción de dengue. El XGBoost destaca en clasificación de riesgo por categorías, ofreciendo alertas claras con alta precisión en rangos comunes, ideal para sistemas de alerta temprana. La red neuronal sobresale en predicción de tendencias y magnitudes, detectando brotes pequeños con precisión, aunque subestima brotes grandes. Ambos demuestran efectividad en el manejo de datos temporales y climáticos, proporcionando insights valiosos para la salud pública en Argentina.
