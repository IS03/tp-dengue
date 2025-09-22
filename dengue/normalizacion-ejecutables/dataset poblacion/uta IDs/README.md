# Agregador de UTA_ID a Archivos de Población

Este script agrega la columna "UTA_ID" al principio de los archivos CSV de población, basándose en el "Código UTA 2020" de `lista-departamentos.csv`.

## Funcionalidades

### Procesamiento
- Agrega columna "UTA_ID" al principio de cada archivo CSV
- Matching estricto: Nombre del partido + Provincia del archivo
- Obtiene el UTA_ID del "Código UTA 2020" de `lista-departamentos.csv`

### Backup Automático
- Crea backups automáticos antes de cualquier modificación
- Sistema de numeración: back1, back2, back3, etc.
- Los backups se guardan en: `dataset-poblacion/backup/automatico/revision partidos/`

### Manejo de Errores
- Reporta errores detallados en terminal
- Exporta errores a archivo CSV
- Muestra sugerencias para partidos no encontrados

## Uso

```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/normalizacion poblacion/uta IDs"
python3 agregar_uta_id_poblacion.py
```

## Menú Principal

1. **Procesar todos los archivos**: Ejecuta el procesamiento completo
2. **Mostrar resumen por archivo**: Muestra estadísticas por archivo
3. **Mostrar errores detallados**: Lista todos los errores con detalles
4. **Ver sugerencias para un partido**: Busca partidos similares
5. **Exportar errores a CSV**: Guarda errores en archivo
6. **Incrementar contador de backup**: Cambia el número de backup
7. **Salir**: Termina el programa

## Lógica de Matching

### Ejemplo de Procesamiento:
```
Archivo: buenos aires.csv
Partido: "avellaneda"
↓
Buscar en lista-departamentos.csv:
- Nombre = "avellaneda"
- Provincia = "buenos aires"
↓
Obtener: Código UTA 2020 = "6035"
↓
Resultado: UTA_ID = "6035"
```

### Estructura del Archivo Resultante:
```csv
UTA_ID,Partido,2018,2019,2020,2021,2022,2023,2024,2025
6035,avellaneda,354314,355352,356392,357440,358512,359550,360583,361532
```

**Nota**: El script detecta automáticamente si la columna se llama "Partido" (Buenos Aires) o "Departamento" (otras provincias).

## Tipos de Errores

### UTA_ID No Encontrado
- El partido no existe en esa provincia específica
- Se deja la columna UTA_ID vacía
- Se reporta el error

### Columna Faltante
- No se encuentra la columna "Partido" ni "Departamento" en el archivo
- Se reporta el error y se omite el archivo

### Error de Procesamiento
- Errores técnicos al procesar el archivo
- Se reporta el error específico

## Sistema de Backups

### Numeración Automática:
- Primera ejecución: `back1/`
- Segunda ejecución: `back2/`
- Tercera ejecución: `back3/`
- etc.

### Estructura de Backup:
```
dataset-poblacion/backup/automatico/revision partidos/
├── back1/
│   ├── buenos aires.csv
│   ├── catamarca.csv
│   └── ...
├── back2/
│   ├── buenos aires.csv
│   └── ...
└── errores_uta_id_YYYYMMDD_HHMMSS.csv
```

## Ejemplo de Uso

1. Ejecutar el script
2. Seleccionar opción 1 para procesar archivos
3. Ver resumen de procesamiento
4. Seleccionar opción 3 para ver errores detallados
5. Seleccionar opción 4 para buscar sugerencias
6. Seleccionar opción 5 para exportar errores

## Notas Importantes

- **Matching Estricto**: El partido debe existir exactamente en esa provincia
- **Backup Automático**: Siempre se crean backups antes de modificar
- **Columna al Principio**: UTA_ID se agrega como primera columna
- **Manejo de Duplicados**: Partidos con mismo nombre en diferentes provincias se manejan correctamente
- **Exportación de Errores**: Los errores se pueden exportar para análisis posterior
