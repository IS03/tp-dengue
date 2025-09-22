# 🔹 Pasos para un buen EDA

## 1. Entender la estructura del dataset
- Revisar dimensiones: `shape` (número de filas y columnas).  
- Ver primeras y últimas filas: `head()`, `tail()`.  
- Tipos de datos: `dtypes`, `info()`.  
- Identificar variables: **categóricas, numéricas, de fecha, texto**.  

---

## 2. Revisar valores faltantes
- Conteo de nulos por columna: `isnull().sum()`.  
- Porcentaje de nulos respecto al total.  
- Estrategias para tratarlos:
  - ❌ Eliminar columna (si hay demasiados nulos).  
  - 🔄 Imputar (media, mediana, moda, forward-fill, etc.).  
  - 🏷️ Dejar explícito el `"missing"` como categoría (en variables categóricas).  

  Para valores nulos de temperatura tanto minima como maxima, se puede usar el metodo de `.ffill()`
  que lo que hace es rellenar esos valores con los ultimos valores validos. Para hacer eso, es necesario
  agrupar por estación y despues ordenar los datos por `fecha` de manera ascendente.

  Otra manera de imputar esos valores, puede ser revisando los datos de la misma estación en el mismo dia pero en diferentes años, y asi obtener un promedio de la temperatura que suele haber en esa estación en especifico en una etapa en especifico.

---

## 3. Detectar duplicados
- Revisar filas duplicadas: `duplicated().sum()`.  
- Eliminar si corresponde: `drop_duplicates()`.  

---

## 4. Estadística descriptiva básica
- Numéricas: `describe()` → media, mediana, min, max, percentiles.  
- Categóricas: `value_counts()` → conteo de categorías.  
- Revisar distribuciones de frecuencia para variables clave.  

---

## 5. Análisis univariado
- 📊 Histogramas → variables numéricas.  
- 📦 Barras → variables categóricas.  
- 📉 Boxplots → detección de outliers.  

---

## 6. Análisis bivariado
- 🔗 Correlaciones entre numéricas: `corr()` + heatmap.  
- 📦 Relación categóricas ↔ numéricas: boxplot, violin plot.  
- 📋 Tablas de contingencia o `groupby()` para combinaciones de categóricas.  

---

## 7. Detección de outliers
- Boxplots, método IQR (rango intercuartílico).  
- Métodos estadísticos o visuales.  
- Evaluar si son errores o datos extremos válidos.  

---

## 8. Variables temporales (si existen)
- Revisar rangos de fechas.  
- Detectar estacionalidad y tendencias.  
- Ver consistencia en el tiempo (lagunas, duplicaciones).  

---

## 9. Revisar consistencia de datos
- Validar rangos esperados (ejemplo: edad ≥ 0).  
- Unificar formatos en categóricas (ejemplo: `"Male"`, `"male"`, `"M"`).  
- Conversión de unidades si es necesario.  

---

## 🔟 Visualización general
- 📊 Histogramas globales.  
- 🌡️ Heatmap de correlación.  
- 🔍 Gráficos de dispersión para relaciones clave.  



