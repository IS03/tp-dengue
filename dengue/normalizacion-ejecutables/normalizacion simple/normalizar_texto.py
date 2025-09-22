#!/usr/bin/env python3
"""
Script para normalizar texto en archivos CSV
- Convierte todo a minúsculas
- Quita tildes y acentos
- Elimina caracteres especiales, puntos, comas, etc.
- Deja solo letras y números
"""

import pandas as pd
import os
import re
import unicodedata
from pathlib import Path

def normalizar_texto(texto):
    """
    Normaliza un texto eliminando tildes, caracteres especiales y convirtiendo a minúsculas
    
    Args:
        texto: El texto a normalizar
    
    Returns:
        str: Texto normalizado
    """
    if pd.isna(texto) or texto == '':
        return texto
    
    # Convertir a string si no lo es
    texto = str(texto)
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Quitar tildes y acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    
    # Quitar caracteres especiales, puntos, comas, etc. - dejar solo letras, números y espacios
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    
    # Quitar espacios múltiples y espacios al inicio/final
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

def normalizar_archivo_csv(archivo_path, excluir_columnas=None):
    """
    Normaliza el texto en un archivo CSV
    
    Args:
        archivo_path (str): Ruta del archivo CSV
        excluir_columnas (list): Lista de nombres de columnas a excluir de la normalización
    
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    try:
        print(f"Procesando: {archivo_path}")
        
        # Leer el archivo con diferentes codificaciones
        df = None
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(archivo_path, encoding=encoding)
                print(f"  ✓ Leído con codificación: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print(f"  ✗ No se pudo leer el archivo con ninguna codificación")
            return False
        
        print(f"  Archivo original: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        # Normalizar todas las columnas de texto, excluyendo las especificadas
        columnas_procesadas = 0
        columnas_excluidas = 0
        
        for columna in df.columns:
            if df[columna].dtype == 'object':  # Solo columnas de texto
                if excluir_columnas and columna in excluir_columnas:
                    print(f"  ⚠️  Excluyendo columna: {columna}")
                    columnas_excluidas += 1
                else:
                    df[columna] = df[columna].apply(normalizar_texto)
                    columnas_procesadas += 1
        
        print(f"  Columnas de texto normalizadas: {columnas_procesadas}")
        if columnas_excluidas > 0:
            print(f"  Columnas excluidas: {columnas_excluidas}")
        
        # Guardar el archivo normalizado
        df.to_csv(archivo_path, index=False, encoding='utf-8')
        print(f"  ✓ Archivo normalizado guardado")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error al procesar {archivo_path}: {str(e)}")
        return False

def main():
    """Función principal que procesa solo los archivos CSV de dataset-departamentos"""
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue")
    carpeta_departamentos = base_path / "dataset-departamentos"
    
    # Columnas a excluir de la normalización (latitud y longitud)
    columnas_excluir = ["Latitud", "Longitud"]
    
    archivos_procesados = 0
    archivos_exitosos = 0
    
    print("=== NORMALIZACIÓN DE TEXTO EN ARCHIVOS CSV ===")
    print(f"Procesando solo: {carpeta_departamentos}")
    print(f"Excluyendo columnas: {', '.join(columnas_excluir)}")
    print()
    
    if not carpeta_departamentos.exists():
        print(f"✗ Carpeta no encontrada: {carpeta_departamentos}")
        return
    
    # Buscar todos los archivos CSV en la carpeta dataset-departamentos
    archivos_csv = list(carpeta_departamentos.glob("*.csv"))
    
    if not archivos_csv:
        print(f"  No se encontraron archivos CSV en dataset-departamentos")
        return
    
    for archivo in archivos_csv:
        archivos_procesados += 1
        if normalizar_archivo_csv(archivo, excluir_columnas=columnas_excluir):
            archivos_exitosos += 1
        print()
    
    print("=== RESUMEN ===")
    print(f"Archivos procesados: {archivos_procesados}")
    print(f"Archivos exitosos: {archivos_exitosos}")
    print(f"Archivos con errores: {archivos_procesados - archivos_exitosos}")
    
    if archivos_exitosos == archivos_procesados:
        print("🎉 ¡Todos los archivos fueron normalizados exitosamente!")
    else:
        print("⚠️  Algunos archivos tuvieron errores durante la normalización")

if __name__ == "__main__":
    main()
