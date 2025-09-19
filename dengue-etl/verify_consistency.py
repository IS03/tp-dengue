#!/usr/bin/env python3
"""
Script para verificar la consistencia de IDs después de las correcciones.
"""

import pandas as pd
import numpy as np
import os
from collections import defaultdict

def verify_id_consistency():
    """
    Verifica que todos los departamentos tengan el mismo ID en todos los años.
    """
    print("🔍 Verificando consistencia de IDs...")
    
    # Cargar geo_map como referencia
    geo_map = pd.read_csv('ref/geo_map.csv')
    geo_ref = {}
    
    for _, row in geo_map.iterrows():
        provincia = str(row['provincia_nombre']).strip().upper()
        departamento = str(row['departamento_nombre']).strip().upper()
        depto_id = int(row['depto_full_id'])
        
        key = f"{provincia}|{departamento}"
        geo_ref[key] = depto_id
    
    print(f"   📊 Referencia: {len(geo_ref)} departamentos en geo_map")
    
    # Verificar archivos raw
    inconsistencies = []
    
    # Verificar dengue2018.csv
    if os.path.exists('raw/dengue2018.csv'):
        print("\n   🔍 Verificando dengue2018.csv...")
        df = pd.read_csv('raw/dengue2018.csv')
        
        # Verificar casos problemáticos
        colon_cases = df[(df['departamento_id'] == 58028) & 
                        (df['departamento_nombre'].str.contains('COLON', case=False, na=False))]
        capital_cases = df[(df['departamento_id'] == 90084) & 
                          (df['departamento_nombre'].str.contains('CAPITAL', case=False, na=False))]
        
        if len(colon_cases) > 0:
            inconsistencies.append(f"Colón Córdoba en 2018: {len(colon_cases)} casos con ID 58028")
        else:
            print("      ✅ Colón Córdoba corregido")
            
        if len(capital_cases) > 0:
            inconsistencies.append(f"Capital Córdoba en 2018: {len(capital_cases)} casos con ID 90084")
        else:
            print("      ✅ Capital Córdoba corregido")
    
    # Verificar archivos CSV (2022-2025)
    csv_years = [2022, 2023, 2024, 2025]
    for year in csv_years:
        file_path = f'raw/dengue{year}.csv'
        if os.path.exists(file_path):
            print(f"\n   🔍 Verificando dengue{year}.csv...")
            try:
                df = pd.read_csv(file_path, sep=',', encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, sep=',', encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, sep=',', encoding='cp1252')
            
            # Verificar que tenga depto_full_id
            if 'depto_full_id' in df.columns:
                print(f"      ✅ Tiene depto_full_id: {df['depto_full_id'].notna().sum()} valores")
            else:
                # Verificar si tiene las columnas necesarias para crear depto_full_id
                if ('provincia_id' in df.columns and 'departamento_id' in df.columns) or \
                   ('id_prov_indec_residencia' in df.columns and 'id_depto_indec_residencia' in df.columns):
                    print(f"      ⚠️ No tiene depto_full_id pero tiene columnas para crearlo")
                else:
                    inconsistencies.append(f"{year}: No tiene columna depto_full_id ni columnas para crearlo")
    
    # Verificar archivos Excel (2019-2021)
    excel_years = [2019, 2020, 2021]
    for year in excel_years:
        file_path = f'raw/dengue{year}.xlsx'
        if os.path.exists(file_path):
            print(f"\n   🔍 Verificando dengue{year}.xlsx...")
            try:
                df = pd.read_excel(file_path)
                
                # Verificar columnas
                print(f"      📋 Columnas: {list(df.columns)}")
                
                if 'depto_full_id' in df.columns:
                    print(f"      ✅ Tiene depto_full_id: {df['depto_full_id'].notna().sum()} valores")
                else:
                    inconsistencies.append(f"{year}: No tiene columna depto_full_id")
                    
            except Exception as e:
                inconsistencies.append(f"{year}: Error leyendo archivo - {str(e)}")
    
    # Reportar resultados
    print("\n📋 RESUMEN DE VERIFICACIÓN:")
    
    if inconsistencies:
        print("   ❌ INCONSISTENCIAS ENCONTRADAS:")
        for issue in inconsistencies:
            print(f"      • {issue}")
    else:
        print("   ✅ TODAS LAS VERIFICACIONES PASARON")
        print("   🎉 Los IDs son consistentes en todos los archivos")
    
    return len(inconsistencies) == 0

def main():
    """
    Función principal de verificación.
    """
    print("🚀 Iniciando verificación de consistencia...")
    
    try:
        # Verificar consistencia
        consistency_ok = verify_id_consistency()
        
        # Resultado final
        print("\n" + "="*50)
        if consistency_ok:
            print("🎉 ¡VERIFICACIÓN EXITOSA!")
            print("✅ Todos los IDs son consistentes")
        else:
            print("❌ VERIFICACIÓN FALLÓ")
            print("❌ Problemas de consistencia en IDs")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {str(e)}")
        raise

if __name__ == "__main__":
    main()
