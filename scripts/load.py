#!/usr/bin/env python3
"""
Script para cargar datos en la base de datos SQLite desde los archivos fuente
"""

import sqlite3
import csv
import pandas as pd
import pyarrow.parquet as pq
import logging
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('load.log'),
        logging.StreamHandler()
    ]
)

class DataLoader:
    def __init__(self, db_path=None):
        if db_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(script_dir, '../data/database.db')
            self.data_dir = os.path.join(script_dir, '../data')
        else:
            self.db_path = db_path
            self.data_dir = os.path.dirname(db_path) if os.path.dirname(db_path) else '../data'

    def get_connection(self):
        """Obtiene conexión a la base de datos con foreign keys habilitadas"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def load_dim_fecha(self):
        """Carga datos de calendario.csv a dim_fecha"""
        logging.info("Cargando dimensión fecha...")

        csv_path = os.path.join(self.data_dir, 'calendario.csv')
        if not os.path.exists(csv_path):
            logging.error(f"Archivo no encontrado: {csv_path}")
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Mapear nombres de columnas
                column_mapping = {
                    'fecha': 'fecha',
                    'anio': 'anio',
                    'mes': 'mes',
                    'dia': 'dia',
                    'trimestre': 'trimestre',
                    'semestre': 'semestre',
                    'quincena': 'quincena',
                    'semanaMes': 'semana_mes',
                    'semana': 'semana',
                    'diaSemana': 'dia_semana',
                    'diaNumeroSemana': 'dia_numero_semana',
                    'bisiesto': 'bisiesto'
                }

                data = []
                for row in reader:
                    # Convertir bisiesto a integer (0/1)
                    bisiesto = 1 if row.get('bisiesto', '').lower() == 'true' else 0

                    data.append((
                        row['fecha'],
                        int(row['anio']),
                        int(row['mes']),
                        int(row['dia']),
                        int(row['trimestre']),
                        int(row['semestre']),
                        int(row['quincena']),
                        int(row['semanaMes']),
                        int(row['semana']),
                        row['diaSemana'],
                        int(row['diaNumeroSemana']),
                        bisiesto
                    ))

                # Insertar en lotes
                cursor.executemany("""
                    INSERT OR IGNORE INTO dim_fecha
                    (fecha, anio, mes, dia, trimestre, semestre, quincena,
                     semana_mes, semana, dia_semana, dia_numero_semana, bisiesto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)

                conn.commit()
                logging.info(f"Insertadas {len(data)} filas en dim_fecha")

        except Exception as e:
            logging.error(f"Error cargando dim_fecha: {e}")
            conn.rollback()
        finally:
            conn.close()

    def load_dim_ubicacion(self):
        """Carga ubicaciones únicas desde estaciones y población"""
        logging.info("Cargando dimensión ubicación...")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Obtener ubicaciones de estaciones meteorológicas
            stations_path = os.path.join(self.data_dir, 'estaciones-meteorologicas-inta.csv')
            locations = set()

            if os.path.exists(stations_path):
                with open(stations_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Crear clave única: provincia|departamento|localidad
                        key = (
                            row.get('Provincia', '').strip(),
                            row.get('Localidad', '').strip(),
                            row.get('Localidad', '').strip()  # localidad = Localidad
                        )
                        locations.add(key)

            # Obtener ubicaciones de población
            poblacion_path = os.path.join(self.data_dir, 'poblacion.csv')
            if os.path.exists(poblacion_path):
                with open(poblacion_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        key = (
                            row.get('provincia_nombre', '').strip(),
                            row.get('departamento_nombre', '').strip(),
                            None  # población no tiene localidad específica
                        )
                        locations.add(key)

            # Insertar ubicaciones únicas
            data = []
            for provincia, departamento, localidad in locations:
                data.append((provincia, departamento, localidad, None, None, None, None))

            cursor.executemany("""
                INSERT OR IGNORE INTO dim_ubicacion
                (provincia, departamento, localidad, latitud, longitud, altura, ubicacion_detalle)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, data)

            conn.commit()
            logging.info(f"Insertadas {len(data)} ubicaciones únicas")

        except Exception as e:
            logging.error(f"Error cargando dim_ubicacion: {e}")
            conn.rollback()
        finally:
            conn.close()

    def load_dim_estacion(self):
        """Carga datos de estaciones meteorológicas"""
        logging.info("Cargando dimensión estación...")

        csv_path = os.path.join(self.data_dir, 'estaciones-meteorologicas-inta.csv')
        if not os.path.exists(csv_path):
            logging.error(f"Archivo no encontrado: {csv_path}")
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                data = []
                for row in reader:
                    # Buscar ubicacion_id
                    cursor.execute("""
                        SELECT ubicacion_id FROM dim_ubicacion
                        WHERE provincia = ? AND departamento = ? AND localidad = ?
                    """, (row['Provincia'], row['Localidad'], row['Localidad']))

                    ubicacion_id = cursor.fetchone()
                    ubicacion_id = ubicacion_id[0] if ubicacion_id else None

                    # Convertir fechas
                    desde = row.get('Desde', '')
                    hasta = row.get('Hasta', '')

                    data.append((
                        int(row['Id']),
                        row['Nombre'],
                        row.get('Tipo', ''),
                        ubicacion_id,
                        row.get('Id Interno', ''),
                        desde if desde else None,
                        hasta if hasta else None
                    ))

                cursor.executemany("""
                    INSERT OR IGNORE INTO dim_estacion
                    (id_estacion, nombre, tipo, ubicacion_id, id_interno, desde, hasta)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)

                conn.commit()
                logging.info(f"Insertadas {len(data)} estaciones")

        except Exception as e:
            logging.error(f"Error cargando dim_estacion: {e}")
            conn.rollback()
        finally:
            conn.close()

    def load_dim_poblacion(self):
        """Carga datos de población"""
        logging.info("Cargando dimensión población...")

        csv_path = os.path.join(self.data_dir, 'poblacion.csv')
        if not os.path.exists(csv_path):
            logging.error(f"Archivo no encontrado: {csv_path}")
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                data = []
                for row in reader:
                    # Buscar ubicacion_id
                    cursor.execute("""
                        SELECT ubicacion_id FROM dim_ubicacion
                        WHERE provincia = ? AND departamento = ?
                    """, (row['provincia_nombre'], row['departamento_nombre']))

                    ubicacion_id = cursor.fetchone()
                    ubicacion_id = ubicacion_id[0] if ubicacion_id else None

                    if ubicacion_id:
                        data.append((
                            ubicacion_id,
                            int(row['anio']),
                            float(row['poblacion'])
                        ))

                cursor.executemany("""
                    INSERT OR IGNORE INTO dim_poblacion
                    (ubicacion_id, anio, poblacion)
                    VALUES (?, ?, ?)
                """, data)

                conn.commit()
                logging.info(f"Insertadas {len(data)} filas de población")

        except Exception as e:
            logging.error(f"Error cargando dim_poblacion: {e}")
            conn.rollback()
        finally:
            conn.close()

    def load_fact_clima(self):
        """Carga datos climáticos desde parquet"""
        logging.info("Cargando hechos climáticos...")

        parquet_path = os.path.join(self.data_dir, 'datos_clima_transformados.parquet')
        if not os.path.exists(parquet_path):
            logging.error(f"Archivo no encontrado: {parquet_path}")
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Leer parquet
            table = pq.read_table(parquet_path)
            df = table.to_pandas()

            logging.info(f"Columnas en datos climáticos: {df.columns.tolist()}")
            logging.info(f"Shape: {df.shape}")

            # Procesar en lotes para evitar memoria excesiva
            batch_size = 10000
            total_inserted = 0

            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                data = []

                for _, row in batch.iterrows():
                    # Buscar fecha_id (asumiendo que hay una columna 'fecha')
                    fecha_id = None
                    if 'fecha' in row:
                        # Convertir timestamp de pandas a string de fecha
                        fecha_str = str(row['fecha'].date()) if hasattr(row['fecha'], 'date') else str(row['fecha']).split(' ')[0]
                        cursor.execute("SELECT fecha_id FROM dim_fecha WHERE fecha = ?",
                                      (fecha_str,))
                        result = cursor.fetchone()
                        fecha_id = result[0] if result else None

                    # Buscar estacion_id (asumiendo que hay una columna 'id_estacion')
                    estacion_id = None
                    if 'id_estacion' in row:
                        estacion_val = str(row['id_estacion'])
                        # Buscar por id_interno primero (parece ser el formato NHxxxx)
                        cursor.execute("SELECT estacion_id FROM dim_estacion WHERE id_interno = ?",
                                      (estacion_val,))
                        result = cursor.fetchone()
                        if result:
                            estacion_id = result[0]
                        else:
                            # Si no encuentra por id_interno, intentar por id_estacion numérico
                            try:
                                cursor.execute("SELECT estacion_id FROM dim_estacion WHERE id_estacion = ?",
                                              (int(estacion_val),))
                                result = cursor.fetchone()
                                estacion_id = result[0] if result else None
                            except (ValueError, TypeError):
                                estacion_id = None

                    # Crear tupla con los valores disponibles
                    # Ajustar según las columnas reales del parquet
                    clima_data = (
                        fecha_id,
                        estacion_id,
                        row.get('temperatura_maxima'),  # temperatura_maxima
                        row.get('temperatura_minima'),  # temperatura_minima
                        row.get('temperatura_media'),   # temperatura_media
                        row.get('humedad_media'),       # humedad_relativa -> humedad_media
                        row.get('precipitacion_pluviometrica'),  # precipitacion -> precipitacion_pluviometrica
                        None,  # velocidad_viento no disponible
                        None,  # direccion_viento no disponible
                        None,  # presion_atmosferica no disponible
                        row.get('radiacion_global')     # radiacion_solar -> radiacion_global
                    )
                    data.append(clima_data)

                if data:
                    cursor.executemany("""
                        INSERT OR IGNORE INTO fact_clima
                        (fecha_id, estacion_id, temperatura_max, temperatura_min, temperatura_media,
                         humedad_relativa, precipitacion, velocidad_viento, direccion_viento,
                         presion_atmosferica, radiacion_solar)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, data)

                    total_inserted += len(data)
                    logging.info(f"Procesado lote {i//batch_size + 1}, {total_inserted} filas insertadas")

            conn.commit()
            logging.info(f"Total filas climáticas insertadas: {total_inserted}")

        except Exception as e:
            logging.error(f"Error cargando fact_clima: {e}")
            conn.rollback()
        finally:
            conn.close()

    def load_fact_dengue(self):
        """Carga datos de dengue desde CSV"""
        logging.info("Cargando hechos dengue...")

        csv_path = os.path.join(self.data_dir, '../dengue/A-final/dengue-final.csv')
        if not os.path.exists(csv_path):
            logging.error(f"Archivo no encontrado: {csv_path}")
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            df = pd.read_csv(csv_path)
            logging.info(f"Columnas en datos dengue: {df.columns.tolist()}")
            logging.info(f"Shape: {df.shape}")

            # Procesar en lotes
            batch_size = 10000
            total_inserted = 0

            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                data = []

                for _, row in batch.iterrows():
                    # Buscar ubicacion_id por provincia y departamento
                    # Normalizar nombres para mejor matching
                    provincia = str(row['provincia_nombre']).strip().upper()
                    departamento = str(row['departamento_nombre']).strip().upper()

                    # Mapear nombres comunes
                    if provincia == 'CIUDAD DE BUENOS AIRES':
                        provincia = 'CIUDAD AUTONOMA DE BUENOS AIRES'
                    elif provincia == 'BUENOS AIRES':
                        provincia = 'BUENOS AIRES'

                    ubicacion_id = None
                    cursor.execute("""
                        SELECT ubicacion_id FROM dim_ubicacion
                        WHERE UPPER(provincia) = ? AND UPPER(departamento) = ?
                    """, (provincia, departamento))
                    result = cursor.fetchone()
                    ubicacion_id = result[0] if result else None

                    # Crear fecha_id desde ano y semanas_epidemiologicas
                    fecha_id = None
                    cursor.execute("""
                        SELECT fecha_id FROM dim_fecha
                        WHERE anio = ? AND semana = ?
                        ORDER BY fecha LIMIT 1
                    """, (int(row['ano']), int(row['semanas_epidemiologicas'])))
                    result = cursor.fetchone()
                    fecha_id = result[0] if result else None

                    if ubicacion_id and fecha_id:
                        data.append((
                            fecha_id,
                            ubicacion_id,
                            int(row.get('cantidad_casos', 0)),
                            0,  # casos_sospechosos no disponible
                            0,  # hospitalizaciones no disponible
                            0   # muertes no disponible
                        ))

                if data:
                    cursor.executemany("""
                        INSERT OR IGNORE INTO fact_dengue
                        (fecha_id, ubicacion_id, casos_confirmados, casos_sospechosos,
                         hospitalizaciones, muertes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, data)

                    total_inserted += len(data)
                    logging.info(f"Procesado lote {i//batch_size + 1}, {total_inserted} filas insertadas")

            conn.commit()
            logging.info(f"Total filas dengue insertadas: {total_inserted}")

        except Exception as e:
            logging.error(f"Error cargando fact_dengue: {e}")
            conn.rollback()
        finally:
            conn.close()

    def run_all_loads(self):
        """Ejecuta todas las cargas de datos"""
        logging.info("Iniciando carga completa de datos...")

        start_time = datetime.now()

        try:
            self.load_dim_fecha()
            self.load_dim_ubicacion()
            self.load_dim_estacion()
            self.load_dim_poblacion()
            self.load_fact_clima()
            self.load_fact_dengue()

            end_time = datetime.now()
            duration = end_time - start_time
            logging.info(f"Carga completa finalizada en {duration}")

        except Exception as e:
            logging.error(f"Error en carga completa: {e}")

def main():
    loader = DataLoader()

    print("Iniciando carga de datos...")
    print("Ver logs en scripts/load.log")

    loader.run_all_loads()

    print("Carga finalizada. Verifica los logs para detalles.")

if __name__ == "__main__":
    main()