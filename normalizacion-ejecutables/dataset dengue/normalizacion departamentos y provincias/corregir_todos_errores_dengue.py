#!/usr/bin/env python3
"""
Script para corregir automáticamente todos los errores detectados en los datasets de dengue

Este script:
1. Lee la lista-departamentos.csv como fuente de verdad
2. Aplica correcciones automáticas a todos los archivos de dengue (2018-2025)
3. Corrige provincias incorrectas basándose en el departamento
4. Corrige nombres de departamentos incorrectos
5. Crea backups antes de modificar
"""

import pandas as pd
import os
import re
import unicodedata
import shutil
from pathlib import Path
from difflib import get_close_matches

def normalizar_nombre(nombre):
    """
    Normaliza un nombre para hacer comparaciones más robustas
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

def crear_backup(archivo_original):
    """
    Crea un backup del archivo original
    """
    backup_dir = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/correcciones automaticas")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_path = backup_dir / f"backup_{archivo_original.name}"
    
    try:
        shutil.copy2(archivo_original, backup_path)
        print(f"  ✓ Backup creado: {backup_path}")
        return True
    except Exception as e:
        print(f"  ✗ Error creando backup: {str(e)}")
        return False

def corregir_archivo_dengue(archivo_dengue, diccionario_departamentos, nombres_departamentos):
    """
    Corrige un archivo de dengue aplicando todas las correcciones necesarias
    """
    print(f"\n{'='*80}")
    print(f"CORRIGIENDO: {archivo_dengue.name}")
    print(f"{'='*80}")
    
    try:
        # Crear backup
        if not crear_backup(archivo_dengue):
            print("  ✗ No se pudo crear backup, saltando archivo")
            return False
        
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
        correcciones_departamento = 0
        correcciones_provincia = 0
        correcciones_especificas = 0
        
        # Correcciones específicas conocidas
        correcciones_especificas_dict = {
            'saladias': ('saladas', 'corrientes'),
            'general angel v penaloza': ('general angel vera penaloza', 'la rioja'),
            'juan bautista alberdi': ('juan b alberdi', 'tucuman'),
            'misiones': ('misiones capital', 'misiones')
        }
        
        # Procesar cada fila
        for index, row in df_dengue.iterrows():
            departamento_actual = str(row['departamento_nombre']).strip()
            provincia_actual = str(row['provincia_nombre']).strip()
            
            # Aplicar correcciones específicas conocidas
            if departamento_actual.lower() in correcciones_especificas_dict:
                nuevo_departamento, nueva_provincia = correcciones_especificas_dict[departamento_actual.lower()]
                df_dengue.at[index, 'departamento_nombre'] = nuevo_departamento
                df_dengue.at[index, 'provincia_nombre'] = nueva_provincia
                correcciones_especificas += 1
                continue
            
            # Buscar coincidencia exacta del departamento
            if departamento_actual.lower() in diccionario_departamentos:
                provincia_correcta = diccionario_departamentos[departamento_actual.lower()]
                
                # Si la provincia no coincide, corregirla
                if provincia_actual.lower() != provincia_correcta.lower():
                    df_dengue.at[index, 'provincia_nombre'] = provincia_correcta
                    correcciones_provincia += 1
            
            # Si no hay coincidencia exacta, buscar sugerencias
            else:
                sugerencias = get_close_matches(
                    departamento_actual.lower(), 
                    [nombre.lower() for nombre in nombres_departamentos], 
                    n=3, 
                    cutoff=0.7
                )
                
                if sugerencias:
                    mejor_sugerencia = sugerencias[0]
                    provincia_sugerencia = diccionario_departamentos[mejor_sugerencia]
                    
                    # Verificar si la provincia actual coincide con la sugerencia
                    if provincia_actual.lower() == provincia_sugerencia.lower():
                        # Solo corregir el nombre del departamento
                        df_dengue.at[index, 'departamento_nombre'] = mejor_sugerencia
                        correcciones_departamento += 1
                    else:
                        # Corregir ambos
                        df_dengue.at[index, 'departamento_nombre'] = mejor_sugerencia
                        df_dengue.at[index, 'provincia_nombre'] = provincia_sugerencia
                        correcciones_departamento += 1
                        correcciones_provincia += 1
        
        # Guardar archivo corregido
        df_dengue.to_csv(archivo_dengue, index=False, encoding='utf-8')
        
        print(f"\n  === ESTADÍSTICAS DE CORRECCIÓN ===")
        print(f"  ✓ Correcciones específicas: {correcciones_especificas}")
        print(f"  ✓ Correcciones de departamento: {correcciones_departamento}")
        print(f"  ✓ Correcciones de provincia: {correcciones_provincia}")
        print(f"  ✓ Total de correcciones: {correcciones_especificas + correcciones_departamento + correcciones_provincia}")
        print(f"  ✓ Archivo guardado exitosamente")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error procesando archivo: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=== CORRECCIÓN AUTOMÁTICA DE TODOS LOS ERRORES DENGUE ===")
    print("Este script corrige automáticamente todos los errores detectados")
    print("en los datasets de dengue basándose en lista-departamentos.csv")
    print()
    
    # Rutas de archivos
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue")
    archivo_departamentos = base_path / "dataset-departamentos" / "lista-departamentos.csv"
    
    # Archivos de dengue a corregir (2018-2025)
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
        print("✗ Error: No se encontraron archivos de dengue para corregir")
        return
    
    print(f"Archivos de dengue a corregir: {len(archivos_existentes)}")
    for archivo in archivos_existentes:
        print(f"  - {archivo.name}")
    print()
    
    # Crear diccionario de departamentos a provincias
    diccionario, nombres_departamentos = crear_diccionario_departamentos_provincias(archivo_departamentos)
    if diccionario is None:
        print("✗ No se pudo crear el diccionario de departamentos")
        return
    
    # Corregir cada archivo de dengue
    archivos_corregidos = 0
    for archivo_dengue in archivos_existentes:
        if corregir_archivo_dengue(archivo_dengue, diccionario, nombres_departamentos):
            archivos_corregidos += 1
    
    print(f"\n{'='*80}")
    print(f"RESUMEN FINAL:")
    print(f"Archivos procesados: {len(archivos_existentes)}")
    print(f"Archivos corregidos exitosamente: {archivos_corregidos}")
    print(f"Archivos con errores: {len(archivos_existentes) - archivos_corregidos}")
    
    if archivos_corregidos == len(archivos_existentes):
        print("\n🎉 ¡Todos los archivos fueron corregidos exitosamente!")
        print("Los backups se guardaron en: /Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/correcciones automaticas/")
    else:
        print("\n⚠️  Algunos archivos tuvieron errores durante la corrección")

if __name__ == "__main__":
    main()
