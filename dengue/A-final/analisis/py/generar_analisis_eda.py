#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar análisis EDA del dataset de dengue
Genera tres archivos:
1. info.txt - Información de columnas y tipos de datos
2. analisis.txt - Estadísticas descriptivas por columna
3. cantidades.txt - Conteos y distribuciones
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def crear_directorio_analisis():
    """Crea el directorio de análisis si no existe"""
    directorio = Path("C:/Facu/Cuarto Semestre/PP3/tp-dengue/dengue/A-final/analisis/info")
    directorio.mkdir(parents=True, exist_ok=True)
    return directorio

def cargar_dataset():
    """Carga el dataset de dengue"""
    archivo = "C:/Facu/Cuarto Semestre/PP3/tp-dengue/dengue/A-final/dengue-final.csv"
    try:
        df = pd.read_csv(archivo)
        print(f"✓ Dataset cargado: {df.shape[0]:,} filas, {df.shape[1]} columnas")
        return df
    except Exception as e:
        print(f"✗ Error al cargar dataset: {e}")
        return None

def generar_archivo_info(df, directorio):
    """Genera archivo con información de columnas y tipos de datos"""
    archivo_info = directorio / "info.txt"
    
    with open(archivo_info, 'w', encoding='utf-8') as f:
        f.write("INFORMACIÓN DEL DATASET DE DENGUE\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Dimensiones del dataset: {df.shape[0]:,} filas × {df.shape[1]} columnas\n")
        f.write(f"Memoria utilizada: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n")
        
        f.write("DESCRIPCIÓN DE COLUMNAS:\n")
        f.write("-" * 30 + "\n\n")
        
        for col in df.columns:
            f.write(f"COLUMNA: {col}\n")
            f.write(f"Tipo de datos: {df[col].dtype}\n")
            f.write(f"Valores únicos: {df[col].nunique():,}\n")
            f.write(f"Valores faltantes: {df[col].isnull().sum():,} ({df[col].isnull().sum()/len(df)*100:.2f}%)\n")
            
            # Descripción específica por columna
            if col == 'id_uta':
                f.write("Descripción: Código UTA 2020 único para cada departamento\n")
                f.write(f"Rango: {df[col].min():.0f} - {df[col].max():.0f}\n")
            elif col == 'departamento_nombre':
                f.write("Descripción: Nombre del departamento/partido\n")
                f.write(f"Ejemplos: {', '.join(df[col].unique()[:5])}\n")
            elif col == 'provincia_nombre':
                f.write("Descripción: Nombre de la provincia\n")
                f.write(f"Provincias: {', '.join(df[col].unique())}\n")
            elif col == 'ano':
                f.write("Descripción: Año de los datos epidemiológicos\n")
                f.write(f"Años: {sorted(df[col].unique())}\n")
            elif col == 'semanas_epidemiologicas':
                f.write("Descripción: Semana epidemiológica del año (1-52)\n")
                f.write(f"Rango: {df[col].min():.0f} - {df[col].max():.0f}\n")
            elif col == 'grupo_edad_id':
                f.write("Descripción: ID numérico del grupo etario\n")
                f.write(f"Grupos: {sorted(df[col].unique())}\n")
            elif col == 'grupo_edad_desc':
                f.write("Descripción: Descripción del grupo etario\n")
                f.write(f"Grupos: {', '.join(df[col].unique())}\n")
            elif col == 'cantidad_casos':
                f.write("Descripción: Número de casos de dengue reportados\n")
                f.write(f"Rango: {df[col].min():.0f} - {df[col].max():.0f}\n")
            elif col == 'poblacion':
                f.write("Descripción: Población del departamento en ese año\n")
                f.write(f"Rango: {df[col].min():.0f} - {df[col].max():.0f}\n")
            
            f.write("\n" + "-" * 50 + "\n\n")
    
    print(f"✓ Archivo info.txt generado: {archivo_info}")

