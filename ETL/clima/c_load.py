# -*- coding: utf-8 -*-
"""
ETL Load Module: Carga de datos transformados a la base de datos
---------------------------------------------------------------
Este módulo implementa las funciones necesarias para cargar los datos
transformados del clima a la base de datos SQLite, incluyendo la creación
de tablas, preparación de datos y carga masiva.
"""

import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from typing import Tuple, Optional
import sys
sys.path.append(os.path.dirname(__file__))
from b_transform import transform_clima_data
import scripts.create_database as baseDatos  # Importar para usar el engine y crear tablas si es necesario

# Configuración de logging
log = logging.getLogger(__name__)

# =============================================================================
# Funciones de creación de tablas (usando baseDatos.py)
# =============================================================================

def create_tables(engine) -> bool:
    """
    Crea todas las tablas necesarias en la base de datos usando baseDatos.py.
    Retorna True si se crearon exitosamente, False en caso contrario.
    """
    try:
        # Importar y ejecutar la creación de tablas desde baseDatos.py
        # Esto asegura que se use el esquema completo definido en baseDatos.py
        log.info("Creando tablas usando baseDatos.py...")
        # Las tablas ya se crean al importar baseDatos.py, pero podemos verificar
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            required_tables = ['calendario', 'estaciones', 'clima']
            missing_tables = [t for t in required_tables if t not in tables]
            if missing_tables:
                log.warning(f"Tablas faltantes: {missing_tables}. Ejecutando creación desde baseDatos.py")
                # Re-ejecutar el DDL de baseDatos.py
                with engine.begin() as conn:
                    for stmt in baseDatos.ddl.strip().split(";"):
                        s = stmt.strip()
                        if s:
                            conn.execute(text(s))
            else:
                log.info("Todas las tablas requeridas existen")

        log.info("Tablas verificadas/creadas exitosamente")
        return True

    except SQLAlchemyError as e:
        log.error(f"Error creando tablas: {e}")
        return False


