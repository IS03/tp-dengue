#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear columna de ID en datasets de dengue basada en Código UTA 2020
de lista-departamentos.csv mediante match de departamento_nombre y provincia_nombre
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def normalizar_texto(texto):
    """Normaliza texto para comparación: minúsculas, sin acentos, sin espacios extra"""
    if pd.isna(texto) or texto == '':
        return ''
    
    # Convertir a string y normalizar
    texto = str(texto).strip().lower()
    
    # Reemplazar acentos y caracteres especiales
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u', 'ç': 'c',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ã': 'a', 'õ': 'o', 'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o'
    }
    
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    
    # Eliminar espacios extra
    texto = ' '.join(texto.split())
    
    return texto

def cargar_referencia():
    """Carga el archivo de referencia con los códigos UTA 2020"""
    try:
        df_ref = pd.read_csv('/Users/ignaciosenestrari/Facu/tp-dengue/dataset-departamentos/lista-departamentos.csv')
        df_ref = df_ref.dropna(subset=['Nombre', 'Provincia', 'Código UTA 2020'])
        
        # Normalizar nombres para matching
        df_ref['Nombre_normalizado'] = df_ref['Nombre'].apply(normalizar_texto)
        df_ref['Provincia_normalizada'] = df_ref['Provincia'].apply(normalizar_texto)
        
        print(f"[OK] Archivo de referencia cargado: {len(df_ref)} departamentos")
        return df_ref
    except Exception as e:
        print(f"[ERROR] Error al cargar archivo de referencia: {e}")
        return None

