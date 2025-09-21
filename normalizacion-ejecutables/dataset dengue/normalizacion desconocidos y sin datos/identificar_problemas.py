#!/usr/bin/env python3
"""
Script para identificar filas problemáticas en los archivos de dengue
Muestra filas con valores nulos, desconocidos, vacíos o problemáticos
NO modifica los archivos, solo reporta los problemas
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def identificar_valores_problematicos():
    """
    Identifica valores problemáticos en todos los archivos de dengue
    """
    print("=== IDENTIFICACIÓN DE VALORES PROBLEMÁTICOS ===")
    
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    
    # Obtener todos los archivos CSV (excluyendo backup)
    archivos_csv = [f for f in base_path.glob("*.csv") if not f.name.startswith("backup")]
    archivos_csv.sort()
    
    print(f"Archivos a revisar: {len(archivos_csv)}")
    for archivo in archivos_csv:
        print(f"  - {archivo.name}")
    print()
    
    # Definir valores problemáticos
    valores_problematicos = {
        'desconocido': ['desconocido', 'desconocida', 'unknown', 'n/a', 'na'],
        'ids_desconocidos': [999, 99, '999', '99'],
        'valores_vacios': ['', ' ', '  ', 'nan', 'NaN', 'None', 'null', 'NULL'],
        'valores_numericos_problematicos': [0, '0']  # Para campos que no deberían ser 0
    }
    
    total_problemas = 0
    
    for archivo in archivos_csv:
        print(f"\n{'='*60}")
        print(f"📁 ANALIZANDO: {archivo.name}")
        print(f"{'='*60}")
        
        try:
            # Leer el archivo
            df = pd.read_csv(archivo, encoding='utf-8')
            print(f"Total de filas: {len(df)}")
            print(f"Total de columnas: {len(df.columns)}")
            
            problemas_archivo = 0
            
            # 1. Verificar valores nulos (NaN)
            print(f"\n🔍 1. VALORES NULOS (NaN):")
            filas_con_nulos = df.isnull().any(axis=1)
            if filas_con_nulos.any():
                filas_nulos = df[filas_con_nulos]
                print(f"   ❌ Encontradas {len(filas_nulos)} filas con valores nulos:")
                for idx, row in filas_nulos.iterrows():
                    columnas_nulas = [col for col in df.columns if pd.isnull(row[col])]
                    print(f"      Fila {idx + 2}: Columnas nulas: {columnas_nulas}")
                    print(f"      Datos: {dict(row)}")
                    print()
                problemas_archivo += len(filas_nulos)
            else:
                print(f"   ✅ No hay valores nulos")
            
            # 2. Verificar valores "desconocido"
            print(f"\n🔍 2. VALORES 'DESCONOCIDO':")
            filas_desconocido = pd.DataFrame()
            for col in df.columns:
                if df[col].dtype == 'object':  # Solo columnas de texto
                    mask = df[col].astype(str).str.lower().isin([v.lower() for v in valores_problematicos['desconocido']])
                    if mask.any():
                        filas_desconocido = pd.concat([filas_desconocido, df[mask]], ignore_index=True)
            
            if not filas_desconocido.empty:
                filas_desconocido = filas_desconocido.drop_duplicates()
                print(f"   ❌ Encontradas {len(filas_desconocido)} filas con valores 'desconocido':")
                for idx, row in filas_desconocido.iterrows():
                    print(f"      Fila {idx + 2}: {dict(row)}")
                    print()
                problemas_archivo += len(filas_desconocido)
            else:
                print(f"   ✅ No hay valores 'desconocido'")
            
            # 3. Verificar IDs problemáticos (999, 99)
            print(f"\n🔍 3. IDs PROBLEMÁTICOS (999, 99):")
            columnas_id = [col for col in df.columns if 'id' in col.lower()]
            filas_ids_problematicos = pd.DataFrame()
            
            for col in columnas_id:
                mask = df[col].astype(str).isin([str(v) for v in valores_problematicos['ids_desconocidos']])
                if mask.any():
                    filas_ids_problematicos = pd.concat([filas_ids_problematicos, df[mask]], ignore_index=True)
            
            if not filas_ids_problematicos.empty:
                filas_ids_problematicos = filas_ids_problematicos.drop_duplicates()
                print(f"   ❌ Encontradas {len(filas_ids_problematicos)} filas con IDs problemáticos:")
                for idx, row in filas_ids_problematicos.iterrows():
                    print(f"      Fila {idx + 2}: {dict(row)}")
                    print()
                problemas_archivo += len(filas_ids_problematicos)
            else:
                print(f"   ✅ No hay IDs problemáticos")
            
            # 4. Verificar valores vacíos o solo espacios
            print(f"\n🔍 4. VALORES VACÍOS O SOLO ESPACIOS:")
            filas_vacias = pd.DataFrame()
            for col in df.columns:
                if df[col].dtype == 'object':  # Solo columnas de texto
                    # Convertir a string y verificar si está vacío después de quitar espacios
                    mask = df[col].astype(str).str.strip().isin(valores_problematicos['valores_vacios'])
                    if mask.any():
                        filas_vacias = pd.concat([filas_vacias, df[mask]], ignore_index=True)
            
            if not filas_vacias.empty:
                filas_vacias = filas_vacias.drop_duplicates()
                print(f"   ❌ Encontradas {len(filas_vacias)} filas con valores vacíos:")
                for idx, row in filas_vacias.iterrows():
                    print(f"      Fila {idx + 2}: {dict(row)}")
                    print()
                problemas_archivo += len(filas_vacias)
            else:
                print(f"   ✅ No hay valores vacíos")
            
            # 5. Verificar inconsistencias en datos
            print(f"\n🔍 5. INCONSISTENCIAS EN DATOS:")
            inconsistencias = 0
            
            # Verificar que departamento_id y departamento_nombre coincidan
            if 'departamento_id' in df.columns and 'departamento_nombre' in df.columns:
                # Filas donde el ID es 999 pero el nombre no es "desconocido"
                mask_inconsistente = (df['departamento_id'].astype(str) == '999') & \
                                   (df['departamento_nombre'].astype(str).str.lower() != 'desconocido')
                if mask_inconsistente.any():
                    filas_inconsistente = df[mask_inconsistente]
                    print(f"   ❌ Encontradas {len(filas_inconsistente)} filas con inconsistencia departamento:")
                    for idx, row in filas_inconsistente.iterrows():
                        print(f"      Fila {idx + 2}: ID={row['departamento_id']}, Nombre='{row['departamento_nombre']}'")
                        print()
                    inconsistencias += len(filas_inconsistente)
            
            # Verificar que provincia_id y provincia_nombre coincidan
            if 'provincia_id' in df.columns and 'provincia_nombre' in df.columns:
                mask_inconsistente = (df['provincia_id'].astype(str) == '99') & \
                                   (df['provincia_nombre'].astype(str).str.lower() != 'desconocida')
                if mask_inconsistente.any():
                    filas_inconsistente = df[mask_inconsistente]
                    print(f"   ❌ Encontradas {len(filas_inconsistente)} filas con inconsistencia provincia:")
                    for idx, row in filas_inconsistente.iterrows():
                        print(f"      Fila {idx + 2}: ID={row['provincia_id']}, Nombre='{row['provincia_nombre']}'")
                        print()
                    inconsistencias += len(filas_inconsistente)
            
            if inconsistencias == 0:
                print(f"   ✅ No hay inconsistencias detectadas")
            
            problemas_archivo += inconsistencias
            
            # Resumen del archivo
            print(f"\n📊 RESUMEN DE {archivo.name}:")
            print(f"   Total de problemas encontrados: {problemas_archivo}")
            if problemas_archivo == 0:
                print(f"   ✅ ¡Archivo sin problemas detectados!")
            else:
                print(f"   ⚠️  Archivo requiere revisión manual")
            
            total_problemas += problemas_archivo
            
        except Exception as e:
            print(f"❌ Error procesando {archivo.name}: {str(e)}")
    
    # Resumen general
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN GENERAL")
    print(f"{'='*60}")
    print(f"Total de archivos procesados: {len(archivos_csv)}")
    print(f"Total de problemas encontrados: {total_problemas}")
    
    if total_problemas == 0:
        print(f"🎉 ¡TODOS LOS ARCHIVOS ESTÁN LIMPIOS!")
    else:
        print(f"⚠️  SE ENCONTRARON {total_problemas} PROBLEMAS QUE REQUIEREN REVISIÓN MANUAL")
        print(f"\n💡 RECOMENDACIONES:")
        print(f"   1. Revisa cada fila problemática mostrada arriba")
        print(f"   2. Corrige manualmente los valores incorrectos")
        print(f"   3. Ejecuta este script nuevamente para verificar las correcciones")
    
    return total_problemas

def analizar_archivo_especifico(nombre_archivo):
    """
    Analiza un archivo específico en detalle
    """
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    archivo = base_path / nombre_archivo
    
    if not archivo.exists():
        print(f"❌ Error: El archivo '{nombre_archivo}' no existe")
        return
    
    print(f"=== ANÁLISIS DETALLADO DE {nombre_archivo} ===")
    
    try:
        df = pd.read_csv(archivo, encoding='utf-8')
        print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"Columnas: {list(df.columns)}")
        
        # Mostrar estadísticas básicas
        print(f"\n📊 ESTADÍSTICAS BÁSICAS:")
        for col in df.columns:
            if df[col].dtype == 'object':
                valores_unicos = df[col].nunique()
                print(f"   {col}: {valores_unicos} valores únicos")
            else:
                print(f"   {col}: min={df[col].min()}, max={df[col].max()}, media={df[col].mean():.2f}")
        
        # Mostrar primeras y últimas filas
        print(f"\n📋 PRIMERAS 5 FILAS:")
        print(df.head().to_string())
        
        print(f"\n📋 ÚLTIMAS 5 FILAS:")
        print(df.tail().to_string())
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        # Si se especifica un archivo, analizarlo en detalle
        archivo = sys.argv[1]
        analizar_archivo_especifico(archivo)
    else:
        # Análisis general de todos los archivos
        identificar_valores_problematicos()

if __name__ == "__main__":
    main()
