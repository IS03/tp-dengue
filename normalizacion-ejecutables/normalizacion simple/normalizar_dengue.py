#!/usr/bin/env python3
"""
Script para normalizar archivos de dengue específicamente
- Arregla problemas de codificación
- Estandariza nombres de columnas
- Normaliza texto (sin ñ, sin tildes, sin caracteres especiales)
- Elimina filas y columnas vacías
- Convierte estructura a formato estándar
"""

import pandas as pd
import os
import re
import unicodedata
from pathlib import Path

def normalizar_texto_dengue(texto):
    """
    Normaliza texto específicamente para archivos de dengue
    - Sin ñ (usa 'ano' en lugar de 'año')
    - Todo en minúsculas
    - Sin tildes ni acentos
    - Sin caracteres especiales (puntos, comas, etc.)
    """
    if pd.isna(texto) or texto == '':
        return texto
    
    texto = str(texto)
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Arreglar problemas de codificación específicos - usar 'ano' en lugar de 'año'
    texto = texto.replace('año', 'ano')
    texto = texto.replace('años', 'anos')
    texto = texto.replace('ao', 'ano')
    texto = texto.replace('aos', 'anos')
    texto = texto.replace('anos', 'anos')  # Ya está bien
    texto = texto.replace('dias', 'dias')
    texto = texto.replace('días', 'dias')
    texto = texto.replace('das', 'dias')
    
    # Quitar tildes y acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    
    # Quitar caracteres especiales, puntos, comas, etc. - dejar solo letras, números y espacios
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    
    # Quitar espacios múltiples y espacios al inicio/final
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def mapear_columnas_2023_2024_2025(df):
    """
    Mapea las columnas de los archivos 2023-2025 al formato estándar
    """
    mapeo_columnas = {
        'id_depto_indec_residencia': 'departamento_id',
        'departamento_residencia': 'departamento_nombre', 
        'id_prov_indec_residencia': 'provincia_id',
        'provincia_residencia': 'provincia_nombre',
        'anio_min': 'ano',
        'evento': 'evento_nombre',
        'id_grupo_etario': 'grupo_edad_id',
        'grupo_etario': 'grupo_edad_desc',
        'sepi_min': 'semanas_epidemiologicas',
        'cantidad': 'cantidad_casos'
    }
    
    # Renombrar columnas
    df = df.rename(columns=mapeo_columnas)
    
    return df

def normalizar_archivo_dengue(archivo_path):
    """
    Normaliza un archivo de dengue específico
    """
    try:
        print(f"\n=== Procesando: {archivo_path.name} ===")
        
        # Leer archivo con diferentes codificaciones
        df = None
        encoding_usado = None
        
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(archivo_path, encoding=encoding, sep=';')
                encoding_usado = encoding
                print(f"  ✓ Leído con codificación: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"  ✗ No se pudo leer el archivo")
            return False
        
        print(f"  Archivo original: {df.shape[0]} filas, {df.shape[1]} columnas")
        print(f"  Columnas: {list(df.columns)}")
        
        # Mapear columnas si es necesario (para 2023, 2024, 2025)
        if 'id_depto_indec_residencia' in df.columns:
            print("  Mapeando columnas al formato estándar...")
            df = mapear_columnas_2023_2024_2025(df)
            print(f"  Columnas después del mapeo: {list(df.columns)}")
        
        # Normalizar texto en columnas de texto
        columnas_texto = ['departamento_nombre', 'provincia_nombre', 'evento_nombre', 'grupo_edad_desc']
        for col in columnas_texto:
            if col in df.columns:
                print(f"  Normalizando columna: {col}")
                df[col] = df[col].apply(normalizar_texto_dengue)
        
        # Limpiar datos - eliminar filas y columnas vacías
        print("  Limpiando datos...")
        
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        filas_eliminadas = df.shape[0]
        
        # Eliminar columnas completamente vacías
        df = df.dropna(axis=1, how='all')
        columnas_eliminadas = df.shape[1]
        
        # Eliminar filas que solo contienen espacios en blanco o valores vacíos
        for col in df.columns:
            if df[col].dtype == 'object':  # Solo para columnas de texto
                df[col] = df[col].astype(str).str.strip()
        
        # Eliminar filas donde todas las columnas son cadenas vacías o 'nan'
        mask = df.astype(str).apply(lambda x: x.str.strip()).eq('').all(axis=1) | \
               df.astype(str).apply(lambda x: x.str.strip()).eq('nan').all(axis=1)
        df = df[~mask]
        filas_vacias_eliminadas = mask.sum()
        
        print(f"  Filas completamente vacías eliminadas: {filas_eliminadas}")
        print(f"  Columnas completamente vacías eliminadas: {columnas_eliminadas}")
        print(f"  Filas con solo espacios/vacías eliminadas: {filas_vacias_eliminadas}")
        
        # Guardar archivo normalizado con separador de comas
        df.to_csv(archivo_path, index=False, encoding='utf-8', sep=',')
        print(f"  ✓ Archivo normalizado guardado: {df.shape[0]} filas, {df.shape[1]} columnas")
        print(f"  ✓ Separador: coma (,)")
        print(f"  ✓ Codificación: UTF-8")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def main():
    """Función principal"""
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    
    # Archivos a normalizar
    archivos_a_normalizar = [
        "dengue-2022.csv",  # También tiene problemas de codificación
        "dengue-2023.csv",
        "dengue-2024.csv", 
        "dengue-2025.csv"
    ]
    
    print("=== NORMALIZACIÓN DE ARCHIVOS DE DENGUE ===")
    print("Mejoras aplicadas:")
    print("  - Sin ñ (usa 'ano' en lugar de 'año')")
    print("  - Todo en minúsculas")
    print("  - Sin tildes ni acentos")
    print("  - Sin caracteres especiales (puntos, comas, etc.)")
    print("  - Elimina filas y columnas vacías")
    print("  - Separador: coma (,)")
    print("  - Codificación: UTF-8")
    print()
    print("Archivos a procesar:")
    for archivo in archivos_a_normalizar:
        print(f"  - {archivo}")
    print()
    
    archivos_procesados = 0
    archivos_exitosos = 0
    
    for archivo_nombre in archivos_a_normalizar:
        archivo_path = base_path / archivo_nombre
        
        if not archivo_path.exists():
            print(f"⚠️  Archivo no encontrado: {archivo_nombre}")
            continue
        
        archivos_procesados += 1
        if normalizar_archivo_dengue(archivo_path):
            archivos_exitosos += 1
    
    print(f"\n=== RESUMEN ===")
    print(f"Archivos procesados: {archivos_procesados}")
    print(f"Archivos exitosos: {archivos_exitosos}")
    print(f"Archivos con errores: {archivos_procesados - archivos_exitosos}")
    
    if archivos_exitosos == archivos_procesados:
        print("🎉 ¡Todos los archivos fueron normalizados exitosamente!")
    else:
        print("⚠️  Algunos archivos tuvieron errores")

if __name__ == "__main__":
    main()
