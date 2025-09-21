#!/usr/bin/env python3
"""
Script genérico para limpiar archivos CSV eliminando filas y columnas vacías
Uso: python3 limpiar_csv.py <archivo_entrada.csv>
"""

import pandas as pd
import sys
import os
from pathlib import Path

def limpiar_csv(archivo_entrada):
    """
    Limpia un archivo CSV eliminando filas y columnas vacías y sobrescribe el original
    
    Args:
        archivo_entrada (str): Ruta del archivo CSV a limpiar
    
    Returns:
        bool: True si la limpieza fue exitosa, False en caso contrario
    """
    try:
        print(f"Leyendo archivo: {archivo_entrada}")
        
        # Leer el archivo CSV con diferentes codificaciones
        try:
            df = pd.read_csv(archivo_entrada, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(archivo_entrada, encoding='latin-1')
            except UnicodeDecodeError:
                df = pd.read_csv(archivo_entrada, encoding='cp1252')
        
        print(f"Archivo original: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        # Eliminar filas completamente vacías (todas las columnas son NaN)
        df_limpio = df.dropna(how='all')
        filas_eliminadas = df.shape[0] - df_limpio.shape[0]
        
        # Eliminar columnas completamente vacías (todas las filas son NaN)
        df_limpio = df_limpio.dropna(axis=1, how='all')
        columnas_eliminadas = df.shape[1] - df_limpio.shape[1]
        
        # Eliminar filas que solo contienen espacios en blanco o valores vacíos
        # Convertir a string y verificar si está vacío después de quitar espacios
        for col in df_limpio.columns:
            if df_limpio[col].dtype == 'object':  # Solo para columnas de texto
                df_limpio[col] = df_limpio[col].astype(str).str.strip()
        
        # Eliminar filas donde todas las columnas son cadenas vacías o 'nan'
        mask = df_limpio.astype(str).apply(lambda x: x.str.strip()).eq('').all(axis=1) | \
               df_limpio.astype(str).apply(lambda x: x.str.strip()).eq('nan').all(axis=1)
        df_limpio = df_limpio[~mask]
        filas_vacias_eliminadas = mask.sum()
        
        print(f"Filas completamente vacías eliminadas: {filas_eliminadas}")
        print(f"Columnas completamente vacías eliminadas: {columnas_eliminadas}")
        print(f"Filas con solo espacios/vacías eliminadas: {filas_vacias_eliminadas}")
        print(f"Archivo limpio: {df_limpio.shape[0]} filas, {df_limpio.shape[1]} columnas")
        
        # Sobrescribir el archivo original
        df_limpio.to_csv(archivo_entrada, index=False, encoding='utf-8')
        print(f"✓ Archivo sobrescrito: {archivo_entrada}")
        
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: No se encontró el archivo '{archivo_entrada}'")
        return False
    except Exception as e:
        print(f"✗ Error al procesar el archivo: {str(e)}")
        return False

def main():
    """Función principal del script"""
    if len(sys.argv) < 2:
        print("✗ Error: Debes especificar un archivo CSV")
        print("Uso: python3 limpiar_csv.py archivo.csv")
        sys.exit(1)
    
    archivo_entrada = sys.argv[1]
    
    # Verificar que el archivo de entrada existe
    if not os.path.exists(archivo_entrada):
        print(f"✗ Error: El archivo '{archivo_entrada}' no existe")
        sys.exit(1)
    
    # Ejecutar la limpieza
    exito = limpiar_csv(archivo_entrada)
    
    if not exito:
        sys.exit(1)

if __name__ == "__main__":
    main()
