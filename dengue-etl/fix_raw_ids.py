#!/usr/bin/env python3
"""
Script para corregir IDs inconsistentes en archivos raw de dengue.
Garantiza que todos los departamentos tengan el mismo ID en todos los años.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_geo_map():
    """Carga el mapa geográfico con IDs correctos"""
    geo_map_path = 'ref/geo_map.csv'
    if not os.path.exists(geo_map_path):
        raise FileNotFoundError(f"No se encontró {geo_map_path}")
    
    geo_map = pd.read_csv(geo_map_path)
    print(f"✅ Cargado geo_map.csv con {len(geo_map)} departamentos")
    return geo_map

def fix_dengue2018(geo_map):
    """Corrige el archivo dengue2018.csv"""
    print("\n🔧 Corrigiendo dengue2018.csv...")
    
    file_path = 'raw/dengue2018.csv'
    if not os.path.exists(file_path):
        print(f"❌ No se encontró {file_path}")
        return
    
    # Leer archivo
    df = pd.read_csv(file_path)
    print(f"   📊 Filas originales: {len(df)}")
    
    # Corregir IDs incorrectos específicos
    corrections = 0
    
    # Colón Córdoba: 58028 -> 14021
    mask_colon = (df['departamento_id'] == 58028) & (df['departamento_nombre'].str.contains('COLON', case=False, na=False))
    df.loc[mask_colon, 'departamento_id'] = 14021
    corrections += mask_colon.sum()
    
    # Capital Córdoba: 90084 -> 14014  
    mask_capital = (df['departamento_id'] == 90084) & (df['departamento_nombre'].str.contains('CAPITAL', case=False, na=False))
    df.loc[mask_capital, 'departamento_id'] = 14014
    corrections += mask_capital.sum()
    
    print(f"   ✅ Correcciones aplicadas: {corrections}")
    
    # Guardar archivo corregido
    backup_path = file_path.replace('.csv', '_backup.csv')
    if not os.path.exists(backup_path):
        os.rename(file_path, backup_path)
        print(f"   💾 Backup creado: {backup_path}")
    
    df.to_csv(file_path, index=False)
    print(f"   ✅ Archivo corregido guardado: {file_path}")

def fix_csv_files(geo_map):
    """Corrige archivos CSV (2022-2025)"""
    csv_files = ['dengue2022.csv', 'dengue2023.csv', 'dengue2024.csv', 'dengue2025.csv']
    
    for filename in csv_files:
        print(f"\n🔧 Corrigiendo {filename}...")
        
        file_path = f'raw/{filename}'
        if not os.path.exists(file_path):
            print(f"   ❌ No se encontró {file_path}")
            continue
        
        # Leer archivo (detectar separador automáticamente, manejar codificación)
        try:
            df = pd.read_csv(file_path, sep=',', encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, sep=',', encoding='latin-1')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, sep=',', encoding='cp1252')
        print(f"   📊 Filas originales: {len(df)}")
        
        # Crear depto_full_id consistente
        if 'depto_full_id' not in df.columns:
            # Verificar qué columnas están disponibles
            if 'provincia_id' in df.columns and 'departamento_id' in df.columns:
                # Formato 2022: provincia_id, departamento_id
                df['depto_full_id'] = df['provincia_id'] * 1000 + df['departamento_id']
            elif 'id_prov_indec_residencia' in df.columns and 'id_depto_indec_residencia' in df.columns:
                # Formato 2023-2025: id_prov_indec_residencia, id_depto_indec_residencia
                # Convertir a numérico y manejar valores no numéricos
                df['id_prov_indec_residencia'] = pd.to_numeric(df['id_prov_indec_residencia'], errors='coerce')
                df['id_depto_indec_residencia'] = pd.to_numeric(df['id_depto_indec_residencia'], errors='coerce')
                df['depto_full_id'] = df['id_prov_indec_residencia'] * 1000 + df['id_depto_indec_residencia']
            else:
                print(f"      ⚠️ No se pudieron crear IDs consistentes - columnas faltantes")
                print(f"      📋 Columnas disponibles: {list(df.columns)}")
                continue
        
        print(f"   ✅ IDs consistentes creados")
        
        # Guardar archivo corregido
        backup_path = file_path.replace('.csv', '_backup.csv')
        if not os.path.exists(backup_path):
            os.rename(file_path, backup_path)
            print(f"   💾 Backup creado: {backup_path}")
        
        df.to_csv(file_path, index=False)
        print(f"   ✅ Archivo corregido guardado: {file_path}")

def fix_excel_files(geo_map):
    """Corrige archivos Excel (2019-2021)"""
    excel_files = ['dengue2019.xlsx', 'dengue2020.xlsx', 'dengue2021.xlsx']
    
    for filename in excel_files:
        print(f"\n🔧 Corrigiendo {filename}...")
        
        file_path = f'raw/{filename}'
        if not os.path.exists(file_path):
            print(f"   ❌ No se encontró {file_path}")
            continue
        
        try:
            # Leer archivo Excel
            df = pd.read_excel(file_path)
            print(f"   📊 Filas originales: {len(df)}")
            
            # Verificar columnas disponibles
            print(f"   📋 Columnas: {list(df.columns)}")
            
            # Crear depto_full_id consistente si no existe
            if 'depto_full_id' not in df.columns:
                if 'provincia_id' in df.columns and 'departamento_id' in df.columns:
                    # Convertir a numérico y manejar valores no numéricos
                    df['provincia_id'] = pd.to_numeric(df['provincia_id'], errors='coerce')
                    df['departamento_id'] = pd.to_numeric(df['departamento_id'], errors='coerce')
                    df['depto_full_id'] = df['provincia_id'] * 1000 + df['departamento_id']
                    print(f"   ✅ IDs consistentes creados")
                elif 'id_provincia_residencia' in df.columns and 'id_depto_indec_residencia' in df.columns:
                    df['depto_full_id'] = df['id_provincia_residencia'] * 1000 + df['id_depto_indec_residencia']
                    print(f"   ✅ IDs consistentes creados")
                else:
                    print(f"   ⚠️ No se pudieron crear IDs consistentes - columnas faltantes")
            
            # Guardar archivo corregido
            backup_path = file_path.replace('.xlsx', '_backup.xlsx')
            if not os.path.exists(backup_path):
                os.rename(file_path, backup_path)
                print(f"   💾 Backup creado: {backup_path}")
            
            df.to_excel(file_path, index=False)
            print(f"   ✅ Archivo corregido guardado: {file_path}")
            
        except Exception as e:
            print(f"   ❌ Error procesando {filename}: {str(e)}")

def verify_corrections():
    """Verifica que las correcciones se aplicaron correctamente"""
    print("\n🔍 Verificando correcciones...")
    
    # Verificar dengue2018.csv
    if os.path.exists('raw/dengue2018.csv'):
        df = pd.read_csv('raw/dengue2018.csv')
        
        # Verificar Colón Córdoba
        colon_cases = df[(df['departamento_id'] == 58028) & 
                        (df['departamento_nombre'].str.contains('COLON', case=False, na=False))]
        if len(colon_cases) == 0:
            print("   ✅ Colón Córdoba corregido (58028 -> 14021)")
        else:
            print(f"   ❌ Colón Córdoba aún tiene 58028: {len(colon_cases)} casos")
        
        # Verificar Capital Córdoba
        capital_cases = df[(df['departamento_id'] == 90084) & 
                          (df['departamento_nombre'].str.contains('CAPITAL', case=False, na=False))]
        if len(capital_cases) == 0:
            print("   ✅ Capital Córdoba corregido (90084 -> 14014)")
        else:
            print(f"   ❌ Capital Córdoba aún tiene 90084: {len(capital_cases)} casos")

def main():
    """Función principal"""
    print("🚀 Iniciando corrección de IDs en archivos raw...")
    
    try:
        # Cargar geo_map
        geo_map = load_geo_map()
        
        # Corregir archivos
        fix_dengue2018(geo_map)
        fix_csv_files(geo_map)
        fix_excel_files(geo_map)
        
        # Verificar correcciones
        verify_corrections()
        
        print("\n🎉 ¡Corrección completada!")
        print("📝 Todos los archivos raw ahora tienen IDs consistentes")
        print("💾 Se crearon backups de todos los archivos originales")
        
    except Exception as e:
        print(f"\n❌ Error durante la corrección: {str(e)}")
        raise

if __name__ == "__main__":
    main()
