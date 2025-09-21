#!/usr/bin/env python3
"""
Script para corregir problemas específicos en las columnas de los archivos de dengue
1. Arreglar dengue-2022.csv: cambiar 'año' por 'ano'
2. Reordenar columnas en 2023-2025 para que coincidan con el formato estándar
"""

import pandas as pd
from pathlib import Path

def corregir_dengue_2022():
    """
    Corrige el problema de 'año' en dengue-2022.csv
    """
    archivo_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/dengue-2022.csv")
    
    try:
        print("=== Corrigiendo dengue-2022.csv ===")
        print("  Cambiando 'año' por 'ano' en el encabezado...")
        
        # Leer el archivo
        df = pd.read_csv(archivo_path, encoding='utf-8')
        print(f"  Archivo original: {df.shape[0]} filas, {df.shape[1]} columnas")
        print(f"  Columnas antes: {list(df.columns)}")
        
        # Cambiar 'año' por 'ano' en el encabezado
        df.columns = df.columns.str.replace('año', 'ano')
        
        print(f"  Columnas después: {list(df.columns)}")
        
        # Guardar el archivo corregido
        df.to_csv(archivo_path, index=False, encoding='utf-8')
        print(f"  ✓ Archivo corregido guardado")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def reordenar_columnas_2023_2024_2025():
    """
    Reordena las columnas en los archivos 2023, 2024 y 2025
    """
    archivos = [
        "dengue-2023.csv",
        "dengue-2024.csv", 
        "dengue-2025.csv"
    ]
    
    # Orden correcto de columnas (formato estándar)
    orden_correcto = [
        'departamento_id',
        'departamento_nombre', 
        'provincia_id',
        'provincia_nombre',
        'ano',
        'semanas_epidemiologicas',
        'evento_nombre',
        'grupo_edad_id',
        'grupo_edad_desc',
        'cantidad_casos'
    ]
    
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    
    archivos_procesados = 0
    archivos_exitosos = 0
    
    for archivo_nombre in archivos:
        archivo_path = base_path / archivo_nombre
        
        try:
            print(f"\n=== Reordenando columnas en {archivo_nombre} ===")
            
            # Leer el archivo
            df = pd.read_csv(archivo_path, encoding='utf-8')
            print(f"  Archivo original: {df.shape[0]} filas, {df.shape[1]} columnas")
            print(f"  Columnas antes: {list(df.columns)}")
            
            # Reordenar las columnas
            df = df[orden_correcto]
            
            print(f"  Columnas después: {list(df.columns)}")
            
            # Guardar el archivo reordenado
            df.to_csv(archivo_path, index=False, encoding='utf-8')
            print(f"  ✓ Archivo reordenado guardado")
            
            archivos_procesados += 1
            archivos_exitosos += 1
            
        except Exception as e:
            print(f"  ✗ Error en {archivo_nombre}: {str(e)}")
            archivos_procesados += 1
    
    return archivos_procesados, archivos_exitosos

def verificar_estructura():
    """
    Verifica que todos los archivos tengan la misma estructura
    """
    print("\n=== Verificando estructura de todos los archivos ===")
    
    archivos = [
        "dengue-2018.csv",
        "dengue-2019.csv", 
        "dengue-2020.csv",
        "dengue-2021.csv",
        "dengue-2022.csv",
        "dengue-2023.csv",
        "dengue-2024.csv",
        "dengue-2025.csv"
    ]
    
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    
    estructuras = {}
    
    for archivo_nombre in archivos:
        archivo_path = base_path / archivo_nombre
        
        try:
            df = pd.read_csv(archivo_path, encoding='utf-8')
            columnas = list(df.columns)
            estructuras[archivo_nombre] = columnas
            print(f"  {archivo_nombre}: {len(columnas)} columnas")
            
        except Exception as e:
            print(f"  ✗ Error leyendo {archivo_nombre}: {str(e)}")
    
    # Verificar si todas las estructuras son iguales
    primera_estructura = None
    todos_iguales = True
    
    for archivo, columnas in estructuras.items():
        if primera_estructura is None:
            primera_estructura = columnas
        elif columnas != primera_estructura:
            todos_iguales = False
            print(f"  ❌ {archivo} tiene estructura diferente")
        else:
            print(f"  ✅ {archivo} tiene estructura correcta")
    
    if todos_iguales:
        print(f"\n🎉 ¡Todos los archivos tienen la misma estructura!")
        print(f"   Estructura estándar: {primera_estructura}")
    else:
        print(f"\n⚠️  Algunos archivos tienen estructuras diferentes")
    
    return todos_iguales

def main():
    """Función principal"""
    print("=== CORRECCIÓN DE ESTRUCTURA DE COLUMNAS ===")
    print("Problemas a corregir:")
    print("  1. dengue-2022.csv: cambiar 'año' por 'ano'")
    print("  2. dengue-2023/2024/2025: reordenar columnas")
    print()
    
    # Paso 1: Corregir dengue-2022.csv
    exito_2022 = corregir_dengue_2022()
    
    # Paso 2: Reordenar columnas en 2023-2025
    procesados, exitosos = reordenar_columnas_2023_2024_2025()
    
    # Paso 3: Verificar estructura final
    estructura_correcta = verificar_estructura()
    
    print(f"\n=== RESUMEN ===")
    print(f"dengue-2022.csv corregido: {'✅' if exito_2022 else '❌'}")
    print(f"Archivos 2023-2025 reordenados: {exitosos}/{procesados}")
    print(f"Estructura final correcta: {'✅' if estructura_correcta else '❌'}")
    
    if exito_2022 and exitosos == procesados and estructura_correcta:
        print("\n🎉 ¡Todos los problemas fueron corregidos exitosamente!")
    else:
        print("\n⚠️  Algunos problemas no se pudieron corregir")

if __name__ == "__main__":
    main()
