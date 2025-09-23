# 📊 Proyecto de Análisis de Dengue en Argentina

## 📋 Descripción del Proyecto

Este proyecto consiste en un sistema completo de procesamiento, normalización y análisis de datos epidemiológicos de dengue en Argentina. El sistema integra datos de casos de dengue con información demográfica y geográfica para crear un dataset unificado y normalizado que permite análisis epidemiológicos detallados.

**Estado del proyecto**: ✅ **COMPLETADO** - Dataset final consolidado con 68,127 registros

## 🎯 Objetivos

- **Normalización de datos**: Estandarizar formatos, nombres y códigos de identificación
- **Integración de fuentes**: Combinar datos de dengue con información demográfica y geográfica
- **Calidad de datos**: Implementar verificaciones y correcciones automáticas
- **Trazabilidad**: Mantener backups y registros de todos los cambios realizados
- **Análisis epidemiológico**: Facilitar estudios de incidencia, distribución temporal y espacial

## 📊 Fuentes de Datos

### 1. Datos de Dengue
- **Fuente**: Ministerio de Salud de Argentina
- **Período**: 2018-2025
- **Formato original**: Excel/CSV con información semanal
- **Variables**: Casos por departamento, provincia, grupo etario, semana epidemiológica

### 2. Datos Demográficos
- **Fuente**: INDEC (Instituto Nacional de Estadística y Censos)
- **Período**: 2018-2025
- **Cobertura**: Todos los departamentos de Argentina
- **Variables**: Población por departamento y año

### 3. Datos Geográficos
- **Fuente**: Lista oficial de departamentos
- **Cobertura**: 531 departamentos de Argentina
- **Variables**: Códigos UTA 2020, coordenadas, información socioeconómica

## 🏗️ Estructura del Proyecto

```
tp-dengue/
├── A-final/                          # Dataset final consolidado
│   ├── dengue-final.csv              # Dataset unificado y normalizado (68,127 registros)
│   └── analisis/                     # Análisis EDA del dataset final
│       ├── info/                     # Información estadística
│       │   ├── excel/                # Reportes en formato Excel
│       │   ├── html/                 # Reporte HTML interactivo
│       │   └── markdown/             # Reporte EDA en Markdown
│       └── py/                       # Scripts de análisis
├── dataset-dengue/                   # Datos de casos de dengue
│   ├── bruto/                        # Datos originales sin procesar (12 archivos)
│   ├── procesado/                    # Datos normalizados por año (8 archivos)
│   └── backup/                       # Backups automáticos (48 archivos)
├── dataset-departamentos/            # Información geográfica
│   ├── bruto/                        # Lista original de departamentos
│   └── procesado/                    # Lista normalizada (531 departamentos)
├── dataset-poblacion/                # Datos demográficos
│   ├── bruto/                        # Archivos originales por provincia (24 archivos)
│   ├── procesado/                    # Archivos normalizados (24 archivos)
│   └── backup/                       # Backups automáticos (120 archivos)
└── normalizacion-ejecutables/        # Scripts de procesamiento
    ├── dataset dengue/               # Scripts específicos para dengue
    │   ├── merch con la poblacion en dengue/    # Integración de población
    │   ├── normalizacion dengue edades y grupos/ # Normalización etaria
    │   ├── normalizacion departamentos y provincias/ # Normalización geográfica
    │   ├── normalizacion desconocidos y sin datos/   # Manejo de datos faltantes
    │   └── uta IDs/                  # Asignación de códigos UTA
    ├── dataset poblacion/            # Scripts para datos demográficos
    │   ├── normalizacion poblacion departamentos/    # Normalización geográfica
    │   ├── normalizacion poblacion valores/          # Verificación de valores
    │   └── uta IDs/                  # Asignación de códigos UTA
    └── normalizacion simple/         # Scripts de normalización básica (9 scripts)
```

## 🔄 Flujo de Procesamiento

### Fase 1: Normalización Básica
1. **Conversión de formatos**: Excel → CSV
2. **Limpieza de texto**: Eliminación de acentos, caracteres especiales
3. **Estandarización de columnas**: Nombres consistentes
4. **Eliminación de datos vacíos**: Filas y columnas sin información

### Fase 2: Normalización de Datos de Dengue
1. **Normalización de departamentos y provincias**:
   - Verificación contra lista oficial
   - Corrección de nombres inconsistentes
   - Asignación de códigos UTA 2020

2. **Normalización de grupos etarios**:
   - Estandarización de rangos de edad
   - Corrección de inconsistencias temporales

