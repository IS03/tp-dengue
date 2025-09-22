#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar la columna 'poblacion' de los archivos CSV de dengue.
"""

import pandas as pd
import os
from pathlib import Path

def eliminar_columna_poblacion(archivo_csv):
    """
    Elimina la columna 'poblacion' de un archivo CSV.
    
    Args:
        archivo_csv (str): Ruta al archivo CSV
        
    Returns:
        bool: True si se eliminó exitosamente, False en caso contrario
    """
    try:
        # Leer el archivo CSV
        print(f"Procesando: {archivo_csv}")
        df = pd.read_csv(archivo_csv)
        
        # Verificar si la columna 'poblacion' existe
        if 'poblacion' not in df.columns:
            print(f"  ⚠️  La columna 'poblacion' no existe en {archivo_csv}")
            return False
        
        # Eliminar la columna 'poblacion'
        df_sin_poblacion = df.drop('poblacion', axis=1)
        
        # Guardar el archivo modificado
        df_sin_poblacion.to_csv(archivo_csv, index=False)
        
        print(f"  ✅ Columna 'poblacion' eliminada exitosamente de {archivo_csv}")
        print(f"     Columnas restantes: {list(df_sin_poblacion.columns)}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error procesando {archivo_csv}: {str(e)}")
        return False

def main():
    """
    Función principal que procesa todos los archivos de dengue especificados.
    """
    # Directorio base
    directorio_base = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    
    # Lista de archivos a procesar
    archivos_dengue = [
        "dengue-2025.csv",
        "dengue-2023.csv", 
        "dengue-2018.csv",
        "dengue-2022.csv",
        "dengue-2021.csv",
        "dengue-2019.csv",
        "dengue-2020.csv"
    ]
    
    print("🗑️  Eliminando columna 'poblacion' de archivos de dengue...")
    print("=" * 60)
    
    archivos_procesados = 0
    archivos_exitosos = 0
    
    for archivo in archivos_dengue:
        ruta_archivo = directorio_base / archivo
        
        if ruta_archivo.exists():
            archivos_procesados += 1
            if eliminar_columna_poblacion(ruta_archivo):
                archivos_exitosos += 1
        else:
            print(f"⚠️  Archivo no encontrado: {ruta_archivo}")
    
    print("=" * 60)
    print(f"📊 Resumen:")
    print(f"   Archivos procesados: {archivos_procesados}")
    print(f"   Archivos exitosos: {archivos_exitosos}")
    print(f"   Archivos con errores: {archivos_procesados - archivos_exitosos}")
    
    if archivos_exitosos == archivos_procesados:
        print("🎉 ¡Todos los archivos fueron procesados exitosamente!")
    else:
        print("⚠️  Algunos archivos tuvieron problemas durante el procesamiento.")

if __name__ == "__main__":
    main()
