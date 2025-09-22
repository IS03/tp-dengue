#!/usr/bin/env python3
"""
Script para actualizar la columna provincia_nombre en dengue-2025.csv
basándose en la búsqueda de departamento_nombre en lista-departamentos.csv

El script:
1. Lee cada departamento_nombre de dengue-2025.csv
2. Busca ese nombre en la columna 'Nombre' de lista-departamentos.csv
3. Si encuentra coincidencia, extrae el valor de la columna 'Provincia'
4. Actualiza la columna provincia_nombre en la fila correspondiente
"""

import pandas as pd
import os
import re
import unicodedata
from pathlib import Path

def normalizar_nombre(nombre):
    """
    Normaliza un nombre para hacer comparaciones más robustas
    - Convierte a minúsculas
    - Quita espacios extra
    - Quita caracteres especiales
    - Elimina acentos
    """
    if pd.isna(nombre) or nombre == '':
        return ''
    
    nombre = str(nombre).lower().strip()
    
    # Eliminar acentos
    nombre = unicodedata.normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if unicodedata.category(c) != 'Mn')
    
    # Quitar caracteres especiales y espacios múltiples
    nombre = re.sub(r'[^a-z0-9\s]', ' ', nombre)
    nombre = re.sub(r'\s+', ' ', nombre).strip()
    
    return nombre

def crear_diccionario_departamentos_provincias(archivo_departamentos):
    """
    Crea un diccionario que mapea nombres de departamentos a provincias
    """
    print(f"Leyendo archivo de departamentos: {archivo_departamentos}")
    
    try:
        df_departamentos = pd.read_csv(archivo_departamentos, encoding='utf-8')
        print(f"  ✓ Archivo leído: {df_departamentos.shape[0]} filas, {df_departamentos.shape[1]} columnas")
        print(f"  ✓ Columnas disponibles: {list(df_departamentos.columns)}")
        
        # Verificar que las columnas necesarias existen
        if 'Nombre' not in df_departamentos.columns:
            print("  ✗ Error: No se encontró la columna 'Nombre'")
            return None
        if 'Provincia' not in df_departamentos.columns:
            print("  ✗ Error: No se encontró la columna 'Provincia'")
            return None
        
        # Crear diccionario
        diccionario = {}
        coincidencias_exactas = 0
        coincidencias_normalizadas = 0
        
        for index, row in df_departamentos.iterrows():
            nombre_departamento = str(row['Nombre']).strip()
            provincia = str(row['Provincia']).strip()
            
            # Agregar coincidencia exacta
            diccionario[nombre_departamento.lower()] = provincia
            coincidencias_exactas += 1
            
            # Agregar coincidencia normalizada
            nombre_normalizado = normalizar_nombre(nombre_departamento)
            if nombre_normalizado and nombre_normalizado != nombre_departamento.lower():
                diccionario[nombre_normalizado] = provincia
                coincidencias_normalizadas += 1
        
        print(f"  ✓ Diccionario creado: {coincidencias_exactas} coincidencias exactas")
        print(f"  ✓ Coincidencias normalizadas adicionales: {coincidencias_normalizadas}")
        print(f"  ✓ Total de entradas en diccionario: {len(diccionario)}")
        
        return diccionario
        
    except Exception as e:
        print(f"  ✗ Error leyendo archivo de departamentos: {str(e)}")
        return None

