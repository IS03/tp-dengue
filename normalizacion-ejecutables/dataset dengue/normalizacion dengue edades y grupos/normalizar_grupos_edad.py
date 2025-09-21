#!/usr/bin/env python3
"""
Script para normalizar las columnas grupo_edad_id y grupo_edad_desc
en todos los archivos de dengue según el mapeo estándar.
"""

import pandas as pd
import os
import sys
from pathlib import Path

def cargar_mapeo_estandar():
    """Carga el mapeo estándar de grupos de edad."""
    mapeo_path = Path(__file__).parent / "mapeo_grupos_edad_estandar.csv"
    mapeo_df = pd.read_csv(mapeo_path)
    
    # Crear diccionarios para mapeo bidireccional
    id_to_desc = dict(zip(mapeo_df['grupo_edad_id'], mapeo_df['grupo_edad_desc']))
    desc_to_id = dict(zip(mapeo_df['grupo_edad_desc'], mapeo_df['grupo_edad_id']))
    
    return id_to_desc, desc_to_id

def normalizar_archivo(archivo_path, id_to_desc, desc_to_id):
    """Normaliza un archivo CSV específico."""
    print(f"\n🔧 Normalizando: {archivo_path.name}")
    
    # Leer el archivo
    df = pd.read_csv(archivo_path)
    
    # Crear backup
    backup_path = archivo_path.parent / "backup" / f"backup_{archivo_path.name}"
    backup_path.parent.mkdir(exist_ok=True)
    df.to_csv(backup_path, index=False)
    print(f"✅ Backup creado: {backup_path}")
    
    cambios_realizados = []
    
    # Normalizar grupo_edad_id (convertir a entero, eliminar .0)
    if 'grupo_edad_id' in df.columns:
        df['grupo_edad_id'] = pd.to_numeric(df['grupo_edad_id'], errors='coerce')
        df['grupo_edad_id'] = df['grupo_edad_id'].astype('Int64')  # Permite NaN
        
        # Contar cambios de formato
        cambios_formato = df['grupo_edad_id'].notna().sum()
        if cambios_formato > 0:
            cambios_realizados.append(f"Convertidos {cambios_formato} IDs a formato entero")
    
    # Normalizar grupo_edad_desc
    if 'grupo_edad_desc' in df.columns:
        # Limpiar descripciones (eliminar espacios extra, normalizar)
        df['grupo_edad_desc'] = df['grupo_edad_desc'].astype(str).str.strip()
        df['grupo_edad_desc'] = df['grupo_edad_desc'].replace('nan', '')
        
        # Mapear descripciones incorrectas a las correctas
        mapeos_desc = {
            'de 10 a 14 anos': 'de 10 a 14 anos',
            'de 15 a 19 anos': 'de 15 a 19 anos',
            'de 20 a 24 anos': 'de 20 a 24 anos',
            'de 25 a 34 anos': 'de 25 a 34 anos',
            'de 35 a 44 anos': 'de 35 a 44 anos',
            'de 45 a 65 anos': 'de 45 a 65 anos',
            'mayores de 65 anos': 'mayores de 65 anos',
            'neonato hasta 28 dias': 'neonato hasta 28 dias',
            'posneonato 29 hasta 365 dias': 'posneonato 29 hasta 365 dias',
            'de 13 a 24 meses': 'de 13 a 24 meses',
            'de 2 a 4 anos': 'de 2 a 4 anos',
            'de 5 a 9 anos': 'de 5 a 9 anos'
        }
        
        df['grupo_edad_desc'] = df['grupo_edad_desc'].map(mapeos_desc).fillna(df['grupo_edad_desc'])
        
        cambios_desc = df['grupo_edad_desc'].notna().sum()
        if cambios_desc > 0:
            cambios_realizados.append(f"Normalizadas {cambios_desc} descripciones")
    
    # Corregir inconsistencias entre ID y descripción
    if 'grupo_edad_id' in df.columns and 'grupo_edad_desc' in df.columns:
        inconsistencias_corregidas = 0
        
        for idx, row in df.iterrows():
            if pd.notna(row['grupo_edad_id']) and pd.notna(row['grupo_edad_desc']):
                id_actual = int(row['grupo_edad_id'])
                desc_actual = str(row['grupo_edad_desc']).strip()
                
                # Si el ID tiene una descripción estándar, usar esa
                if id_actual in id_to_desc:
                    desc_correcta = id_to_desc[id_actual]
                    if desc_actual != desc_correcta:
                        df.at[idx, 'grupo_edad_desc'] = desc_correcta
                        inconsistencias_corregidas += 1
                
                # Si la descripción tiene un ID estándar, usar ese
                elif desc_actual in desc_to_id:
                    id_correcto = desc_to_id[desc_actual]
                    if id_actual != id_correcto:
                        df.at[idx, 'grupo_edad_id'] = id_correcto
                        inconsistencias_corregidas += 1
        
        if inconsistencias_corregidas > 0:
            cambios_realizados.append(f"Corregidas {inconsistencias_corregidas} inconsistencias ID-descripción")
    
    # Guardar archivo normalizado
    df.to_csv(archivo_path, index=False)
    
    if cambios_realizados:
        print("📝 Cambios realizados:")
        for cambio in cambios_realizados:
            print(f"   - {cambio}")
    else:
        print("ℹ️  No se requirieron cambios")
    
    return len(cambios_realizados) > 0

