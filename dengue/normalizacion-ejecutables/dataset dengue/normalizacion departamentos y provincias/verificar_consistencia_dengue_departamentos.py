#!/usr/bin/env python3
"""
Script para verificar la consistencia entre los datasets de dengue y lista-departamentos.csv

Este script:
1. Lee la lista-departamentos.csv como fuente de verdad
2. Verifica cada archivo de dengue (2023, 2024, 2025)
3. Detecta discrepancias en departamento_nombre y provincia_nombre
4. Muestra errores detallados con sugerencias de corrección
"""

import pandas as pd
import os
import re
import unicodedata
from pathlib import Path
from difflib import get_close_matches

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
        
        # Verificar que las columnas necesarias existen
        if 'Nombre' not in df_departamentos.columns:
            print("  ✗ Error: No se encontró la columna 'Nombre'")
            return None, None
        if 'Provincia' not in df_departamentos.columns:
            print("  ✗ Error: No se encontró la columna 'Provincia'")
            return None, None
        
        # Crear diccionario y lista de nombres
        diccionario = {}
        nombres_departamentos = []
        
        for index, row in df_departamentos.iterrows():
            nombre_departamento = str(row['Nombre']).strip()
            provincia = str(row['Provincia']).strip()
            
            # Agregar al diccionario
            diccionario[nombre_departamento.lower()] = provincia
            nombres_departamentos.append(nombre_departamento)
        
        print(f"  ✓ Diccionario creado: {len(diccionario)} departamentos")
        print(f"  ✓ Lista de nombres creada: {len(nombres_departamentos)} departamentos")
        
        return diccionario, nombres_departamentos
        
    except Exception as e:
        print(f"  ✗ Error leyendo archivo de departamentos: {str(e)}")
        return None, None

