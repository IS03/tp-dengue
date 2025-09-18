# 📊 Sistema de Análisis de Dengue en Argentina (2018-2025)

Este sistema procesa y organiza datos oficiales de casos de dengue en Argentina, proporcionando información clara y accesible para análisis epidemiológicos, reportes y visualizaciones.

## 🎯 ¿Qué encontrarás aquí?

### 📁 **Datos Procesados** (carpeta `processed/`)

#### 📈 **Casos por Departamento y Semana Epidemiológica**
- **Archivo**: `weekly_by_depto.csv` / `weekly_by_depto.parquet`
- **Contiene**: Casos de dengue desglosados por departamento, semana epidemiológica y año
- **Incluye**: Población e incidencia calculada por cada departamento
- **Ideal para**: Mapas interactivos, análisis temporal detallado, dashboards

#### 📅 **Casos por Provincia y Mes**
- **Archivo**: `monthly_by_prov.csv` / `monthly_by_prov.parquet`
- **Contiene**: Resumen mensual de casos por provincia
- **Ideal para**: Reportes ejecutivos, análisis de tendencias estacionales

#### 🗂️ **Dataset Completo**
- **Archivo**: `dengue_2018_2025_clean.csv` / `dengue_2018_2025_clean.parquet`
- **Contiene**: Todos los casos individuales con información detallada
- **Incluye**: Datos por grupo etario, fechas exactas, información geográfica completa
- **Ideal para**: Análisis epidemiológicos profundos, estudios de investigación

### 📋 **Reportes de Calidad** (carpeta `reports/`)

#### ✅ **Reporte de Procesamiento**
- **Archivo**: `quality_report.csv`
- **Contiene**: Estadísticas de procesamiento por archivo fuente
- **Información**: Registros leídos, limpiados, duplicados eliminados
- **Útil para**: Verificar la integridad de los datos procesados

#### 👥 **Reporte de Población**
- **Archivo**: `poblacion_quality.csv`
- **Contiene**: Validación de datos demográficos utilizados
- **Útil para**: Verificar cobertura poblacional por departamento

## 🚀 **¿Cómo usar estos datos?**

### Para **Dashboards y Visualizaciones**:
- Usa `weekly_by_depto.csv` para mapas de calor por departamento
- Combina con archivos GeoJSON de Argentina para mapas interactivos
- La columna `incidencia` te permite comparar regiones independientemente del tamaño poblacional

### Para **Reportes Ejecutivos**:
- Usa `monthly_by_prov.csv` para resúmenes mensuales
- Perfecto para gráficos de tendencias y comparaciones entre provincias

### Para **Investigación Epidemiológica**:
- Usa `dengue_2018_2025_clean.csv` para análisis detallados
- Incluye información por grupo etario y fechas exactas
- Permite estudios de patrones temporales y demográficos

## 📊 **Estructura de los Datos**

### Columnas principales en `weekly_by_depto.csv`:
- `anio`: Año del registro
- `semana_epi`: Semana epidemiológica (1-52/53)
- `provincia_nombre`: Nombre de la provincia
- `departamento_nombre`: Nombre del departamento
- `cantidad_casos`: Número de casos reportados
- `poblacion`: Población del departamento
- `incidencia`: Casos por 100,000 habitantes

### Columnas principales en `monthly_by_prov.csv`:
- `anio`: Año del registro
- `mes`: Mes del año (1-12)
- `provincia_nombre`: Nombre de la provincia
- `cantidad_casos`: Total de casos del mes

## 🔧 **Para Desarrolladores**

### Requisitos técnicos:
- Python 3.10+
- Librerías: pandas, openpyxl, pyarrow

### Ejecutar el procesamiento:
```bash
python etl_dengue.py --input_dir ./raw --out_dir ./processed \
  --geo_map ./ref/geo_map.csv \
  --population ./ref/poblacion.csv
```

### Estructura del proyecto:
```
dengue_etl/
  raw/           # Archivos fuente originales
  ref/           # Archivos de referencia (geografía, población)
  processed/     # 📊 DATOS PROCESADOS (aquí están tus informes)
  reports/       # 📋 Reportes de calidad
  logs/          # Registros de procesamiento
```

## 📞 **¿Necesitas ayuda?**

Los archivos están listos para usar en Excel, Power BI, Tableau, Python, R o cualquier herramienta de análisis. Si necesitas un formato específico o tienes preguntas sobre los datos, revisa los reportes de calidad en la carpeta `reports/`.
