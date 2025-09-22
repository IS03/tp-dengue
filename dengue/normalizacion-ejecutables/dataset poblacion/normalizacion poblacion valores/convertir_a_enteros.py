#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir todos los valores numéricos a enteros en los archivos de población.
Convierte los valores flotantes (.0) a enteros en todos los archivos CSV de población.
"""

import pandas as pd
import os
import glob

def convertir_valores_a_enteros(archivo_csv):
    """
    Convierte todos los valores numéricos de un archivo CSV a enteros.
    
    Args:
        archivo_csv (str): Ruta al archivo CSV a procesar
    
    Returns:
        bool: True si se procesó correctamente, False en caso contrario
    """
    try:
        print(f"Procesando: {archivo_csv}")
        
        # Leer el archivo CSV
        df = pd.read_csv(archivo_csv)
        
        # Convertir los nombres de las columnas numéricas a enteros (excluyendo la primera columna)
        columnas_originales = df.columns.tolist()
        columnas_nuevas = []
        
        for i, columna in enumerate(columnas_originales):
            if i == 0:
                # Mantener la primera columna sin cambios (nombre del departamento/partido/comuna)
                columnas_nuevas.append(columna)
            else:
                # Convertir el nombre de la columna a entero si es numérico
                try:
                    # Intentar convertir a float y luego a int
                    valor_numerico = float(columna)
                    if valor_numerico.is_integer():
                        columnas_nuevas.append(str(int(valor_numerico)))
                    else:
                        columnas_nuevas.append(str(int(round(valor_numerico))))
                except ValueError:
                    # Si no es numérico, mantener el nombre original
                    columnas_nuevas.append(columna)
        
        # Asignar los nuevos nombres de columnas
        df.columns = columnas_nuevas
        
        # Obtener las columnas numéricas (excluyendo la primera columna que es el nombre del departamento/partido/comuna)
        columnas_numericas = df.columns[1:]
        
        # Convertir cada columna numérica a entero
        for columna in columnas_numericas:
            # Convertir a numérico primero (por si hay valores no numéricos)
            df[columna] = pd.to_numeric(df[columna], errors='coerce')
            # Redondear a entero y luego convertir a tipo entero
            df[columna] = df[columna].round().astype('Int64')  # Int64 permite valores NaN
        
        # Guardar el archivo modificado
        df.to_csv(archivo_csv, index=False)
        print(f"✓ Convertido exitosamente: {archivo_csv}")
        return True
        
    except Exception as e:
        print(f"✗ Error procesando {archivo_csv}: {str(e)}")
        return False

def main():
    """
    Función principal que procesa todos los archivos de población.
    """
    # Directorio base donde están los archivos de población
    directorio_poblacion = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-poblacion"
    
    # Lista de archivos específicos que mencionaste
    archivos_especificos = [
        "buenos aires.csv",
        "caba.csv", 
        "chaco.csv",
        "catamarca.csv",
        "chubut.csv",
        "cordoba.csv",
        "corrientes.csv",
        "formosa.csv",
        "entre rios.csv",
        "jujuy.csv",
        "la pampa.csv",
        "la rioja.csv",
        "mendoza.csv",
        "misiones.csv",
        "neuquen.csv",
        "rio negro.csv",
        "salta.csv",
        "san juan.csv",
        "san luis.csv",
        "santa cruz.csv",
        "santa fe.csv",
        "tierra del fuego.csv",
        "santiago del estero.csv",
        "tucuman.csv"
    ]
    
    print("=" * 60)
    print("CONVERSIÓN DE VALORES NUMÉRICOS A ENTEROS")
    print("Archivos de Población")
    print("=" * 60)
    
    archivos_procesados = 0
    archivos_exitosos = 0
    archivos_fallidos = 0
    
    # Procesar cada archivo específico
    for archivo in archivos_especificos:
        ruta_archivo = os.path.join(directorio_poblacion, archivo)
        
        if os.path.exists(ruta_archivo):
            archivos_procesados += 1
            if convertir_valores_a_enteros(ruta_archivo):
                archivos_exitosos += 1
            else:
                archivos_fallidos += 1
        else:
            print(f"⚠ Archivo no encontrado: {ruta_archivo}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE PROCESAMIENTO")
    print("=" * 60)
    print(f"Archivos procesados: {archivos_procesados}")
    print(f"Archivos exitosos: {archivos_exitosos}")
    print(f"Archivos fallidos: {archivos_fallidos}")
    
    if archivos_fallidos == 0:
        print("\n✓ Todos los archivos se procesaron correctamente!")
    else:
        print(f"\n⚠ {archivos_fallidos} archivo(s) tuvieron errores durante el procesamiento.")
    
    print("\nConversión completada.")

if __name__ == "__main__":
    main()
