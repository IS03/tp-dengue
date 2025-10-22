# Proyecto por Semana - Análisis Epidemiológico de Dengue en Argentina

## Resumen Ejecutivo

Este documento detalla el desarrollo cronológico del proyecto de análisis epidemiológico de dengue en Argentina, realizado durante 7 semanas a partir del 5 de septiembre. El proyecto evolucionó desde la ideación inicial hasta la creación de un sistema completo de procesamiento, normalización y análisis de datos epidemiológicos.

**Período**: 5 de septiembre - 7 semanas de desarrollo  
**Resultado final**: 68,127 registros consolidados con 765,848 casos de dengue  
**Problemas resueltos**: 19 issues técnicos identificados y solucionados  
**Scripts desarrollados**: 48 scripts de procesamiento automatizado

---

## **SEMANA 1** (5-11 septiembre)
### **Fase de Ideación y Exploración**

**Actividad Principal**: Lluvia de ideas de proyectos
- **Propuestas de finanzas**: Predecir estafas, predecir estabilidad del país
- **Propuestas de salud**: Análisis de dengue
- **Herramientas utilizadas**: ChatGPT, Cursor, Cloud

**Trabajo Técnico Realizado**:
- Investigación inicial de datasets disponibles
- Exploración de fuentes de datos del gobierno
- Análisis preliminar de viabilidad de proyectos

**Resultado**: Decisión de explorar múltiples direcciones antes de definir el enfoque final

---

## **SEMANA 2** (12-18 septiembre)
### **Enfoque en Vulnerabilidad Económica**

**Actividad Principal**: Desarrollo de propuesta de índice de vulnerabilidad
- Búsqueda activa de datos económicos
- Consultas al profesor para orientación
- Definición de estructura del proyecto

**Trabajo Técnico Realizado**:
- Exploración de fuentes de datos económicos
- Investigación de indicadores de vulnerabilidad
- Planificación de metodología de análisis

**Resultado**: Propuesta estructurada pero cambio de dirección hacia el final de la semana

---

## **SEMANA 3** (19-25 septiembre)
### **Vuelta al Dengue y Planificación**

**Actividad Principal**: Reorientación hacia análisis de dengue
- Llevaron todos los datasets brutos disponibles
- Planificación de enfoque del proyecto
- División de tareas entre miembros del equipo

**Trabajo Técnico Realizado**:
- **Análisis inicial de 12 archivos brutos** de dengue (2018-2025)
- **Identificación de problemas estructurales**:
  - Múltiples formatos (Excel, CSV)
  - Codificaciones diferentes
  - Estructuras de datos inconsistentes
- **Exploración de datasets de población** (24 archivos por provincia)

