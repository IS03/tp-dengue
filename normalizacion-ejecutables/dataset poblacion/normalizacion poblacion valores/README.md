# Verificador de Valores - Datasets de Población

## Descripción
Script para verificar valores extraños, nulos, vacíos y desconocidos en todos los datasets de población de la provincia.

## Características
- ✅ **Backup automático**: Crea backup antes de ejecutar
- ✅ **Verificación completa**: Revisa todos los archivos CSV del directorio
- ✅ **Modo interactivo**: Permite revisar problemas encontrados
- ✅ **Ignora columna A**: No verifica nombres de departamentos/comunas/partidos
- ✅ **Reporte detallado**: Muestra archivo, línea, columna y motivo del problema

## Tipos de Problemas Detectados
- Valores nulos (NaN)
- Valores vacíos o espacios en blanco
- Valores no numéricos donde deberían ser números
- Valores no enteros (población debe ser entera)
- Valores negativos
- Valores desconocidos: "desconocido", "sin datos", "N/A", "?", etc.

## Uso

### Ejecutar desde terminal:
```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/normalizacion poblacion"
python3 verificar_valores_poblacion.py
```

### O ejecutar directamente:
```bash
python3 "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/normalizacion poblacion/verificar_valores_poblacion.py"
```

## Flujo de Trabajo
1. **Backup**: Crea backup automático en `dataset-poblacion/backup/automatico/revision valores/`
2. **Verificación**: Revisa todos los archivos CSV del directorio
3. **Reporte**: Muestra resumen de problemas encontrados
4. **Interactivo**: Permite revisar cada problema individualmente

## Opciones Interactivas
Cuando encuentra problemas, puedes:
- **Saltar**: Ignorar el problema actual
- **Ver detalles**: Mostrar información completa del archivo
- **Terminar**: Salir de la verificación

## Estructura de Archivos
```
dataset-poblacion/
├── buenos aires.csv
├── caba.csv
├── cordoba.csv
└── ... (otros archivos)

backup/automatico/revision valores/
└── backup_YYYYMMDD_HHMMSS/
    ├── buenos aires.csv
    ├── caba.csv
    └── ... (copias de seguridad)
```

## Requisitos
- Python 3.6+
- pandas
- Acceso de escritura al directorio de backup

## Notas Importantes
- El script **ignora la primera columna** (nombres de departamentos/comunas/partidos)
- Solo verifica las columnas de años (2018-2025) que contienen valores de población
- Los backups se crean con timestamp para evitar sobrescribir
- El script es seguro: no modifica archivos originales, solo crea backups
