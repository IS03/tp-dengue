#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir las columnas de grupos de edad en dengue-2020.csv
- Intercambia valores entre grupo_edad_id y grupo_edad_desc
- Mapea correctamente usando el índice de grupos de edad
"""

import pandas as pd
import numpy as np
import os

def cargar_indice_grupos_edad():
    """Carga el índice de grupos de edad y crea mapeos bidireccionales"""
    indice_path = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/indice_grupos_edad.csv"
    
    # Cargar el índice
    indice_df = pd.read_csv(indice_path)
    
    # Limpiar datos vacíos
    indice_df = indice_df.dropna()
    
    # Crear mapeos
    id_to_desc = {}
    desc_to_id = {}
    
    for _, row in indice_df.iterrows():
        grupo_id = str(row['grupo_edad_id']).strip()
        grupo_desc = str(row['grupo_edad_desc']).strip()
        
        if grupo_id and grupo_desc and grupo_id != 'nan' and grupo_desc != 'nan':
            id_to_desc[grupo_id] = grupo_desc
            desc_to_id[grupo_desc] = grupo_id
    
    return id_to_desc, desc_to_id

def corregir_grupos_edad():
    """Corrige las columnas de grupos de edad en dengue-2020.csv"""
    
    # Rutas de archivos
    archivo_original = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/dengue-2020.csv"
    archivo_backup = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup/dengue-2020-backup.csv"
    
    print("Cargando índice de grupos de edad...")
    id_to_desc, desc_to_id = cargar_indice_grupos_edad()
    
    print("Cargando archivo dengue-2020.csv...")
    df = pd.read_csv(archivo_original)
    
    print(f"Archivo cargado: {len(df)} filas")
    print("Columnas:", list(df.columns))
    
    # Crear backup
    print("Creando backup...")
    df.to_csv(archivo_backup, index=False)
    print(f"Backup creado en: {archivo_backup}")
    
    # Mostrar estado inicial
    print("\n=== ESTADO INICIAL ===")
    print("Valores únicos en grupo_edad_id:", df['grupo_edad_id'].unique())
    print("Valores únicos en grupo_edad_desc:", df['grupo_edad_desc'].unique())
    
    # Intercambiar valores entre las columnas
    print("\n=== INTERCAMBIANDO VALORES ===")
    
    # Crear copias temporales
    temp_id = df['grupo_edad_id'].copy()
    temp_desc = df['grupo_edad_desc'].copy()
    
    # Intercambiar: los valores de grupo_edad_desc van a grupo_edad_id
    df['grupo_edad_id'] = temp_desc
    df['grupo_edad_desc'] = temp_id
    
    print("Valores intercambiados entre las columnas")
    
    # Mostrar estado después del intercambio
    print("\n=== DESPUÉS DEL INTERCAMBIO ===")
    print("Valores únicos en grupo_edad_id:", df['grupo_edad_id'].unique())
    print("Valores únicos en grupo_edad_desc:", df['grupo_edad_desc'].unique())
    
    # Mapear valores usando el índice
    print("\n=== MAPEANDO VALORES ===")
    
    # Limpiar valores nulos y convertir a string
    df['grupo_edad_id'] = df['grupo_edad_id'].fillna('').astype(str)
    df['grupo_edad_desc'] = df['grupo_edad_desc'].fillna('').astype(str)
    
    # Mapear grupo_edad_id a descripciones correctas
    def mapear_id_a_desc(valor):
        if pd.isna(valor) or valor == '' or valor == 'nan':
            return ''
        
        # Convertir a string y limpiar
        valor_str = str(valor).strip()
        
        # Si es un número, buscar en el mapeo
        if valor_str.replace('.', '').replace('-', '').isdigit():
            # Convertir a entero si es posible
            try:
                valor_num = int(float(valor_str))
                valor_str = str(valor_num)
            except:
                pass
            
            if valor_str in id_to_desc:
                return id_to_desc[valor_str]
        
        return valor_str
    
    # Mapear grupo_edad_desc a IDs correctos
    def mapear_desc_a_id(valor):
        if pd.isna(valor) or valor == '' or valor == 'nan':
            return ''
        
        # Convertir a string y limpiar
        valor_str = str(valor).strip()
        
        # Si es una descripción, buscar en el mapeo
        if valor_str in desc_to_id:
            return desc_to_id[valor_str]
        
        return valor_str
    
    # Aplicar mapeos
    print("Mapeando grupo_edad_id a descripciones...")
    df['grupo_edad_desc'] = df['grupo_edad_id'].apply(mapear_id_a_desc)
    
    print("Mapeando grupo_edad_desc a IDs...")
    df['grupo_edad_id'] = df['grupo_edad_desc'].apply(mapear_desc_a_id)
    
    # Mostrar estado final
    print("\n=== ESTADO FINAL ===")
    print("Valores únicos en grupo_edad_id:", df['grupo_edad_id'].unique())
    print("Valores únicos en grupo_edad_desc:", df['grupo_edad_desc'].unique())
    
    # Guardar archivo corregido
    print("\n=== GUARDANDO ARCHIVO CORREGIDO ===")
    df.to_csv(archivo_original, index=False)
    print(f"Archivo corregido guardado en: {archivo_original}")
    
    # Mostrar estadísticas
    print("\n=== ESTADÍSTICAS FINALES ===")
    print(f"Total de filas procesadas: {len(df)}")
    print(f"Filas con grupo_edad_id válido: {len(df[df['grupo_edad_id'] != ''])}")
    print(f"Filas con grupo_edad_desc válido: {len(df[df['grupo_edad_desc'] != ''])}")
    
    # Mostrar algunos ejemplos
    print("\n=== EJEMPLOS DE RESULTADO ===")
    ejemplos = df[df['grupo_edad_id'] != ''].head(10)
    for _, row in ejemplos.iterrows():
        print(f"ID: {row['grupo_edad_id']} -> Desc: {row['grupo_edad_desc']}")

if __name__ == "__main__":
    try:
        corregir_grupos_edad()
        print("\n✅ Proceso completado exitosamente!")
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")
        import traceback
        traceback.print_exc()
