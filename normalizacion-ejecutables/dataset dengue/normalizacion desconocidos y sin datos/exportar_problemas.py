#!/usr/bin/env python3
"""
Script para exportar filas problemáticas a archivos CSV separados
Permite revisar y corregir los problemas de forma más cómoda
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def exportar_problemas_a_csv():
    """
    Exporta las filas problemáticas de cada archivo a CSVs separados
    """
    print("=== EXPORTACIÓN DE FILAS PROBLEMÁTICAS ===")
    
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    output_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/revision manual/problemas-identificados")
    
    # Crear directorio de salida si no existe
    output_path.mkdir(exist_ok=True)
    
    # Obtener todos los archivos CSV (excluyendo backup)
    archivos_csv = [f for f in base_path.glob("*.csv") if not f.name.startswith("backup")]
    archivos_csv.sort()
    
    print(f"Archivos a procesar: {len(archivos_csv)}")
    print(f"Directorio de salida: {output_path}")
    print()
    
    total_problemas_exportados = 0
    
    for archivo in archivos_csv:
        print(f"📁 Procesando: {archivo.name}")
        
        try:
            # Leer el archivo
            df = pd.read_csv(archivo, encoding='utf-8')
            
            # Lista para almacenar todas las filas problemáticas
            filas_problematicas = []
            tipos_problema = []
            
            # 1. Valores nulos
            filas_nulos = df[df.isnull().any(axis=1)]
            if not filas_nulos.empty:
                filas_problematicas.append(filas_nulos)
                tipos_problema.extend(['VALORES_NULOS'] * len(filas_nulos))
            
            # 2. Valores "desconocido"
            for col in df.columns:
                if df[col].dtype == 'object':
                    mask = df[col].astype(str).str.lower().isin(['desconocido', 'desconocida', 'unknown', 'n/a', 'na'])
                    if mask.any():
                        filas_desconocido = df[mask]
                        filas_problematicas.append(filas_desconocido)
                        tipos_problema.extend([f'DESCONOCIDO_EN_{col}'] * len(filas_desconocido))
            
            # 3. IDs problemáticos
            columnas_id = [col for col in df.columns if 'id' in col.lower()]
            for col in columnas_id:
                mask = df[col].astype(str).isin(['999', '99'])
                if mask.any():
                    filas_ids = df[mask]
                    filas_problematicas.append(filas_ids)
                    tipos_problema.extend([f'ID_PROBLEMATICO_EN_{col}'] * len(filas_ids))
            
            # 4. Valores vacíos
            for col in df.columns:
                if df[col].dtype == 'object':
                    mask = df[col].astype(str).str.strip().isin(['', 'nan', 'NaN', 'None', 'null', 'NULL'])
                    if mask.any():
                        filas_vacias = df[mask]
                        filas_problematicas.append(filas_vacias)
                        tipos_problema.extend([f'VALOR_VACIO_EN_{col}'] * len(filas_vacias))
            
            # Combinar todas las filas problemáticas
            if filas_problematicas:
                df_problemas = pd.concat(filas_problematicas, ignore_index=True)
                df_problemas = df_problemas.drop_duplicates()
                
                # Agregar columna con tipo de problema
                df_problemas['tipo_problema'] = tipos_problema[:len(df_problemas)]
                
                # Agregar número de fila original
                df_problemas['fila_original'] = df_problemas.index + 2  # +2 porque pandas indexa desde 0 y hay header
                
                # Exportar a CSV
                archivo_salida = output_path / f"problemas_{archivo.name}"
                df_problemas.to_csv(archivo_salida, index=False, encoding='utf-8')
                
                print(f"   ✅ Exportadas {len(df_problemas)} filas problemáticas a: {archivo_salida.name}")
                total_problemas_exportados += len(df_problemas)
                
                # Mostrar resumen de tipos de problemas
                tipos_unicos = df_problemas['tipo_problema'].value_counts()
                print(f"   📊 Tipos de problemas encontrados:")
                for tipo, cantidad in tipos_unicos.items():
                    print(f"      - {tipo}: {cantidad} filas")
            else:
                print(f"   ✅ No se encontraron problemas")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total de filas problemáticas exportadas: {total_problemas_exportados}")
    print(f"   Archivos de problemas guardados en: {output_path}")
    
    if total_problemas_exportados > 0:
        print(f"\n💡 PRÓXIMOS PASOS:")
        print(f"   1. Revisa los archivos CSV en {output_path}")
        print(f"   2. Corrige manualmente los valores problemáticos")
        print(f"   3. Ejecuta 'identificar_problemas.py' nuevamente para verificar")

def main():
    """Función principal"""
    exportar_problemas_a_csv()

if __name__ == "__main__":
    main()