def crear_backup(archivo_original):
    """Crea backup del archivo original"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/uta IDs"
        os.makedirs(backup_dir, exist_ok=True)
        
        nombre_archivo = os.path.basename(archivo_original)
        backup_path = os.path.join(backup_dir, f"backup_{nombre_archivo}")
        
        shutil.copy2(archivo_original, backup_path)
        print(f"[OK] Backup creado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"[ERROR] Error al crear backup: {e}")
        return None

def procesar_dataset_dengue(archivo_dengue, df_referencia):
    """Procesa un dataset de dengue y agrega la columna de ID"""
    try:
        print(f"\n[INFO] Procesando: {archivo_dengue}")
        
        # Cargar dataset de dengue
        df_dengue = pd.read_csv(archivo_dengue)
        print(f"[OK] Dataset cargado: {len(df_dengue)} registros")
        
        # Verificar que existan las columnas necesarias
        columnas_requeridas = ['departamento_nombre', 'provincia_nombre']
        for col in columnas_requeridas:
            if col not in df_dengue.columns:
                print(f"[ERROR] Columna '{col}' no encontrada en el dataset")
                return False
        
        # Verificar si ya existe la columna UTA ID
        if 'departamento_id_uta_2020' in df_dengue.columns:
            print(f"[WARNING] La columna 'departamento_id_uta_2020' ya existe en el archivo")
            respuesta = input("¿Desea sobrescribirla? (s/n): ").strip().lower()
            if respuesta != 's':
                print("[INFO] Saltando archivo...")
                return True
        
        # Normalizar nombres en el dataset de dengue
        df_dengue['departamento_nombre_norm'] = df_dengue['departamento_nombre'].apply(normalizar_texto)
        df_dengue['provincia_nombre_norm'] = df_dengue['provincia_nombre'].apply(normalizar_texto)
        
        # Crear diccionario de mapeo desde la referencia
        mapeo_ids = {}
        for _, row in df_referencia.iterrows():
            key = (row['Nombre_normalizado'], row['Provincia_normalizada'])
            mapeo_ids[key] = row['Código UTA 2020']
        
        # Aplicar mapeo para crear la columna de ID
        def obtener_id_uta(row):
            key = (row['departamento_nombre_norm'], row['provincia_nombre_norm'])
            return mapeo_ids.get(key, None)
        
        df_dengue['departamento_id_uta_2020'] = df_dengue.apply(obtener_id_uta, axis=1)
        
        # Limpiar columnas temporales
        df_dengue = df_dengue.drop(['departamento_nombre_norm', 'provincia_nombre_norm'], axis=1)
        
        # Estadísticas
        total_registros = len(df_dengue)
        registros_con_id = df_dengue['departamento_id_uta_2020'].notna().sum()
        registros_sin_id = total_registros - registros_con_id
        
        print(f"[INFO] Total de registros: {total_registros}")
        print(f"[INFO] Registros con ID asignado: {registros_con_id}")
        print(f"[INFO] Registros sin ID: {registros_sin_id}")
        
        if registros_sin_id > 0:
            print(f"[WARNING] {registros_sin_id} registros no pudieron ser mapeados")
            
            # Mostrar algunos ejemplos de registros sin ID
            sin_id = df_dengue[df_dengue['departamento_id_uta_2020'].isna()]
            ejemplos = sin_id[['departamento_nombre', 'provincia_nombre']].drop_duplicates().head(10)
            
            if not ejemplos.empty:
                print("\n[WARNING] Ejemplos de registros sin ID:")
                for _, row in ejemplos.iterrows():
                    print(f"  - {row['departamento_nombre']} | {row['provincia_nombre']}")
        
        # Crear backup antes de modificar
        backup_path = crear_backup(archivo_dengue)
        if not backup_path:
            print("[ERROR] No se pudo crear backup. Abortando...")
            return False
        
        # Guardar archivo modificado
        df_dengue.to_csv(archivo_dengue, index=False)
        print(f"[OK] Archivo actualizado: {archivo_dengue}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al procesar {archivo_dengue}: {e}")
        return False

def obtener_archivos_dengue():
    """Obtiene la lista de archivos de dengue disponibles"""
    directorio_dengue = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue"
    archivos = []
    
    for archivo in os.listdir(directorio_dengue):
        if archivo.startswith('dengue-') and archivo.endswith('.csv'):
            archivos.append(os.path.join(directorio_dengue, archivo))
    
    return sorted(archivos)

def main():
    """Función principal"""
    print("=" * 80)
    print("GENERADOR DE COLUMNA UTA ID - DATASETS DENGUE")
    print("=" * 80)
    print("Este script crea una columna 'departamento_id_uta_2020' en los datasets de dengue")
    print("basándose en el Código UTA 2020 de lista-departamentos.csv")
    print("MATCH: departamento_nombre + provincia_nombre")
    print("BACKUP: /Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/uta IDs")
    print("=" * 80)
    
    # Cargar archivo de referencia
    df_referencia = cargar_referencia()
    if df_referencia is None:
        return
    
    # Obtener archivos de dengue
    archivos_dengue = obtener_archivos_dengue()
    if not archivos_dengue:
        print("[ERROR] No se encontraron archivos de dengue")
        return
    
    print(f"\nArchivos de dengue encontrados: {len(archivos_dengue)}")
    for archivo in archivos_dengue:
        print(f"  - {os.path.basename(archivo)}")
    
    print("\n" + "=" * 50)
    print("OPCIONES:")
    print("1. Procesar todos los archivos")
    print("2. Procesar un archivo específico")
    print("3. Salir")
    print("=" * 50)
    
    while True:
        try:
            opcion = input("\nSeleccione una opción (1-3): ").strip()
            
            if opcion == "1":
                # Procesar todos los archivos
                print(f"\n[INFO] Procesando {len(archivos_dengue)} archivos...")
                exitosos = 0
                
                for archivo in archivos_dengue:
                    if procesar_dataset_dengue(archivo, df_referencia):
                        exitosos += 1
                
                print(f"\n[RESUMEN] Procesados exitosamente: {exitosos}/{len(archivos_dengue)} archivos")
                break
                
            elif opcion == "2":
                # Procesar archivo específico
                print(f"\nArchivos disponibles:")
                for i, archivo in enumerate(archivos_dengue, 1):
                    print(f"{i}. {os.path.basename(archivo)}")
                
                while True:
                    try:
                        seleccion = int(input(f"\nSeleccione archivo (1-{len(archivos_dengue)}): ")) - 1
                        if 0 <= seleccion < len(archivos_dengue):
                            archivo_seleccionado = archivos_dengue[seleccion]
                            if procesar_dataset_dengue(archivo_seleccionado, df_referencia):
                                print(f"\n[OK] Archivo procesado exitosamente")
                            else:
                                print(f"\n[ERROR] Error al procesar archivo")
                            break
                        else:
                            print("Selección inválida")
                    except ValueError:
                        print("Ingrese un número válido")
                break
                
            elif opcion == "3":
                print("Saliendo...")
                break
                
            else:
                print("Opción inválida. Seleccione 1, 2 o 3.")
                
        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
