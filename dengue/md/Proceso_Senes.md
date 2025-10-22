# Proceso Senes - Sistema de Normalización Epidemiológica de Datos

## Resumen Ejecutivo

El Proceso Senes es un sistema completo de procesamiento, normalización y análisis de datos epidemiológicos de dengue en Argentina. Desarrollado para integrar datos de casos de dengue con información demográfica y geográfica, creando un dataset unificado y normalizado que permite análisis epidemiológicos detallados.

**Estado**: Completado exitosamente  
**Período**: 2018-2025  
**Registros procesados**: 68,127  
**Casos de dengue**: 765,848  
**Departamentos únicos**: 429  
**Cobertura**: 24 provincias + CABA

## Objetivos del Proyecto

- Normalización de datos epidemiológicos
- Integración de fuentes múltiples
- Mejora de calidad de datos
- Trazabilidad completa de cambios
- Facilitación de análisis epidemiológicos

## Fuentes de Datos

### Datos de Dengue
- **Fuente**: Ministerio de Salud de Argentina
- **Período**: 2018-2025
- **Formato**: Excel/CSV con información semanal
- **Variables**: Casos por departamento, provincia, grupo etario, semana epidemiológica

### Datos Demográficos
- **Fuente**: INDEC (Instituto Nacional de Estadística y Censos)
- **Período**: 2018-2025
- **Cobertura**: Todos los departamentos de Argentina
- **Variables**: Población por departamento y año

### Datos Geográficos
- **Fuente**: Lista oficial de departamentos
- **Cobertura**: 531 departamentos de Argentina
- **Variables**: Códigos UTA 2020, coordenadas, información socioeconómica

## Problemas Identificados y Resueltos

### 1. Problemas de Codificación y Formato
**Problemas encontrados**:
- Múltiples codificaciones (UTF-8, Latin-1, CP1252)
- Archivos Excel mezclados con CSV
- Separadores inconsistentes (; vs ,)
- Caracteres especiales y acentos problemáticos

**Soluciones implementadas**:
- Sistema de detección automática de codificación
- Conversión estandarizada a CSV con separador de comas
- Normalización de caracteres especiales

### 2. Inconsistencias Geográficas
**Problemas encontrados**:
- Nombres de departamentos diferentes entre archivos
- Variaciones en provincias (mayúsculas/minúsculas)
- Caracteres especiales (ñ, tildes, acentos)
- Espacios extra y caracteres invisibles

**Soluciones implementadas**:
- Sistema de normalización de texto robusto
- Comparación con lista oficial de departamentos
- Sugerencias automáticas para nombres similares
- Corrección interactiva para casos complejos

### 3. Datos Faltantes y Problemáticos
**Problemas encontrados**:
- Valores "desconocido", "sin dato", "N/A" en múltiples formatos
- IDs problemáticos (99, 999) no correspondientes
- Filas completamente vacías o con solo espacios
- Inconsistencias entre IDs y descripciones de grupos etarios

**Soluciones implementadas**:
- Sistema de limpieza automática de datos problemáticos
- Eliminación de filas con valores inconsistentes
- Mapeo bidireccional para corrección de inconsistencias

### 4. Problemas de Integración
**Problemas encontrados**:
- Matching geográfico entre fuentes diferentes
- Inconsistencias temporales entre años
- Estructuras de datos diferentes por año
- Validación cruzada entre múltiples fuentes

**Soluciones implementadas**:
- Sistema de matching inteligente por provincia + departamento + año
- Normalización de estructuras de datos
- Verificación cruzada automática

## Metodología de Procesamiento

### Fase 1: Normalización Básica
1. **Conversión de formatos**: Excel → CSV
2. **Limpieza de texto**: Sin ñ, sin tildes, sin caracteres especiales
3. **Estandarización de columnas**: Nombres consistentes
4. **Eliminación de datos vacíos**: Filas y columnas sin información

### Fase 2: Normalización de Datos de Dengue
1. **Verificación de departamentos y provincias** contra lista oficial
2. **Normalización de grupos etarios** y corrección de inconsistencias
3. **Manejo de datos faltantes** y valores inconsistentes
4. **Asignación de códigos UTA 2020**

