#!/usr/bin/env python3
"""
Script para construir el maestro de población a partir de archivos Excel.
Procesa archivos de proyecciones de población por provincia y departamento (2010-2025).
"""

import os
import sys
import pandas as pd
import numpy as np
import glob
import shutil
from pathlib import Path
import unicodedata
import re
from typing import Dict, List, Tuple, Optional
import warnings

# Constantes del script
RAW_DIRS = ["../poblacion"]
OUT_CSV = "ref/poblacion.csv"
QUALITY_CSV = "reports/poblacion_quality.csv"
YEAR_MIN = 2010
YEAR_MAX = 2025

# Keywords para detección de columnas (case/acentos-insensitive)
KEYWORDS_ANIO = ["anio", "año", "year"]
KEYWORDS_PROVINCIA = ["provincia", "prov"]
KEYWORDS_DEPARTAMENTO = ["departamento", "depto", "partido", "comuna"]
KEYWORDS_POBLACION = ["poblacion", "población", "total", "ambos sexos", "total ambos sexos"]

def normalize_text(text: str) -> str:
    """
    Normaliza texto: MAYÚSCULAS, sin tildes, trim.
    Unifica "CABA" → "CIUDAD AUTONOMA DE BUENOS AIRES".
    """
    if pd.isna(text) or text is None:
        return ""
    
    # Convertir a string y trim
    text = str(text).strip()
    
    # Remover tildes y caracteres especiales
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Convertir a mayúsculas
    text = text.upper()
    
    # Unificar CABA
    if text in ["CABA", "CIUDAD AUTONOMA DE BUENOS AIRES", "CIUDAD AUTÓNOMA DE BUENOS AIRES"]:
        text = "CIUDAD AUTONOMA DE BUENOS AIRES"
    
    return text

