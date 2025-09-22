# Verificador de Departamentos y Provincias - Datasets Dengue

## Descripción
Este script verifica y corrige discrepancias entre los nombres de departamentos y provincias en los datasets de dengue comparándolos con el archivo de referencia `lista-departamentos.csv`.

## Características principales

### ✅ **Fuente de verdad**
- El archivo `lista-departamentos.csv` es la referencia oficial
- Los datasets de dengue se adaptan a este índice

### 🔍 **Tipos de discrepancias detectadas**
1. **Ambos nombres vacíos**: Tanto departamento como provincia están vacíos
2. **Departamento vacío**: Solo el departamento está vacío
3. **Provincia vacía**: Solo la provincia está vacía
4. **Departamento no encontrado**: El departamento no existe en la referencia (después de verificar sugerencias)
5. **Provincia no coincide**: El departamento existe pero la provincia es diferente (después de verificar todas las coincidencias)

### 🧠 **Lógica inteligente de verificación**
- **Coincidencia exacta**: Si encuentra departamento + provincia exactos, no muestra error
- **Verificación de sugerencias**: Si el departamento no existe, verifica si alguna sugerencia similar coincide con la provincia
- **Múltiples departamentos**: Si hay varios departamentos con el mismo nombre, verifica si alguno coincide con la provincia
- **Solo errores reales**: Solo muestra como error cuando realmente no hay coincidencia posible

### 📍 **Información de ubicación**
- **Número de fila CSV**: Muestra la fila exacta donde está el error en el archivo CSV original
- **ID de departamento**: Identificador único del departamento
- **Nombres originales**: Los nombres tal como aparecen en el dataset

### 🎯 **Coincidencias**
- **Solo por nombre**: Compara `departamento_nombre` + `provincia_nombre` con `Nombre` + `Provincia`
- **Ignora IDs**: No considera códigos UTA ni IDs de departamento

## Uso

### Ejecutar el script
```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/normalizacion departamentos y provincias"
python verificar_departamentos_provincias.py
```

### Flujo de trabajo
1. **Seleccionar año**: Elige el año específico a procesar
2. **Revisar discrepancias**: El script muestra todas las discrepancias encontradas
3. **Decidir corrección**: Confirma si deseas corregir las discrepancias
4. **Backup automático**: Se crea backup antes de modificar
5. **Corrección interactiva**: Corrige una discrepancia a la vez con opciones claras
6. **Guardar cambios**: Confirma si deseas guardar los cambios

### Opciones de corrección
Para cada discrepancia puedes:
- **Corregir manualmente**: Escribir el nombre correcto
- **Usar sugerencias**: Aplicar correcciones automáticas cuando están disponibles
- **Borrar registros**: Eliminar todos los registros del departamento problemático
- **Saltear**: Mantener como está

## Archivos de backup
Los backups se guardan en:
```
/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/dep y prov/
```

## Normalización de texto
El script normaliza automáticamente:
- Elimina acentos
- Convierte a minúsculas
- Elimina espacios extra
- Maneja caracteres especiales

## Sugerencias inteligentes
Para nombres no encontrados, el script ofrece sugerencias basadas en:
- Coincidencias parciales
- Similitud de texto
- Máximo 5 sugerencias por discrepancia

## Años disponibles
El script detecta automáticamente los archivos disponibles:
- dengue-2018.csv
- dengue-2019.csv
- dengue-2020.csv
- dengue-2021.csv
- dengue-2022.csv
- dengue-2023.csv
- dengue-2024.csv
- dengue-2025.csv

## Requisitos
- Python 3.6+
- pandas
- unicodedata (incluido en Python)
- difflib (incluido en Python)
- re (incluido en Python)

## Estructura de archivos
```
normalizacion departamentos y provincias/
├── verificar_departamentos_provincias.py
└── README.md
```

## Ejemplo de uso
```
Verificador de Departamentos y Provincias - Datasets Dengue
======================================================================
El archivo lista-departamentos.csv es la fuente de verdad
Los datasets de dengue se adaptaran a este indice
COINCIDENCIAS: Solo por nombre (departamento + provincia)
INCLUYE: Nombres vacios como discrepancias
======================================================================
[OK] Archivo de referencia cargado: 531 departamentos
Años disponibles: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025

==================================================
OPCIONES:
1. Procesar un año específico
2. Salir

Seleccione una opcion (1-2): 1

Años disponibles: 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025
Ingrese el año a procesar: 2018

[INFO] Procesando año 2018...
[OK] Archivo de referencia cargado: 531 departamentos
[OK] Dataset cargado: 919 registros
[INFO] Analizando 45 departamentos únicos...

[WARNING] Año 2018: Se encontraron 3 discrepancias:
================================================================================

1. Departamento No Encontrado
   ID: 12345
   Fila CSV: 15
   Departamento: nombre_incorrecto
   Provincia: buenos aires
   Sugerencias: nombre_correcto1, nombre_correcto2

2. Provincia No Coincide
   ID: 67890
   Fila CSV: 23
   Departamento: la plata
   Provincia: provincia_incorrecta
   Provincia correcta: buenos aires

3. Departamento Vacio
   ID: 11111
   Fila CSV: 45
   Departamento: [VACIO]
   Provincia: santa fe

¿Desea corregir las discrepancias del año 2018? (s/n): s
```
