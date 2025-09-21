# Verificador y Corregidor de Partidos

Este script verifica la consistencia entre los archivos CSV de población y la lista de departamentos, permitiendo corregir errores de forma interactiva.

## Funcionalidades

### Verificación
- Verifica que cada partido en los CSV de población exista en `lista-departamentos.csv`
- Verifica que la provincia del partido coincida con el nombre del archivo CSV
- Genera reportes detallados de errores encontrados

### Corrección Interactiva
- **Cambiar nombre del partido**: Permite corregir nombres incorrectos
- **Eliminar fila**: Elimina filas con datos incorrectos
- **Ver sugerencias**: Muestra partidos similares para facilitar la corrección

### Backup Automático
- Crea backups automáticos antes de cualquier modificación
- Los backups se guardan en: `dataset-poblacion/backup/automatico/revision partidos/`

## Uso

```bash
cd "/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/dataset poblacion/normalizacion poblacion departamentos"
python3 verificar_y_corregir_partidos.py
```

## Menú Principal

1. **Verificar todos los archivos**: Ejecuta la verificación completa
2. **Mostrar resumen de errores**: Muestra estadísticas de errores
3. **Mostrar errores detallados**: Lista todos los errores con detalles
4. **Corregir error específico**: Permite corregir errores uno por uno
5. **Salir**: Termina el programa

## Tipos de Errores Detectados

### Partido No Existe
- El partido no se encuentra en `lista-departamentos.csv`
- Opciones de corrección:
  - Cambiar nombre del partido
  - Ver sugerencias de nombres similares
  - Eliminar la fila

### Provincia Incorrecta
- El partido existe pero pertenece a una provincia diferente
- Opciones de corrección:
  - Cambiar nombre del partido
  - Eliminar la fila

## Estructura de Archivos

```
dataset-poblacion/
├── *.csv (archivos de población)
└── backup/
    └── automatico/
        └── revision partidos/
            └── backup_YYYYMMDD_HHMMSS/
                └── *.csv (backups)
```

## Ejemplo de Uso

1. Ejecutar el script
2. Seleccionar opción 1 para verificar archivos
3. Seleccionar opción 3 para ver errores detallados
4. Seleccionar opción 4 para corregir errores
5. Elegir el error a corregir
6. Seleccionar el tipo de corrección
7. Confirmar cambios

## Notas Importantes

- Siempre se crean backups antes de modificar archivos
- Los cambios se aplican inmediatamente
- El script mantiene un registro de errores corregidos
- Se pueden corregir múltiples errores en una sesión
