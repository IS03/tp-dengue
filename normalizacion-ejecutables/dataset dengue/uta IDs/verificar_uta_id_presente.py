#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que todos los datasets de dengue tengan la columna departamento_id_uta_2020
"""

import pandas as pd
import os
from datetime import datetime

def obtener_archivos_dengue():
    """Obtiene la lista de archivos de dengue disponibles"""
    directorio_dengue = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue"
    archivos = []
    
    for archivo in os.listdir(directorio_dengue):
        if archivo.startswith('dengue-') and archivo.endswith('.csv'):
            archivos.append(os.path.join(directorio_dengue, archivo))
    
    return sorted(archivos)

def verificar_archivo(archivo_path):
    """Verifica si un archivo tiene la columna UTA ID y proporciona estadísticas"""
    try:
        # Cargar solo las primeras filas para verificar columnas
        df = pd.read_csv(archivo_path, nrows=5)
        
        # Verificar si existe la columna
        tiene_uta_id = 'departamento_id_uta_2020' in df.columns
        
        # Si tiene la columna, cargar todo el archivo para estadísticas
        if tiene_uta_id:
            df_completo = pd.read_csv(archivo_path)
            total_registros = len(df_completo)
            registros_con_id = df_completo['departamento_id_uta_2020'].notna().sum()
            registros_sin_id = total_registros - registros_con_id
            porcentaje_con_id = (registros_con_id / total_registros * 100) if total_registros > 0 else 0
            
            return {
                'archivo': os.path.basename(archivo_path),
                'tiene_uta_id': True,
                'total_registros': total_registros,
                'registros_con_id': registros_con_id,
                'registros_sin_id': registros_sin_id,
                'porcentaje_con_id': porcentaje_con_id,
                'error': None
            }
        else:
            return {
                'archivo': os.path.basename(archivo_path),
                'tiene_uta_id': False,
                'total_registros': None,
                'registros_con_id': None,
                'registros_sin_id': None,
                'porcentaje_con_id': None,
                'error': None
            }
            
    except Exception as e:
        return {
            'archivo': os.path.basename(archivo_path),
            'tiene_uta_id': False,
            'total_registros': None,
            'registros_con_id': None,
            'registros_sin_id': None,
            'porcentaje_con_id': None,
            'error': str(e)
        }

def generar_reporte(resultados):
    """Genera un reporte detallado de los resultados"""
    print("\n" + "=" * 100)
    print("REPORTE DE VERIFICACIÓN DE COLUMNA UTA ID")
    print("=" * 100)
    
    # Estadísticas generales
    total_archivos = len(resultados)
    archivos_con_uta_id = sum(1 for r in resultados if r['tiene_uta_id'])
    archivos_sin_uta_id = total_archivos - archivos_con_uta_id
    archivos_con_error = sum(1 for r in resultados if r['error'])
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total de archivos: {total_archivos}")
    print(f"   Archivos con UTA ID: {archivos_con_uta_id}")
    print(f"   Archivos sin UTA ID: {archivos_sin_uta_id}")
    print(f"   Archivos con error: {archivos_con_error}")
    
    # Archivos sin UTA ID
    if archivos_sin_uta_id > 0:
        print(f"\n❌ ARCHIVOS SIN COLUMNA UTA ID ({archivos_sin_uta_id}):")
        print("-" * 80)
        for resultado in resultados:
            if not resultado['tiene_uta_id'] and not resultado['error']:
                print(f"   • {resultado['archivo']}")
    
    # Archivos con errores
    if archivos_con_error > 0:
        print(f"\n⚠️  ARCHIVOS CON ERRORES ({archivos_con_error}):")
        print("-" * 80)
        for resultado in resultados:
            if resultado['error']:
                print(f"   • {resultado['archivo']}: {resultado['error']}")
    
    # Archivos con UTA ID - detalle
    if archivos_con_uta_id > 0:
        print(f"\n✅ ARCHIVOS CON COLUMNA UTA ID ({archivos_con_uta_id}):")
        print("-" * 100)
        print(f"{'Archivo':<25} {'Total':<10} {'Con ID':<10} {'Sin ID':<10} {'% Con ID':<10}")
        print("-" * 100)
        
        for resultado in resultados:
            if resultado['tiene_uta_id'] and not resultado['error']:
                print(f"{resultado['archivo']:<25} "
                      f"{resultado['total_registros']:<10} "
                      f"{resultado['registros_con_id']:<10} "
                      f"{resultado['registros_sin_id']:<10} "
                      f"{resultado['porcentaje_con_id']:<10.1f}%")
    
    # Resumen de calidad
    print(f"\n📈 RESUMEN DE CALIDAD:")
    if archivos_con_uta_id > 0:
        resultados_validos = [r for r in resultados if r['tiene_uta_id'] and not r['error']]
        if resultados_validos:
            porcentaje_promedio = sum(r['porcentaje_con_id'] for r in resultados_validos) / len(resultados_validos)
            archivos_100_porciento = sum(1 for r in resultados_validos if r['porcentaje_con_id'] == 100.0)
            archivos_problemas = sum(1 for r in resultados_validos if r['porcentaje_con_id'] < 100.0)
            
            print(f"   Porcentaje promedio de registros con ID: {porcentaje_promedio:.1f}%")
            print(f"   Archivos con 100% de registros mapeados: {archivos_100_porciento}")
            print(f"   Archivos con registros sin mapear: {archivos_problemas}")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if archivos_sin_uta_id > 0:
        print(f"   • Ejecutar 'crear_columna_uta_id.py' para agregar la columna a {archivos_sin_uta_id} archivos")
    
    if archivos_con_error > 0:
        print(f"   • Revisar {archivos_con_error} archivos con errores de lectura")
    
    archivos_problemas = [r for r in resultados if r['tiene_uta_id'] and r['porcentaje_con_id'] < 100.0 and not r['error']]
    if archivos_problemas:
        print(f"   • Revisar {len(archivos_problemas)} archivos con registros sin mapear")
        print(f"   • Considerar ejecutar 'verificar_uta_id_correcto.py' para validar los IDs")

def exportar_reporte_csv(resultados, archivo_salida):
    """Exporta el reporte a un archivo CSV"""
    try:
        df_reporte = pd.DataFrame(resultados)
        df_reporte.to_csv(archivo_salida, index=False)
        print(f"\n[OK] Reporte exportado a: {archivo_salida}")
    except Exception as e:
        print(f"[ERROR] Error al exportar reporte: {e}")

def main():
    """Función principal"""
    print("=" * 80)
    print("VERIFICADOR DE COLUMNA UTA ID - DATASETS DENGUE")
    print("=" * 80)
    print("Este script verifica que todos los datasets de dengue tengan")
    print("la columna 'departamento_id_uta_2020' y proporciona estadísticas")
    print("=" * 80)
    
    # Obtener archivos de dengue
    archivos_dengue = obtener_archivos_dengue()
    if not archivos_dengue:
        print("[ERROR] No se encontraron archivos de dengue")
        return
    
    print(f"\n[INFO] Verificando {len(archivos_dengue)} archivos...")
    
    # Verificar cada archivo
    resultados = []
    for i, archivo in enumerate(archivos_dengue, 1):
        print(f"[{i}/{len(archivos_dengue)}] Verificando {os.path.basename(archivo)}...")
        resultado = verificar_archivo(archivo)
        resultados.append(resultado)
    
    # Generar reporte
    generar_reporte(resultados)
    
    # Preguntar si exportar reporte
    print("\n" + "=" * 50)
    try:
        exportar = input("¿Desea exportar el reporte a CSV? (s/n): ").strip().lower()
        if exportar == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_reporte = f"/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/uta IDs/reporte_uta_id_{timestamp}.csv"
            exportar_reporte_csv(resultados, archivo_reporte)
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario")

if __name__ == "__main__":
    main()
