#!/usr/bin/env python3
"""
Script para eliminar columnas específicas del archivo lista-departamentos.csv
Elimina las columnas G, H, I: "Ruta raiz de servicos OWS", "Capa", "Filtros de la Capa"
"""

import pandas as pd
import os
from pathlib import Path

def eliminar_columnas_departamentos():
    """
    Elimina las columnas G, H, I del archivo lista-departamentos.csv
    """
    archivo_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-departamentos/lista-departamentos.csv")
    
    # Columnas a eliminar (G, H, I)
    columnas_eliminar = [
        "Ruta raiz de servicos OWS",  # Columna G
        "Capa",                       # Columna H  
        "Filtros de la Capa"          # Columna I
    ]
    
    try:
        print(f"Procesando archivo: {archivo_path}")
        
        # Leer el archivo
        df = pd.read_csv(archivo_path, encoding='utf-8')
        print(f"Archivo original: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        # Mostrar columnas antes de eliminar
        print(f"Columnas antes de eliminar:")
        for i, col in enumerate(df.columns, 1):
            if col in columnas_eliminar:
                print(f"  {chr(64+i)}: {col} ← ELIMINAR")
            else:
                print(f"  {chr(64+i)}: {col}")
        
        # Verificar que las columnas existen
        columnas_existentes = [col for col in columnas_eliminar if col in df.columns]
        columnas_no_encontradas = [col for col in columnas_eliminar if col not in df.columns]
        
        if columnas_no_encontradas:
            print(f"⚠️  Columnas no encontradas: {columnas_no_encontradas}")
        
        if not columnas_existentes:
            print("✗ No se encontraron columnas para eliminar")
            return False
        
        # Eliminar las columnas
        df_limpio = df.drop(columns=columnas_existentes)
        
        print(f"\nColumnas eliminadas: {len(columnas_existentes)}")
        for col in columnas_existentes:
            print(f"  - {col}")
        
        print(f"Archivo después de eliminar: {df_limpio.shape[0]} filas, {df_limpio.shape[1]} columnas")
        
        # Guardar el archivo modificado
        df_limpio.to_csv(archivo_path, index=False, encoding='utf-8')
        print(f"✓ Archivo guardado: {archivo_path}")
        
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: No se encontró el archivo '{archivo_path}'")
        return False
    except Exception as e:
        print(f"✗ Error al procesar el archivo: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=== ELIMINACIÓN DE COLUMNAS EN LISTA-DEPARTAMENTOS ===")
    print("Eliminando columnas G, H, I:")
    print("  G: Ruta raiz de servicos OWS")
    print("  H: Capa") 
    print("  I: Filtros de la Capa")
    print()
    
    exito = eliminar_columnas_departamentos()
    
    if exito:
        print("\n🎉 ¡Columnas eliminadas exitosamente!")
    else:
        print("\n❌ Error al eliminar las columnas")

if __name__ == "__main__":
    main()
