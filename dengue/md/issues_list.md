# Problemas con IDs #1

Los 8 dataset de dengue, del 18 al 25, tienen distintos id y distintos nombres (abreviaturas) de departamentos y provincias.


# Problemas de Codificación y Formato **#2**

* Issue: Archivos originales con problemas de codificación UTF-8
* Solución: Script normalizar_dengue.py para estandarizar codificación
* Evidencia: Múltiples archivos .xlsx y .csv con caracteres especiales


# Inconsistencias en Nombres de Departamentos y Provincias **#3**

* Issue: Nombres inconsistentes entre datasets (ej: "CABA" vs "Ciudad de Buenos Aires")
* Solución: Sistema de verificación y corrección interactiva
* Scripts: verificar_departamentos_provincias.py, normalizar_departamentos.py
* Backups: Carpeta dep y prov/ con 8 backups por año


# Valores Desconocidos y Sin Datos **#4**

* Issue: Registros con valores "desconocido", "sin datos", IDs 999/99
* Solución: Scripts de identificación y corrección automática/interactiva
* Scripts: identificar_problemas.py, exportar_problemas.py, corregir_problemas_automatico.py
* Backups: Carpeta desc y sd/ con 8 backups por año



# Inconsistencias en Grupos Etarios **#5**

* Issue: Rangos de edad inconsistentes entre años (ej: "de 10 a 14" vs "de 15 a 19")
* Solución: Normalización específica por año
* Scripts: normalizar_grupos_edad.py, corregir_grupos_edad_2020.py
* Backups: Carpeta correcciones automaticas/ con 8 backups por año


# Matching de Departamentos con Lista Oficial **#6**

* Issue: Departamentos en datasets de dengue no coincidían con lista oficial
* Solución: Sistema de matching estricto con sugerencias inteligentes
* Scripts: verificar_departamentos_provincias.py con lógica de sugerencias
* Referencia: lista-departamentos.csv como fuente de verdad


# Asignación de Códigos UTA 2020 **#7**

* Issue: Falta de identificadores únicos para departamentos
* Solución: Sistema de asignación automática de códigos UTA
* Scripts: crear_columna_uta_id.py, verificar_uta_id_presente.py, verificar_uta_id_correcto.py
* Backups: Carpeta uta IDs/ con 8 backups por año



# Inconsistencias en Nombres de Partidos **#8**

* Issue: Nombres de partidos en archivos de población no coincidían con lista oficial
* Solución: Verificación y corrección interactiva por provincia
* Scripts: verificar_y_corregir_partidos.py, normalizar_nombres_departamentos.py
* Backups: 3 iteraciones de backup (back1/, back2/, back3/)


# Valores Problemáticos en Datos de Población **#9**

* Issue: Valores nulos, no numéricos, negativos en datos de población
* Solución: Verificación y corrección de valores
* Scripts: verificar_valores_poblacion.py, convertir_a_enteros.py
* Backups: 2 backups con timestamp en revision valores/


# Asignación de UTA_ID a Archivos de Población **#10**

* Issue: Falta de códigos UTA en archivos de población
* Solución: Sistema de matching y asignación automática
* Scripts: agregar_uta_id_poblacion.py, eliminar_todas_uta_id.py


# Matching de Población con Datos de Dengue **#11**

* Issue: Dificultad para integrar datos demográficos con epidemiológicos
* Solución: Sistema de matching por provincia + departamento + año
* Scripts: agregar_poblacion_dengue.py, eliminar_columna_poblacion.py
* Backups: Carpeta poblacion/back1/ con 8 archivos


# Inconsistencias en Estructura de Columnas **#12**

* Issue: Columnas con nombres diferentes entre archivos
* Solución: Normalización de nombres de columnas
* Scripts: corregir_columnas.py, verificar_columnas.py, eliminar_columnas.py


# Conversión de Formatos **#13**

* Issue: Archivos en formato Excel (.xlsx, .xls) que necesitaban conversión
* Solución: Script de conversión automática
* Scripts: convertir_excel_a_csv.py


# Limpieza de Datos **#14**

* Issue: Filas y columnas vacías, datos duplicados
* Solución: Scripts de limpieza automática
* Scripts: limpiar_csv.py, normalizar_texto.py


# Normalización de Texto **#15**

* Issue: Acentos, caracteres especiales, mayúsculas/minúsculas inconsistentes
* Solución: Sistema de normalización de texto
* Scripts: normalizar_texto.py con reglas específicas para dengue


# Gestión de Backups **#16**

* Issue: Necesidad de preservar versiones anteriores durante correcciones
* Solución: Sistema automático de backups numerados
* Estructura: Backups organizados por tipo de procesamiento


# Trazabilidad de Cambios **#17**

* Issue: Necesidad de rastrear origen de cada dato
* Solución: Columna fila_original y sistema de referencias
* Implementación: Mantenimiento de vínculos con archivos fuente


# Verificación de Consistencia **#18**

* Issue: Necesidad de validar correcciones automáticas
* Solución: Scripts de verificación cruzada
* Scripts: verificar_consistencia_dengue_departamentos.py, verificar_uta_id_correcto.py


# Corrección de Capitales **#19**

* Issue: Nombres de capitales inconsistentes
* Solución: Scripts específicos para capitales
* Scripts: corregir_capitales.py, corregir_capitales_dengue.py, normalizar_capital.py