def generar_archivo_analisis(df, directorio):
    """Genera archivo con estadísticas descriptivas por columna"""
    archivo_analisis = directorio / "analisis.txt"
    
    with open(archivo_analisis, 'w', encoding='utf-8') as f:
        f.write("ANÁLISIS ESTADÍSTICO DEL DATASET DE DENGUE\n")
        f.write("=" * 50 + "\n\n")
        
        # Estadísticas generales
        f.write("ESTADÍSTICAS GENERALES:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Total de registros: {len(df):,}\n")
        f.write(f"Total de columnas: {len(df.columns)}\n")
        f.write(f"Período de datos: {df['ano'].min():.0f} - {df['ano'].max():.0f}\n")
        f.write(f"Total de casos de dengue: {df['cantidad_casos'].sum():,.0f}\n")
        f.write(f"Población total promedio: {df['poblacion'].mean():,.0f}\n\n")
        
        # Análisis por columna
        for col in df.columns:
            f.write(f"COLUMNA: {col}\n")
            f.write("-" * 20 + "\n")
            
            if df[col].dtype in ['int64', 'float64']:
                # Estadísticas para variables numéricas
                f.write(f"Tipo: Numérica\n")
                f.write(f"Media: {df[col].mean():.2f}\n")
                f.write(f"Mediana: {df[col].median():.2f}\n")
                moda = df[col].mode()
                f.write(f"Moda: {moda.iloc[0] if not moda.empty else 'N/A'}\n")
                f.write(f"Desviación estándar: {df[col].std():.2f}\n")
                f.write(f"Varianza: {df[col].var():.2f}\n")
                f.write(f"Mínimo: {df[col].min():.2f}\n")
                f.write(f"Máximo: {df[col].max():.2f}\n")
                f.write(f"Rango: {df[col].max() - df[col].min():.2f}\n")
                f.write(f"Percentil 25: {df[col].quantile(0.25):.2f}\n")
                f.write(f"Percentil 75: {df[col].quantile(0.75):.2f}\n")
                if df[col].mean() != 0:
                    f.write(f"Coeficiente de variación: {(df[col].std()/df[col].mean()*100):.2f}%\n")
                else:
                    f.write(f"Coeficiente de variación: N/A (media = 0)\n")
                
                # Análisis de distribución
                if col == 'cantidad_casos':
                    f.write(f"Casos con valor 0: {(df[col] == 0).sum():,} ({(df[col] == 0).sum()/len(df)*100:.2f}%)\n")
                    f.write(f"Casos con valor > 0: {(df[col] > 0).sum():,} ({(df[col] > 0).sum()/len(df)*100:.2f}%)\n")
                
            else:
                # Estadísticas para variables categóricas
                f.write(f"Tipo: Categórica\n")
                f.write(f"Valores únicos: {df[col].nunique():,}\n")
                moda = df[col].mode()
                f.write(f"Moda: {moda.iloc[0] if not moda.empty else 'N/A'}\n")
                if not df[col].value_counts().empty:
                    f.write(f"Frecuencia de la moda: {df[col].value_counts().iloc[0]:,}\n")
                else:
                    f.write(f"Frecuencia de la moda: 0\n")
                
                # Top 5 valores más frecuentes
                f.write(f"Top 5 valores más frecuentes:\n")
                top_5 = df[col].value_counts().head()
                for valor, frecuencia in top_5.items():
                    f.write(f"  {valor}: {frecuencia:,} ({frecuencia/len(df)*100:.2f}%)\n")
            
            f.write("\n" + "=" * 50 + "\n\n")
    
    print(f"✓ Archivo analisis.txt generado: {archivo_analisis}")

