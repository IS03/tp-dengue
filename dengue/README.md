# 📊 Proyecto de Análisis de Dengue en Argentina

## 📋 Descripción del Proyecto

Este proyecto consiste en un sistema completo de procesamiento, normalización y análisis de datos epidemiológicos de dengue en Argentina. El sistema integra datos de casos de dengue con información demográfica y geográfica para crear un dataset unificado y normalizado que permite análisis epidemiológicos detallados.

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
│   └── dengue-final.csv              # Dataset unificado y normalizado
├── dataset-dengue/                   # Datos de casos de dengue
│   ├── bruto/                        # Datos originales sin procesar
│   ├── procesado/                    # Datos normalizados por año
│   └── backup/                       # Backups automáticos
├── dataset-departamentos/            # Información geográfica
│   ├── bruto/                        # Lista original de departamentos
│   └── procesado/                    # Lista normalizada
├── dataset-poblacion/                # Datos demográficos
│   ├── bruto/                        # Archivos originales por provincia
│   ├── procesado/                    # Archivos normalizados
│   └── backup/                       # Backups automáticos
└── normalizacion-ejecutables/        # Scripts de procesamiento
    ├── dataset dengue/               # Scripts específicos para dengue
    ├── dataset poblacion/            # Scripts para datos demográficos
    └── normalizacion simple/         # Scripts de normalización básica
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

### Normalización de Dengue

#### `normalizar_dengue.py`
- Normalización básica de archivos de dengue
- Estandarización de texto y columnas
- Eliminación de datos vacíos

#### `verificar_departamentos_provincias.py`
- Verificación de consistencia geográfica
- Corrección interactiva de discrepancias
- Matching con lista oficial de departamentos

#### `normalizar_grupos_edad.py`
- Estandarización de rangos etarios
- Corrección de inconsistencias temporales

### Normalización de Población

#### `verificar_y_corregir_partidos.py`
- Validación de nombres de partidos
- Corrección interactiva de errores
- Sugerencias automáticas

#### `verificar_valores_poblacion.py`
- Detección de valores incorrectos
- Verificación de tipos de datos
- Corrección de inconsistencias

### Integración de Datos

#### `agregar_poblacion_dengue.py`
- Merge de datos demográficos con dengue
- Matching por provincia, departamento y año
- Agregación de columna población

#### `crear_columna_uta_id.py`
- Asignación de códigos UTA 2020
- Identificación única de departamentos
- Verificación de consistencia

## 📈 Dataset Final

### Estructura del Dataset Consolidado (`dengue-final.csv`)

| Columna | Descripción | Tipo |
|---------|-------------|------|
| `departamento_nombre` | Nombre del departamento | String |
| `provincia_id` | ID numérico de la provincia | Integer |
| `provincia_nombre` | Nombre de la provincia | String |
| `ano` | Año de los datos | Integer |
| `semanas_epidemiologicas` | Semana epidemiológica | Integer |
| `evento_nombre` | Tipo de evento (dengue) | String |
| `grupo_edad_id` | ID del grupo etario | Integer |
| `grupo_edad_desc` | Descripción del grupo etario | String |
| `cantidad_casos` | Número de casos | Float |
| `departamento_nombre_normalizado` | Nombre normalizado | String |
| `provincia_nombre_normalizado` | Provincia normalizada | String |
| `fila_original` | Referencia al archivo original | Integer |
| `departamento_id_uta_2020` | Código UTA 2020 | Integer |
| `poblacion` | Población del departamento | Integer |

### Estadísticas del Dataset
- **Período**: 2018-2025
- **Registros**: ~68,000 filas
- **Departamentos**: 531 departamentos de Argentina
- **Cobertura**: 24 provincias + CABA
- **Variables**: 14 columnas normalizadas

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
- Python 3.6+
- pandas
- Acceso a archivos del proyecto

### Ejecución de Scripts
```bash
# Normalización básica
cd normalizacion-ejecutables/normalizacion\ simple/
python normalizar_dengue.py

# Verificación de departamentos
cd normalizacion-ejecutables/dataset\ dengue/normalizacion\ departamentos\ y\ provincias/
python verificar_departamentos_provincias.py

# Integración de población
cd normalizacion-ejecutables/dataset\ dengue/merch\ con\ la\ poblacion\ en\ dengue/
python agregar_poblacion_dengue.py
```

### Flujo Recomendado
1. **Normalización básica** de archivos originales
2. **Verificación y corrección** de datos geográficos
3. **Normalización de población** y verificación de valores
4. **Integración** de datos demográficos
5. **Asignación de códigos UTA** para identificación única
6. **Consolidación final** en dataset unificado

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
- `A-final/dengue-final.csv` - Dataset consolidado final
- `dataset-departamentos/procesado/lista-departamentos.csv` - Lista oficial de departamentos
- `dataset-dengue/procesado/dengue-*.csv` - Datos de dengue por año
- `dataset-poblacion/procesado/*.csv` - Datos demográficos por provincia

### Scripts de Procesamiento
- `normalizacion-ejecutables/normalizacion simple/` - Normalización básica
- `normalizacion-ejecutables/dataset dengue/` - Procesamiento específico de dengue
- `normalizacion-ejecutables/dataset poblacion/` - Procesamiento de datos demográficos

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

---

**Desarrollado para análisis epidemiológico de dengue en Argentina**  
*Sistema de procesamiento y normalización de datos de vigilancia epidemiológica*
