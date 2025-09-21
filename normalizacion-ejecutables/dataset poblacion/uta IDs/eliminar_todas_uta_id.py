#!/usr/bin/env python3
"""
Script para eliminar todas las columnas UTA_ID (incluyendo UTA_ID.1, UTA_ID.2, etc.) 
de todos los archivos CSV de población.
"""

import os
import pandas as pd
import glob

def eliminar_todas_columnas_uta_id():
    """
    Elimina todas las columnas que empiecen con 'UTA_ID' de todos los archivos CSV 
    en el directorio dataset-poblacion.
    """
    # Directorio donde están los archivos CSV
    directorio = "dataset-poblacion"
    
    # Verificar que el directorio existe
    if not os.path.exists(directorio):
        print(f"Error: El directorio '{directorio}' no existe.")
        return
    
    # Obtener todos los archivos CSV en el directorio
    archivos_csv = glob.glob(os.path.join(directorio, "*.csv"))
    
    if not archivos_csv:
        print(f"No se encontraron archivos CSV en el directorio '{directorio}'.")
        return
    
    print(f"Procesando {len(archivos_csv)} archivos CSV...")
    
    archivos_procesados = 0
    archivos_con_uta_id = 0
    total_columnas_eliminadas = 0
    
    for archivo in archivos_csv:
        try:
            # Leer el archivo CSV
            df = pd.read_csv(archivo)
            
            # Encontrar todas las columnas que empiecen con 'UTA_ID'
            columnas_uta_id = [col for col in df.columns if col.startswith('UTA_ID')]
            
            if columnas_uta_id:
                # Mostrar qué columnas se van a eliminar
                print(f"✓ {os.path.basename(archivo)}: Eliminando columnas {columnas_uta_id}")
                
                # Eliminar todas las columnas UTA_ID
                df = df.drop(columns=columnas_uta_id)
                
                # Guardar el archivo modificado
                df.to_csv(archivo, index=False)
                
                archivos_con_uta_id += 1
                total_columnas_eliminadas += len(columnas_uta_id)
            else:
                print(f"- {os.path.basename(archivo)}: No tiene columnas UTA_ID")
            
            archivos_procesados += 1
            
        except Exception as e:
            print(f"✗ Error procesando {os.path.basename(archivo)}: {str(e)}")
    
    print(f"\nResumen:")
    print(f"- Archivos procesados: {archivos_procesados}")
    print(f"- Archivos con columnas UTA_ID eliminadas: {archivos_con_uta_id}")
    print(f"- Total de columnas UTA_ID eliminadas: {total_columnas_eliminadas}")
    print(f"- Archivos sin columnas UTA_ID: {archivos_procesados - archivos_con_uta_id}")

if __name__ == "__main__":
    eliminar_todas_columnas_uta_id()