### Fase 3: Normalización de Datos Demográficos
1. **Verificación de partidos** contra lista oficial
2. **Validación de valores** de población
3. **Asignación de códigos UTA** para identificación única

### Fase 4: Integración de Datos
1. **Merge de datos demográficos** con dengue
2. **Matching por provincia + departamento + año**
3. **Consolidación final** en dataset unificado
4. **Verificación de consistencia** final

## Estrategias Técnicas Implementadas

### Sistema de Backups Automáticos
- Backups antes de cada modificación con timestamps
- Numeración secuencial (back1, back2, back3, etc.)
- Organización por tipo de procesamiento
- Preservación de originales sin pérdida de datos

### Sistema de Limpieza en Múltiples Niveles
**Nivel 1: Limpieza Básica**
- Eliminación de filas y columnas completamente vacías
- Limpieza de espacios en blanco
- Eliminación de filas con solo valores vacíos

**Nivel 2: Normalización de Texto**
- Eliminación de acentos y tildes
- Conversión a minúsculas
- Eliminación de caracteres especiales
- Normalización de espacios múltiples

**Nivel 3: Verificación Geográfica**
- Comparación con lista oficial de departamentos
- Sugerencias automáticas para nombres similares
- Corrección interactiva para casos complejos

### Sistema de Verificación Cruzada
- Validación entre diferentes fuentes de datos
- Detección automática de inconsistencias
- Sugerencias inteligentes basadas en similitud
- Corrección interactiva para casos ambiguos

## Soluciones Técnicas Desarrolladas

### Detección Automática de Codificación
```python
for encoding in ['utf-8', 'latin-1', 'cp1252']:
    try:
        df = pd.read_csv(archivo_path, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue
```

### Normalización de Texto Robusta
```python
def normalizar_texto_dengue(texto):
    texto = texto.lower()
    texto = texto.replace('año', 'ano')  # Sin ñ
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
```

### Sistema de Mapeo Bidireccional
- ID → Descripción y Descripción → ID
- Corrección automática de inconsistencias
- Validación cruzada entre ambos campos

### Limpieza Automática de Datos Problemáticos
```python
valores_problematicos = ['desconocido', 'desconocida', 'unknown', 'n/a', 'na', 'sin dato', 'sin datos']
mask_desconocido = (
    df['departamento_nombre'].astype(str).str.lower().isin(valores_problematicos) &
    df['provincia_nombre'].astype(str).str.lower().isin(valores_problematicos)
)
```

## Sistema de Monitoreo y Trazabilidad

### Logging Detallado
- Contadores de eliminaciones por tipo
- Registro de cambios realizados
- Estadísticas de procesamiento por archivo

### Verificación Post-Procesamiento
- Validación de consistencia después de cada paso
- Detección de errores restantes
- Reportes de calidad de datos

### Sistema de Corrección Interactiva
- Menús interactivos para casos complejos
- Sugerencias automáticas para correcciones
- Opción de cancelar cambios si es necesario

## Resultados Obtenidos

### Dataset Final Consolidado
- **68,127 registros** con 9 columnas normalizadas
- **765,848 casos de dengue** procesados
- **100% de registros** con códigos UTA 2020 asignados
- **Integración completa** de datos demográficos

### Estructura del Dataset Final
| Columna | Descripción | Valores Únicos |
|---------|-------------|----------------|
| id_uta | Código UTA 2020 único | 429 |
| departamento_nombre | Nombre del departamento | 429 |
| provincia_nombre | Nombre de la provincia | 24 |
| ano | Año de los datos | 8 |
| semanas_epidemiologicas | Semana epidemiológica | 53 |
| grupo_edad_id | ID del grupo etario | 11 |
| grupo_edad_desc | Descripción del grupo etario | 11 |
| cantidad_casos | Número de casos | 430 |
| poblacion | Población del departamento | 1,474 |

### Estadísticas Principales
- **Período**: 2018-2025
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

## Sistema de Procesamiento

### Scripts Desarrollados (48 total)
- **Normalización básica** (9 scripts)
- **Procesamiento específico de dengue** (5 módulos)
- **Procesamiento de datos demográficos** (3 módulos)
- **Sistema de backups** automático

### Sistema de Backups (168 archivos)
- **Backups automáticos** por tipo de procesamiento
- **Numeración secuencial** para trazabilidad
- **Preservación de originales** sin pérdida

