#!/usr/bin/env python3
"""
Script para verificar que todos los archivos de dengue tengan exactamente las mismas columnas
Compara: orden, nombres y cantidad de columnas
"""

import pandas as pd
from pathlib import Path

def verificar_columnas_detallado():
    """
    Verifica en detalle las columnas de todos los archivos de dengue
    """
    print("=== VERIFICACIÓN DETALLADA DE COLUMNAS ===")
    
    base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue")
    
    # Obtener todos los archivos CSV
    archivos_csv = list(base_path.glob("*.csv"))
    archivos_csv.sort()  # Ordenar alfabéticamente
    
    print(f"Archivos encontrados: {len(archivos_csv)}")
    for archivo in archivos_csv:
        print(f"  - {archivo.name}")
    print()
    
    # Estructura de referencia (tomada del primer archivo)
    estructura_referencia = None
    archivo_referencia = None
    
    # Diccionario para almacenar las estructuras de cada archivo
    estructuras = {}
    
    print("=== ANÁLISIS DETALLADO ===")
    
    for archivo in archivos_csv:
        try:
            # Leer solo el encabezado
            df = pd.read_csv(archivo, encoding='utf-8', nrows=0)
            columnas = list(df.columns)
            estructuras[archivo.name] = columnas
            
            print(f"\n📁 {archivo.name}")
            print(f"   Cantidad de columnas: {len(columnas)}")
            print(f"   Columnas: {columnas}")
            
            # Establecer estructura de referencia
            if estructura_referencia is None:
                estructura_referencia = columnas
                archivo_referencia = archivo.name
                print(f"   ✅ Estructura de referencia establecida")
            else:
                # Comparar con la estructura de referencia
                if columnas == estructura_referencia:
                    print(f"   ✅ IDÉNTICO a {archivo_referencia}")
                else:
                    print(f"   ❌ DIFERENTE a {archivo_referencia}")
                    
                    # Mostrar diferencias específicas
                    if len(columnas) != len(estructura_referencia):
                        print(f"      - Cantidad: {len(columnas)} vs {len(estructura_referencia)}")
                    
                    # Verificar orden
                    if columnas != estructura_referencia:
                        print(f"      - Orden diferente")
                        for i, (col_ref, col_act) in enumerate(zip(estructura_referencia, columnas)):
                            if col_ref != col_act:
                                print(f"        Posición {i}: '{col_ref}' vs '{col_act}'")
                    
                    # Verificar nombres
                    columnas_ref_set = set(estructura_referencia)
                    columnas_act_set = set(columnas)
                    
                    if columnas_ref_set != columnas_act_set:
                        print(f"      - Nombres diferentes:")
                        solo_en_ref = columnas_ref_set - columnas_act_set
                        solo_en_act = columnas_act_set - columnas_ref_set
                        
                        if solo_en_ref:
                            print(f"        Solo en referencia: {list(solo_en_ref)}")
                        if solo_en_act:
                            print(f"        Solo en actual: {list(solo_en_act)}")
            
        except Exception as e:
            print(f"\n❌ Error leyendo {archivo.name}: {str(e)}")
            estructuras[archivo.name] = None
    
    # Resumen final
    print(f"\n=== RESUMEN FINAL ===")
    
    archivos_correctos = 0
    archivos_incorrectos = 0
    
    for archivo_nombre, columnas in estructuras.items():
        if columnas is None:
            print(f"❌ {archivo_nombre}: Error al leer")
            archivos_incorrectos += 1
        elif columnas == estructura_referencia:
            print(f"✅ {archivo_nombre}: Correcto")
            archivos_correctos += 1
        else:
            print(f"❌ {archivo_nombre}: Incorrecto")
            archivos_incorrectos += 1
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Archivos correctos: {archivos_correctos}")
    print(f"   Archivos incorrectos: {archivos_incorrectos}")
    print(f"   Total de archivos: {len(archivos_csv)}")
    
    if archivos_incorrectos == 0:
        print(f"\n🎉 ¡TODOS LOS ARCHIVOS TIENEN LA MISMA ESTRUCTURA!")
        print(f"   Estructura estándar: {estructura_referencia}")
    else:
        print(f"\n⚠️  HAY DIFERENCIAS EN {archivos_incorrectos} ARCHIVO(S)")
    
    return archivos_incorrectos == 0

def main():
    """Función principal"""
    verificar_columnas_detallado()

if __name__ == "__main__":
    main()