def actualizar_provincias_dengue(archivo_dengue, diccionario_departamentos):
    """
    Actualiza la columna provincia_nombre en el archivo de dengue
    """
    print(f"\nProcesando archivo de dengue: {archivo_dengue}")
    
    try:
        # Leer archivo de dengue
        df_dengue = pd.read_csv(archivo_dengue, encoding='utf-8')
        print(f"  ✓ Archivo leído: {df_dengue.shape[0]} filas, {df_dengue.shape[1]} columnas")
        
        # Verificar que las columnas necesarias existen
        if 'departamento_nombre' not in df_dengue.columns:
            print("  ✗ Error: No se encontró la columna 'departamento_nombre'")
            return False
        if 'provincia_nombre' not in df_dengue.columns:
            print("  ✗ Error: No se encontró la columna 'provincia_nombre'")
            return False
        
        # Contadores para estadísticas
        actualizaciones_exactas = 0
        actualizaciones_normalizadas = 0
        sin_coincidencia = 0
        departamentos_unicos = df_dengue['departamento_nombre'].unique()
        
        print(f"  ✓ Departamentos únicos a procesar: {len(departamentos_unicos)}")
        
        # Procesar cada fila
        for index, row in df_dengue.iterrows():
            departamento_actual = str(row['departamento_nombre']).strip()
            provincia_encontrada = None
            
            # Corrección específica para "saladias" -> "saladas" con provincia "corrientes"
            if departamento_actual.lower() == "saladias":
                provincia_encontrada = "corrientes"
                # También actualizar el nombre del departamento
                df_dengue.at[index, 'departamento_nombre'] = "saladas"
                actualizaciones_exactas += 1
                print(f"    ✓ Corregido: 'saladias' -> 'saladas' (corrientes)")
            
            # Buscar coincidencia exacta (en minúsculas)
            elif departamento_actual.lower() in diccionario_departamentos:
                provincia_encontrada = diccionario_departamentos[departamento_actual.lower()]
                actualizaciones_exactas += 1
            
            # Si no hay coincidencia exacta, buscar coincidencia normalizada
            elif normalizar_nombre(departamento_actual) in diccionario_departamentos:
                provincia_encontrada = diccionario_departamentos[normalizar_nombre(departamento_actual)]
                actualizaciones_normalizadas += 1
            
            # Actualizar la provincia si se encontró
            if provincia_encontrada:
                df_dengue.at[index, 'provincia_nombre'] = provincia_encontrada
            else:
                sin_coincidencia += 1
                if sin_coincidencia <= 10:  # Mostrar solo los primeros 10
                    print(f"    ⚠️  Sin coincidencia: '{departamento_actual}'")
        
        # Guardar archivo actualizado
        df_dengue.to_csv(archivo_dengue, index=False, encoding='utf-8')
        
        print(f"\n  === ESTADÍSTICAS DE ACTUALIZACIÓN ===")
        print(f"  ✓ Actualizaciones exactas: {actualizaciones_exactas}")
        print(f"  ✓ Actualizaciones normalizadas: {actualizaciones_normalizadas}")
        print(f"  ⚠️  Sin coincidencia: {sin_coincidencia}")
        print(f"  ✓ Total de filas procesadas: {len(df_dengue)}")
        print(f"  ✓ Archivo guardado exitosamente")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error procesando archivo de dengue: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=== ACTUALIZACIÓN DE PROVINCIAS DESDE DEPARTAMENTOS ===")
    print("Este script actualiza la columna provincia_nombre en los archivos de dengue")
    print("basándose en la búsqueda de departamento_nombre en lista-departamentos.csv")
    print()
    
    # Rutas de archivos
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue")
    archivo_departamentos = base_path / "dataset-departamentos" / "lista-departamentos.csv"
    
    # Archivos de dengue a procesar
    archivos_dengue = [
        base_path / "dataset-dengue" / "dengue-2023.csv",
        base_path / "dataset-dengue" / "dengue-2024.csv", 
        base_path / "dataset-dengue" / "dengue-2025.csv"
    ]
    
    # Verificar que el archivo de departamentos existe
    if not archivo_departamentos.exists():
        print(f"✗ Error: No se encontró el archivo {archivo_departamentos}")
        return
    
    # Verificar que los archivos de dengue existen
    archivos_existentes = []
    for archivo in archivos_dengue:
        if archivo.exists():
            archivos_existentes.append(archivo)
        else:
            print(f"⚠️  Archivo no encontrado: {archivo.name}")
    
    if not archivos_existentes:
        print("✗ Error: No se encontraron archivos de dengue para procesar")
        return
    
    print(f"Archivos de dengue a procesar: {len(archivos_existentes)}")
    for archivo in archivos_existentes:
        print(f"  - {archivo.name}")
    print()
    
    # Crear diccionario de departamentos a provincias
    diccionario = crear_diccionario_departamentos_provincias(archivo_departamentos)
    if diccionario is None:
        print("✗ No se pudo crear el diccionario de departamentos")
        return
    
    # Actualizar provincias en cada archivo de dengue
    archivos_exitosos = 0
    for archivo_dengue in archivos_existentes:
        print(f"\n{'='*60}")
        if actualizar_provincias_dengue(archivo_dengue, diccionario):
            archivos_exitosos += 1
    
    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL:")
    print(f"Archivos procesados: {len(archivos_existentes)}")
    print(f"Archivos exitosos: {archivos_exitosos}")
    print(f"Archivos con errores: {len(archivos_existentes) - archivos_exitosos}")
    
    if archivos_exitosos == len(archivos_existentes):
        print("\n🎉 ¡Todas las actualizaciones completadas exitosamente!")
    else:
        print("\n⚠️  Algunas actualizaciones tuvieron errores")

if __name__ == "__main__":
    main()