def verificar_archivo_dengue(archivo_dengue, diccionario_departamentos, nombres_departamentos):
    """
    Verifica un archivo de dengue contra la lista de departamentos
    """
    print(f"\n{'='*80}")
    print(f"VERIFICANDO: {archivo_dengue.name}")
    print(f"{'='*80}")
    
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
        errores = []
        departamentos_unicos = df_dengue['departamento_nombre'].unique()
        
        print(f"  ✓ Departamentos únicos a verificar: {len(departamentos_unicos)}")
        print()
        
        # Verificar cada departamento único
        for departamento in departamentos_unicos:
            if pd.isna(departamento) or departamento == '':
                continue
                
            departamento_str = str(departamento).strip()
            departamento_normalizado = normalizar_nombre(departamento_str)
            
            # Buscar coincidencia exacta
            if departamento_str.lower() in diccionario_departamentos:
                provincia_correcta = diccionario_departamentos[departamento_str.lower()]
                
                # Verificar si la provincia en el dataset coincide
                filas_departamento = df_dengue[df_dengue['departamento_nombre'] == departamento]
                provincias_en_dataset = filas_departamento['provincia_nombre'].unique()
                
                for provincia_dataset in provincias_en_dataset:
                    if pd.isna(provincia_dataset) or provincia_dataset == '':
                        errores.append({
                            'tipo': 'Provincia Vacía',
                            'departamento': departamento_str,
                            'provincia_dataset': '[VACÍA]',
                            'provincia_correcta': provincia_correcta,
                            'filas_afectadas': len(filas_departamento[filas_departamento['provincia_nombre'].isna() | (filas_departamento['provincia_nombre'] == '')])
                        })
                    elif str(provincia_dataset).strip().lower() != provincia_correcta.lower():
                        errores.append({
                            'tipo': 'Provincia No Coincide',
                            'departamento': departamento_str,
                            'provincia_dataset': str(provincia_dataset).strip(),
                            'provincia_correcta': provincia_correcta,
                            'filas_afectadas': len(filas_departamento[filas_departamento['provincia_nombre'] == provincia_dataset])
                        })
            
            # Si no hay coincidencia exacta, buscar sugerencias
            else:
                # Buscar sugerencias similares
                sugerencias = get_close_matches(
                    departamento_str.lower(), 
                    [nombre.lower() for nombre in nombres_departamentos], 
                    n=5, 
                    cutoff=0.6
                )
                
                # Verificar si alguna sugerencia coincide con la provincia del dataset
                provincia_encontrada = None
                for sugerencia in sugerencias:
                    if sugerencia in diccionario_departamentos:
                        provincia_sugerencia = diccionario_departamentos[sugerencia]
                        filas_departamento = df_dengue[df_dengue['departamento_nombre'] == departamento]
                        provincias_en_dataset = filas_departamento['provincia_nombre'].unique()
                        
                        for provincia_dataset in provincias_en_dataset:
                            if not pd.isna(provincia_dataset) and str(provincia_dataset).strip().lower() == provincia_sugerencia.lower():
                                provincia_encontrada = provincia_sugerencia
                                break
                        
                        if provincia_encontrada:
                            break
                
                if provincia_encontrada:
                    # Hay una sugerencia que coincide con la provincia
                    errores.append({
                        'tipo': 'Departamento No Encontrado (con sugerencia)',
                        'departamento': departamento_str,
                        'provincia_dataset': str(filas_departamento['provincia_nombre'].iloc[0]).strip(),
                        'provincia_correcta': provincia_encontrada,
                        'sugerencias': sugerencias[:3],
                        'filas_afectadas': len(filas_departamento)
                    })
                else:
                    # No hay coincidencia
                    errores.append({
                        'tipo': 'Departamento No Encontrado',
                        'departamento': departamento_str,
                        'provincia_dataset': str(filas_departamento['provincia_nombre'].iloc[0]).strip() if len(filas_departamento) > 0 else '[VACÍA]',
                        'provincia_correcta': '[NO ENCONTRADA]',
                        'sugerencias': sugerencias[:3],
                        'filas_afectadas': len(filas_departamento)
                    })
        
        # Mostrar errores encontrados
        if errores:
            print(f"  ⚠️  SE ENCONTRARON {len(errores)} TIPOS DE ERRORES:")
            print()
            
            for i, error in enumerate(errores, 1):
                print(f"  {i}. {error['tipo'].upper()}")
                print(f"     Departamento: '{error['departamento']}'")
                print(f"     Provincia en dataset: '{error['provincia_dataset']}'")
                print(f"     Provincia correcta: '{error['provincia_correcta']}'")
                print(f"     Filas afectadas: {error['filas_afectadas']}")
                
                if 'sugerencias' in error and error['sugerencias']:
                    print(f"     Sugerencias: {', '.join(error['sugerencias'])}")
                
                print()
        else:
            print("  ✅ NO SE ENCONTRARON ERRORES - Todos los departamentos y provincias coinciden correctamente")
        
        return len(errores) == 0
        
    except Exception as e:
        print(f"  ✗ Error procesando archivo: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=== VERIFICACIÓN DE CONSISTENCIA DENGUE - DEPARTAMENTOS ===")
    print("Este script verifica que los datasets de dengue coincidan con lista-departamentos.csv")
    print("Detecta errores en departamento_nombre y provincia_nombre")
    print()
    
    # Rutas de archivos
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue")
    archivo_departamentos = base_path / "dataset-departamentos" / "lista-departamentos.csv"
    
    # Archivos de dengue a verificar (2018-2025)
    archivos_dengue = []
    for año in range(2018, 2026):  # 2018 a 2025
        archivo = base_path / "dataset-dengue" / f"dengue-{año}.csv"
        archivos_dengue.append(archivo)
    
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
        print("✗ Error: No se encontraron archivos de dengue para verificar")
        return
    
    print(f"Archivos de dengue a verificar: {len(archivos_existentes)}")
    for archivo in archivos_existentes:
        print(f"  - {archivo.name}")
    print()
    
    # Crear diccionario de departamentos a provincias
    diccionario, nombres_departamentos = crear_diccionario_departamentos_provincias(archivo_departamentos)
    if diccionario is None:
        print("✗ No se pudo crear el diccionario de departamentos")
        return
    
    # Verificar cada archivo de dengue
    archivos_sin_errores = 0
    for archivo_dengue in archivos_existentes:
        if verificar_archivo_dengue(archivo_dengue, diccionario, nombres_departamentos):
            archivos_sin_errores += 1
    
    print(f"\n{'='*80}")
    print(f"RESUMEN FINAL:")
    print(f"Archivos verificados: {len(archivos_existentes)}")
    print(f"Archivos sin errores: {archivos_sin_errores}")
    print(f"Archivos con errores: {len(archivos_existentes) - archivos_sin_errores}")
    
    if archivos_sin_errores == len(archivos_existentes):
        print("\n🎉 ¡Todos los archivos están consistentes con la lista de departamentos!")
    else:
        print("\n⚠️  Algunos archivos tienen inconsistencias que deben corregirse")

if __name__ == "__main__":
    main()