def verificar_archivo(archivo_path):
    """Verifica la consistencia del archivo normalizado."""
    print(f"\n🔍 Verificando: {archivo_path.name}")
    
    df = pd.read_csv(archivo_path)
    
    if 'grupo_edad_id' not in df.columns or 'grupo_edad_desc' not in df.columns:
        print("❌ Columnas grupo_edad_id o grupo_edad_desc no encontradas")
        return False
    
    # Verificar tipos de datos
    ids_enteros = df['grupo_edad_id'].dtype in ['int64', 'Int64']
    print(f"✅ IDs como enteros: {ids_enteros}")
    
    # Verificar inconsistencias restantes
    inconsistencias = 0
    id_to_desc, desc_to_id = cargar_mapeo_estandar()
    
    for idx, row in df.iterrows():
        if pd.notna(row['grupo_edad_id']) and pd.notna(row['grupo_edad_desc']):
            id_actual = int(row['grupo_edad_id'])
            desc_actual = str(row['grupo_edad_desc']).strip()
            
            if id_actual in id_to_desc:
                desc_esperada = id_to_desc[id_actual]
                if desc_actual != desc_esperada:
                    inconsistencias += 1
                    if inconsistencias <= 5:  # Mostrar solo las primeras 5
                        print(f"⚠️  Inconsistencia en fila {idx}: ID {id_actual} → '{desc_actual}' (esperado: '{desc_esperada}')")
    
    if inconsistencias == 0:
        print("✅ Sin inconsistencias detectadas")
    else:
        print(f"⚠️  {inconsistencias} inconsistencias detectadas")
    
    return inconsistencias == 0

def main():
    """Función principal."""
    print("🚀 Iniciando normalización de grupos de edad...")
    
    # Cargar mapeo estándar
    try:
        id_to_desc, desc_to_id = cargar_mapeo_estandar()
        print(f"✅ Mapeo estándar cargado: {len(id_to_desc)} grupos de edad")
    except Exception as e:
        print(f"❌ Error cargando mapeo estándar: {e}")
        return
    
    # Directorio de archivos de dengue
    dataset_dir = Path(__file__).parent.parent / "dataset-dengue"
    
    # Lista de archivos a procesar
    archivos_dengue = [
        "dengue-2018.csv",
        "dengue-2019.csv", 
        "dengue-2020.csv",
        "dengue-2021.csv",
        "dengue-2022.csv",
        "dengue-2023.csv",
        "dengue-2024.csv",
        "dengue-2025.csv"
    ]
    
    archivos_procesados = 0
    archivos_verificados = 0
    
    for archivo_nombre in archivos_dengue:
        archivo_path = dataset_dir / archivo_nombre
        
        if not archivo_path.exists():
            print(f"⚠️  Archivo no encontrado: {archivo_nombre}")
            continue
        
        try:
            # Normalizar archivo
            if normalizar_archivo(archivo_path, id_to_desc, desc_to_id):
                archivos_procesados += 1
            
            # Verificar archivo
            if verificar_archivo(archivo_path):
                archivos_verificados += 1
                
        except Exception as e:
            print(f"❌ Error procesando {archivo_nombre}: {e}")
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos procesados: {archivos_procesados}")
    print(f"   - Archivos verificados correctamente: {archivos_verificados}")
    print(f"   - Total de archivos: {len(archivos_dengue)}")

if __name__ == "__main__":
    main()
