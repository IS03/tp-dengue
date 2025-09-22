#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que los códigos UTA ID en los datasets de dengue
coincidan correctamente con los códigos de lista-departamentos.csv
"""

import pandas as pd
import os
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
        
        # Crear diccionario de mapeo
        mapeo_correcto = {}
        for _, row in df_ref.iterrows():
            key = (row['Nombre_normalizado'], row['Provincia_normalizada'])
            mapeo_correcto[key] = {
                'codigo_uta': row['Código UTA 2020'],
                'nombre_original': row['Nombre'],
                'provincia_original': row['Provincia']
            }
        
        print(f"[OK] Archivo de referencia cargado: {len(df_ref)} departamentos")
        return mapeo_correcto, df_ref
    except Exception as e:
        print(f"[ERROR] Error al cargar archivo de referencia: {e}")
        return None, None

def verificar_archivo(archivo_path, mapeo_correcto):
    """Verifica si los códigos UTA ID en un archivo son correctos"""
    try:
        print(f"\n[INFO] Verificando: {os.path.basename(archivo_path)}")
        
        # Cargar dataset
        df = pd.read_csv(archivo_path)
        
        # Verificar que exista la columna UTA ID
        if 'departamento_id_uta_2020' not in df.columns:
            return {
                'archivo': os.path.basename(archivo_path),
                'tiene_uta_id': False,
                'total_registros': len(df),
                'registros_con_id': 0,
                'registros_correctos': 0,
                'registros_incorrectos': 0,
                'registros_sin_id': len(df),
                'errores': [],
                'error': None
            }
        
        # Normalizar nombres en el dataset
        df['departamento_nombre_norm'] = df['departamento_nombre'].apply(normalizar_texto)
        df['provincia_nombre_norm'] = df['provincia_nombre'].apply(normalizar_texto)
        
        # Verificar cada registro
        errores = []
        registros_con_id = 0
        registros_correctos = 0
        registros_incorrectos = 0
        registros_sin_id = 0
        
        for idx, row in df.iterrows():
            if pd.isna(row['departamento_id_uta_2020']):
                registros_sin_id += 1
                continue
            
            registros_con_id += 1
            key = (row['departamento_nombre_norm'], row['provincia_nombre_norm'])
            
            if key in mapeo_correcto:
                codigo_correcto = mapeo_correcto[key]['codigo_uta']
                if row['departamento_id_uta_2020'] == codigo_correcto:
                    registros_correctos += 1
                else:
                    registros_incorrectos += 1
                    errores.append({
                        'fila': idx + 2,  # +2 porque pandas es 0-indexed y CSV tiene header
                        'departamento': row['departamento_nombre'],
                        'provincia': row['provincia_nombre'],
                        'codigo_actual': row['departamento_id_uta_2020'],
                        'codigo_correcto': codigo_correcto,
                        'departamento_correcto': mapeo_correcto[key]['nombre_original'],
                        'provincia_correcta': mapeo_correcto[key]['provincia_original']
                    })
            else:
                registros_incorrectos += 1
                errores.append({
                    'fila': idx + 2,
                    'departamento': row['departamento_nombre'],
                    'provincia': row['provincia_nombre'],
                    'codigo_actual': row['departamento_id_uta_2020'],
                    'codigo_correcto': 'NO ENCONTRADO',
                    'departamento_correcto': 'N/A',
                    'provincia_correcta': 'N/A'
                })
        
        # Limpiar columnas temporales
        df = df.drop(['departamento_nombre_norm', 'provincia_nombre_norm'], axis=1)
        
        return {
            'archivo': os.path.basename(archivo_path),
            'tiene_uta_id': True,
            'total_registros': len(df),
            'registros_con_id': registros_con_id,
            'registros_correctos': registros_correctos,
            'registros_incorrectos': registros_incorrectos,
            'registros_sin_id': registros_sin_id,
            'errores': errores,
            'error': None
        }
        
    except Exception as e:
        return {
            'archivo': os.path.basename(archivo_path),
            'tiene_uta_id': False,
            'total_registros': 0,
            'registros_con_id': 0,
            'registros_correctos': 0,
            'registros_incorrectos': 0,
            'registros_sin_id': 0,
            'errores': [],
            'error': str(e)
        }

def generar_reporte(resultados):
    """Genera un reporte detallado de los resultados"""
    print("\n" + "=" * 120)
    print("REPORTE DE VERIFICACIÓN DE CÓDIGOS UTA ID")
    print("=" * 120)
    
    # Estadísticas generales
    total_archivos = len(resultados)
    archivos_con_uta_id = sum(1 for r in resultados if r['tiene_uta_id'])
    archivos_sin_uta_id = total_archivos - archivos_con_uta_id
    archivos_con_error = sum(1 for r in resultados if r['error'])
    
    total_registros = sum(r['total_registros'] for r in resultados)
    total_con_id = sum(r['registros_con_id'] for r in resultados)
    total_correctos = sum(r['registros_correctos'] for r in resultados)
    total_incorrectos = sum(r['registros_incorrectos'] for r in resultados)
    total_sin_id = sum(r['registros_sin_id'] for r in resultados)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total de archivos: {total_archivos}")
    print(f"   Archivos con UTA ID: {archivos_con_uta_id}")
    print(f"   Archivos sin UTA ID: {archivos_sin_uta_id}")
    print(f"   Archivos con error: {archivos_con_error}")
    
    print(f"\n📈 ESTADÍSTICAS DE REGISTROS:")
    print(f"   Total de registros: {total_registros:,}")
    print(f"   Registros con ID: {total_con_id:,}")
    print(f"   Registros correctos: {total_correctos:,}")
    print(f"   Registros incorrectos: {total_incorrectos:,}")
    print(f"   Registros sin ID: {total_sin_id:,}")
    
    if total_con_id > 0:
        porcentaje_correctos = (total_correctos / total_con_id) * 100
        print(f"   Porcentaje de códigos correctos: {porcentaje_correctos:.1f}%")
    
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
        print("-" * 120)
        print(f"{'Archivo':<25} {'Total':<8} {'Con ID':<8} {'Correctos':<10} {'Incorrectos':<12} {'Sin ID':<8} {'% Correctos':<12}")
        print("-" * 120)
        
        for resultado in resultados:
            if resultado['tiene_uta_id'] and not resultado['error']:
                porcentaje = (resultado['registros_correctos'] / resultado['registros_con_id'] * 100) if resultado['registros_con_id'] > 0 else 0
                print(f"{resultado['archivo']:<25} "
                      f"{resultado['total_registros']:<8} "
                      f"{resultado['registros_con_id']:<8} "
                      f"{resultado['registros_correctos']:<10} "
                      f"{resultado['registros_incorrectos']:<12} "
                      f"{resultado['registros_sin_id']:<8} "
                      f"{porcentaje:<12.1f}%")
    
    # Errores detallados
    archivos_con_errores = [r for r in resultados if r['tiene_uta_id'] and r['errores'] and not r['error']]
    if archivos_con_errores:
        print(f"\n🔍 ERRORES DETALLADOS:")
        print("-" * 120)
        
        for resultado in archivos_con_errores:
            print(f"\n📁 {resultado['archivo']} ({len(resultado['errores'])} errores):")
            print("-" * 100)
            
            # Mostrar solo los primeros 10 errores por archivo
            errores_mostrar = resultado['errores'][:10]
            for error in errores_mostrar:
                print(f"   Fila {error['fila']}: {error['departamento']} | {error['provincia']}")
                print(f"      Código actual: {error['codigo_actual']}")
                print(f"      Código correcto: {error['codigo_correcto']}")
                if error['codigo_correcto'] != 'NO ENCONTRADO':
                    print(f"      Referencia: {error['departamento_correcto']} | {error['provincia_correcta']}")
                print()
            
            if len(resultado['errores']) > 10:
                print(f"   ... y {len(resultado['errores']) - 10} errores más")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if archivos_sin_uta_id > 0:
        print(f"   • Ejecutar 'crear_columna_uta_id.py' para agregar la columna a {archivos_sin_uta_id} archivos")
    
    if total_incorrectos > 0:
        print(f"   • Corregir {total_incorrectos:,} registros con códigos UTA incorrectos")
        print(f"   • Considerar re-ejecutar 'crear_columna_uta_id.py' para regenerar los IDs")
    
    if total_sin_id > 0:
        print(f"   • Revisar {total_sin_id:,} registros sin ID (posibles problemas de matching)")

def exportar_errores_csv(resultados, archivo_salida):
    """Exporta los errores a un archivo CSV"""
    try:
        todos_errores = []
        for resultado in resultados:
            if resultado['tiene_uta_id'] and resultado['errores']:
                for error in resultado['errores']:
                    error['archivo'] = resultado['archivo']
                    todos_errores.append(error)
        
        if todos_errores:
            df_errores = pd.DataFrame(todos_errores)
            df_errores.to_csv(archivo_salida, index=False)
            print(f"\n[OK] Errores exportados a: {archivo_salida}")
            print(f"[INFO] Total de errores exportados: {len(todos_errores)}")
        else:
            print(f"\n[INFO] No hay errores para exportar")
            
    except Exception as e:
        print(f"[ERROR] Error al exportar errores: {e}")

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
    print("VERIFICADOR DE CÓDIGOS UTA ID - DATASETS DENGUE")
    print("=" * 80)
    print("Este script verifica que los códigos UTA ID en los datasets de dengue")
    print("coincidan correctamente con los códigos de lista-departamentos.csv")
    print("=" * 80)
    
    # Cargar archivo de referencia
    mapeo_correcto, df_referencia = cargar_referencia()
    if mapeo_correcto is None:
        return
    
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
        resultado = verificar_archivo(archivo, mapeo_correcto)
        resultados.append(resultado)
    
    # Generar reporte
    generar_reporte(resultados)
    
    # Preguntar si exportar errores
    print("\n" + "=" * 50)
    try:
        exportar = input("¿Desea exportar los errores a CSV? (s/n): ").strip().lower()
        if exportar == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_errores = f"/Users/ignaciosenestrari/Facu/tp-dengue/normalizacion-ejecutables/uta IDs/errores_uta_id_{timestamp}.csv"
            exportar_errores_csv(resultados, archivo_errores)
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario")

if __name__ == "__main__":
    main()
