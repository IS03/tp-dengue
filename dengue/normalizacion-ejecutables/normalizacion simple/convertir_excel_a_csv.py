#!/usr/bin/env python3
"""
Script para convertir archivos Excel (.xlsx) a CSV
Específicamente para examinar las columnas H e I del archivo 2020.xlsx
"""

import pandas as pd
import os
from pathlib import Path

def convertir_excel_a_csv():
    """
    Convierte el archivo Excel 2020.xlsx a CSV para poder examinarlo
    """
    print("=== CONVERSIÓN DE EXCEL A CSV ===")
    
    # Ruta del archivo Excel
    archivo_excel = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/2020.xlsx")
    archivo_csv = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/2020_converted.csv")
    
    if not archivo_excel.exists():
        print(f"❌ Archivo no encontrado: {archivo_excel}")
        return False
    
    try:
        print(f"📁 Leyendo archivo Excel: {archivo_excel.name}")
        
        # Leer el archivo Excel
        df = pd.read_excel(archivo_excel)
        
        print(f"✅ Archivo leído exitosamente")
        print(f"   Filas: {len(df)}")
        print(f"   Columnas: {len(df.columns)}")
        print(f"   Nombres de columnas: {list(df.columns)}")
        
        # Mostrar información específica de las columnas H e I
        print(f"\n🔍 ANÁLISIS DE COLUMNAS H e I:")
        
        if len(df.columns) >= 8:  # Columna H (índice 7)
            col_h = df.columns[7]
            print(f"   Columna H (índice 7): '{col_h}'")
            print(f"   Valores únicos en columna H: {df[col_h].unique()[:10]}")  # Primeros 10 valores únicos
            print(f"   Valores nulos en columna H: {df[col_h].isnull().sum()}")
        
        if len(df.columns) >= 9:  # Columna I (índice 8)
            col_i = df.columns[8]
            print(f"   Columna I (índice 8): '{col_i}'")
            print(f"   Valores únicos en columna I: {df[col_i].unique()[:10]}")  # Primeros 10 valores únicos
            print(f"   Valores nulos en columna I: {df[col_i].isnull().sum()}")
        
        # Mostrar las primeras filas para examinar los datos
        print(f"\n📋 PRIMERAS 10 FILAS:")
        print(df.head(10).to_string())
        
        # Guardar como CSV
        print(f"\n💾 Guardando como CSV: {archivo_csv.name}")
        df.to_csv(archivo_csv, index=False, encoding='utf-8')
        
        print(f"✅ Conversión completada exitosamente")
        print(f"   Archivo CSV creado: {archivo_csv}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")
        return False

def examinar_columnas_especificas():
    """
    Examina específicamente las columnas H e I del archivo convertido
    """
    archivo_csv = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/2020_converted.csv")
    
    if not archivo_csv.exists():
        print(f"❌ Archivo CSV no encontrado: {archivo_csv}")
        return
    
    try:
        print(f"\n=== EXAMEN DETALLADO DE COLUMNAS H e I ===")
        
        df = pd.read_csv(archivo_csv, encoding='utf-8')
        
        if len(df.columns) >= 8:
            col_h = df.columns[7]
            print(f"\n🔍 COLUMNA H: '{col_h}'")
            print(f"   Tipo de datos: {df[col_h].dtype}")
            print(f"   Total de valores: {len(df[col_h])}")
            print(f"   Valores únicos: {df[col_h].nunique()}")
            print(f"   Valores nulos: {df[col_h].isnull().sum()}")
            print(f"   Valores únicos completos: {sorted(df[col_h].dropna().unique())}")
            
            # Mostrar distribución de valores
            print(f"   Distribución de valores:")
            value_counts = df[col_h].value_counts().head(10)
            for valor, count in value_counts.items():
                print(f"     {valor}: {count} veces")
        
        if len(df.columns) >= 9:
            col_i = df.columns[8]
            print(f"\n🔍 COLUMNA I: '{col_i}'")
            print(f"   Tipo de datos: {df[col_i].dtype}")
            print(f"   Total de valores: {len(df[col_i])}")
            print(f"   Valores únicos: {df[col_i].nunique()}")
            print(f"   Valores nulos: {df[col_i].isnull().sum()}")
            print(f"   Valores únicos completos: {sorted(df[col_i].dropna().unique())}")
            
            # Mostrar distribución de valores
            print(f"   Distribución de valores:")
            value_counts = df[col_i].value_counts().head(10)
            for valor, count in value_counts.items():
                print(f"     {valor}: {count} veces")
        
        # Mostrar algunas filas de ejemplo
        print(f"\n📋 EJEMPLOS DE FILAS (columnas H e I):")
        if len(df.columns) >= 9:
            columnas_mostrar = [df.columns[7], df.columns[8]]
            print(df[columnas_mostrar].head(20).to_string())
        
    except Exception as e:
        print(f"❌ Error examinando columnas: {str(e)}")

def main():
    """Función principal"""
    if convertir_excel_a_csv():
        examinar_columnas_especificas()
    else:
        print("❌ No se pudo completar la conversión")

if __name__ == "__main__":
    main()