def create_calendario_table(engine) -> bool:
    """
    Crea y pobla la tabla calendario con fechas desde 1900 hasta 2100.
    Retorna True si se creó exitosamente, False en caso contrario.
    """
    try:
        # Verificar si ya existe la tabla calendario
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM calendario"))
            count = result.scalar()
            if count > 0:
                log.info("Tabla calendario ya poblada")
                return True

        # Crear rango de fechas en lotes más pequeños para evitar límite de variables SQL
        start_date = pd.Timestamp('1900-01-01')
        end_date = pd.Timestamp('2100-12-31')
        batch_size = 365  # Un año por lote

        total_inserted = 0
        current_date = start_date

        while current_date <= end_date:
            batch_end = min(current_date + pd.Timedelta(days=batch_size-1), end_date)
            fechas = pd.date_range(start=current_date, end=batch_end, freq='D')

            # Crear DataFrame con las columnas necesarias
            calendario_df = pd.DataFrame({
                'fecha': fechas.strftime('%Y-%m-%d'),
                'dia': fechas.day,
                'mes': fechas.month,
                'anio': fechas.year,
                'semana': fechas.isocalendar().week,
                'trimestre': ((fechas.month - 1) // 3) + 1,
                'semestre': ((fechas.month - 1) // 6) + 1,
                'bisiesto': fechas.is_leap_year.astype(int),
                'quincena': ((fechas.day - 1) // 15) + 1
            })

            # Crear IdFecha como YYYYMMDD
            calendario_df['IdFecha'] = fechas.strftime('%Y%m%d').astype(int)

            # Cargar a la base de datos
            calendario_df.to_sql('calendario', engine, if_exists='append', index=False, method='multi')

            total_inserted += len(calendario_df)
            current_date = batch_end + pd.Timedelta(days=1)

        log.info(f"Tabla calendario poblada con {total_inserted} fechas")
        return True

    except SQLAlchemyError as e:
        log.error(f"Error creando tabla calendario: {e}")
        return False


def load_estaciones_to_db(engine) -> bool:
    """
    Carga las estaciones meteorológicas desde el CSV a la base de datos.
    Retorna True si se cargaron exitosamente, False en caso contrario.
    """
    try:
        csv_path = "data/estaciones-meteorologicas-inta.csv"
        if not os.path.exists(csv_path):
            log.warning(f"No se encontró el archivo de estaciones: {csv_path}")
            return False

        # Leer CSV de estaciones
        df_est = pd.read_csv(csv_path)

        # Normalizar nombres de columnas: lowercase, replace spaces with underscores
        df_est.columns = [c.lower().replace(' ', '_') for c in df_est.columns]

        # Renombrar columnas específicas
        df_est.rename(columns={'nombre': 'estacion', 'altura': 'altitud'}, inplace=True)

        # Verificar columnas necesarias
        required_cols = ['id_interno', 'estacion']
        missing_cols = [col for col in required_cols if col not in df_est.columns]
        if missing_cols:
            log.error(f"Faltan columnas requeridas en el CSV de estaciones: {missing_cols}")
            return False

        # Verificar si ya existen datos en la tabla estaciones
        with engine.connect() as conn:
            est_count = conn.execute(text("SELECT COUNT(*) FROM estaciones")).scalar()

        if est_count > 0:
            log.info("La tabla de estaciones ya tiene datos, saltando carga")
            return True

        # Preparar datos para insertar
        # Usar 'id_interno' como id_estacion_original, generar IdEstacion autoincremental

        # Convertir tipos de datos
        df_est['id_interno'] = df_est['id_interno'].astype(str)  # Mantener como string
        df_est['latitud'] = pd.to_numeric(df_est['latitud'], errors='coerce')
        df_est['longitud'] = pd.to_numeric(df_est['longitud'], errors='coerce')
        df_est['altitud'] = pd.to_numeric(df_est['altitud'], errors='coerce')

        # Crear DataFrame único de estaciones
        est_unique = df_est[['id_interno', 'estacion']].drop_duplicates(subset=['id_interno']).reset_index(drop=True)
        est_unique = est_unique.rename(columns={'id_interno': 'id_estacion_original'})

        # Agregar coordenadas si existen
        if 'latitud' in df_est.columns and 'longitud' in df_est.columns:
            coords = df_est[['id_interno', 'latitud', 'longitud', 'altitud']].drop_duplicates(subset=['id_interno'])
            est_unique = est_unique.merge(
                coords,
                left_on='id_estacion_original', right_on='id_interno', how='left'
            ).drop(columns=['id_interno'])

        # Convertir tipos para SQLite
        est_unique['id_estacion_original'] = est_unique['id_estacion_original'].astype(str)
        est_unique['estacion'] = est_unique['estacion'].astype(str)

        # Insertar estaciones en lotes más pequeños
        batch_size = 50
        for i in range(0, len(est_unique), batch_size):
            batch = est_unique.iloc[i:i+batch_size]
            try:
                batch.to_sql('estaciones', engine, if_exists='append', index=False, method='multi')
            except Exception as e:
                log.warning(f"Error en lote {i//batch_size + 1}: {e}")
                # Intentar insertar uno por uno
                for _, row in batch.iterrows():
                    try:
                        row.to_frame().T.to_sql('estaciones', engine, if_exists='append', index=False, method='multi')
                    except Exception as e2:
                        log.warning(f"Error insertando estación {row['id_estacion_original']}: {e2}")

        log.info(f"Estaciones cargadas: {len(est_unique)}")
        return True

    except Exception as e:
        log.error(f"Error cargando estaciones: {e}")
        return False


# =============================================================================
# Funciones de preparación y carga de datos climáticos
# =============================================================================

def prepare_clima_data(df_transformed: pd.DataFrame, engine) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepara los datos climáticos transformados para la carga a la base de datos.
    Retorna una tupla (df_valido, df_invalido) con los datos válidos e inválidos.
    """
    try:
        # Copia del DataFrame
        df = df_transformed.copy()

        # Verificar columnas requeridas
        required_cols = ['id_estacion', 'fecha']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            log.error(f"Faltan columnas requeridas: {missing_cols}")
            return pd.DataFrame(), df

        # Crear IdFecha desde fecha
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        df['IdFecha'] = df['fecha'].dt.strftime('%Y%m%d').astype('Int64')

        # Mapear id_estacion a IdEstacion usando la tabla estaciones
        with engine.connect() as conn:
            estaciones_df = pd.read_sql("SELECT IdEstacion, id_estacion_original FROM estaciones", conn)
            estaciones_map = dict(zip(estaciones_df['id_estacion_original'], estaciones_df['IdEstacion']))

        df['IdEstacion'] = df['id_estacion'].map(estaciones_map)

        # Limpiar valores inválidos
        df_invalid = df[df['IdEstacion'].isna()].copy()
        df = df.dropna(subset=['IdEstacion'])

        # Columnas de clima a mantener
        clima_cols = [
            'precipitacion_pluviometrica',
            'temperatura_minima',
            'temperatura_maxima',
            'temperatura_media',
            'humedad_media',
            'rocio_medio',
            'tension_vapor_medio',
            'radiacion_global',
            'heliofania_efectiva',
            'heliofania_relativa'
        ]

        # Filtrar solo columnas que existen
        existing_clima_cols = [col for col in clima_cols if col in df.columns]

        # DataFrame final con columnas necesarias
        df_clima = df[['IdEstacion', 'IdFecha'] + existing_clima_cols].copy()

        # Renombrar temperatura_media a temperatura_promedio para coincidir con la tabla
        if 'temperatura_media' in df_clima.columns:
            df_clima = df_clima.rename(columns={'temperatura_media': 'temperatura_promedio'})

        # Renombrar tesion_vapor_media a tension_vapor_medio
        if 'tesion_vapor_media' in df_clima.columns:
            df_clima = df_clima.rename(columns={'tesion_vapor_media': 'tension_vapor_medio'})

        log.info(f"Datos preparados: {len(df_clima)} válidos, {len(df_invalid)} inválidos")
        return df_clima, df_invalid

    except Exception as e:
        log.error(f"Error preparando datos climáticos: {e}")
        return pd.DataFrame(), df_transformed


def load_clima_to_db(engine, df_clima: pd.DataFrame) -> bool:
    """
    Carga los datos climáticos preparados a la tabla clima.
    Retorna True si se cargaron exitosamente, False en caso contrario.
    """
    try:
        if df_clima.empty:
            log.warning("No hay datos climáticos para cargar")
            return False

        # Verificar que existan las claves foráneas
        with engine.connect() as conn:
            # Verificar estaciones
            estaciones_validas = df_clima['IdEstacion'].isin(
                pd.read_sql("SELECT IdEstacion FROM estaciones", conn)['IdEstacion']
            )
            if not estaciones_validas.all():
                invalid_est = df_clima[~estaciones_validas]['IdEstacion'].unique()
                log.warning(f"Estaciones inválidas encontradas: {invalid_est}")
                df_clima = df_clima[estaciones_validas]

            # Verificar fechas
            fechas_validas = df_clima['IdFecha'].isin(
                pd.read_sql("SELECT IdFecha FROM calendario", conn)['IdFecha']
            )
            if not fechas_validas.all():
                invalid_fechas = df_clima[~fechas_validas]['IdFecha'].unique()
                log.warning(f"Fechas inválidas encontradas: {invalid_fechas}")
                df_clima = df_clima[fechas_validas]

        if df_clima.empty:
            log.error("No quedan datos válidos después de validación de FK")
            return False

        # Cargar datos usando to_sql con manejo de conflictos
        df_clima.to_sql('clima', engine, if_exists='append', index=False, method='multi')

        log.info(f"Datos climáticos cargados: {len(df_clima)} registros")
        return True

    except SQLAlchemyError as e:
        log.error(f"Error cargando datos climáticos: {e}")
        return False


# =============================================================================
# Pipeline principal (para uso directo)
# =============================================================================

def pipeline(engine, df_transformed: pd.DataFrame) -> bool:
    """
    Ejecuta el pipeline completo de carga: preparación y carga de datos climáticos.
    """
    try:
        log.info("Iniciando pipeline de carga...")

        # Preparar datos
        df_clima, df_invalidos = prepare_clima_data(df_transformed, engine)

        if df_clima.empty:
            log.warning("No hay datos válidos para cargar")
            return False

        # Cargar datos
        success = load_clima_to_db(engine, df_clima)

        if success:
            log.info("Pipeline de carga completado exitosamente")
            print(f"Registros cargados: {len(df_clima)}")
            print(f"Registros inválidos: {len(df_invalidos)}")

        return success

    except Exception as e:
        log.error(f"Error en pipeline de carga: {e}")
        return False


def main(input_path: str) -> bool:
    """
    Función principal para ejecutar el ETL completo: extraer, transformar y cargar datos climáticos.
    """
    try:
        log.info("Iniciando ETL completo de datos climáticos...")

        # Usar el engine de baseDatos.py
        engine = baseDatos.engine

        # Crear tablas si no existen
        if not create_tables(engine):
            log.error("Error creando tablas")
            return False

        # Crear calendario si no existe
        if not create_calendario_table(engine):
            log.error("Error creando calendario")
            return False

        # Cargar estaciones si no existen
        if not load_estaciones_to_db(engine):
            log.error("Error cargando estaciones")
            return False

        # Cargar y transformar datos
        if not os.path.isfile(input_path):
            log.error(f"No existe el archivo de entrada: {input_path}")
            return False

        df_in = pd.read_parquet(input_path) if input_path.lower().endswith(".parquet") else pd.read_csv(input_path)
        df_transformed = transform_clima_data(df_in)

        # Ejecutar pipeline de carga
        success = pipeline(engine, df_transformed)

        if success:
            log.info("ETL completo finalizado exitosamente")

        return success

    except Exception as e:
        log.error(f"Error en ETL completo: {e}")
        return False
