#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades comunes para el ETL de Dengue.
Incluye funciones para encoding, logging, validación y normalización.
"""

import logging
import logging.handlers
import unicodedata
import chardet
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np

from config import ENCODINGS, CSV_SEPARATORS, LOG_CONFIG, ensure_directories

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

def setup_logging(name: str = 'dengue_etl') -> logging.Logger:
    """
    Configura el sistema de logging para el ETL.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    # Asegurar que el directorio de logs existe
    ensure_directories()
    
    # Configurar el logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # Evitar duplicar handlers si ya están configurados
    if logger.handlers:
        return logger
    
    # Formato de logging
    formatter = logging.Formatter(LOG_CONFIG['format'])
    
    # Handler para archivo
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_CONFIG['file'],
        maxBytes=LOG_CONFIG['max_size'],
        backupCount=LOG_CONFIG['backup_count'],
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# =============================================================================
# MANEJO DE ENCODING
# =============================================================================

def detect_encoding(file_path: Path, sample_size: int = 1024) -> str:
    """
    Detecta el encoding de un archivo de texto.
    
    Args:
        file_path: Ruta al archivo
        sample_size: Tamaño de la muestra a leer para detección
        
    Returns:
        Encoding detectado
    """
    try:
        # Leer una muestra del archivo
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        
        # Usar chardet para detectar encoding
        detected = chardet.detect(sample)
        if detected['confidence'] > 0.7:
            encoding = detected['encoding']
            if encoding in ENCODINGS:
                return encoding
        
        # Fallback: probar encodings comunes
        for encoding in ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(sample_size)
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
                
    except Exception as e:
        logging.warning(f"Error detectando encoding para {file_path}: {e}")
    
    # Fallback final
    return 'utf-8'

def detect_csv_separator(file_path: Path, encoding: str = 'utf-8', sample_size: int = 1024) -> str:
    """
    Detecta el separador de un archivo CSV.
    
    Args:
        file_path: Ruta al archivo CSV
        encoding: Encoding del archivo
        sample_size: Tamaño de la muestra a leer
        
    Returns:
        Separador detectado
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            sample = f.read(sample_size)
        
        # Buscar la primera línea que parezca un header
        lines = sample.splitlines()
        if not lines:
            return ','
        
        # Contar separadores en las primeras líneas
        separator_counts = {}
        for line in lines[:3]:  # Revisar primeras 3 líneas
            for sep in CSV_SEPARATORS:
                count = line.count(sep)
                if count > 0:
                    separator_counts[sep] = separator_counts.get(sep, 0) + count
        
        # Retornar el separador más común
        if separator_counts:
            return max(separator_counts, key=separator_counts.get)
        
    except Exception as e:
        logging.warning(f"Error detectando separador para {file_path}: {e}")
    
    return ','  # Fallback

def read_csv_robust(file_path: Path, **kwargs) -> pd.DataFrame:
    """
    Lee un archivo CSV de manera robusta, detectando automáticamente encoding y separador.
    
    Args:
        file_path: Ruta al archivo CSV
        **kwargs: Argumentos adicionales para pd.read_csv
        
    Returns:
        DataFrame leído
    """
    # Detectar encoding y separador
    encoding = detect_encoding(file_path)
    separator = detect_csv_separator(file_path, encoding)
    
    # Configuración por defecto
    default_kwargs = {
        'sep': separator,
        'encoding': encoding,
        'dtype': str,
        'low_memory': False
    }
    
    # Combinar con argumentos proporcionados
    default_kwargs.update(kwargs)
    
    try:
        return pd.read_csv(file_path, **default_kwargs)
    except Exception as e:
        logging.error(f"Error leyendo CSV {file_path}: {e}")
        raise

# =============================================================================
# NORMALIZACIÓN DE TEXTO
# =============================================================================

def strip_accents(text: str) -> str:
    """
    Elimina tildes y caracteres especiales de un texto.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto sin tildes
    """
    if pd.isna(text) or text is None:
        return text
    
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text)) 
                   if unicodedata.category(c) != 'Mn')

def normalize_text(text: str) -> str:
    """
    Normaliza texto: elimina tildes, convierte a mayúsculas y elimina espacios.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if pd.isna(text) or text is None:
        return text
    
    return strip_accents(str(text)).strip().upper()

def normalize_series(series: pd.Series) -> pd.Series:
    """
    Normaliza una serie de pandas aplicando normalize_text.
    
    Args:
        series: Serie a normalizar
        
    Returns:
        Serie normalizada
    """
    return series.apply(normalize_text)

# =============================================================================
# VALIDACIÓN DE DATOS
# =============================================================================

def validate_epidemiological_week(year: int, week: int) -> bool:
    """
    Valida si una semana epidemiológica es válida para un año dado.
    
    Args:
        year: Año
        week: Semana epidemiológica
        
    Returns:
        True si es válida, False en caso contrario
    """
    if not (1 <= week <= 53):
        return False
    
    try:
        # Verificar que la semana existe para ese año
        # Usar formato ISO week
        date_str = f"{year}-W{week:02d}-1"
        pd.to_datetime(date_str, format="%G-W%V-%u")
        return True
    except (ValueError, TypeError):
        return False

