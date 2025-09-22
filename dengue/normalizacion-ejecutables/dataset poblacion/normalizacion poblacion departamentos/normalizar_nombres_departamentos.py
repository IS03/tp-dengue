#!/usr/bin/env python3
"""
Script para normalizar nombres de departamentos en archivos de población.

Modificaciones a realizar:
1. Si la columna A dice "capital", agregar el nombre de la provincia
2. Corregir "general angel v penaloza" a "general angel vera penaloza"
3. Cambiar "tierra del fuego" a "tierra del fuego antartida e islas del atlantico sur"
"""

import csv
import os
import re

def get_province_name_from_filename(filename):
    """Extrae el nombre de la provincia del nombre del archivo"""
    # Remover la extensión .csv
    name = filename.replace('.csv', '')
    
    # Mapeo de nombres de archivo a nombres de provincia
    province_mapping = {
        'buenos aires': 'buenos aires',
        'caba': 'ciudad autonoma de buenos aires',
        'catamarca': 'catamarca',
        'chaco': 'chaco',
        'chubut': 'chubut',
        'cordoba': 'cordoba',
        'corrientes': 'corrientes',
        'entre rios': 'entre rios',
        'formosa': 'formosa',
        'jujuy': 'jujuy',
        'la pampa': 'la pampa',
        'la rioja': 'la rioja',
        'mendoza': 'mendoza',
        'tucuman': 'tucuman',
        'tierra del fuego antartida e islas del atlantico sur': 'tierra del fuego antartida e islas del atlantico sur',
        'santiago del estero': 'santiago del estero',
        'santa fe': 'santa fe',
        'santa cruz': 'santa cruz',
        'san juan': 'san juan',
        'san luis': 'san luis',
        'salta': 'salta',
        'rio negro': 'rio negro',
        'neuquen': 'neuquen',
        'misiones': 'misiones'
    }
    
    return province_mapping.get(name.lower(), name)

def normalize_department_name(department_name, province_name, filename):
    """Normaliza el nombre del departamento según las reglas especificadas"""
    original_name = department_name.strip()
    
    # 1. Si dice "capital", agregar el nombre de la provincia
    if original_name.lower() == 'capital':
        return f"{province_name} capital"
    
    # 2. Corregir "general angel v penaloza" a "general angel vera penaloza"
    if original_name.lower() == 'general angel v penaloza':
        return 'general angel vera penaloza'
    
    # 3. Si es "tierra del fuego", cambiar a "tierra del fuego antartida e islas del atlantico sur"
    if original_name.lower() == 'tierra del fuego':
        return 'tierra del fuego antartida e islas del atlantico sur'
    
    # Si no hay cambios necesarios, devolver el nombre original
    return original_name

def process_file(file_path):
    """Procesa un archivo CSV aplicando las normalizaciones"""
    filename = os.path.basename(file_path)
    province_name = get_province_name_from_filename(filename)
    
    print(f"Procesando: {filename} (Provincia: {province_name})")
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
    
    if not rows:
        print(f"Archivo vacío: {filename}")
        return
    
    # Procesar cada fila
    modified_rows = []
    changes_made = 0
    
    for i, row in enumerate(rows):
        if i == 0:  # Header
            modified_rows.append(row)
            continue
        
        if len(row) > 0:  # Asegurar que hay al menos una columna
            original_department = row[0]
            normalized_department = normalize_department_name(original_department, province_name, filename)
            
            if original_department != normalized_department:
                print(f"  Cambio: '{original_department}' -> '{normalized_department}'")
                changes_made += 1
                row[0] = normalized_department
        
        modified_rows.append(row)
    
    # Escribir el archivo modificado
    with open(file_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(modified_rows)
    
    print(f"  {changes_made} cambios realizados en {filename}")

def main():
    """Función principal"""
    # Directorio base de los archivos de población
    base_dir = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-poblacion"
    
    # Lista de archivos a procesar
    files = [
        "buenos aires.csv",
        "caba.csv", 
        "catamarca.csv",
        "chaco.csv",
        "chubut.csv",
        "cordoba.csv",
        "corrientes.csv",
        "entre rios.csv",
        "formosa.csv",
        "jujuy.csv",
        "la pampa.csv",
        "la rioja.csv",
        "mendoza.csv",
        "tucuman.csv",
        "tierra del fuego antartida e islas del atlantico sur.csv",
        "santiago del estero.csv",
        "santa fe.csv",
        "santa cruz.csv",
        "san juan.csv",
        "san luis.csv",
        "salta.csv",
        "rio negro.csv",
        "neuquen.csv",
        "misiones.csv"
    ]
    
    total_changes = 0
    
    for filename in files:
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            try:
                process_file(file_path)
            except Exception as e:
                print(f"Error procesando {filename}: {e}")
        else:
            print(f"Archivo no encontrado: {file_path}")
    
    print("\n¡Normalización completada!")

if __name__ == "__main__":
    main()