3. **Manejo de datos faltantes**:
   - Identificación de valores desconocidos
   - Corrección automática e interactiva

### Fase 3: Normalización de Datos Demográficos
1. **Verificación de partidos**:
   - Validación contra lista oficial
   - Corrección de nombres incorrectos

2. **Verificación de valores**:
   - Detección de valores nulos o incorrectos
   - Conversión a enteros

3. **Asignación de códigos UTA**:
   - Agregación de identificadores únicos

### Fase 4: Integración de Datos
1. **Merge con población**:
   - Agregación de datos demográficos por departamento y año
   - Matching: provincia + departamento + año

2. **Consolidación final**:
   - Unificación de todos los datasets
   - Verificación de consistencia

## 🛠️ Scripts Principales

### Normalización Básica (`normalizacion simple/`)

#### `normalizar_dengue.py`
- Normalización básica de archivos de dengue
- Estandarización de texto (sin ñ, sin tildes, sin caracteres especiales)
- Eliminación de datos vacíos y columnas innecesarias
- Conversión a formato estándar con separador de comas

#### `limpiar_csv.py`
- Limpieza general de archivos CSV
- Corrección de problemas de codificación
- Normalización de separadores

#### `normalizar_texto.py`
- Normalización de texto específica para archivos epidemiológicos
- Eliminación de acentos y caracteres especiales
- Estandarización de mayúsculas y espacios

### Normalización de Dengue (`dataset dengue/`)

#### `verificar_departamentos_provincias.py`
- Verificación de consistencia geográfica contra lista oficial
- Corrección interactiva de discrepancias
- Sugerencias automáticas para nombres incorrectos
- Matching con códigos UTA 2020

#### `normalizar_grupos_edad.py`
- Estandarización de rangos etarios
- Corrección de inconsistencias temporales
- Mapeo a grupos etarios estándar

#### `corregir_problemas_automatico.py`
- Corrección automática de problemas comunes
- Manejo de datos faltantes y valores inconsistentes

### Normalización de Población (`dataset poblacion/`)

#### `verificar_y_corregir_partidos.py`
- Validación de nombres de partidos contra lista oficial
- Corrección interactiva de errores
- Sugerencias automáticas basadas en similitud

#### `verificar_valores_poblacion.py`
- Detección de valores incorrectos o nulos
- Verificación de tipos de datos
- Conversión a enteros y corrección de inconsistencias

### Integración de Datos

#### `agregar_poblacion_dengue.py`
- Merge de datos demográficos con dengue
- Matching por provincia, departamento y año
- Agregación de columna población
- Sistema de backups automáticos

#### `crear_columna_uta_id.py`
- Asignación de códigos UTA 2020
- Identificación única de departamentos
- Verificación de consistencia geográfica

### Análisis EDA (`A-final/analisis/py/`)

#### `generar_analisis_eda.py`
- Generación de análisis exploratorio de datos
- Estadísticas descriptivas por columna
- Reportes en múltiples formatos (Excel, HTML, Markdown)
- Análisis de distribuciones y tendencias

## 📈 Dataset Final

### Estructura del Dataset Consolidado (`dengue-final.csv`)

| Columna | Descripción | Tipo | Valores Únicos |
|---------|-------------|------|----------------|
| `id_uta` | Código UTA 2020 único | Integer | 429 |
| `departamento_nombre` | Nombre del departamento | String | 429 |
| `provincia_nombre` | Nombre de la provincia | String | 24 |
| `ano` | Año de los datos | Integer | 8 |
| `semanas_epidemiologicas` | Semana epidemiológica | Float | 53 |
| `grupo_edad_id` | ID del grupo etario | Integer | 11 |
| `grupo_edad_desc` | Descripción del grupo etario | String | 11 |
| `cantidad_casos` | Número de casos | Float | 430 |
| `poblacion` | Población del departamento | Integer | 1,474 |

### Estadísticas del Dataset
- **Período**: 2018-2025
- **Registros**: 68,127 filas
- **Departamentos**: 429 departamentos únicos
- **Cobertura**: 24 provincias + CABA
- **Variables**: 9 columnas normalizadas
- **Total de casos**: 765,848 casos de dengue
- **Población promedio**: 216,043 habitantes por departamento