def find_column_by_keywords(df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
    """
    Encuentra una columna por keywords (case/acentos-insensitive).
    """
    df_columns = [normalize_text(col) for col in df.columns]
    
    for keyword in keywords:
        keyword_norm = normalize_text(keyword)
        for i, col_norm in enumerate(df_columns):
            if keyword_norm in col_norm or col_norm in keyword_norm:
                return df.columns[i]
    
    return None

def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Detecta las columnas relevantes en el DataFrame.
    """
    columns = {
        'anio': find_column_by_keywords(df, KEYWORDS_ANIO),
        'provincia': find_column_by_keywords(df, KEYWORDS_PROVINCIA),
        'departamento': find_column_by_keywords(df, KEYWORDS_DEPARTAMENTO),
        'poblacion': find_column_by_keywords(df, KEYWORDS_POBLACION)
    }
    
    return columns

def process_excel_file(file_path: str) -> pd.DataFrame:
    """
    Procesa un archivo Excel y retorna un DataFrame normalizado.
    """
    print(f"Procesando: {file_path}")
    
    try:
        # Leer todas las hojas del archivo
        excel_file = pd.ExcelFile(file_path)
        all_data = []
        
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Detectar el formato específico de estos archivos
                # Los datos están en formato: primera columna = departamento, columnas Unnamed = años
                if df.shape[1] < 16:  # Debería tener al menos 16 columnas (2010-2025)
                    print(f"  Hoja '{sheet_name}': Formato no reconocido (columnas insuficientes)")
                    continue
                
                # Extraer el nombre de la provincia del nombre de la hoja o del archivo
                provincia_nombre = normalize_text(sheet_name)
                if not provincia_nombre:
                    # Extraer del nombre del archivo
                    filename = os.path.basename(file_path)
                    if 'caba' in filename.lower():
                        provincia_nombre = "CIUDAD AUTONOMA DE BUENOS AIRES"
                    elif 'buenos_aires' in filename.lower():
                        provincia_nombre = "BUENOS AIRES"
                    else:
                        # Extraer del nombre del archivo
                        provincia_part = filename.replace('proy_1025_depto_', '').replace('.xls', '')
                        provincia_nombre = normalize_text(provincia_part.replace('_', ' '))
                
                # Buscar la fila que contiene "Ambos sexos" para identificar los datos
                ambos_sexos_row = None
                for idx, row in df.iterrows():
                    if pd.notna(row.iloc[0]) and 'ambos sexos' in str(row.iloc[0]).lower():
                        ambos_sexos_row = idx
                        break
                
                if ambos_sexos_row is None:
                    print(f"  Hoja '{sheet_name}': No se encontró fila 'Ambos sexos'")
                    continue
                
                # Buscar la fila que contiene el tipo de división (Departamento, Partido, Comuna)
                division_type_row = None
                for idx, row in df.iterrows():
                    if pd.notna(row.iloc[0]) and any(word in str(row.iloc[0]).lower() 
                                                   for word in ['departamento', 'partido', 'comuna']):
                        division_type_row = idx
                        break
                
                if division_type_row is None:
                    print(f"  Hoja '{sheet_name}': No se encontró tipo de división")
                    continue
                
                # Buscar años en la fila de división y en las siguientes filas
                years = []
                for offset in range(0, 3):  # Buscar en la fila de división y las siguientes 2 filas
                    if division_type_row + offset >= len(df):
                        break
                    years_row = df.iloc[division_type_row + offset]
                    for col_idx in range(1, min(17, len(years_row))):  # Columnas 1-16 para años 2010-2025
                        year_val = years_row.iloc[col_idx]
                        if pd.notna(year_val):
                            try:
                                year = int(float(year_val))
                                if YEAR_MIN <= year <= YEAR_MAX:
                                    years.append((col_idx, year))
                            except (ValueError, TypeError):
                                continue
                    if years:  # Si encontramos años, no buscar en más filas
                        break
                
                # Los datos empiezan después de algunas filas vacías
                data_start_row = division_type_row + 3  # Saltar filas vacías
                
                if not years:
                    print(f"  Hoja '{sheet_name}': No se encontraron años válidos")
                    continue
                
                # Procesar cada fila de datos
                processed_rows = []
                for idx in range(data_start_row, len(df)):
                    row = df.iloc[idx]
                    departamento = row.iloc[0]
                    
                    if pd.isna(departamento) or str(departamento).strip() == "":
                        continue
                    
                    departamento_nombre = normalize_text(str(departamento))
                    if not departamento_nombre:
                        continue
                    
                    # Extraer población para cada año
                    for col_idx, year in years:
                        poblacion_val = row.iloc[col_idx]
                        if pd.notna(poblacion_val) and str(poblacion_val).replace('.', '').isdigit():
                            poblacion = float(poblacion_val)
                            if poblacion > 0:
                                processed_rows.append({
                                    'anio': year,
                                    'provincia_nombre': provincia_nombre,
                                    'departamento_nombre': departamento_nombre,
                                    'poblacion': poblacion
                                })
                
                if processed_rows:
                    df_clean = pd.DataFrame(processed_rows)
                    all_data.append(df_clean)
                    print(f"  Hoja '{sheet_name}': {len(df_clean)} filas válidas")
                
            except Exception as e:
                print(f"  Error procesando hoja '{sheet_name}': {e}")
                continue
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            print(f"  Total: {len(result)} filas")
            return result
        else:
            print(f"  No se encontraron datos válidos")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error procesando archivo {file_path}: {e}")
        return pd.DataFrame()

def find_excel_files() -> List[str]:
    """
    Busca recursivamente archivos Excel en los directorios especificados.
    """
    excel_files = []
    
    for raw_dir in RAW_DIRS:
        if os.path.exists(raw_dir):
            # Buscar archivos .xls y .xlsx
            xls_files = glob.glob(os.path.join(raw_dir, "**", "*.xls"), recursive=True)
            xlsx_files = glob.glob(os.path.join(raw_dir, "**", "*.xlsx"), recursive=True)
            excel_files.extend(xls_files + xlsx_files)
        else:
            print(f"Directorio no encontrado: {raw_dir}")
    
    return excel_files

def validate_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Realiza validaciones duras y suaves sobre los datos.
    """
    errors = []
    warnings_list = []
    
    # Validaciones duras
    provincias_unicas = df['provincia_nombre'].nunique()
    if provincias_unicas < 23:
        errors.append(f"Provincias únicas insuficientes: {provincias_unicas} < 23")
    
    filas_totales = len(df)
    if filas_totales <= 5000:
        errors.append(f"Filas totales insuficientes: {filas_totales} <= 5000")
    
    # Verificar cobertura de años por provincia (al menos 10 años de los 16 disponibles)
    for provincia in df['provincia_nombre'].unique():
        anos_prov = df[df['provincia_nombre'] == provincia]['anio'].unique()
        if len(anos_prov) < 10:
            errors.append(f"Provincia {provincia}: solo tiene {len(anos_prov)} años de datos")
    
    # Validaciones suaves
    for provincia in df['provincia_nombre'].unique():
        for anio in df['anio'].unique():
            deptos_con_poblacion = df[
                (df['provincia_nombre'] == provincia) & 
                (df['anio'] == anio)
            ]['departamento_nombre'].nunique()
            
            # Estimación de departamentos totales (varía por provincia)
            deptos_estimados = {
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
            
            deptos_total_estimado = deptos_estimados.get(provincia, 20)  # Default 20
            cobertura = (deptos_con_poblacion / deptos_total_estimado) * 100
            
            if cobertura < 70:
                warnings_list.append(f"Provincia {provincia}, año {anio}: cobertura {cobertura:.1f}% < 70%")
    
    return len(errors) == 0, errors + warnings_list

def generate_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera el reporte de calidad.
    """
    quality_data = []
    
    for provincia in df['provincia_nombre'].unique():
        for anio in df['anio'].unique():
            deptos_con_poblacion = df[
                (df['provincia_nombre'] == provincia) & 
                (df['anio'] == anio)
            ]['departamento_nombre'].nunique()
            
            poblacion_total = df[
                (df['provincia_nombre'] == provincia) & 
                (df['anio'] == anio)
            ]['poblacion'].sum()
            
            # Estimación de departamentos totales
            deptos_estimados = {
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
            
            deptos_total_estimado = deptos_estimados.get(provincia, 20)
            cobertura_pct = (deptos_con_poblacion / deptos_total_estimado) * 100
            
            quality_data.append({
                'provincia_nombre': provincia,
                'anio': int(anio),
                'n_deptos_con_poblacion': deptos_con_poblacion,
                'n_deptos_total_estimado': deptos_total_estimado,
                'cobertura_pct': round(cobertura_pct, 2),
                'poblacion_total_prov_anio': int(poblacion_total)
            })
    
    return pd.DataFrame(quality_data)

def main():
    """
    Función principal del script.
    """
    print("=== CONSTRUCCIÓN DEL MAESTRO DE POBLACIÓN ===")
    
    # Crear directorios de salida si no existen
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    os.makedirs(os.path.dirname(QUALITY_CSV), exist_ok=True)
    
    # Backup del archivo existente
    backup_path = OUT_CSV + ".bak"
    if os.path.exists(OUT_CSV):
        print(f"Creando backup: {OUT_CSV} -> {backup_path}")
        shutil.copy2(OUT_CSV, backup_path)
    
    try:
        # Buscar archivos Excel
        excel_files = find_excel_files()
        print(f"Archivos Excel encontrados: {len(excel_files)}")
        
        if not excel_files:
            print("ERROR: No se encontraron archivos Excel")
            return 1
        
        # Procesar archivos
        all_data = []
        for file_path in excel_files:
            df = process_excel_file(file_path)
            if not df.empty:
                all_data.append(df)
        
        if not all_data:
            print("ERROR: No se encontraron datos válidos en ningún archivo")
            return 1
        
        # Combinar todos los datos
        df_final = pd.concat(all_data, ignore_index=True)
        
        # Agregar por duplicados exactos
        df_final = df_final.groupby(['anio', 'provincia_nombre', 'departamento_nombre'])['poblacion'].sum().reset_index()
        
        # Validar datos
        is_valid, validation_messages = validate_data(df_final)
        
        if not is_valid:
            print("ERROR: Validaciones fallaron:")
            for msg in validation_messages:
                print(f"  - {msg}")
            return 1
        
        # Mostrar warnings
        for msg in validation_messages:
            if "cobertura" in msg.lower():
                print(f"WARNING: {msg}")
        
        # Generar reporte de calidad
        quality_df = generate_quality_report(df_final)
        
        # Guardar archivos
        df_final.to_csv(OUT_CSV, index=False)
        quality_df.to_csv(QUALITY_CSV, index=False)
        
        # Estadísticas finales
        print("\n=== ESTADÍSTICAS FINALES ===")
        print(f"Archivos procesados: {len(excel_files)}")
        print(f"Filas totales: {len(df_final):,}")
        print(f"Provincias únicas: {df_final['provincia_nombre'].nunique()}")
        print(f"Rango de años: {df_final['anio'].min()}-{df_final['anio'].max()}")
        print(f"Cobertura promedio: {quality_df['cobertura_pct'].mean():.1f}%")
        print(f"Archivos generados:")
        print(f"  - {OUT_CSV}")
        print(f"  - {QUALITY_CSV}")
        
        # Limpiar backup si todo salió bien
        if os.path.exists(backup_path):
            os.remove(backup_path)
            print(f"Backup eliminado: {backup_path}")
        
        print("\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        
        # Restaurar backup si existe
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, OUT_CSV)
            print(f"Backup restaurado: {backup_path} -> {OUT_CSV}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
