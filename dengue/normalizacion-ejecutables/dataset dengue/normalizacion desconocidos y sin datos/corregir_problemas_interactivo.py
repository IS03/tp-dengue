#!/usr/bin/env python3
"""
Script interactivo para corregir problemas identificados en los archivos de dengue
Permite corregir fila por fila de forma guiada
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def mostrar_fila_problema(df, indice_fila, tipo_problema):
    """
    Muestra una fila problemática y permite corregirla
    """
    print(f"\n{'='*60}")
    print(f"🔧 CORRIGIENDO PROBLEMA: {tipo_problema}")
    print(f"Fila {indice_fila + 2} (índice {indice_fila})")
    print(f"{'='*60}")
    
    fila = df.iloc[indice_fila]
    print(f"Datos actuales:")
    for col, valor in fila.items():
        print(f"   {col}: {valor}")
    
    print(f"\nOpciones:")
    print(f"  1. Corregir esta fila")
    print(f"  2. Eliminar esta fila")
    print(f"  3. Saltar esta fila")
    print(f"  4. Salir del modo interactivo")
    
    while True:
        try:
            opcion = input(f"\nSelecciona una opción (1-4): ").strip()
            if opcion in ['1', '2', '3', '4']:
                break
            else:
                print("❌ Opción inválida. Selecciona 1, 2, 3 o 4.")
        except KeyboardInterrupt:
            print(f"\n\n👋 Saliendo del modo interactivo...")
            return 'salir'
    
    if opcion == '1':
        return corregir_fila_interactiva(df, indice_fila)
    elif opcion == '2':
        return 'eliminar'
    elif opcion == '3':
        return 'saltar'
    else:
        return 'salir'

def corregir_fila_interactiva(df, indice_fila):
    """
    Permite corregir una fila de forma interactiva
    """
    fila = df.iloc[indice_fila]
    correcciones = {}
    
    print(f"\n📝 CORRECCIÓN DE FILA {indice_fila + 2}")
    print(f"Deja en blanco para mantener el valor actual")
    
    for col in df.columns:
        valor_actual = fila[col]
        print(f"\n{col}: {valor_actual}")
        
        nuevo_valor = input(f"Nuevo valor para '{col}': ").strip()
        
        if nuevo_valor:
            # Validar el tipo de dato
            if df[col].dtype in ['int64', 'float64']:
                try:
                    if '.' in nuevo_valor:
                        correcciones[col] = float(nuevo_valor)
                    else:
                        correcciones[col] = int(nuevo_valor)
                except ValueError:
                    print(f"⚠️  Valor inválido para {col}. Manteniendo valor original.")
            else:
                correcciones[col] = nuevo_valor
    
    if correcciones:
        print(f"\n✅ Correcciones aplicadas:")
        for col, valor in correcciones.items():
            print(f"   {col}: {fila[col]} → {valor}")
        
        confirmar = input(f"\n¿Confirmar correcciones? (s/n): ").strip().lower()
        if confirmar in ['s', 'si', 'sí', 'y', 'yes']:
            return correcciones
    
    return 'sin_cambios'

def corregir_archivo_interactivo(nombre_archivo):
    """
    Corrección interactiva de un archivo específico
    """
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    backup_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico")
    archivo = base_path / nombre_archivo
    
    if not archivo.exists():
        print(f"❌ Error: El archivo '{nombre_archivo}' no existe")
        return
    
    print(f"=== CORRECCIÓN INTERACTIVA DE {nombre_archivo} ===")
    
    try:
        # Leer el archivo
        df = pd.read_csv(archivo, encoding='utf-8')
        print(f"Archivo cargado: {len(df)} filas, {len(df.columns)} columnas")
        
        # Crear backup en la carpeta backup existente
        backup_archivo = backup_path / f"backup_{archivo.name}"
        backup_path.mkdir(exist_ok=True)  # Asegurar que la carpeta existe
        df.to_csv(backup_archivo, index=False, encoding='utf-8')
        print(f"✅ Backup creado: {backup_archivo}")
        
        # Identificar filas problemáticas
        filas_problematicas = []
        filas_eliminadas_automaticamente = []
        
        # 1. Eliminar automáticamente filas donde tanto departamento_nombre como provincia_nombre son "desconocido" o "sin dato"
        if 'departamento_nombre' in df.columns and 'provincia_nombre' in df.columns:
            # Valores problemáticos para eliminar automáticamente
            valores_problematicos = ['desconocido', 'desconocida', 'unknown', 'n/a', 'na', 'sin dato', 'sin datos']
            
            mask_desconocido = (
                df['departamento_nombre'].astype(str).str.lower().isin(valores_problematicos) &
                df['provincia_nombre'].astype(str).str.lower().isin(valores_problematicos)
            )
            filas_eliminadas_automaticamente = df[mask_desconocido].index.tolist()
            df = df[~mask_desconocido]
            print(f"🗑️  Eliminadas automáticamente {len(filas_eliminadas_automaticamente)} filas con departamento y provincia desconocidos/sin dato")
        
        # 2. Valores nulos
        filas_nulos = df[df.isnull().any(axis=1)]
        for idx in filas_nulos.index:
            filas_problematicas.append((idx, 'VALORES_NULOS'))
        
        # 3. Valores "desconocido" o "sin dato" (solo los que no fueron eliminados automáticamente)
        for col in df.columns:
            if df[col].dtype == 'object':
                mask = df[col].astype(str).str.lower().isin(['desconocido', 'desconocida', 'unknown', 'n/a', 'na', 'sin dato', 'sin datos'])
                for idx in df[mask].index:
                    filas_problematicas.append((idx, f'DESCONOCIDO_EN_{col}'))
        
        # 4. IDs problemáticos
        columnas_id = [col for col in df.columns if 'id' in col.lower()]
        for col in columnas_id:
            mask = df[col].astype(str).isin(['999', '99'])
            for idx in df[mask].index:
                filas_problematicas.append((idx, f'ID_PROBLEMATICO_EN_{col}'))
        
        # 5. Valores vacíos
        for col in df.columns:
            if df[col].dtype == 'object':
                mask = df[col].astype(str).str.strip().isin(['', 'nan', 'NaN', 'None', 'null', 'NULL'])
                for idx in df[mask].index:
                    filas_problematicas.append((idx, f'VALOR_VACIO_EN_{col}'))
        
        # Eliminar duplicados
        filas_problematicas = list(set(filas_problematicas))
        filas_problematicas.sort()
        
        print(f"\n🔍 Encontradas {len(filas_problematicas)} filas problemáticas")
        
        if len(filas_problematicas) == 0:
            print(f"✅ ¡No hay problemas que corregir!")
            return
        
        # Procesar cada fila problemática
        filas_eliminadas = []
        correcciones_aplicadas = 0
        
        for i, (indice_fila, tipo_problema) in enumerate(filas_problematicas):
            print(f"\n📊 Progreso: {i+1}/{len(filas_problematicas)}")
            
            resultado = mostrar_fila_problema(df, indice_fila, tipo_problema)
            
            if resultado == 'salir':
                print(f"\n👋 Saliendo del modo interactivo...")
                break
            elif resultado == 'eliminar':
                filas_eliminadas.append(indice_fila)
                print(f"✅ Fila marcada para eliminación")
            elif isinstance(resultado, dict):
                # Aplicar correcciones
                for col, valor in resultado.items():
                    df.at[indice_fila, col] = valor
                correcciones_aplicadas += 1
                print(f"✅ Correcciones aplicadas")
            elif resultado == 'sin_cambios':
                print(f"ℹ️  Sin cambios aplicados")
        
        # Aplicar cambios
        if filas_eliminadas:
            df = df.drop(filas_eliminadas)
            print(f"\n🗑️  Eliminadas {len(filas_eliminadas)} filas adicionales")
        
        total_eliminaciones = len(filas_eliminadas_automaticamente) + len(filas_eliminadas)
        
        if correcciones_aplicadas > 0 or total_eliminaciones > 0:
            # Guardar archivo corregido
            df.to_csv(archivo, index=False, encoding='utf-8')
            print(f"✅ Archivo guardado con {correcciones_aplicadas} correcciones y {total_eliminaciones} eliminaciones totales")
            print(f"   - Eliminaciones automáticas: {len(filas_eliminadas_automaticamente)}")
            print(f"   - Eliminaciones manuales: {len(filas_eliminadas)}")
        else:
            print(f"ℹ️  No se realizaron cambios")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("❌ Error: Debes especificar un archivo CSV")
        print("Uso: python3 corregir_problemas_interactivo.py archivo.csv")
        print("\nEjemplo: python3 corregir_problemas_interactivo.py dengue-2024.csv")
        sys.exit(1)
    
    archivo = sys.argv[1]
    corregir_archivo_interactivo(archivo)

if __name__ == "__main__":
    main()