### Flujo de Procesamiento Recomendado
1. **Normalización básica** de archivos originales
2. **Verificación y corrección** de datos geográficos
3. **Normalización de grupos etarios** y corrección de inconsistencias
4. **Normalización de población** y verificación de valores
5. **Integración** de datos demográficos con dengue
6. **Asignación de códigos UTA** para identificación única
7. **Consolidación final** en dataset unificado
8. **Generación de análisis EDA** para exploración de datos

## Análisis Disponibles

### Epidemiológicos
- Tendencias temporales por año
- Distribución espacial por departamento
- Análisis por grupos etarios
- Patrones estacionales por semana epidemiológica

### Demográficos
- Tasas de incidencia por 100,000 habitantes
- Comparaciones regionales entre provincias
- Análisis urbano-rural

### Integrados
- Factores de riesgo socioeconómicos
- Modelos predictivos basados en datos históricos
- Análisis de clusters espaciales

## Logros del Proyecto

### Calidad de Datos
- ✅ **Normalización completa** de nombres geográficos
- ✅ **Eliminación de inconsistencias** temporales y espaciales
- ✅ **Integración exitosa** de múltiples fuentes
- ✅ **Trazabilidad completa** de todos los cambios

### Sistema Robusto
- ✅ **48 scripts** de procesamiento automatizado
- ✅ **168 archivos de backup** preservando historial
- ✅ **Verificación interactiva** para casos complejos
- ✅ **Documentación completa** de todos los procesos

### Análisis Disponibles
- ✅ **Análisis EDA completo** con reportes en múltiples formatos
- ✅ **Estadísticas descriptivas** por todas las variables
- ✅ **Distribuciones temporales** y espaciales
- ✅ **Top departamentos** por casos y registros

## Archivos Clave del Proyecto

### Datasets Principales
- `A-final/dengue-final.csv` - Dataset consolidado final (68,127 registros)
- `dataset-departamentos/procesado/lista-departamentos.csv` - Lista oficial de departamentos (531 departamentos)
- `dataset-dengue/procesado/dengue-*.csv` - Datos de dengue por año (8 archivos)
- `dataset-poblacion/procesado/*.csv` - Datos demográficos por provincia (24 archivos)

### Análisis y Reportes
- `A-final/analisis/info/markdown/reporte_eda.md` - Reporte EDA completo
- `A-final/analisis/info/html/reporte_eda.html` - Reporte HTML interactivo
- `A-final/analisis/info/excel/` - Reportes en formato Excel (5 archivos)

### Scripts de Procesamiento
- `normalizacion-ejecutables/normalizacion simple/` - Normalización básica (9 scripts)
- `normalizacion-ejecutables/dataset dengue/` - Procesamiento específico de dengue (5 módulos)
- `normalizacion-ejecutables/dataset poblacion/` - Procesamiento de datos demográficos (3 módulos)

### Backups y Trazabilidad
- `dataset-dengue/backup/` - Backups automáticos (48 archivos)
- `dataset-poblacion/backup/` - Backups automáticos (120 archivos)
- **Sistema de numeración secuencial**: back1, back2, back3, etc.

## Conclusiones

El Proceso Senes representa una herramienta valiosa para la vigilancia epidemiológica y la investigación en salud pública, proporcionando datos de alta calidad para la toma de decisiones informadas en el control y prevención del dengue en Argentina.

### Características Técnicas Destacadas
- **Sistema de backups automático** con preservación completa del historial
- **Normalización de texto robusta** para manejo de caracteres especiales
- **Verificación cruzada inteligente** entre múltiples fuentes
- **Sistema de corrección interactiva** para casos complejos
- **Trazabilidad completa** de todos los cambios realizados

### Impacto del Proyecto
- **Base sólida** para investigaciones futuras sobre dengue
- **Datos normalizados** para análisis epidemiológicos precisos
- **Sistema escalable** para futuras actualizaciones de datos
- **Herramienta valiosa** para la vigilancia epidemiológica

---

**Desarrollado para análisis epidemiológico de dengue en Argentina**  
*Sistema de procesamiento y normalización de datos de vigilancia epidemiológica*

**Última actualización**: Septiembre 2025  
**Estado**: ✅ Proyecto completado exitosamente
