#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar el maestro oficial de departamentos desde la API del INDEC.
Descarga y procesa el archivo oficial de códigos de provincias y departamentos.

Uso:
    python build_geo_map.py

Requisitos: pandas, openpyxl, requests
"""

import os
import sys
import shutil
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import requests
from io import BytesIO

# Parámetros de configuración
GEO_URL_OFICIAL = "https://www.indec.gob.ar/ftp/cuadros/territorio/codigos_prov_depto_censo2010.xls"
GEO_OUT_PATH = "ref/geo_map.csv"
BACKUP_SUFFIX = ".bak"

# Columnas esperadas en la salida
OUTPUT_COLS = [
    "provincia_id",
    "provincia_nombre", 
    "departamento_id",
    "departamento_nombre",
    "depto_full_id"
]

def strip_accents(text: str) -> str:
    """Elimina tildes y caracteres especiales de un texto."""
    if pd.isna(text):
        return text
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text)) 
                   if unicodedata.category(c) != 'Mn')

def normalize_text(text: str) -> str:
    """Normaliza texto: elimina tildes, convierte a mayúsculas y elimina espacios."""
    if pd.isna(text):
        return text
    return strip_accents(str(text)).strip().upper()

def download_file(url: str) -> bytes:
    """Descarga un archivo desde una URL y retorna su contenido como bytes."""
    print(f"Descargando archivo desde: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"✓ Descarga exitosa: {len(response.content)} bytes")
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al descargar archivo: {e}")

def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detecta las columnas relevantes en el DataFrame basándose en keywords.
    Retorna un diccionario mapeando nombres estándar a nombres reales de columnas.
    """
    # Para el archivo específico del INDEC, mapear por posición conocida
    col_mapping = {}
    
    # Mapear columnas por posición (basado en la estructura observada)
    if len(df.columns) >= 4:
        # Columna 0: Provincia (nombre)
        col_mapping['provincia_nombre'] = df.columns[0]
        # Columna 1: Código provincia
        col_mapping['provincia_id'] = df.columns[1] 
        # Columna 2: Departamento/partido/comuna (nombre)
        col_mapping['departamento_nombre'] = df.columns[2]
        # Columna 3: Código departamento
        col_mapping['departamento_id'] = df.columns[3]
    
    return col_mapping

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia los datos crudos eliminando filas de encabezado, notas y filas vacías.
    """
    print("Limpiando datos crudos...")
    
    # Eliminar filas completamente vacías
    df = df.dropna(how='all')
    
    # Buscar la fila que contiene "Provincia" (encabezado real)
    header_row = None
    for i, row in df.iterrows():
        if any('provincia' in str(cell).lower() for cell in row if pd.notna(cell)):
            header_row = i
            break
    
    if header_row is not None:
        # Tomar solo las filas después del encabezado
        df = df.iloc[header_row + 1:].copy()
    
    # Eliminar filas que contienen notas o texto explicativo
    df = df[~df.iloc[:, 0].astype(str).str.contains('Nota:|Fuente:|Departamento,', na=False)]
    
    # Eliminar filas donde la primera columna (provincia) esté vacía
    df = df[df.iloc[:, 0].notna()]
    
    # Eliminar filas donde no hay código de provincia válido
    df = df[df.iloc[:, 1].notna()]
    df = df[df.iloc[:, 1].astype(str).str.match(r'^\d{2}$', na=False)]
    
    # Resetear índice
    df = df.reset_index(drop=True)
    
    print(f"✓ Datos limpiados: {len(df)} filas válidas")
    return df

def validate_data(df: pd.DataFrame) -> None:
    """
    Valida que los datos cumplan con los criterios mínimos.
    Aborta con error si no se cumplen las validaciones.
    """
    print("Validando datos...")
    
    # Validación 1: Número mínimo de filas
    if len(df) < 100:
        raise Exception("Fuente incompleta/stub: menos de 100 filas encontradas")
    
    # Validación 2: Provincias únicas ≥ 23
    prov_unicas = df['provincia_id'].nunique()
    if prov_unicas < 23:
        raise Exception(f"Validación fallida: solo {prov_unicas} provincias únicas (mínimo 23)")
    
    # Validación 3: Departamentos únicos ≥ 100 (ajustado según datos oficiales)
    deptos_unicos = df['departamento_id'].nunique()
    if deptos_unicos < 100:
        raise Exception(f"Validación fallida: solo {deptos_unicos} departamentos únicos (mínimo 100)")
    
    # Validación 4: Sin nulos en IDs
    if df['provincia_id'].isna().any():
        raise Exception("Validación fallida: hay valores nulos en provincia_id")
    if df['departamento_id'].isna().any():
        raise Exception("Validación fallida: hay valores nulos en departamento_id")
    
    # Validación 5: Sin duplicados en (provincia_id, departamento_id)
    duplicados = df.duplicated(subset=['provincia_id', 'departamento_id']).sum()
    if duplicados > 0:
        raise Exception(f"Validación fallida: {duplicados} filas duplicadas en (provincia_id, departamento_id)")
    
    print(f"✓ Validaciones exitosas: {len(df)} filas, {prov_unicas} provincias, {deptos_unicos} departamentos")

def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los datos según los requerimientos:
    - Nombres en MAYÚSCULAS, sin tildes, trim
    - Tipos: provincia_id y departamento_id → enteros (Int64)
    - Crear depto_full_id = provincia_id*1000 + departamento_id
    """
    print("Normalizando datos...")
    
    # Normalizar nombres de provincias y departamentos
    df['provincia_nombre'] = df['provincia_nombre'].apply(normalize_text)
    df['departamento_nombre'] = df['departamento_nombre'].apply(normalize_text)
    
    # Convertir IDs a enteros
    df['provincia_id'] = pd.to_numeric(df['provincia_id'], errors='coerce').astype('Int64')
    df['departamento_id'] = pd.to_numeric(df['departamento_id'], errors='coerce').astype('Int64')
    
    # Crear depto_full_id
    df['depto_full_id'] = df['provincia_id'] * 1000 + df['departamento_id']
    df['depto_full_id'] = df['depto_full_id'].astype('Int64')
    
    # Eliminar filas con IDs nulos después de la conversión
    df = df.dropna(subset=['provincia_id', 'departamento_id'])
    
    print(f"✓ Datos normalizados: {len(df)} filas válidas")
    return df

