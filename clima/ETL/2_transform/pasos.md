# 🔹 Pasos de Transformación (T en ETL)

## 🟦 1. Preprocesamiento
En el preprocesamiento organizamos y limpiamos la estructura de los datos (nombres, tipos, fechas, duplicados, consistencia), lo que sirve para dejar el dataset en un formato coherente y confiable.

### 1.1 Normalización de estructura
- Renombrar columnas (minúsculas, sin espacios, con `_`).  
- Ordenar columnas según lógica (ej. primero fechas, luego mediciones).  
- Eliminar columnas redundantes o irrelevantes.  

---

### 1.2 Tipificación de datos
- Convertir columnas de fechas con `pd.to_datetime`.  
- Convertir numéricas a `float` o `int` según corresponda.  
- Convertir categóricas a `category`.  
- Convertir booleanos a `True/False` o `0/1`.  

---

### 1.3 Consistencia de datos
- Rango válido (ej: humedad 0–100%).  
- Coherencia entre columnas (ej: `temperatura_min <= temperatura_max`).  
- Unidades homogéneas (ej: °C en todas, no mezclar con °F).  
- Homogeneizar formatos de texto (mayúsculas/minúsculas).  
- Unificar categorías con nombres distintos pero mismo significado.  

---


## 🟩 2. Procesamiento
En el procesamiento imputamos nulos, tratamos outliers, escalamos variables y generamos nuevas características, lo que sirve para preparar los datos de cada estación de forma correcta y lista para el modelado.

### 2.1 Duplicados
- Detección de filas duplicadas (`duplicated()`).  
- Eliminar duplicados exactos o mantener el primero.  
- Definir criterios de duplicado (ej: misma fecha y estación).  

---

### 2.2 Valores faltantes (nulos)
- Calcular porcentaje de nulos por columna.  
- Decidir estrategia:
  - Eliminar columna (si >80% nulos).  
  - Eliminar filas (si pocos casos y no afectan representatividad).  
  - Imputar:
    - Media, mediana, moda.  
    - Forward-fill / Backward-fill.  
    - Interpolación (lineal, polinómica, spline).  
    - Valores específicos (`0`, `"desconocido"`).  

> ⚠️ **Importante:** la imputación debe realizarse por separado en cada tabla de estación para evitar rellenar valores con datos de otra estación por error.  

---

### 2.3 Valores atípicos (outliers)
- Identificarlos con:
  - Boxplot / IQR.  
  - Z-score / desviación estándar.  
  - Percentiles extremos (<1% o >99%).  
- Estrategias:
  - Mantener si son reales.  
  - Reemplazar con mediana o límite permitido.  
  - Eliminar si son errores evidentes.  

---

### 2.4 Normalización y escalado
- Escalado **Min-Max** → valores entre 0 y 1.  
- **Log-transform** → para distribuciones sesgadas (ej: lluvia, ingresos).  
- **Power transform** (Box-Cox / Yeo-Johnson) → para reducir asimetría.  
- **Clipping** → limitar valores a un rango razonable.  

---

### 2.5 Codificación de variables categóricas
- **Label Encoding** (para ordinales).  
- **One-Hot Encoding** (para nominales).  
- **Binary Encoding** / **Target Encoding** (para muchas categorías).  

---

### 2.6 Creación de nuevas variables (feature engineering)
- Ratios entre columnas (ej: `temp_max/temp_min`).  
- Variables acumuladas o diferencias (`cumsum`, `diff`).  
- Interacciones entre variables (producto, suma, resta).  
- Variables categóricas agrupadas (ej: agrupar provincias en regiones).  

---

### 2.7 Balance de datos (para modelos predictivos)
- Detectar clases desbalanceadas en variables objetivo.  
- Técnicas:
  - Submuestreo / sobremuestreo.  
  - **SMOTE** (sintético).  
  - Ponderación de clases.  

---

### 2.8 Validación final
- Revisión de estadísticos descriptivos después de transformaciones.  
- Visualización rápida (histogramas, boxplots).  
- Comparación con datos crudos para confirmar consistencia.  
