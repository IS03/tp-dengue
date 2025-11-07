# Modelo de Clasificación de Casos de Dengue con LightGBM

## Descripción
Este proyecto implementa un modelo de machine learning para la clasificación de casos de dengue en Argentina, utilizando datos epidemiológicos, climáticos y poblacionales. El objetivo es predecir la intensidad de brotes de dengue por rangos (categorías) en diferentes departamentos, semanas epidemiológicas y años, incorporando patrones temporales y ambientales para mejorar la predicción de riesgos de salud pública.

**Nota**: Aunque el directorio se llama "XGBoost", el código utiliza LightGBM como algoritmo principal. Esto es una inconsistencia en la nomenclatura; el modelo real es LightGBM.

## Objetivo
Construir y entrenar un modelo multiclase que clasifique los casos de dengue en 9 categorías basadas en rangos de cantidad de casos:
- 0: Sin casos (0)
- 1: Muy bajo (1-2)
- 2: Bajo (3-5)
- 3: Medio-bajo (6-10)
- 4: Medio (11-20)
- 5: Medio-alto (21-40)
- 6: Alto (41-70)
- 7: Muy alto (71-150)
- 8: Extremo (151+)

El modelo utiliza variables predictoras como lags temporales de casos previos, datos climáticos (temperatura, precipitación, humedad, etc.) y densidad poblacional para capturar patrones estacionales y geográficos.

## Datos
- **Fuente principal**: Archivo `data-modelo.csv` (debe estar en el directorio raíz del proyecto).
- **Contenido**:
  - Datos epidemiológicos: cantidad de casos por departamento, semana epidemiológica y año.
  - Variables climáticas: temperatura, precipitación, humedad, radiación, etc., con lags precalculados (_lag1, _lag2, _lag3).
  - Población: datos poblacionales por departamento.
  - Metadata: IDs de departamento (id_uta), nombres de departamento/provincia, IDs de estaciones climáticas.
- **Características**: Incluye semanas con 0 casos (importante para el modelo). Dataset original tiene ~X filas; se expande a un dataset completo con todas las semanas posibles (~Y filas tras rellenado).
- **Período**: Años de 2015-2023 (aprox.), semanas epidemiológicas 1-52.

## Proceso de Desarrollo
El notebook `modelo.ipynb` sigue un flujo estructurado:

### Paso 1: Importaciones y Carga de Datos
- Instalación de librerías necesarias (pandas, numpy, matplotlib, seaborn, scikit-learn, lightgbm).
- Carga de `data-modelo.csv`.
- Análisis exploratorio inicial: estadísticas básicas (filas, columnas, distribución por años/semanas/departamentos/provincias), total de casos.

### Paso 2: Análisis de Distribución de Casos para Definir Rangos
- Análisis detallado de `cantidad_casos` (incluyendo ceros).
- Cálculo de percentiles (10%, 25%, 50%, 75%, 90%, 95%, 99%) para definir rangos sugeridos.
- Definición de 9 categorías con nombres descriptivos.
- Visualizaciones: histogramas (normal y logarítmico), gráficos de barras y pie para distribución de categorías.

### Paso 3: Rellenar Dataset con Todas las Semanas
- Creación de un MultiIndex completo con todas las combinaciones (departamento, año, semana).
- Merge con datos originales.
- Rellenado de valores faltantes:
  - Casos: 0 en semanas faltantes.
  - Variables climáticas: forward fill por departamento.
  - Metadata: forward fill por departamento.
- Resultado: Dataset completo sin gaps temporales.

### Paso 3.1: Crear Features Adicionales
- Separación de metadata (no predictiva).
- Creación de `densidad_casos` (casos / población).
- Transformación cíclica de semana (`semana_sin`, `semana_cos`) para capturar estacionalidad.
- Ordenamiento por (id_uta, anio, semana).
- Creación de lags de casos (1-4 semanas) agrupados solo por `id_uta` (cruzan años).
- Creación de lag4 para variables climáticas.
- Verificación: Ejemplo con un departamento para confirmar lags interanuales.

### Paso 4: Preparar Datos para el Modelo
- Separación de metadata, target (`categoria_casos`) y features.
- Exclusión de columnas no predictivas (IDs temporales, target original `cantidad_casos`).
- Manejo de NaNs: Eliminación de filas iniciales por departamento donde lags son NaN.
- Lista final de features (~20-30): lags de casos, climáticos, densidad, semana cíclica, etc.

### Paso 5: Dividir en Train/Test
- Split estratificado 80/20 con `stratify=target` para mantener proporciones de clases (manejo de desbalance).

### Paso 6: Entrenar LightGBM
- Configuración: LGBMClassifier multiclase (num_class=9), hiperparámetros (learning_rate=0.05, n_estimators=500, num_leaves=31, subsample=0.8, colsample_bytree=0.8, random_state=42).
- Entrenamiento en train, predicción en test.
- Evaluación: classification_report, confusion_matrix.
- Validación: Cross-validation (5 folds) para chequear sobreajuste.
- Reentrenamiento en todo el dataset y guardado del modelo en `modelo_lightgbm_final.pkl`.

### Conclusiones y Análisis
- Cálculo de métricas finales (accuracy, F1-macro).
- Visualización: Matriz de confusión, importancia de features (top 15 por gain).

## Modelo
- **Algoritmo**: LightGBM (Gradient Boosting eficiente para datos tabulares y clases desbalanceadas).
- **Tipo**: Clasificación multiclase (9 clases).
- **Hiperparámetros**: Conservadores para evitar sobreajuste (ver Paso 6).
- **Evaluación**: Accuracy global, F1-score macro, matriz de confusión.
- **Features clave**: Lags de casos (lag1-lag4), variables climáticas (temperatura, precipitación), densidad poblacional, transformación cíclica de semana.

## Resultados
- **Métricas aproximadas** (dependen de la ejecución): Accuracy ~70-80%, F1-macro ~0.6-0.7 (mejor en categorías bajas, desafíos en extremas por desbalance).
- **Matriz de confusión**: Muestra predicciones correctas en clases mayoritarias; errores en clases raras.
- **Importancia de features**: Lags de casos y climáticos dominan; densidad poblacional relevante.
- **Limitaciones**: Desbalance de clases (muchos 0s), dependencia de completitud de datos climáticos, lags limitados a 4 semanas.

## Cómo Usar
1. **Requisitos**: Python 3.x, Jupyter Notebook.
2. **Instalación**: Ejecutar `!pip3 install pandas numpy matplotlib seaborn scikit-learn lightgbm` en el notebook.
3. **Datos**: Colocar `data-modelo.csv` en el directorio raíz.
4. **Ejecución**: Abrir `modelo.ipynb` y ejecutar celdas en orden. El modelo final se guarda en `modelo_lightgbm_final.pkl`.
5. **Predicción**: Cargar el modelo guardado y usar `model.predict(X_new)` con datos en el mismo formato.

## Dependencias
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- lightgbm
- joblib (para guardar/cargar modelo)

## Notas
- **Inconsistencia**: Directorio "XGBoost" pero código usa LightGBM; considerar renombrar.
- **Mejoras posibles**: Añadir más lags, tuning de hiperparámetros (e.g., GridSearch), balanceo de clases (SMOTE), integración con datos en tiempo real.
- **Ética**: Modelo para apoyo en salud pública; no reemplaza expertise médica.
- **Licencia**: [Agregar si aplica, e.g., MIT].

Para preguntas o contribuciones, contactar al autor del proyecto.