def generar_archivo_cantidades(df, directorio):
    """Genera archivo con conteos y distribuciones"""
    archivo_cantidades = directorio / "cantidades.txt"
    
    with open(archivo_cantidades, 'w', encoding='utf-8') as f:
        f.write("ANÁLISIS DE CANTIDADES Y DISTRIBUCIONES\n")
        f.write("=" * 50 + "\n\n")
        
        # Información general
        f.write("INFORMACIÓN GENERAL:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total de filas en el dataset: {len(df):,}\n")
        f.write(f"Total de departamentos únicos (id_uta): {df['id_uta'].nunique():,}\n")
        f.write(f"Total de provincias: {df['provincia_nombre'].nunique()}\n")
        f.write(f"Total de años: {df['ano'].nunique()}\n")
        f.write(f"Total de semanas epidemiológicas: {df['semanas_epidemiologicas'].nunique()}\n")
        f.write(f"Total de grupos etarios: {df['grupo_edad_id'].nunique()}\n\n")
        
        # Distribución por año
        f.write("DISTRIBUCIÓN POR AÑO:\n")
        f.write("-" * 20 + "\n")
        distribucion_ano = df['ano'].value_counts().sort_index()
        for ano, cantidad in distribucion_ano.items():
            f.write(f"{ano:.0f}: {cantidad:,} registros\n")
        f.write(f"Total: {distribucion_ano.sum():,} registros\n\n")
        
        # Distribución por provincia
        f.write("DISTRIBUCIÓN POR PROVINCIA:\n")
        f.write("-" * 25 + "\n")
        distribucion_provincia = df['provincia_nombre'].value_counts()
        for provincia, cantidad in distribucion_provincia.items():
            f.write(f"{provincia}: {cantidad:,} registros\n")
        f.write(f"Total: {distribucion_provincia.sum():,} registros\n\n")
        
        # Top 10 departamentos con más registros
        f.write("TOP 10 DEPARTAMENTOS CON MÁS REGISTROS:\n")
        f.write("-" * 40 + "\n")
        top_departamentos = df['departamento_nombre'].value_counts().head(10)
        for i, (departamento, cantidad) in enumerate(top_departamentos.items(), 1):
            f.write(f"{i:2d}. {departamento}: {cantidad:,} registros\n")
        f.write("\n")
        
        # Distribución por grupo etario
        f.write("DISTRIBUCIÓN POR GRUPO ETARIO:\n")
        f.write("-" * 30 + "\n")
        distribucion_edad = df.groupby(['grupo_edad_id', 'grupo_edad_desc']).size().reset_index(name='cantidad')
        distribucion_edad = distribucion_edad.sort_values('grupo_edad_id')
        for _, row in distribucion_edad.iterrows():
            f.write(f"ID {row['grupo_edad_id']}: {row['grupo_edad_desc']} - {row['cantidad']:,} registros\n")
        f.write("\n")
        
        # Análisis de casos de dengue
        f.write("ANÁLISIS DE CASOS DE DENGUE:\n")
        f.write("-" * 25 + "\n")
        f.write(f"Total de casos reportados: {df['cantidad_casos'].sum():,.0f}\n")
        f.write(f"Registros con casos > 0: {(df['cantidad_casos'] > 0).sum():,}\n")
        f.write(f"Registros con casos = 0: {(df['cantidad_casos'] == 0).sum():,}\n")
        f.write(f"Promedio de casos por registro: {df['cantidad_casos'].mean():.2f}\n")
        f.write(f"Mediana de casos por registro: {df['cantidad_casos'].median():.2f}\n\n")
        
        # Top 10 departamentos con más casos
        f.write("TOP 10 DEPARTAMENTOS CON MÁS CASOS DE DENGUE:\n")
        f.write("-" * 45 + "\n")
        casos_por_departamento = df.groupby('departamento_nombre')['cantidad_casos'].sum().sort_values(ascending=False).head(10)
        for i, (departamento, casos) in enumerate(casos_por_departamento.items(), 1):
            f.write(f"{i:2d}. {departamento}: {casos:,.0f} casos\n")
        f.write("\n")
        
        # Distribución de población
        f.write("ANÁLISIS DE POBLACIÓN:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Población total: {df['poblacion'].sum():,.0f}\n")
        f.write(f"Población promedio por departamento: {df['poblacion'].mean():,.0f}\n")
        f.write(f"Población mediana por departamento: {df['poblacion'].median():,.0f}\n")
        f.write(f"Departamento con mayor población: {df.loc[df['poblacion'].idxmax(), 'departamento_nombre']} ({df['poblacion'].max():,.0f})\n")
        f.write(f"Departamento con menor población: {df.loc[df['poblacion'].idxmin(), 'departamento_nombre']} ({df['poblacion'].min():,.0f})\n\n")
        
        # Análisis temporal
        f.write("ANÁLISIS TEMPORAL:\n")
        f.write("-" * 15 + "\n")
        casos_por_ano = df.groupby('ano')['cantidad_casos'].sum().sort_index()
        f.write("Casos de dengue por año:\n")
        for ano, casos in casos_por_ano.items():
            f.write(f"{ano:.0f}: {casos:,.0f} casos\n")
        f.write("\n")
        
        # Análisis por semana epidemiológica
        f.write("DISTRIBUCIÓN POR SEMANA EPIDEMIOLÓGICA:\n")
        f.write("-" * 35 + "\n")
        casos_por_semana = df.groupby('semanas_epidemiologicas')['cantidad_casos'].sum().sort_index()
        f.write("Top 10 semanas con más casos:\n")
        top_semanas = casos_por_semana.sort_values(ascending=False).head(10)
        for semana, casos in top_semanas.items():
            f.write(f"Semana {semana:.0f}: {casos:,.0f} casos\n")
    
    print(f"✓ Archivo cantidades.txt generado: {archivo_cantidades}")

def main():
    """Función principal"""
    print("🔍 GENERADOR DE ANÁLISIS EDA - DATASET DE DENGUE")
    print("=" * 50)
    
    # Crear directorio
    directorio = crear_directorio_analisis()
    print(f"✓ Directorio de análisis: {directorio}")
    
    # Cargar dataset
    df = cargar_dataset()
    if df is None:
        return
    
    print(f"\n📊 Generando archivos de análisis...")
    
    # Generar archivos
    generar_archivo_info(df, directorio)
    generar_archivo_analisis(df, directorio)
    generar_archivo_cantidades(df, directorio)
    
    print(f"\n🎉 ¡Análisis EDA completado!")
    print(f"Archivos generados en: {directorio}")
    print("\nArchivos creados:")
    print("  - info.txt: Información de columnas y tipos de datos")
    print("  - analisis.txt: Estadísticas descriptivas por columna")
    print("  - cantidades.txt: Conteos y distribuciones")

if __name__ == "__main__":
    main()
