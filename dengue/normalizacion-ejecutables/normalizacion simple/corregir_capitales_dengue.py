#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir los nombres de departamentos "capital" en los archivos de dengue
agregando el nombre de la provincia correspondiente
"""

import pandas as pd
import os
import glob

def corregir_capitales_dengue():
    """
    Corrige los nombres de departamentos que son "capital" en todos los archivos de dengue
    agregando el nombre de la provincia correspondiente
    """
    
    # Directorio base
    directorio_dengue = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue"
    
    # Años a procesar
    años = [2018, 2020, 2021, 2022, 2023, 2024, 2025]
    
    total_archivos_procesados = 0
    total_registros_modificados = 0
    
    print("=== CORRECCIÓN DE CAPITALES EN ARCHIVOS DE DENGUE ===\n")
    
    for año in años:
        archivo_csv = os.path.join(directorio_dengue, f"dengue-{año}.csv")
        
        # Verificar que el archivo existe
        if not os.path.exists(archivo_csv):
            print(f"⚠️  Archivo no encontrado: dengue-{año}.csv")
            continue
        
        try:
            print(f"📁 Procesando: dengue-{año}.csv")
            
            # Leer el archivo CSV
            df = pd.read_csv(archivo_csv)
            
            # Mostrar información inicial
            print(f"   Total de registros: {len(df)}")
            
            # Contar cuántos "capital" hay antes de la corrección
            capitales_antes = df[df['departamento_nombre'].str.lower() == 'capital']
            registros_a_modificar = len(capitales_antes)
            
            print(f"   Registros con 'capital' encontrados: {registros_a_modificar}")
            
            if registros_a_modificar > 0:
                print("   Registros que serán modificados:")
                for idx, row in capitales_antes.iterrows():
                    print(f"     - Fila {idx + 2}: '{row['departamento_nombre']}' -> '{row['provincia_nombre']} capital'")
            
            # Aplicar la corrección
            # Buscar filas donde departamento_nombre sea "capital" (case insensitive)
            mask = df['departamento_nombre'].str.lower() == 'capital'
            
            # Para esas filas, cambiar el nombre agregando la provincia
            df.loc[mask, 'departamento_nombre'] = df.loc[mask, 'provincia_nombre'] + ' capital'
            
            # Contar los cambios realizados
            cambios_realizados = mask.sum()
            print(f"   ✅ Corrección aplicada a {cambios_realizados} registros")
            
            # Guardar el archivo modificado
            df.to_csv(archivo_csv, index=False)
            print(f"   💾 Archivo guardado exitosamente")
            
            total_archivos_procesados += 1
            total_registros_modificados += cambios_realizados
            
            # Mostrar los registros modificados
            if cambios_realizados > 0:
                capitales_despues = df[df['departamento_nombre'].str.contains('capital', case=False, na=False)]
                print(f"   Registros modificados:")
                for idx, row in capitales_despues.iterrows():
                    print(f"     - Fila {idx + 2}: '{row['departamento_nombre']}'")
            
            print()  # Línea en blanco para separar archivos
            
        except Exception as e:
            print(f"   ❌ Error al procesar el archivo: {e}")
            print()
    
    # Resumen final
    print("=== RESUMEN FINAL ===")
    print(f"📊 Archivos procesados: {total_archivos_procesados}")
    print(f"📊 Total de registros modificados: {total_registros_modificados}")
    
    if total_registros_modificados > 0:
        print("✅ ¡Corrección completada exitosamente!")
    else:
        print("ℹ️  No se encontraron registros con 'capital' para modificar")

def verificar_archivos():
    """
    Función auxiliar para verificar qué archivos existen
    """
    directorio_dengue = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue"
    años = [2018, 2020, 2021, 2022, 2023, 2024, 2025]
    
    print("=== VERIFICACIÓN DE ARCHIVOS ===")
    for año in años:
        archivo_csv = os.path.join(directorio_dengue, f"dengue-{año}.csv")
        if os.path.exists(archivo_csv):
            print(f"✅ dengue-{año}.csv - Existe")
        else:
            print(f"❌ dengue-{año}.csv - No encontrado")
    print()

if __name__ == "__main__":
    # Primero verificar qué archivos existen
    verificar_archivos()
    
    # Luego procesar los archivos
    corregir_capitales_dengue()
