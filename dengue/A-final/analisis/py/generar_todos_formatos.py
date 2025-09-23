#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar análisis EDA en 4 formatos diferentes:
1. HTML con tablas y estilos
2. Markdown con tablas
3. Excel/CSV estructurado
4. Dashboard interactivo con Streamlit
"""

import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def crear_directorios():
    """Crea los directorios para cada formato"""
    base_dir = Path("C:/Facu/Cuarto Semestre/PP3/tp-dengue/dengue/A-final/analisis/info")
    
    directorios = {
        'html': base_dir / "html",
        'markdown': base_dir / "markdown", 
        'excel': base_dir / "excel",
        'streamlit': base_dir / "streamlit"
    }
    
    for nombre, directorio in directorios.items():
        directorio.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio creado: {directorio}")
    
    return directorios

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

def generar_html(df, directorio):
    """Genera reporte HTML con tablas y estilos"""
    archivo_html = directorio / "reporte_eda.html"
    
    # Calcular estadísticas
    stats_generales = {
        'total_registros': len(df),
        'total_columnas': len(df.columns),
        'periodo': f"{df['ano'].min():.0f} - {df['ano'].max():.0f}",
        'total_casos': df['cantidad_casos'].sum(),
        'poblacion_promedio': df['poblacion'].mean()
    }
    
    # Top departamentos
    top_departamentos = df['departamento_nombre'].value_counts().head(10)
    top_casos = df.groupby('departamento_nombre')['cantidad_casos'].sum().sort_values(ascending=False).head(10)
    
    # Distribución por año
    casos_por_ano = df.groupby('ano')['cantidad_casos'].sum().sort_index()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis EDA - Dataset de Dengue</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Análisis EDA - Dataset de Dengue Argentina</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats_generales['total_registros']:,}</div>
                <div class="stat-label">Total Registros</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats_generales['total_columnas']}</div>
                <div class="stat-label">Columnas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats_generales['total_casos']:,}</div>
                <div class="stat-label">Total Casos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats_generales['poblacion_promedio']:,.0f}</div>
                <div class="stat-label">Población Promedio</div>
            </div>
        </div>

        <h2>📋 Información de Columnas</h2>
        <table>
            <thead>
                <tr>
                    <th>Columna</th>
                    <th>Tipo</th>
                    <th>Valores Únicos</th>
                    <th>Valores Faltantes</th>
                    <th>Descripción</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Información de columnas
    for col in df.columns:
        descripcion = {
            'id_uta': 'Código UTA 2020 único',
            'departamento_nombre': 'Nombre del departamento/partido',
            'provincia_nombre': 'Nombre de la provincia',
            'ano': 'Año de los datos epidemiológicos',
            'semanas_epidemiologicas': 'Semana epidemiológica (1-52)',
            'grupo_edad_id': 'ID numérico del grupo etario',
            'grupo_edad_desc': 'Descripción del grupo etario',
            'cantidad_casos': 'Número de casos de dengue',
            'poblacion': 'Población del departamento'
        }.get(col, 'Sin descripción')
        
        html_content += f"""
                <tr>
                    <td><strong>{col}</strong></td>
                    <td>{df[col].dtype}</td>
                    <td>{df[col].nunique():,}</td>
                    <td>{df[col].isnull().sum():,}</td>
                    <td>{descripcion}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>

        <h2>🏆 Top 10 Departamentos con Más Registros</h2>
        <table>
            <thead>
                <tr>
                    <th>Posición</th>
                    <th>Departamento</th>
                    <th>Registros</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for i, (departamento, cantidad) in enumerate(top_departamentos.items(), 1):
        html_content += f"""
                <tr>
                    <td>{i}</td>
                    <td>{departamento}</td>
                    <td>{cantidad:,}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>

        <h2>🦠 Top 10 Departamentos con Más Casos de Dengue</h2>
        <table>
            <thead>
                <tr>
                    <th>Posición</th>
                    <th>Departamento</th>
                    <th>Casos</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for i, (departamento, casos) in enumerate(top_casos.items(), 1):
        html_content += f"""
                <tr>
                    <td>{i}</td>
                    <td>{departamento}</td>
                    <td>{casos:,}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>

        <h2>📅 Casos de Dengue por Año</h2>
        <table>
            <thead>
                <tr>
                    <th>Año</th>
                    <th>Casos</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for ano, casos in casos_por_ano.items():
        html_content += f"""
                <tr>
                    <td>{ano:.0f}</td>
                    <td>{casos:,}</td>
                </tr>
"""
    
    html_content += f"""
            </tbody>
        </table>

        <div class="footer">
            <p>Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
            <p>Dataset: dengue-final.csv | Total de registros: {len(df):,}</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Reporte HTML generado: {archivo_html}")

def generar_markdown(df, directorio):
    """Genera reporte en formato Markdown"""
    archivo_md = directorio / "reporte_eda.md"
    
    with open(archivo_md, 'w', encoding='utf-8') as f:
        f.write("# 📊 Análisis EDA - Dataset de Dengue Argentina\n\n")
        f.write(f"**Generado:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}\n\n")
        
        # Estadísticas generales
        f.write("## 📈 Estadísticas Generales\n\n")
        f.write("| Métrica | Valor |\n")
        f.write("|---------|-------|\n")
        f.write(f"| Total de registros | {len(df):,} |\n")
        f.write(f"| Total de columnas | {len(df.columns)} |\n")
        f.write(f"| Período de datos | {df['ano'].min():.0f} - {df['ano'].max():.0f} |\n")
        f.write(f"| Total de casos de dengue | {df['cantidad_casos'].sum():,} |\n")
        f.write(f"| Población promedio | {df['poblacion'].mean():,.0f} |\n\n")
        
        # Información de columnas
        f.write("## 📋 Información de Columnas\n\n")
        f.write("| Columna | Tipo | Valores Únicos | Valores Faltantes | Descripción |\n")
        f.write("|---------|------|----------------|-------------------|-------------|\n")
        
        descripciones = {
            'id_uta': 'Código UTA 2020 único',
            'departamento_nombre': 'Nombre del departamento/partido',
            'provincia_nombre': 'Nombre de la provincia',
            'ano': 'Año de los datos epidemiológicos',
            'semanas_epidemiologicas': 'Semana epidemiológica (1-52)',
            'grupo_edad_id': 'ID numérico del grupo etario',
            'grupo_edad_desc': 'Descripción del grupo etario',
            'cantidad_casos': 'Número de casos de dengue',
            'poblacion': 'Población del departamento'
        }
        
        for col in df.columns:
            desc = descripciones.get(col, 'Sin descripción')
            f.write(f"| **{col}** | {df[col].dtype} | {df[col].nunique():,} | {df[col].isnull().sum():,} | {desc} |\n")
        
        f.write("\n")
        
        # Top departamentos
        f.write("## 🏆 Top 10 Departamentos con Más Registros\n\n")
        f.write("| Posición | Departamento | Registros |\n")
        f.write("|----------|--------------|----------|\n")
        
        top_departamentos = df['departamento_nombre'].value_counts().head(10)
        for i, (departamento, cantidad) in enumerate(top_departamentos.items(), 1):
            f.write(f"| {i} | {departamento} | {cantidad:,} |\n")
        
        f.write("\n")
        
        # Top casos
        f.write("## 🦠 Top 10 Departamentos con Más Casos de Dengue\n\n")
        f.write("| Posición | Departamento | Casos |\n")
        f.write("|----------|--------------|-------|\n")
        
        top_casos = df.groupby('departamento_nombre')['cantidad_casos'].sum().sort_values(ascending=False).head(10)
        for i, (departamento, casos) in enumerate(top_casos.items(), 1):
            f.write(f"| {i} | {departamento} | {casos:,} |\n")
        
        f.write("\n")
        
        # Casos por año
        f.write("## 📅 Casos de Dengue por Año\n\n")
        f.write("| Año | Casos |\n")
        f.write("|-----|-------|\n")
        
        casos_por_ano = df.groupby('ano')['cantidad_casos'].sum().sort_index()
        for ano, casos in casos_por_ano.items():
            f.write(f"| {ano:.0f} | {casos:,} |\n")
        
        f.write("\n")
        
        # Estadísticas por columna
        f.write("## 📊 Estadísticas por Columna\n\n")
        
        for col in df.columns:
            f.write(f"### {col}\n\n")
            
            if df[col].dtype in ['int64', 'float64']:
                f.write("| Estadística | Valor |\n")
                f.write("|-------------|-------|\n")
                f.write(f"| Media | {df[col].mean():.2f} |\n")
                f.write(f"| Mediana | {df[col].median():.2f} |\n")
                f.write(f"| Desviación estándar | {df[col].std():.2f} |\n")
                f.write(f"| Mínimo | {df[col].min():.2f} |\n")
                f.write(f"| Máximo | {df[col].max():.2f} |\n")
            else:
                f.write(f"**Valores únicos:** {df[col].nunique():,}\n\n")
                f.write("**Top 5 valores más frecuentes:**\n\n")
                top_5 = df[col].value_counts().head()
                for valor, frecuencia in top_5.items():
                    f.write(f"- {valor}: {frecuencia:,} ({frecuencia/len(df)*100:.2f}%)\n")
            
            f.write("\n")
    
    print(f"✓ Reporte Markdown generado: {archivo_md}")

def generar_excel(df, directorio):
    """Genera archivos Excel/CSV estructurados"""
    # Crear múltiples archivos CSV organizados
    archivos_excel = {
        'resumen_general': directorio / "resumen_general.csv",
        'estadisticas_columnas': directorio / "estadisticas_columnas.csv",
        'top_departamentos': directorio / "top_departamentos.csv",
        'casos_por_ano': directorio / "casos_por_ano.csv",
        'distribucion_provincias': directorio / "distribucion_provincias.csv"
    }
    
    # Resumen general
    resumen = pd.DataFrame({
        'Métrica': ['Total Registros', 'Total Columnas', 'Período', 'Total Casos', 'Población Promedio'],
        'Valor': [len(df), len(df.columns), f"{df['ano'].min():.0f}-{df['ano'].max():.0f}", 
                 df['cantidad_casos'].sum(), df['poblacion'].mean()]
    })
    resumen.to_csv(archivos_excel['resumen_general'], index=False, encoding='utf-8')
    
    # Estadísticas por columna
    stats_columnas = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            stats_columnas.append({
                'Columna': col,
                'Tipo': 'Numérica',
                'Media': df[col].mean(),
                'Mediana': df[col].median(),
                'Desv_Std': df[col].std(),
                'Minimo': df[col].min(),
                'Maximo': df[col].max(),
                'Valores_Unicos': df[col].nunique(),
                'Valores_Faltantes': df[col].isnull().sum()
            })
        else:
            stats_columnas.append({
                'Columna': col,
                'Tipo': 'Categórica',
                'Valores_Unicos': df[col].nunique(),
                'Valores_Faltantes': df[col].isnull().sum(),
                'Moda': df[col].mode().iloc[0] if not df[col].mode().empty else 'N/A'
            })
    
    pd.DataFrame(stats_columnas).to_csv(archivos_excel['estadisticas_columnas'], index=False, encoding='utf-8')
    
    # Top departamentos
    top_departamentos = df['departamento_nombre'].value_counts().head(20).reset_index()
    top_departamentos.columns = ['Departamento', 'Registros']
    top_departamentos['Posicion'] = range(1, len(top_departamentos) + 1)
    top_departamentos = top_departamentos[['Posicion', 'Departamento', 'Registros']]
    top_departamentos.to_csv(archivos_excel['top_departamentos'], index=False, encoding='utf-8')
    
    # Casos por año
    casos_por_ano = df.groupby('ano')['cantidad_casos'].sum().sort_index().reset_index()
    casos_por_ano.columns = ['Año', 'Casos']
    casos_por_ano.to_csv(archivos_excel['casos_por_ano'], index=False, encoding='utf-8')
    
    # Distribución por provincias
    dist_provincias = df['provincia_nombre'].value_counts().reset_index()
    dist_provincias.columns = ['Provincia', 'Registros']
    dist_provincias.to_csv(archivos_excel['distribucion_provincias'], index=False, encoding='utf-8')
    
    print(f"✓ Archivos Excel/CSV generados en: {directorio}")
    for nombre, archivo in archivos_excel.items():
        print(f"  - {archivo.name}")

def generar_streamlit(df, directorio):
    """Genera dashboard interactivo con Streamlit"""
    archivo_streamlit = directorio / "dashboard_eda.py"
    
    streamlit_code = f"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Análisis EDA - Dengue Argentina",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🦠 Análisis EDA - Dataset de Dengue Argentina")
st.markdown("---")

# Cargar datos
@st.cache_data
def load_data():
    return pd.read_csv("C:/Facu/Cuarto Semestre/PP3/tp-dengue/dengue/A-final/dengue-final.csv")

df = load_data()

# Sidebar con filtros
st.sidebar.header("🔍 Filtros")

# Filtro por año
anos_disponibles = sorted(df['ano'].unique())
ano_seleccionado = st.sidebar.selectbox("Seleccionar Año", ["Todos"] + [str(int(a)) for a in anos_disponibles])

# Filtro por provincia
provincias_disponibles = sorted(df['provincia_nombre'].unique())
provincia_seleccionada = st.sidebar.selectbox("Seleccionar Provincia", ["Todas"] + provincias_disponibles)

# Aplicar filtros
df_filtrado = df.copy()
if ano_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['ano'] == int(ano_seleccionado)]
if provincia_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['provincia_nombre'] == provincia_seleccionada]

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Registros", f"{{:,}}".format(len(df_filtrado)))

with col2:
    st.metric("Total Casos", f"{{:,}}".format(df_filtrado['cantidad_casos'].sum()))

with col3:
    st.metric("Departamentos", df_filtrado['departamento_nombre'].nunique())

with col4:
    st.metric("Población Promedio", f"{{:,.0f}}".format(df_filtrado['poblacion'].mean()))

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Casos por Año")
    casos_por_ano = df_filtrado.groupby('ano')['cantidad_casos'].sum().sort_index()
    fig_ano = px.bar(x=casos_por_ano.index, y=casos_por_ano.values, 
                     title="Casos de Dengue por Año",
                     labels={{'x': 'Año', 'y': 'Casos'}})
    st.plotly_chart(fig_ano, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Departamentos")
    top_departamentos = df_filtrado['departamento_nombre'].value_counts().head(10)
    fig_deptos = px.bar(x=top_departamentos.values, y=top_departamentos.index,
                        orientation='h', title="Top 10 Departamentos por Registros",
                        labels={{'x': 'Registros', 'y': 'Departamento'}})
    st.plotly_chart(fig_deptos, use_container_width=True)

# Tabla de datos
st.subheader("📊 Datos Filtrados")
st.dataframe(df_filtrado.head(100), use_container_width=True)

# Estadísticas por columna
st.subheader("📈 Estadísticas por Columna")

columna_seleccionada = st.selectbox("Seleccionar Columna", df.columns)

if df[columna_seleccionada].dtype in ['int64', 'float64']:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Estadísticas Descriptivas:**")
        stats = df[columna_seleccionada].describe()
        st.write(stats)
    
    with col2:
        st.write("**Distribución:**")
        fig_hist = px.histogram(df, x=columna_seleccionada, title=f"Distribución de {{columna_seleccionada}}")
        st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.write("**Valores Únicos:**", df[columna_seleccionada].nunique())
    st.write("**Top 10 Valores:**")
    top_valores = df[columna_seleccionada].value_counts().head(10)
    st.write(top_valores)

# Footer
st.markdown("---")
st.markdown(f"**Reporte generado:** {{datetime.now().strftime('%d/%m/%Y a las %H:%M')}}")
st.markdown(f"**Total de registros en dataset:** {{len(df):,}}")
"""
    
    with open(archivo_streamlit, 'w', encoding='utf-8') as f:
        f.write(streamlit_code)
    
    # Crear archivo requirements para Streamlit
    requirements = directorio / "requirements_streamlit.txt"
    with open(requirements, 'w', encoding='utf-8') as f:
        f.write("streamlit\npandas\nnumpy\nplotly\n")
    
    # Crear archivo de instrucciones
    instrucciones = directorio / "INSTRUCCIONES_STREAMLIT.txt"
    with open(instrucciones, 'w', encoding='utf-8') as f:
        f.write("""
INSTRUCCIONES PARA EJECUTAR EL DASHBOARD STREAMLIT
=================================================

1. Instalar dependencias:
   pip install -r requirements_streamlit.txt

2. Ejecutar el dashboard:
   streamlit run dashboard_eda.py

3. El dashboard se abrirá automáticamente en tu navegador
   (generalmente en http://localhost:8501)

4. Características del dashboard:
   - Filtros interactivos por año y provincia
   - Métricas en tiempo real
   - Gráficos interactivos con Plotly
   - Tabla de datos filtrable
   - Estadísticas por columna seleccionable

5. Para detener el dashboard:
   Presiona Ctrl+C en la terminal
""")
    
    print(f"✓ Dashboard Streamlit generado: {archivo_streamlit}")
    print(f"✓ Archivo de instrucciones: {instrucciones}")