### Top 10 Departamentos con Más Casos
1. **Córdoba Capital**: 63,655 casos
2. **Rosario**: 42,999 casos
3. **Tucumán Capital**: 38,893 casos
4. **Santiago del Estero Capital**: 24,395 casos
5. **San Fernando**: 21,037 casos
6. **Cruz Alta**: 19,143 casos
7. **Salta Capital**: 16,344 casos
8. **Comuna 1**: 14,849 casos
9. **La Matanza**: 13,987 casos
10. **San Justo**: 13,505 casos

### Distribución Temporal de Casos
- **2018**: 1,607 casos
- **2019**: 2,790 casos
- **2020**: 45,079 casos
- **2021**: 3,847 casos
- **2022**: 793 casos
- **2023**: 141,429 casos
- **2024**: 553,535 casos (año pico)
- **2025**: 16,768 casos (parcial)

## ⚙️ Características Técnicas

### Sistema de Backups
- **Backups automáticos**: Antes de cada modificación
- **Numeración secuencial**: back1, back2, back3, etc.
- **Ubicación organizada**: Por tipo de procesamiento
- **Preservación de originales**: Sin pérdida de datos

### Normalización de Texto
- **Eliminación de acentos**: "año" → "ano"
- **Minúsculas**: Estandarización de mayúsculas
- **Caracteres especiales**: Limpieza de símbolos
- **Espacios**: Normalización de espacios múltiples

### Verificación de Calidad
- **Validación cruzada**: Entre diferentes fuentes
- **Detección de errores**: Automática e interactiva
- **Sugerencias inteligentes**: Para correcciones
- **Reportes detallados**: De errores y correcciones

## 📊 Análisis Posibles

### Epidemiológicos
- **Tendencias temporales**: Evolución de casos por año
- **Distribución espacial**: Patrones geográficos
- **Análisis por edad**: Grupos etarios más afectados
- **Estacionalidad**: Patrones por semana epidemiológica

### Demográficos
- **Tasas de incidencia**: Casos por 100,000 habitantes
- **Comparaciones regionales**: Entre provincias
- **Análisis urbano-rural**: Por tipo de departamento
- **Proyecciones**: Basadas en datos demográficos

### Integrados
- **Factores de riesgo**: Relación con variables socioeconómicas
- **Modelos predictivos**: Basados en datos históricos
- **Análisis de clusters**: Agrupaciones espaciales
- **Correlaciones**: Entre variables epidemiológicas y demográficas

## 🚀 Uso del Sistema

### Requisitos
- **Python**: 3.6+
- **Dependencias principales**:
  - pandas: Manipulación de datos
  - numpy: Operaciones numéricas
  - unicodedata: Normalización de texto
  - difflib: Comparación de texto
  - csv, os, shutil: Operaciones de archivos
- **Acceso**: A archivos del proyecto

### Ejecución de Scripts

#### 1. Normalización Básica
```bash
cd normalizacion-ejecutables/normalizacion\ simple/
python normalizar_dengue.py
python limpiar_csv.py
python normalizar_texto.py
```

#### 2. Verificación de Departamentos y Provincias
```bash
cd normalizacion-ejecutables/dataset\ dengue/normalizacion\ departamentos\ y\ provincias/
python verificar_departamentos_provincias.py
```

#### 3. Normalización de Grupos Etarios
```bash
cd normalizacion-ejecutables/dataset\ dengue/normalizacion\ dengue\ edades\ y\ grupos/
python normalizar_grupos_edad.py
```

#### 4. Integración de Población
```bash
cd normalizacion-ejecutables/dataset\ dengue/merch\ con\ la\ poblacion\ en\ dengue/
python agregar_poblacion_dengue.py
```

#### 5. Asignación de Códigos UTA
```bash
cd normalizacion-ejecutables/dataset\ dengue/uta\ IDs/
python crear_columna_uta_id.py
```

#### 6. Generación de Análisis EDA
```bash
cd A-final/analisis/py/
python generar_analisis_eda.py
```

### Flujo Recomendado
1. **Normalización básica** de archivos originales
2. **Verificación y corrección** de datos geográficos
3. **Normalización de grupos etarios** y corrección de inconsistencias
4. **Normalización de población** y verificación de valores
5. **Integración** de datos demográficos con dengue
6. **Asignación de códigos UTA** para identificación única
7. **Consolidación final** en dataset unificado
8. **Generación de análisis EDA** para exploración de datos

## ⚠️ Notas Importantes

### Calidad de Datos
- **Fuente de verdad**: `lista-departamentos.csv` para datos geográficos
- **Matching estricto**: Combinación exacta de provincia + departamento + año
- **Verificación cruzada**: Entre diferentes fuentes de datos
- **Corrección interactiva**: Para casos complejos

