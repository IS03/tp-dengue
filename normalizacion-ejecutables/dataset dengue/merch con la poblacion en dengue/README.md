# Agregador de Población a Archivos de Dengue

Este script agrega la columna "poblacion" al final de los archivos CSV de dengue, obteniendo los valores de los archivos de población según provincia, departamento y año.

## Funcionalidades

### Procesamiento
- Agrega columna "poblacion" al final de cada archivo CSV de dengue
- Matching: provincia_nombre + departamento_nombre + año
- Obtiene valores de los archivos de población correspondientes

### Backup Automático
- Crea backups automáticos antes de cualquier modificación
- Sistema de numeración: back1, back2, back3, etc.
- Los backups se guardan en: `dataset-dengue/backup/backup automatico/poblacion/`

### Manejo de Errores
- Reporta errores detallados en terminal
- Muestra estadísticas por provincia
- Verifica existencia de archivos de población

## Uso

```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/dataset dengue/merch con la poblacion en dengue"
python3 agregar_poblacion_dengue.py
```

## Menú Principal

1. **Procesar todos los archivos de dengue**: Ejecuta el procesamiento completo
2. **Mostrar resumen por archivo**: Muestra estadísticas por archivo
3. **Mostrar errores detallados**: Lista todos los errores con detalles
4. **Mostrar estadísticas por provincia**: Agrupa errores por provincia
5. **Verificar archivo de población**: Verifica si existe archivo de población
6. **Incrementar contador de backup**: Cambia el número de backup
7. **Salir**: Termina el programa

## Lógica de Matching

### Ejemplo de Procesamiento:
```
Archivo dengue: dengue-2018.csv
Fila: provincia_nombre="buenos aires", departamento_nombre="avellaneda", ano="2018"
↓
Archivo población: buenos aires.csv
Buscar: "avellaneda" en columna "Partido"
Año: 2018
↓
Resultado: poblacion = valor de la columna "2018" = 354314
```

### Estructura del Archivo Resultante:
```csv
provincia_nombre,departamento_nombre,año,...,poblacion
buenos aires,avellaneda,2018,...,354314
```

## Columnas Requeridas en Archivos de Dengue

El script requiere que los archivos de dengue tengan estas columnas:
- `provincia_nombre`: Nombre de la provincia
- `departamento_nombre`: Nombre del departamento/partido
- `ano`: Año de los datos

## Tipos de Errores

### Población No Encontrada
- No se encuentra la combinación provincia + departamento + año
- Se deja la columna población vacía
- Se reporta el error

### Columnas Faltantes
- No se encuentran las columnas requeridas en el archivo de dengue
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
dataset-dengue/backup/backup automatico/poblacion/
├── back1/
│   ├── dengue-2018.csv
│   ├── dengue-2019.csv
│   └── ...
├── back2/
│   ├── dengue-2018.csv
│   └── ...
```

## Ejemplo de Uso

1. Ejecutar el script
2. Seleccionar opción 1 para procesar archivos
3. Ver resumen de procesamiento
4. Seleccionar opción 3 para ver errores detallados
5. Seleccionar opción 4 para ver estadísticas por provincia
6. Seleccionar opción 5 para verificar archivos de población

## Notas Importantes

- **Matching Estricto**: La combinación provincia + departamento + año debe existir exactamente
- **Backup Automático**: Siempre se crean backups antes de modificar
- **Columna al Final**: población se agrega como última columna
- **Detección Automática**: Detecta si la columna se llama "Partido" o "Departamento"
- **Verificación de Archivos**: Permite verificar si existen archivos de población para cada provincia