def validate_date_range(year: int, week: int = None, date: pd.Timestamp = None) -> bool:
    """
    Valida si una fecha está en el rango permitido.
    
    Args:
        year: Año
        week: Semana epidemiológica (opcional)
        date: Fecha (opcional)
        
    Returns:
        True si es válida, False en caso contrario
    """
    from config import YEAR_MIN, YEAR_MAX
    
    # Validar año
    if not (YEAR_MIN <= year <= YEAR_MAX):
        return False
    
    # Validar semana si se proporciona
    if week is not None and not validate_epidemiological_week(year, week):
        return False
    
    # Validar fecha si se proporciona
    if date is not None:
        if not (YEAR_MIN <= date.year <= YEAR_MAX):
            return False
    
    return True

def validate_geo_consistency(df: pd.DataFrame, geo_map: pd.DataFrame) -> Dict[str, Any]:
    """
    Valida la consistencia geográfica de un DataFrame.
    
    Args:
        df: DataFrame a validar
        geo_map: DataFrame con mapeo geográfico
        
    Returns:
        Diccionario con resultados de validación
    """
    results = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'invalid_provinces': [],
        'invalid_departments': []
    }
    
    # Validar provincias
    if 'provincia_id' in df.columns and 'provincia_id' in geo_map.columns:
        invalid_prov = df[~df['provincia_id'].isin(geo_map['provincia_id'])]
        if not invalid_prov.empty:
            results['invalid_provinces'] = invalid_prov['provincia_id'].unique().tolist()
            results['warnings'].append(f"Provincias inválidas encontradas: {results['invalid_provinces']}")
    
    # Validar departamentos
    if 'departamento_id' in df.columns and 'departamento_id' in geo_map.columns:
        invalid_dept = df[~df['departamento_id'].isin(geo_map['departamento_id'])]
        if not invalid_dept.empty:
            results['invalid_departments'] = invalid_dept['departamento_id'].unique().tolist()
            results['warnings'].append(f"Departamentos inválidos encontrados: {results['invalid_departments']}")
    
    return results

# =============================================================================
# MANEJO DE VALORES FALTANTES
# =============================================================================

def handle_missing_values(df: pd.DataFrame, column: str, strategy: str = 'fill', 
                         fill_value: Any = None) -> pd.DataFrame:
    """
    Maneja valores faltantes en una columna específica.
    
    Args:
        df: DataFrame
        column: Nombre de la columna
        strategy: Estrategia ('fill', 'drop', 'flag')
        fill_value: Valor para llenar (si strategy='fill')
        
    Returns:
        DataFrame modificado
    """
    if column not in df.columns:
        return df
    
    if strategy == 'fill':
        if fill_value is not None:
            df[column] = df[column].fillna(fill_value)
        else:
            # Valor por defecto según el tipo de columna
            if df[column].dtype in ['int64', 'float64']:
                df[column] = df[column].fillna(0)
            else:
                df[column] = df[column].fillna('SIN ESPECIFICAR')
    
    elif strategy == 'drop':
        df = df.dropna(subset=[column])
    
    elif strategy == 'flag':
        df[f'{column}_missing'] = df[column].isna()
        df[column] = df[column].fillna('SIN ESPECIFICAR')
    
    return df

# =============================================================================
# UTILIDADES DE ARCHIVOS
# =============================================================================

def safe_file_operation(operation, file_path: Path, backup: bool = True) -> Any:
    """
    Ejecuta una operación de archivo de manera segura con backup.
    
    Args:
        operation: Función a ejecutar
        file_path: Ruta del archivo
        backup: Si crear backup antes de la operación
        
    Returns:
        Resultado de la operación
    """
    backup_path = None
    
    try:
        # Crear backup si es necesario
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            import shutil
            shutil.copy2(file_path, backup_path)
        
        # Ejecutar operación
        result = operation()
        
        # Limpiar backup si todo salió bien
        if backup_path and backup_path.exists():
            backup_path.unlink()
        
        return result
        
    except Exception as e:
        # Restaurar backup si existe
        if backup_path and backup_path.exists():
            import shutil
            shutil.copy2(backup_path, file_path)
            logging.info(f"Backup restaurado: {backup_path} -> {file_path}")
        
        raise e

# =============================================================================
# UTILIDADES DE ESTADÍSTICAS
# =============================================================================

def calculate_incidence(cases: pd.Series, population: pd.Series, 
                       per_100k: int = 100000) -> pd.Series:
    """
    Calcula la incidencia por 100,000 habitantes.
    
    Args:
        cases: Serie con número de casos
        population: Serie con población
        per_100k: Factor de conversión (por defecto 100,000)
        
    Returns:
        Serie con incidencia
    """
    incidence = (cases / population * per_100k)
    return incidence.replace([np.inf, -np.inf], np.nan)

def get_data_quality_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera un resumen de calidad de datos.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con métricas de calidad
    """
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'dtypes': df.dtypes.to_dict()
    }
    
    # Agregar estadísticas por columna
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            summary[f'{col}_stats'] = {
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'std': df[col].std()
            }
        else:
            summary[f'{col}_unique'] = df[col].nunique()
    
    return summary