def main():
    """Función principal"""
    print("🚀 GENERADOR DE ANÁLISIS EDA EN 4 FORMATOS")
    print("=" * 50)
    
    # Crear directorios
    directorios = crear_directorios()
    
    # Cargar dataset
    df = cargar_dataset()
    if df is None:
        return
    
    print(f"\n📊 Generando análisis en 4 formatos...")
    
    # Generar cada formato
    print("\n1️⃣ Generando HTML...")
    generar_html(df, directorios['html'])
    
    print("\n2️⃣ Generando Markdown...")
    generar_markdown(df, directorios['markdown'])
    
    print("\n3️⃣ Generando Excel/CSV...")
    generar_excel(df, directorios['excel'])
    
    print("\n4️⃣ Generando Streamlit...")
    generar_streamlit(df, directorios['streamlit'])
    
    print(f"\n🎉 ¡Todos los formatos generados exitosamente!")
    print(f"\n📁 Archivos creados en:")
    for nombre, directorio in directorios.items():
        print(f"  📂 {nombre.upper()}: {directorio}")
    
    print(f"\n💡 Recomendaciones:")
    print(f"  🌐 HTML: Abre reporte_eda.html en tu navegador")
    print(f"  📝 Markdown: Abre reporte_eda.md en cualquier editor")
    print(f"  📊 Excel: Abre los archivos CSV en Excel")
    print(f"  🚀 Streamlit: Ejecuta 'streamlit run dashboard_eda.py'")

if __name__ == "__main__":
    main()