def backup_existing_file(file_path: str) -> None:
    """Crea backup del archivo existente si existe."""
    if os.path.exists(file_path):
        backup_path = file_path + BACKUP_SUFFIX
        print(f"Creando backup: {file_path} → {backup_path}")
        shutil.move(file_path, backup_path)
        print("✓ Backup creado exitosamente")

def save_geo_map(df: pd.DataFrame, output_path: str) -> None:
    """Guarda el DataFrame como CSV en la ruta especificada."""
    print(f"Guardando archivo: {output_path}")
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Guardar con las columnas en el orden correcto
    df_output = df[OUTPUT_COLS].copy()
    df_output.to_csv(output_path, index=False, encoding='utf-8')
    print("✓ Archivo guardado exitosamente")

def main():
    """Función principal del script."""
    print("=== Generador de Maestro de Departamentos ===")
    print(f"URL fuente: {GEO_URL_OFICIAL}")
    print(f"Archivo destino: {GEO_OUT_PATH}")
    
    try:
        # 1. Descargar archivo
        file_content = download_file(GEO_URL_OFICIAL)
        
        # 2. Leer archivo Excel (hoja de Departamentos)
        print("Leyendo archivo Excel (hoja Departamentos)...")
        df = pd.read_excel(BytesIO(file_content), sheet_name='Departamentos', dtype=str)
        print(f"✓ Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
        
        # 3. Limpiar datos crudos
        df = clean_raw_data(df)
        
        # 4. Detectar columnas
        print("Detectando columnas...")
        col_mapping = detect_columns(df)
        print(f"Columnas detectadas: {col_mapping}")
        
        # Verificar que se detectaron todas las columnas necesarias
        required_cols = ['provincia_id', 'provincia_nombre', 'departamento_id', 'departamento_nombre']
        missing_cols = [col for col in required_cols if col not in col_mapping]
        if missing_cols:
            raise Exception(f"No se pudieron detectar las columnas: {missing_cols}")
        
        # 4. Mapear columnas
        df_mapped = df[list(col_mapping.values())].copy()
        df_mapped.columns = list(col_mapping.keys())
        
        # 5. Normalizar datos
        df_normalized = normalize_data(df_mapped)
        
        # 6. Validar datos
        validate_data(df_normalized)
        
        # 7. Crear backup si existe archivo anterior
        backup_existing_file(GEO_OUT_PATH)
        
        # 8. Guardar archivo final
        save_geo_map(df_normalized, GEO_OUT_PATH)
        
        # 9. Mostrar resumen final
        print("\n=== RESUMEN FINAL ===")
        print(f"Archivo generado: {GEO_OUT_PATH}")
        print(f"Total de filas: {len(df_normalized)}")
        print(f"Provincias únicas: {df_normalized['provincia_id'].nunique()}")
        print(f"Departamentos únicos: {df_normalized['departamento_id'].nunique()}")
        print("✓ Proceso completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("El archivo existente no fue modificado.")
        sys.exit(1)

if __name__ == "__main__":
    main()
