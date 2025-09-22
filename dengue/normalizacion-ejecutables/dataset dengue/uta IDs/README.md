# Generador y Verificador de Códigos UTA ID - Datasets Dengue

## Descripción
Esta carpeta contiene scripts para crear, verificar y validar la columna `departamento_id_uta_2020` en los datasets de dengue, basándose en los códigos UTA 2020 del archivo de referencia `lista-departamentos.csv`.

## Scripts disponibles

### 1. `crear_columna_uta_id.py`
**Propósito**: Crea la columna `departamento_id_uta_2020` en los datasets de dengue.

**Funcionalidades**:
- Carga el archivo de referencia `lista-departamentos.csv`
- Hace match entre `departamento_nombre` + `provincia_nombre` del dataset de dengue con `Nombre` + `Provincia` del archivo de referencia
- Asigna el `Código UTA 2020` correspondiente
- Crea backups automáticos en `/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/uta IDs`
- Proporciona estadísticas de mapeo
- Permite procesar todos los archivos o uno específico

**Uso**:
```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/uta IDs"
python crear_columna_uta_id.py
```

### 2. `verificar_uta_id_presente.py`
**Propósito**: Verifica que todos los datasets de dengue tengan la columna `departamento_id_uta_2020`.

**Funcionalidades**:
- Verifica la presencia de la columna en todos los archivos
- Proporciona estadísticas de cobertura (cuántos registros tienen ID asignado)
- Genera reporte detallado con porcentajes
- Exporta reporte a CSV
- Identifica archivos que necesitan procesamiento

**Uso**:
```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/uta IDs"
python verificar_uta_id_presente.py
```

### 3. `verificar_uta_id_correcto.py`
**Propósito**: Verifica que los códigos UTA ID asignados sean correctos según el archivo de referencia.

**Funcionalidades**:
- Compara cada código UTA ID con el código correcto del archivo de referencia
- Identifica registros con códigos incorrectos
- Proporciona detalles de errores (fila, departamento, provincia, código actual vs correcto)
- Genera reporte detallado de precisión
- Exporta errores a CSV para corrección manual

**Uso**:
```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/uta IDs"
python verificar_uta_id_correcto.py
```

## Flujo de trabajo recomendado

### 1. Crear columnas UTA ID
```bash
python crear_columna_uta_id.py
```
- Selecciona "1" para procesar todos los archivos
- Revisa las estadísticas de mapeo
- Los backups se crean automáticamente

### 2. Verificar cobertura
```bash
python verificar_uta_id_presente.py
```
- Confirma que todos los archivos tengan la columna
- Revisa el porcentaje de registros mapeados
- Identifica archivos problemáticos

### 3. Validar precisión
```bash
python verificar_uta_id_correcto.py
```
- Verifica que los códigos sean correctos
- Revisa errores detallados
- Exporta errores para corrección si es necesario

## Características técnicas

### Normalización de texto
Todos los scripts normalizan automáticamente:
- Elimina acentos y caracteres especiales
- Convierte a minúsculas
- Elimina espacios extra
- Maneja caracteres especiales (ñ, ü, etc.)

### Matching
- **Coincidencia exacta**: `departamento_nombre` + `provincia_nombre` del dataset de dengue
- **Referencia**: `Nombre` + `Provincia` de `lista-departamentos.csv`
- **Resultado**: Asignación del `Código UTA 2020` correspondiente

### Backups
- **Ubicación**: `/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/uta IDs`
- **Formato**: `backup_dengue-YYYY.csv`
- **Creación**: Automática antes de modificar archivos

### Reportes
- **Estadísticas detalladas**: Total de registros, mapeados, sin mapear
- **Porcentajes de cobertura**: Porcentaje de registros con ID asignado
- **Errores específicos**: Fila, departamento, provincia, códigos actual vs correcto
- **Exportación CSV**: Para análisis posterior

## Archivos de salida

### Reportes generados
- `reporte_uta_id_YYYYMMDD_HHMMSS.csv`: Reporte de cobertura
- `errores_uta_id_YYYYMMDD_HHMMSS.csv`: Lista detallada de errores

### Backups
- `backup_dengue-YYYY.csv`: Copias de seguridad de archivos originales

## Requisitos
- Python 3.6+
- pandas
- Archivo de referencia: `/Users/ignaciosenestrari/Facu/tp-dengue/dataset-departamentos/lista-departamentos.csv`
- Datasets de dengue: `/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/dengue-*.csv`

## Estructura de archivos
```
uta IDs/
├── crear_columna_uta_id.py
├── verificar_uta_id_presente.py
├── verificar_uta_id_correcto.py
├── README.md
└── reportes/ (generados automáticamente)
    ├── reporte_uta_id_*.csv
    └── errores_uta_id_*.csv
```

## Ejemplo de uso completo

```bash
# 1. Crear columnas UTA ID
python crear_columna_uta_id.py
# Seleccionar opción 1 (procesar todos)
# Revisar estadísticas

# 2. Verificar cobertura
python verificar_uta_id_presente.py
# Revisar reporte de cobertura
# Exportar reporte si es necesario

# 3. Validar precisión
python verificar_uta_id_correcto.py
# Revisar reporte de precisión
# Exportar errores si es necesario
```

## Solución de problemas

### Registros sin mapear
- Verificar nombres de departamentos y provincias
- Revisar normalización de texto
- Considerar correcciones manuales en el archivo de referencia

### Códigos incorrectos
- Re-ejecutar `crear_columna_uta_id.py`
- Verificar cambios en el archivo de referencia
- Revisar normalización de texto

### Archivos sin columna UTA ID
- Ejecutar `crear_columna_uta_id.py`
- Verificar permisos de escritura
- Revisar estructura de archivos CSV