### Trazabilidad
- **Backups automáticos**: Preservación de versiones anteriores
- **Registro de cambios**: Documentación de modificaciones
- **Referencias originales**: Mantenimiento de vínculos con datos fuente
- **Auditoría**: Posibilidad de rastrear origen de cada dato

### Escalabilidad
- **Procesamiento por lotes**: Manejo eficiente de grandes volúmenes
- **Modularidad**: Scripts independientes y reutilizables
- **Automatización**: Procesos repetibles y consistentes
- **Extensibilidad**: Fácil incorporación de nuevos años o variables

## 🎯 Resultados

El proyecto ha logrado crear un dataset epidemiológico robusto y normalizado que permite:

- **Análisis epidemiológicos** precisos y confiables
- **Comparaciones temporales** y espaciales consistentes
- **Integración** de múltiples fuentes de datos
- **Trazabilidad completa** de todos los cambios realizados
- **Base sólida** para investigaciones futuras sobre dengue en Argentina

Este sistema representa una herramienta valiosa para la vigilancia epidemiológica y la investigación en salud pública, proporcionando datos de alta calidad para la toma de decisiones informadas en el control y prevención del dengue.

## 📁 Archivos Clave

### Datasets Principales
- **`A-final/dengue-final.csv`** - Dataset consolidado final (68,127 registros)
- **`dataset-departamentos/procesado/lista-departamentos.csv`** - Lista oficial de departamentos (531 departamentos)
- **`dataset-dengue/procesado/dengue-*.csv`** - Datos de dengue por año (8 archivos)
- **`dataset-poblacion/procesado/*.csv`** - Datos demográficos por provincia (24 archivos)

### Análisis y Reportes
- **`A-final/analisis/info/markdown/reporte_eda.md`** - Reporte EDA completo
- **`A-final/analisis/info/html/reporte_eda.html`** - Reporte HTML interactivo
- **`A-final/analisis/info/excel/`** - Reportes en formato Excel (5 archivos)

### Scripts de Procesamiento
- **`normalizacion-ejecutables/normalizacion simple/`** - Normalización básica (9 scripts)
- **`normalizacion-ejecutables/dataset dengue/`** - Procesamiento específico de dengue (5 módulos)
- **`normalizacion-ejecutables/dataset poblacion/`** - Procesamiento de datos demográficos (3 módulos)

### Backups y Trazabilidad
- **`dataset-dengue/backup/`** - Backups automáticos (48 archivos)
- **`dataset-poblacion/backup/`** - Backups automáticos (120 archivos)
- **Sistema de numeración secuencial**: back1, back2, back3, etc.

## 🔧 Mantenimiento

### Actualización de Datos
1. Agregar nuevos archivos en las carpetas `bruto/`
2. Ejecutar scripts de normalización correspondientes
3. Verificar calidad de datos procesados
4. Actualizar dataset consolidado

### Resolución de Problemas
- Revisar logs de errores en los scripts
- Verificar backups automáticos
- Consultar documentación específica en cada carpeta
- Validar consistencia con archivos de referencia

## 📊 Resumen de Logros

### Datos Procesados
- ✅ **68,127 registros** consolidados en dataset final
- ✅ **765,848 casos de dengue** totales procesados
- ✅ **429 departamentos únicos** normalizados
- ✅ **24 provincias + CABA** cubiertas
- ✅ **8 años de datos** (2018-2025) integrados

### Calidad de Datos
- ✅ **100% de registros** con códigos UTA 2020 asignados
- ✅ **Normalización completa** de nombres geográficos
- ✅ **Verificación cruzada** con fuentes oficiales
- ✅ **Trazabilidad completa** de todos los cambios

### Análisis Disponibles
- ✅ **Análisis EDA completo** con reportes en múltiples formatos
- ✅ **Estadísticas descriptivas** por todas las variables
- ✅ **Distribuciones temporales** y espaciales
- ✅ **Top departamentos** por casos y registros

### Sistema de Procesamiento
- ✅ **48 scripts** de normalización y procesamiento
- ✅ **Sistema de backups** automático con 168 archivos de respaldo
- ✅ **Verificación interactiva** para casos complejos
- ✅ **Documentación completa** de todos los procesos

---

**Desarrollado para análisis epidemiológico de dengue en Argentina**  
*Sistema de procesamiento y normalización de datos de vigilancia epidemiológica*

**Última actualización**: Septiembre 2025  
**Estado**: ✅ Proyecto completado exitosamente
