# 🦟 Análisis Epidemiológico de Dengue en Argentina
## Sistema Integrado de Datos Epidemiológicos y Climáticos

### 👥 Equipo de Desarrollo
- **Uriel** - Módulo Clima (EDA/ETL de variables meteorológicas)
- **Senes** - Módulo Dengue (Procesamiento y normalización de datos epidemiológicos)
- **Juani** - Módulo Estaciones (Mapeo geográfico departamento-estación)

### 📋 Descripción General
Sistema completo de análisis epidemiológico que integra datos de casos de dengue con variables climáticas para identificar patrones, factores de riesgo y desarrollar modelos predictivos.

### 🎯 Objetivos del Proyecto
- **Análisis epidemiológico**: Patrones temporales y espaciales de dengue
- **Análisis climático**: Variables meteorológicas y su relación con brotes
- **Integración de datos**: Mapeo departamento-estación meteorológica
- **Modelado predictivo**: Factores de riesgo ambientales

### 🏗️ Componentes Principales

#### 1. 📊 Módulo Dengue (A-final) - Senes
- **Dataset consolidado**: 68,127 registros con 765,848 casos
- **Cobertura**: 429 departamentos, 24 provincias + CABA
- **Período**: 2018-2025
- **Variables**: Casos por departamento, grupo etario, semana epidemiológica

#### 2. 🌡️ Módulo Clima (EDA/ETL) - Uriel
- **Variables climáticas**: 38 variables meteorológicas
- **Estaciones**: 531 estaciones meteorológicas del INTA
- **Período**: Datos diarios históricos
- **Variables clave**: Precipitación, temperatura, humedad, viento

#### 3. 🗺️ Módulo de Mapeo (Estaciones) - Juani
- **Archivo**: `departamentos_con_estacion.csv`
- **Función**: Vinculación geográfica departamento-estación
- **Cobertura**: 429 departamentos mapeados
- **Distancia**: Cálculo de proximidad geográfica

### 📈 Análisis Disponibles

#### Epidemiológicos
- **Tendencias temporales**: Evolución de casos por año
- **Distribución espacial**: Patrones geográficos por departamento
- **Análisis por edad**: Grupos etarios más afectados
- **Estacionalidad**: Patrones por semana epidemiológica

#### Climáticos
- **Variables de precipitación**: Relación lluvia-criaderos
- **Variables de temperatura**: Supervivencia y actividad del vector
- **Variables de humedad**: Condiciones ambientales
- **Variables de viento**: Dispersión del vector

#### Integrados
- **Factores de riesgo**: Relación clima-dengue
- **Modelos predictivos**: Basados en variables ambientales
- **Análisis de clusters**: Agrupaciones espaciales
- **Correlaciones**: Entre variables epidemiológicas y climáticas

### 🔧 Uso del Sistema

#### Requisitos
- **Python**: 3.6+
- **Dependencias**: pandas, numpy, matplotlib, seaborn, scikit-learn
- **Acceso**: A archivos del proyecto

#### Flujo de Trabajo
1. **Carga de datos**: Dengue + Clima + Mapeo
2. **Análisis exploratorio**: EDA de cada componente
3. **Integración**: Mapeo departamento-estación
4. **Análisis conjunto**: Variables epidemiológicas + climáticas
5. **Modelado**: Factores de riesgo y predicción

### 📊 Métricas del Proyecto

#### Datos Procesados
- **Dengue**: 68,127 registros
- **Clima**: 923,867 registros
- **Estaciones**: 531 estaciones
- **Departamentos**: 429 únicos

#### Cobertura Temporal
- **Dengue**: 2018-2025 (8 años)
- **Clima**: Datos históricos diarios
- **Actualización**: Según disponibilidad de fuentes

#### Calidad de Datos
- **Completitud**: 95%+
- **Consistencia**: Verificada
- **Trazabilidad**: Completa

### 💡 Casos de Uso

#### Para Investigadores
- Análisis de tendencias epidemiológicas
- Identificación de factores de riesgo
- Desarrollo de modelos predictivos

#### Para Funcionarios de Salud
- Monitoreo de brotes
- Planificación de recursos
- Alertas tempranas

#### Para Estudiantes
- Aprendizaje de análisis de datos
- Proyectos de investigación
- Tesis y trabajos finales

### 🚀 Inicio Rápido

#### 1. Análisis de Dengue
```python
# Cargar dataset de dengue
df_dengue = pd.read_csv('dengue/A-final/dengue-final.csv')

# Análisis básico
print(f"Registros: {df_dengue.shape[0]:,}")
print(f"Casos totales: {df_dengue['cantidad_casos'].sum():,.0f}")
```

#### 2. Análisis de Clima
```python
# Cargar datos climáticos
df_clima = pd.read_parquet('clima/data/datos-todas-estaciones.parquet')

# Variables clave para dengue
variables_dengue = [
    'precipitacion_pluviometrica',
    'temperatura_abrigo_150cm_minima',
    'temperatura_abrigo_150cm_maxima',
    'humedad_media_8_14_20'
]
```

#### 3. Mapeo Geográfico
```python
# Cargar mapeo departamento-estación
df_mapeo = pd.read_csv('estaciones/departamentos_con_estacion.csv')

# Verificar cobertura
print(f"Departamentos mapeados: {df_mapeo['departamento_nombre'].nunique()}")
```

### 📚 Documentación Específica

#### Dengue (Senes)
- **README**: `dengue/README.md`
- **Proceso Senes**: `dengue/md/Proceso_Senes.md`
- **Proyecto por Semana**: `dengue/md/Proyecto_por_Semana.md`

#### Clima (Uriel)
- **EDA**: `clima/EDA/EDA_clima.ipynb`
- **Variables**: `clima/markdown/diccionario_variables.md`
- **Importancia**: `clima/markdown/variables_importancia.md`

#### Estaciones (Juani)
- **Mapeo**: `estaciones/departamentos_con_estacion.csv`
- **Análisis**: `estaciones/departamentos - estacion.ipynb`

### 🎯 Próximos Pasos

1. **Análisis de correlación**: Dengue vs variables climáticas
2. **Modelado predictivo**: Factores de riesgo ambientales
3. **Análisis espacial**: Clusters geográficos
4. **Validación**: Comparación con brotes históricos

### 📊 Archivos Clave

#### Datasets Principales
- `dengue/A-final/dengue-final.csv` - Dataset consolidado de dengue
- `clima/data/datos-todas-estaciones.parquet` - Datos climáticos
- `estaciones/departamentos_con_estacion.csv` - Mapeo geográfico

#### Análisis
- `dengue/A-final/analisis/` - EDA de dengue
- `clima/EDA/EDA_clima.ipynb` - EDA de clima
- `estaciones/departamentos - estacion.ipynb` - Análisis de mapeo

### 🔧 Mantenimiento

#### Actualización de Datos
1. Agregar nuevos datos en carpetas correspondientes
2. Ejecutar scripts de normalización
3. Actualizar mapeo geográfico
4. Regenerar análisis EDA

#### Resolución de Problemas
- Revisar logs de errores
- Verificar consistencia de datos
- Validar mapeo geográfico
- Consultar documentación específica

---

**Desarrollado para análisis epidemiológico de dengue en Argentina**  
*Sistema integrado de datos epidemiológicos y climáticos*

**Equipo**: Uriel (Clima) | Senes (Dengue) | Juani (Estaciones)  
**Última actualización**: Septiembre 2025  
**Estado**: ✅ Sistema funcional y documentado