**Problemas Identificados** (Issues #1, #2, #13, #14):
- **#1**: Los 8 datasets de dengue tienen distintos IDs y nombres de departamentos
- **#2**: Problemas de codificación UTF-8 en archivos originales
- **#13**: Archivos en formato Excel (.xlsx, .xls) que necesitaban conversión
- **#14**: Filas y columnas vacías, datos duplicados

**Resultado**: Definición de tu responsabilidad específica: crear tabla consolidada de dengue

---

## **SEMANA 4** (26 septiembre - 2 octubre)
### **Primer Intento de Consolidación**

**Actividad Principal**: Creación de tabla de dengue
- **Tu tarea específica**: Crear tabla con casos por semana, año, departamento y edades
- **Herramientas utilizadas**: ChatGPT para estructura y pasos, Cursor para desarrollo
- **Proceso**: Análisis de estructura, planificación de pasos, implementación inicial

**Trabajo Técnico Realizado**:
- **Primer intento de consolidación** de datos
- **Identificación de problemas críticos**:
  - Datos cruzados entre archivos
  - Falta de normalización geográfica
  - Inconsistencias en formatos temporales
  - Nombres de departamentos diferentes entre archivos

**Problemas Enfrentados** (Issues #3, #4, #5, #6, #15):
- **#3**: Nombres inconsistentes entre datasets (ej: "CABA" vs "Ciudad de Buenos Aires")
- **#4**: Registros con valores "desconocido", "sin datos", IDs 999/99
- **#5**: Rangos de edad inconsistentes entre años
- **#6**: Departamentos en datasets no coincidían con lista oficial
- **#15**: Acentos, caracteres especiales, mayúsculas/minúsculas inconsistentes

**Momento de Frustración Principal**:
- Al testear la tabla inicial, descubriste que faltaba normalización
- Había muchos datos cruzados
- Todo era más complicado de lo esperado

**Resultado**: Reconocimiento de la necesidad de normalización previa

---

## **SEMANA 5** (3-9 octubre)
### **Reinicio y Normalización de Dengue**

**Actividad Principal**: Decisión de reiniciar desde cero
- **Decisión crítica**: Borrar todo lo realizado y empezar con normalización
- **Enfoque**: Normalización de tablas de dengue (una por año)
- **Problemas identificados**: Casos nulos, vacíos, formatos distintos, nombres de departamentos diferentes

**Trabajo Técnico Realizado**:
- **Desarrollo de scripts de normalización básica**:
  - `normalizar_dengue.py` - Normalización específica de archivos de dengue
  - `limpiar_csv.py` - Limpieza general de archivos CSV
  - `normalizar_texto.py` - Normalización de texto específica

**Problemas Técnicos Resueltos** (Issues #2, #4, #14, #15, #16):
- **#2**: Script normalizar_dengue.py para estandarizar codificación
- **#4**: Scripts de identificación y corrección automática de valores desconocidos
- **#14**: Scripts de limpieza automática de filas y columnas vacías
- **#15**: Sistema de normalización de texto con reglas específicas para dengue
- **#16**: Sistema automático de backups numerados

**Solución Clave Implementada**:
- **Extracción de listado oficial de departamentos** de la nación
- **Normalización del listado** como referencia estándar
- **Uso del listado para normalizar** departamentos en datasets de dengue

**Backups Creados**:
- **Carpeta `correcciones automaticas/`** con 8 backups por año
- **Carpeta `desc y sd/`** con 8 backups por año

**Resultado**: Base sólida para normalización geográfica

---

## **SEMANA 6** (10-16 octubre)
### **Normalización de Población e Integración Final**

**Actividad Principal**: Normalización de datos demográficos e integración
- **Normalización de datasets de población** por departamento y provincia
- **Normalización de nombres de columnas**, eliminación de datos vacíos
- **Integración final** de todos los datos en tabla consolidada

**Trabajo Técnico Realizado**:
- **Desarrollo de scripts de normalización de población**:
  - `verificar_y_corregir_partidos.py` - Verificación de consistencia geográfica
  - `verificar_valores_poblacion.py` - Validación de valores demográficos
  - `agregar_poblacion_dengue.py` - Integración de datos demográficos

**Problemas Técnicos Resueltos** (Issues #7, #8, #9, #10, #11, #12, #17, #18, #19):
- **#7**: Sistema de asignación automática de códigos UTA
- **#8**: Verificación y corrección interactiva de nombres de partidos
- **#9**: Verificación y corrección de valores problemáticos en población
- **#10**: Sistema de matching y asignación automática de UTA_ID
- **#11**: Sistema de matching por provincia + departamento + año
- **#12**: Normalización de nombres de columnas entre archivos
- **#17**: Sistema de trazabilidad con columna fila_original
- **#18**: Scripts de verificación cruzada para validar correcciones
- **#19**: Scripts específicos para corrección de capitales

**Sistema de Backups Implementado**:
- **Backups automáticos** antes de cada modificación
- **Organización por tipo** de procesamiento:
  - `correcciones automaticas/` - Backups de limpieza automática
  - `dep y prov/` - Backups de normalización geográfica
  - `desc y sd/` - Backups de normalización de grupos etarios
  - `poblacion/` - Backups de integración demográfica
  - `uta IDs/` - Backups de asignación de códigos

**Problemas Técnicos Resueltos**:
- **Matching geográfico**: Sistema de matching por provincia + departamento + año
- **Validación cruzada**: Verificación entre diferentes fuentes
- **Asignación de códigos UTA**: Identificación única de departamentos
- **Integración de datos**: Merge inteligente de múltiples fuentes

**Momento de Mayor Avance Técnico**:
- **Sistema de matching inteligente** implementado
- **Verificación cruzada automática** entre fuentes
- **Sistema de backups robusto** con trazabilidad completa

**Resultado**: Dataset consolidado con 68,127 registros y 765,848 casos de dengue

---

## **SEMANA 7** (17-23 octubre)
### **Documentación y Decisiones de Modelo**

**Actividad Principal**: Documentación y colaboración en elección de modelo
- **Creación de documentación completa** del proceso
- **Colaboración en decisión de modelo** de machine learning
- **Debates sobre enfoque del modelo**

**Trabajo Técnico Realizado**:
- **Desarrollo de análisis EDA**:
  - `generar_analisis_eda.py` - Generación de análisis exploratorio
  - Reportes en múltiples formatos (Excel, HTML, Markdown)
  - Estadísticas descriptivas por todas las variables

**Debates Técnicos**:
- **Número aproximado de casos** vs valores exactos
- **Filtros por semanas** vs análisis temporal completo
- **Filtros por edades** vs análisis por grupos etarios
- **Variables categóricas** vs numéricas
- **Enfoque del modelo**: Predictivo vs clasificatorio

**Herramientas Utilizadas**:
- **ChatGPT**: Para consultas técnicas y estructuración
- **Cursor**: Para desarrollo y debugging
- **Cloud**: Para procesamiento y almacenamiento

**Resultado Final**:
- **Dataset consolidado**: 68,127 registros con 9 columnas normalizadas
- **Sistema de procesamiento**: 48 scripts automatizados
- **Backups completos**: 168 archivos de respaldo
- **Documentación**: Proceso Senes completo

---

## **RESUMEN DE PROBLEMAS RESUELTOS POR SEMANA**

### **Semana 4 - Identificación de Problemas**:
- **#1**: IDs y nombres inconsistentes entre datasets
- **#2**: Problemas de codificación UTF-8
- **#3**: Nombres inconsistentes de departamentos y provincias
- **#4**: Valores desconocidos y sin datos
- **#5**: Inconsistencias en grupos etarios
- **#13**: Conversión de formatos Excel
- **#14**: Limpieza de datos
- **#15**: Normalización de texto

### **Semana 5 - Normalización Básica**:
- **#2**: Scripts de normalización de codificación
- **#4**: Scripts de corrección automática de valores problemáticos
- **#14**: Scripts de limpieza automática
- **#15**: Sistema de normalización de texto
- **#16**: Sistema de backups automáticos

### **Semana 6 - Integración Completa**:
- **#6**: Matching de departamentos con lista oficial
- **#7**: Asignación de códigos UTA 2020
- **#8**: Inconsistencias en nombres de partidos
- **#9**: Valores problemáticos en datos de población
- **#10**: Asignación de UTA_ID a archivos de población
- **#11**: Matching de población con datos de dengue
- **#12**: Inconsistencias en estructura de columnas
- **#17**: Trazabilidad de cambios
- **#18**: Verificación de consistencia
- **#19**: Corrección de capitales

---

## **DETALLE DE ISSUES TÉCNICOS RESUELTOS**

### **Issue #1: Problemas con IDs**
- **Problema**: Los 8 dataset de dengue, del 18 al 25, tienen distintos id y distintos nombres (abreviaturas) de departamentos y provincias
- **Solución**: Sistema de normalización y matching con lista oficial
- **Scripts**: `verificar_departamentos_provincias.py`, `crear_columna_uta_id.py`

### **Issue #2: Problemas de Codificación y Formato**
- **Problema**: Archivos originales con problemas de codificación UTF-8
- **Solución**: Script normalizar_dengue.py para estandarizar codificación
- **Evidencia**: Múltiples archivos .xlsx y .csv con caracteres especiales

### **Issue #3: Inconsistencias en Nombres de Departamentos y Provincias**
- **Problema**: Nombres inconsistentes entre datasets (ej: "CABA" vs "Ciudad de Buenos Aires")
- **Solución**: Sistema de verificación y corrección interactiva
- **Scripts**: `verificar_departamentos_provincias.py`, `normalizar_departamentos.py`
- **Backups**: Carpeta dep y prov/ con 8 backups por año

### **Issue #4: Valores Desconocidos y Sin Datos**
- **Problema**: Registros con valores "desconocido", "sin datos", IDs 999/99
- **Solución**: Scripts de identificación y corrección automática/interactiva
- **Scripts**: `identificar_problemas.py`, `exportar_problemas.py`, `corregir_problemas_automatico.py`
- **Backups**: Carpeta desc y sd/ con 8 backups por año

### **Issue #5: Inconsistencias en Grupos Etarios**
- **Problema**: Rangos de edad inconsistentes entre años (ej: "de 10 a 14" vs "de 15 a 19")
- **Solución**: Normalización específica por año
- **Scripts**: `normalizar_grupos_edad.py`, `corregir_grupos_edad_2020.py`
- **Backups**: Carpeta correcciones automaticas/ con 8 backups por año

### **Issue #6: Matching de Departamentos con Lista Oficial**
- **Problema**: Departamentos en datasets de dengue no coincidían con lista oficial
- **Solución**: Sistema de matching estricto con sugerencias inteligentes
- **Scripts**: `verificar_departamentos_provincias.py` con lógica de sugerencias
- **Referencia**: lista-departamentos.csv como fuente de verdad

### **Issue #7: Asignación de Códigos UTA 2020**
- **Problema**: Falta de identificadores únicos para departamentos
- **Solución**: Sistema de asignación automática de códigos UTA
- **Scripts**: `crear_columna_uta_id.py`, `verificar_uta_id_presente.py`, `verificar_uta_id_correcto.py`
- **Backups**: Carpeta uta IDs/ con 8 backups por año

### **Issue #8: Inconsistencias en Nombres de Partidos**
- **Problema**: Nombres de partidos en archivos de población no coincidían con lista oficial
- **Solución**: Verificación y corrección interactiva por provincia
- **Scripts**: `verificar_y_corregir_partidos.py`, `normalizar_nombres_departamentos.py`
- **Backups**: 3 iteraciones de backup (back1/, back2/, back3/)

### **Issue #9: Valores Problemáticos en Datos de Población**
- **Problema**: Valores nulos, no numéricos, negativos en datos de población
- **Solución**: Verificación y corrección de valores
- **Scripts**: `verificar_valores_poblacion.py`, `convertir_a_enteros.py`
- **Backups**: 2 backups con timestamp en revision valores/

### **Issue #10: Asignación de UTA_ID a Archivos de Población**
- **Problema**: Falta de códigos UTA en archivos de población
- **Solución**: Sistema de matching y asignación automática
- **Scripts**: `agregar_uta_id_poblacion.py`, `eliminar_todas_uta_id.py`

### **Issue #11: Matching de Población con Datos de Dengue**
- **Problema**: Dificultad para integrar datos demográficos con epidemiológicos
- **Solución**: Sistema de matching por provincia + departamento + año
- **Scripts**: `agregar_poblacion_dengue.py`, `eliminar_columna_poblacion.py`
- **Backups**: Carpeta poblacion/back1/ con 8 archivos

### **Issue #12: Inconsistencias en Estructura de Columnas**
- **Problema**: Columnas con nombres diferentes entre archivos
- **Solución**: Normalización de nombres de columnas
- **Scripts**: `corregir_columnas.py`, `verificar_columnas.py`, `eliminar_columnas.py`

### **Issue #13: Conversión de Formatos**
- **Problema**: Archivos en formato Excel (.xlsx, .xls) que necesitaban conversión
- **Solución**: Script de conversión automática
- **Scripts**: `convertir_excel_a_csv.py`

### **Issue #14: Limpieza de Datos**
- **Problema**: Filas y columnas vacías, datos duplicados
- **Solución**: Scripts de limpieza automática
- **Scripts**: `limpiar_csv.py`, `normalizar_texto.py`

### **Issue #15: Normalización de Texto**
- **Problema**: Acentos, caracteres especiales, mayúsculas/minúsculas inconsistentes
- **Solución**: Sistema de normalización de texto
- **Scripts**: `normalizar_texto.py` con reglas específicas para dengue

### **Issue #16: Gestión de Backups**
- **Problema**: Necesidad de preservar versiones anteriores durante correcciones
- **Solución**: Sistema automático de backups numerados
- **Estructura**: Backups organizados por tipo de procesamiento

### **Issue #17: Trazabilidad de Cambios**
- **Problema**: Necesidad de rastrear origen de cada dato
- **Solución**: Columna fila_original y sistema de referencias
- **Implementación**: Mantenimiento de vínculos con archivos fuente

### **Issue #18: Verificación de Consistencia**
- **Problema**: Necesidad de validar correcciones automáticas
- **Solución**: Scripts de verificación cruzada
- **Scripts**: `verificar_consistencia_dengue_departamentos.py`, `verificar_uta_id_correcto.py`

### **Issue #19: Corrección de Capitales**
- **Problema**: Nombres de capitales inconsistentes
- **Solución**: Scripts específicos para capitales
- **Scripts**: `corregir_capitales.py`, `corregir_capitales_dengue.py`, `normalizar_capital.py`

---

## **RESUMEN DE LOGROS TÉCNICOS**

### **Problemas Principales Resueltos** (19 issues identificados y resueltos):
1. **Inconsistencias de formato** entre 12 archivos de dengue
2. **Problemas de codificación** en múltiples archivos
3. **Nombres geográficos inconsistentes** entre fuentes
4. **Datos faltantes y problemáticos** en múltiples formatos
5. **Integración de fuentes múltiples** (dengue + población + geografía)

### **Soluciones Técnicas Implementadas**:
1. **Sistema de normalización en múltiples niveles**
2. **Detección automática de codificación**
3. **Sistema de matching inteligente**
4. **Backups automáticos con trazabilidad**
5. **Verificación cruzada entre fuentes**

### **Resultados Cuantitativos**:
- **68,127 registros** procesados exitosamente
- **765,848 casos de dengue** integrados
- **429 departamentos únicos** normalizados
- **24 provincias + CABA** cubiertas
- **8 años de datos** (2018-2025) consolidados

### **Sistema de Procesamiento Desarrollado**:
- **48 scripts** de procesamiento automatizado
- **168 archivos de backup** preservando historial
- **Sistema de verificación interactiva** para casos complejos
- **Documentación completa** de todos los procesos

---

## **CONCLUSIONES**

Este proyecto representa un trabajo técnico excepcional que demuestra la capacidad para:

- **Identificar y resolver problemas complejos** de calidad de datos
- **Desarrollar soluciones innovadoras** para integración de fuentes múltiples
- **Implementar sistemas robustos** de procesamiento y verificación
- **Mantener trazabilidad completa** de todos los cambios realizados
- **Crear un sistema escalable** para futuras actualizaciones de datos

El desarrollo cronológico muestra una evolución natural desde la ideación hasta la implementación técnica, con momentos de frustración que llevaron a decisiones críticas de reinicio y enfoque en la normalización como base fundamental del proyecto.

---

**Desarrollado para análisis epidemiológico de dengue en Argentina**  
*Sistema de procesamiento y normalización de datos de vigilancia epidemiológica*

**Última actualización**: Septiembre 2025  
**Estado**: ✅ Proyecto completado exitosamente
