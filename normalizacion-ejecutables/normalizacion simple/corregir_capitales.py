#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir los nombres de departamentos "capital" agregando el nombre de la provincia
"""

import pandas as pd
import os

def corregir_capitales():
    """
    Corrige los nombres de departamentos que son "capital" agregando el nombre de la provincia
    """
    
    # Ruta del archivo
    archivo_csv = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-departamentos/lista-departamentos.csv"
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_csv):
        print(f"Error: No se encontró el archivo {archivo_csv}")
        return
    
    try:
        # Leer el archivo CSV
        print("Leyendo archivo CSV...")
        df = pd.read_csv(archivo_csv)
        
        # Mostrar información inicial
        print(f"Total de registros: {len(df)}")
        
        # Contar cuántos "capital" hay antes de la corrección
        capitales_antes = df[df['Nombre'].str.lower() == 'capital']
        print(f"Registros con 'capital' encontrados: {len(capitales_antes)}")
        
        if len(capitales_antes) > 0:
            print("\nRegistros que serán modificados:")
            for idx, row in capitales_antes.iterrows():
                print(f"  - Fila {idx + 2}: '{row['Nombre']}' -> '{row['Provincia']} capital'")
        
        # Aplicar la corrección
        # Buscar filas donde Nombre sea "capital" (case insensitive)
        mask = df['Nombre'].str.lower() == 'capital'
        
        # Para esas filas, cambiar el nombre agregando la provincia
        df.loc[mask, 'Nombre'] = df.loc[mask, 'Provincia'] + ' capital'
        
        # Mostrar los cambios realizados
        print(f"\nCorrección aplicada a {mask.sum()} registros")
        
        # Guardar el archivo modificado
        print("Guardando archivo modificado...")
        df.to_csv(archivo_csv, index=False)
        
        print("¡Archivo actualizado exitosamente!")
        
        # Mostrar los registros modificados
        capitales_despues = df[df['Nombre'].str.contains('capital', case=False, na=False)]
        if len(capitales_despues) > 0:
            print("\nRegistros modificados:")
            for idx, row in capitales_despues.iterrows():
                print(f"  - Fila {idx + 2}: '{row['Nombre']}'")
        
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    corregir_capitales()
