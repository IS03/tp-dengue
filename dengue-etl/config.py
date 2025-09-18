#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración centralizada para el ETL de Dengue.
Contiene todos los parámetros, constantes y configuraciones del sistema.
"""

import os
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN GENERAL
# =============================================================================

# Años de procesamiento
YEAR_MIN = 2018
YEAR_MAX = 2025

# Semanas epidemiológicas
WEEK_MIN = 1
WEEK_MAX = 53

# IDs para datos desconocidos
UNKNOWN_DEPT_ID = 999
UNKNOWN_PROV_ID = 99

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS
# =============================================================================

# Directorios
BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
REF_DIR = BASE_DIR / "ref"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Archivos de referencia
GEO_MAP_FILE = REF_DIR / "geo_map.csv"
POPULATION_FILE = REF_DIR / "poblacion.csv"

# Archivos de salida
OUTPUT_FILES = {
    'clean_data': PROCESSED_DIR / "dengue_2018_2025_clean",
    'weekly_depto': PROCESSED_DIR / "weekly_by_depto",
    'monthly_prov': PROCESSED_DIR / "monthly_by_prov"
}

# Reportes
QUALITY_REPORT = REPORTS_DIR / "quality_report.csv"
POPULATION_QUALITY = REPORTS_DIR / "poblacion_quality.csv"

# =============================================================================
# CONFIGURACIÓN DE ENCODING
# =============================================================================

# Encodings a probar en orden de preferencia
ENCODINGS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']

# Separadores de CSV a detectar
CSV_SEPARATORS = [',', ';', '|', '\t']

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOGS_DIR / "etl.log",
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# =============================================================================
# CONFIGURACIÓN DE VALIDACIÓN
# =============================================================================

# Validaciones de calidad
VALIDATION_RULES = {
    'min_provinces': 23,
    'min_departments': 100,
    'min_total_rows': 5000,
    'min_years_per_province': 10,
    'min_coverage_percentage': 70.0
}

# =============================================================================
# CONFIGURACIÓN DE NORMALIZACIÓN
# =============================================================================

# Sinónimos de provincias para normalización
PROVINCE_SYNONYMS = {
    "CABA": "CIUDAD AUTONOMA DE BUENOS AIRES",
    "C.A.B.A.": "CIUDAD AUTONOMA DE BUENOS AIRES",
    "CIUDAD AUTONOMA DE BUENOS AIRES": "CIUDAD AUTONOMA DE BUENOS AIRES",
    "CAPITAL FEDERAL": "CIUDAD AUTONOMA DE BUENOS AIRES",
    "TIERRA DEL FUEGO, ANTARTIDA E ISLAS DEL ATLANTICO SUR": "TIERRA DEL FUEGO"
}

# Eventos de dengue válidos
DENGUE_EVENTS = {"dengue", "dengue clasico", "dengue grave", "dengue (todos)"}

# =============================================================================
# CONFIGURACIÓN DE COLUMNAS
# =============================================================================

# Columnas estándar del esquema
STANDARD_COLUMNS = [
    "provincia_id", "provincia_nombre",
    "departamento_id", "departamento_nombre",
    "anio", "semana_epi", "fecha",
    "evento_nombre",
    "grupo_edad_id", "grupo_edad_desc",
    "cantidad_casos"
]

# Aliases de columnas para mapeo automático
COLUMN_ALIASES = {
    "provincia_id": ["provincia_id", "idprovincia", "id_provincia", "cod_prov", 
                     "codigo_provincia", "id_prov_indec_residencia"],
    "provincia_nombre": ["provincia", "provincia_nombre", "nombre_provincia", 
                         "provincia_residencia"],
    "departamento_id": ["departamento_id", "cod_depto", "codigo_departamento", 
                        "iddepto", "id_departamento", "id_depto_indec_residencia"],
    "departamento_nombre": ["departamento", "depto", "departamento_nombre", 
                            "nombre_departamento", "departamento_residencia"],
    "anio": ["anio", "año", "year", "ano", "anio_min"],
    "semana_epi": ["semana_epi", "semana", "semana_epidemiologica", 
                   "semanas_epidemiologicas", "semana_isl", "sepi_min"],
    "fecha": ["fecha", "fec", "date"],
    "evento_nombre": ["evento", "evento_nombre", "enfermedad", "diagnostico"],
    "grupo_edad_id": ["grupo_edad_id", "id_grupo_edad", "id_grupo_etario"],
    "grupo_edad_desc": ["grupo_edad_desc", "grupo_edad", "grupo_etario", "rango_edad"],
    "cantidad_casos": ["cantidad_casos", "casos", "cant_casos", "cantidad", "n_casos"]
}

# =============================================================================
# CONFIGURACIÓN DE POBLACIÓN
# =============================================================================

# Keywords para detección de columnas en archivos de población
POPULATION_KEYWORDS = {
    'anio': ["anio", "año", "year"],
    'provincia': ["provincia", "prov"],
    'departamento': ["departamento", "depto", "partido", "comuna"],
    'poblacion': ["poblacion", "población", "total", "ambos sexos", "total ambos sexos"]
}

# Estimación de departamentos por provincia
ESTIMATED_DEPARTMENTS = {
    'BUENOS AIRES': 135,
    'CIUDAD AUTONOMA DE BUENOS AIRES': 15,
    'CATAMARCA': 16,
    'CHACO': 25,
    'CHUBUT': 15,
    'CORDOBA': 26,
    'CORRIENTES': 25,
    'ENTRE RIOS': 17,
    'FORMOSA': 9,
    'JUJUY': 16,
    'LA PAMPA': 22,
    'LA RIOJA': 18,
    'MENDOZA': 18,
    'MISIONES': 17,
    'NEUQUEN': 16,
    'RIO NEGRO': 13,
    'SALTA': 23,
    'SAN JUAN': 19,
    'SAN LUIS': 9,
    'SANTA CRUZ': 7,
    'SANTA FE': 19,
    'SANTIAGO DEL ESTERO': 27,
    'TIERRA DEL FUEGO': 3,
    'TUCUMAN': 17
}

# =============================================================================
# CONFIGURACIÓN DE GEOGRAFÍA
# =============================================================================

# URL oficial del INDEC para códigos geográficos
GEO_URL_OFICIAL = "https://www.indec.gob.ar/ftp/cuadros/territorio/codigos_prov_depto_censo2010.xls"

# Columnas de salida para geo_map
GEO_OUTPUT_COLUMNS = [
    "provincia_id",
    "provincia_nombre", 
    "departamento_id",
    "departamento_nombre",
    "depto_full_id"
]

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def ensure_directories():
    """Crea todos los directorios necesarios si no existen."""
    directories = [RAW_DIR, PROCESSED_DIR, REF_DIR, REPORTS_DIR, LOGS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_output_path(base_name: str, format: str = 'csv') -> Path:
    """Obtiene la ruta completa para un archivo de salida."""
    if base_name in OUTPUT_FILES:
        return OUTPUT_FILES[base_name].with_suffix(f'.{format}')
    else:
        return PROCESSED_DIR / f"{base_name}.{format}"

def is_valid_year(year: int) -> bool:
    """Valida si un año está en el rango permitido."""
    return YEAR_MIN <= year <= YEAR_MAX

def is_valid_week(week: int) -> bool:
    """Valida si una semana epidemiológica está en el rango permitido."""
    return WEEK_MIN <= week <= WEEK_MAX

def is_unknown_id(id_value, id_type: str = 'dept') -> bool:
    """Verifica si un ID corresponde a datos desconocidos."""
    if id_type == 'dept':
        return id_value == UNKNOWN_DEPT_ID
    elif id_type == 'prov':
        return id_value == UNKNOWN_PROV_ID
    return False
