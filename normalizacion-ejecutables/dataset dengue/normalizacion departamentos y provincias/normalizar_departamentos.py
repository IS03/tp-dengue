1#!/usr/bin/env python3
"""
Script para normalizar la columna departamento_nombre en los archivos de dengue.
- Cambia "quimes" por "quilmes"
- Cambia palabras que contienen "grl" por "general"
"""

import os
import csv
import re
from pathlib import Path

def normalizar_departamentos_en_archivo(archivo_path):
    """
    Normaliza la columna departamento_nombre en un archivo CSV.
    
    Args:
        archivo_path (str): Ruta al archivo CSV a normalizar
    """
    print(f"Procesando: {archivo_path}")
    
    # Leer el archivo original
    filas_modificadas = 0
    filas_totales = 0
    
    with open(archivo_path, 'r', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        filas = list(lector)
    
    # Procesar cada fila
    for i, fila in enumerate(filas):
        filas_totales += 1
        if len(fila) >= 2:  # Asegurar que hay al menos 2 columnas
            # Columna B (departamento_nombre) es índice 1
            departamento_original = fila[1]
            departamento_modificado = departamento_original
            
            # Cambiar "quimes" por "quilmes"
            if departamento_original.lower() == "quimes":
                departamento_modificado = "quilmes"
                filas_modificadas += 1
            
            # Cambiar palabras que contienen "grl" por "general"
            # Usar regex para encontrar palabras que contengan "grl" (case insensitive)
            if re.search(r'\b\w*grl\w*\b', departamento_original, re.IGNORECASE):
                # Reemplazar cualquier palabra que contenga "grl" con "general"
                departamento_modificado = re.sub(r'\b\w*grl\w*\b', 'general', departamento_original, flags=re.IGNORECASE)
                filas_modificadas += 1
            
            # Actualizar la fila si hubo cambios
            if departamento_modificado != departamento_original:
                fila[1] = departamento_modificado
    
    # Escribir el archivo modificado
    with open(archivo_path, 'w', encoding='utf-8', newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerows(filas)
    
    print(f"  Filas procesadas: {filas_totales}")
    print(f"  Filas modificadas: {filas_modificadas}")
    print(f"  ✓ Archivo normalizado exitosamente\n")
    
    return filas_modificadas

def main():
    """Función principal que procesa todos los archivos de dengue 2018-2025."""
    
    # Directorio base
    directorio_base = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    
    # Lista de archivos a procesar (solo los archivos principales, no los backups)
    archivos_a_procesar = []
    for año in range(2018, 2026):  # 2018 a 2025
        archivo = directorio_base / f"dengue-{año}.csv"
        if archivo.exists():
            archivos_a_procesar.append(archivo)
        else:
            print(f"⚠️  Archivo no encontrado: {archivo}")
    
    print(f"Archivos encontrados para procesar: {len(archivos_a_procesar)}")
    print("=" * 60)
    
    total_modificaciones = 0
    
    # Procesar cada archivo
    for archivo in archivos_a_procesar:
        try:
            modificaciones = normalizar_departamentos_en_archivo(str(archivo))
            total_modificaciones += modificaciones
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")
    
    print("=" * 60)
    print(f"RESUMEN:")
    print(f"Archivos procesados: {len(archivos_a_procesar)}")
    print(f"Total de modificaciones realizadas: {total_modificaciones}")
    print("✓ Normalización completada")

if __name__ == "__main__":
    main()
