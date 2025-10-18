#!/usr/bin/env python3
"""
Script para crear la base de datos SQLite con la estructura definida en database_schema.txt
Adaptado para SQLite desde PostgreSQL
"""

import sqlite3
import os

def create_database(db_path='../data/database.db'):
    """
    Crea la base de datos SQLite con todas las tablas definidas en el esquema
    """

    # SQL adaptado para SQLite
    sqlite_schema = """
-- Estructura de Base de Datos para Datos de Dengue
-- Unificando datos de calendario, clima, estaciones meteorológicas y población

-- Tabla de Dimensiones: Fecha (desde calendario.csv)
CREATE TABLE IF NOT EXISTS dim_fecha (
    fecha_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL UNIQUE,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    quincena INTEGER NOT NULL,
    semana_mes INTEGER NOT NULL,
    semana INTEGER NOT NULL,
    dia_semana TEXT NOT NULL,
    dia_numero_semana INTEGER NOT NULL,
    bisiesto INTEGER NOT NULL
);

-- Tabla de Dimensiones: Ubicación (desde estaciones-meteorologicas-inta.csv y poblacion.csv)
CREATE TABLE IF NOT EXISTS dim_ubicacion (
    ubicacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    provincia TEXT NOT NULL,
    departamento TEXT NOT NULL,
    localidad TEXT,
    latitud REAL,
    longitud REAL,
    altura REAL,
    ubicacion_detalle TEXT
);

-- Tabla de Dimensiones: Estación Meteorológica (desde estaciones-meteorologicas-inta.csv)
CREATE TABLE IF NOT EXISTS dim_estacion (
    estacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estacion INTEGER NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    tipo TEXT,
    ubicacion_id INTEGER,
    id_interno TEXT,
    desde TEXT,
    hasta TEXT,
    FOREIGN KEY (ubicacion_id) REFERENCES dim_ubicacion(ubicacion_id)
);

-- Tabla de Dimensiones: Población (desde poblacion.csv)
CREATE TABLE IF NOT EXISTS dim_poblacion (
    poblacion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ubicacion_id INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    poblacion REAL NOT NULL,
    FOREIGN KEY (ubicacion_id) REFERENCES dim_ubicacion(ubicacion_id)
);

-- Tabla de Hechos: Datos Climáticos (desde datos_clima_transformados.parquet)
CREATE TABLE IF NOT EXISTS fact_clima (
    clima_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_id INTEGER NOT NULL,
    estacion_id INTEGER NOT NULL,
    temperatura_max REAL,
    temperatura_min REAL,
    temperatura_media REAL,
    humedad_relativa REAL,
    precipitacion REAL,
    velocidad_viento REAL,
    direccion_viento REAL,
    presion_atmosferica REAL,
    radiacion_solar REAL,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fecha_id) REFERENCES dim_fecha(fecha_id),
    FOREIGN KEY (estacion_id) REFERENCES dim_estacion(estacion_id)
);

-- Tabla de Hechos: Casos de Dengue (si hay datos de dengue, asumiendo estructura)
CREATE TABLE IF NOT EXISTS fact_dengue (
    dengue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_id INTEGER NOT NULL,
    ubicacion_id INTEGER NOT NULL,
    casos_confirmados INTEGER DEFAULT 0,
    casos_sospechosos INTEGER DEFAULT 0,
    hospitalizaciones INTEGER DEFAULT 0,
    muertes INTEGER DEFAULT 0,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fecha_id) REFERENCES dim_fecha(fecha_id),
    FOREIGN KEY (ubicacion_id) REFERENCES dim_ubicacion(ubicacion_id)
);

-- Índices para optimización de consultas
CREATE INDEX IF NOT EXISTS idx_dim_fecha_fecha ON dim_fecha(fecha);
CREATE INDEX IF NOT EXISTS idx_dim_fecha_anio_mes ON dim_fecha(anio, mes);
CREATE INDEX IF NOT EXISTS idx_dim_ubicacion_provincia ON dim_ubicacion(provincia);
CREATE INDEX IF NOT EXISTS idx_dim_ubicacion_departamento ON dim_ubicacion(departamento);
CREATE INDEX IF NOT EXISTS idx_dim_estacion_ubicacion ON dim_estacion(ubicacion_id);
CREATE INDEX IF NOT EXISTS idx_dim_poblacion_ubicacion_anio ON dim_poblacion(ubicacion_id, anio);
CREATE INDEX IF NOT EXISTS idx_fact_clima_fecha ON fact_clima(fecha_id);
CREATE INDEX IF NOT EXISTS idx_fact_clima_estacion ON fact_clima(estacion_id);
CREATE INDEX IF NOT EXISTS idx_fact_clima_fecha_estacion ON fact_clima(fecha_id, estacion_id);
"""

    conn = None
    try:
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Conectar a la base de datos (se crea si no existe)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Habilitar foreign keys en SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Ejecutar el esquema
        cursor.executescript(sqlite_schema)

        # Confirmar cambios
        conn.commit()

        print(f"Base de datos creada exitosamente en: {db_path}")
        print("Tablas creadas:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")

        # Verificar índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = cursor.fetchall()
        print("Índices creados:")
        for index in indexes:
            print(f"  - {index[0]}")

    except sqlite3.Error as e:
        print(f"Error al crear la base de datos: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Crear la base de datos en el directorio data/
    db_path = '../data/database.db'
    create_database(db_path)

    print("\nPara verificar la estructura, puedes usar:")
    print(f"sqlite3 {db_path} '.schema'")
    print(f"sqlite3 {db_path} '.tables'")