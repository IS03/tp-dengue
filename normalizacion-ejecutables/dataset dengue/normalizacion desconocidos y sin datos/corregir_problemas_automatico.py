#!/usr/bin/env python3
"""
Script automático para corregir problemas identificados en los archivos de dengue
Elimina automáticamente todas las filas problemáticas sin intervención del usuario
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import shutil
from datetime import datetime

def corregir_archivo_automatico(nombre_archivo):
    """
    Corrige automáticamente un archivo CSV eliminando todas las filas problemáticas
    """
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    backup_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico")
    archivo = base_path / nombre_archivo
    
    if not archivo.exists():
        print(f"❌ Archivo no encontrado: {nombre_archivo}")
        return
    
    print(f"\n🔍 Procesando: {nombre_archivo}")
    
    # Crear backup
    backup_path.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_path / f"backup_{timestamp}_{nombre_archivo}"
    shutil.copy2(archivo, backup_file)
    print(f"✅ Backup creado: {backup_file}")
    
    # Leer archivo
    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return
    
    filas_originales = len(df)
    print(f"📊 Filas originales: {filas_originales}")
    
    # Contadores de eliminaciones
    filas_eliminadas_automaticamente = []
    filas_eliminadas_por_nulos = []
    filas_eliminadas_por_desconocido = []
    filas_eliminadas_por_ids = []
    filas_eliminadas_por_vacios = []
    
    # 1. Eliminar automáticamente filas donde tanto departamento_nombre como provincia_nombre son "desconocido" o "sin dato"
    if 'departamento_nombre' in df.columns and 'provincia_nombre' in df.columns:
        valores_problematicos = ['desconocido', 'desconocida', 'unknown', 'n/a', 'na', 'sin dato', 'sin datos']
        
        mask_desconocido = (
            df['departamento_nombre'].astype(str).str.lower().isin(valores_problematicos) &
            df['provincia_nombre'].astype(str).str.lower().isin(valores_problematicos)
        )
        filas_eliminadas_automaticamente = df[mask_desconocido].index.tolist()
        df = df[~mask_desconocido]
        print(f"🗑️  Eliminadas automáticamente {len(filas_eliminadas_automaticamente)} filas con departamento y provincia desconocidos/sin dato")
    
    # 2. Valores nulos
    filas_nulos = df[df.isnull().any(axis=1)]
    filas_eliminadas_por_nulos = filas_nulos.index.tolist()
    df = df.dropna()
    print(f"🗑️  Eliminadas {len(filas_eliminadas_por_nulos)} filas con valores nulos")
    
    # 3. Valores "desconocido" o "sin dato" en columnas individuales
    valores_problematicos = ['desconocido', 'desconocida', 'unknown', 'n/a', 'na', 'sin dato', 'sin datos']
    
    for col in df.columns:
        if df[col].dtype == 'object':
            mask = df[col].astype(str).str.lower().isin(valores_problematicos)
            filas_problematicas = df[mask].index.tolist()
            filas_eliminadas_por_desconocido.extend(filas_problematicas)
            df = df[~mask]
            if len(filas_problematicas) > 0:
                print(f"🗑️  Eliminadas {len(filas_problematicas)} filas con '{col}' desconocido/sin dato")
    
    # 4. IDs problemáticos (99, 999)
    if 'departamento_id' in df.columns:
        mask_id_dep = df['departamento_id'].isin([99, 999, '99', '999'])
        filas_problematicas = df[mask_id_dep].index.tolist()
        filas_eliminadas_por_ids.extend(filas_problematicas)
        df = df[~mask_id_dep]
        if len(filas_problematicas) > 0:
            print(f"🗑️  Eliminadas {len(filas_problematicas)} filas con departamento_id problemático")
    
    if 'provincia_id' in df.columns:
        mask_id_prov = df['provincia_id'].isin([99, 999, '99', '999'])
        filas_problematicas = df[mask_id_prov].index.tolist()
        filas_eliminadas_por_ids.extend(filas_problematicas)
        df = df[~mask_id_prov]
        if len(filas_problematicas) > 0:
            print(f"🗑️  Eliminadas {len(filas_problematicas)} filas con provincia_id problemático")
    
    # 5. Valores vacíos o espacios
    for col in df.columns:
        if df[col].dtype == 'object':
            mask_vacios = df[col].astype(str).str.strip().isin(['', 'nan', 'NaN', 'None', 'null', 'NULL'])
            filas_problematicas = df[mask_vacios].index.tolist()
            filas_eliminadas_por_vacios.extend(filas_problematicas)
            df = df[~mask_vacios]
            if len(filas_problematicas) > 0:
                print(f"🗑️  Eliminadas {len(filas_problematicas)} filas con valores vacíos en '{col}'")
    
    # Eliminar duplicados de las listas
    filas_eliminadas_por_desconocido = list(set(filas_eliminadas_por_desconocido))
    filas_eliminadas_por_ids = list(set(filas_eliminadas_por_ids))
    filas_eliminadas_por_vacios = list(set(filas_eliminadas_por_vacios))
    
    # Guardar archivo corregido
    df.to_csv(archivo, index=False, encoding='utf-8')
    
    # Resumen final
    filas_finales = len(df)
    total_eliminaciones = filas_originales - filas_finales
    
    print(f"\n📊 RESUMEN DE CORRECCIÓN:")
    print(f"   Filas originales: {filas_originales}")
    print(f"   Filas finales: {filas_finales}")
    print(f"   Total eliminadas: {total_eliminaciones}")
    print(f"   - Eliminaciones automáticas (dep+prov): {len(filas_eliminadas_automaticamente)}")
    print(f"   - Eliminaciones por nulos: {len(filas_eliminadas_por_nulos)}")
    print(f"   - Eliminaciones por desconocido: {len(filas_eliminadas_por_desconocido)}")
    print(f"   - Eliminaciones por IDs problemáticos: {len(filas_eliminadas_por_ids)}")
    print(f"   - Eliminaciones por valores vacíos: {len(filas_eliminadas_por_vacios)}")
    
    if total_eliminaciones > 0:
        print(f"✅ Archivo guardado con {total_eliminaciones} eliminaciones")
    else:
        print(f"✅ Archivo sin cambios necesarios")

def main():
    """
    Función principal - procesa todos los archivos automáticamente
    """
    if len(sys.argv) != 2:
        print("❌ Uso: python3 corregir_problemas_automatico.py <nombre_archivo.csv>")
        print("📁 Archivos disponibles:")
        base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
        for archivo in base_path.glob("dengue-*.csv"):
            print(f"   - {archivo.name}")
        return
    
    nombre_archivo = sys.argv[1]
    corregir_archivo_automatico(nombre_archivo)

if __name__ == "__main__":
    main()
