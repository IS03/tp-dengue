import pandas as pd
from sqlalchemy import create_engine, text, Integer, String, Float, Date, Boolean
import numpy as np

# 1) Conectar/crear archivo SQLite
engine = create_engine("sqlite:///database.db", future=True)

# 2) Esquema (dimensiones + hechos) — SQLite
ddl = """
PRAGMA foreign_keys = ON;

-- Dimensiones

-- Calendario (surrogate key IdFecha)
CREATE TABLE IF NOT EXISTS calendario (
    IdFecha          INTEGER PRIMARY KEY,
    fecha            DATE NOT NULL UNIQUE,
    dia              INTEGER,
    mes              INTEGER,
    anio             INTEGER,
    semana           INTEGER,
    trimestre        INTEGER,
    semestre         INTEGER,
    bisiesto         INTEGER,
    quincena         INTEGER
);

-- Provincias
CREATE TABLE IF NOT EXISTS provincias (
    IdProvincia        INTEGER PRIMARY KEY AUTOINCREMENT,
    provincia          TEXT NOT NULL UNIQUE,
    latitud            REAL,
    longitud           REAL,
    altitud            REAL,
    cantidadHabitantes INTEGER
);

-- Localidades (departamentos/municipios)
CREATE TABLE IF NOT EXISTS localidades (
    IdLocalidad   INTEGER PRIMARY KEY AUTOINCREMENT,
    IdProvincia   INTEGER NOT NULL,
    localidad     TEXT NOT NULL,
    latitud       REAL,
    longitud      REAL,
    altitud       REAL,
    habitantes    INTEGER,
    FOREIGN KEY (IdProvincia) REFERENCES provincias(IdProvincia) ON DELETE RESTRICT,
    UNIQUE(IdProvincia, localidad)
);

-- Estaciones Meteorológicas
CREATE TABLE IF NOT EXISTS estaciones (
    IdEstacion   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estacion_original TEXT NOT NULL UNIQUE,  -- id_estacion del parquet
    estacion     TEXT,
    IdLocalidad  INTEGER,
    latitud      REAL,
    longitud     REAL,
    altitud      REAL,
    FOREIGN KEY (IdLocalidad) REFERENCES localidades(IdLocalidad) ON DELETE RESTRICT
);

-- Grupo de Edad
CREATE TABLE IF NOT EXISTS grupoEdad (
    IdGrupo   INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo     TEXT NOT NULL UNIQUE
);

-- --------------- Hechos ---------------

-- Clima (wide): una fila por estación y fecha
CREATE TABLE IF NOT EXISTS clima (
    IdEstacion                    INTEGER NOT NULL,
    IdFecha                       INTEGER NOT NULL,

    precipitacion_pluviometrica   REAL,
    temperatura_minima            REAL,
    temperatura_maxima            REAL,
    temperatura_promedio          REAL,
    humedad_media                 REAL,
    rocio_medio                   REAL,
    tension_vapor_medio           REAL,
    radiacion_global              REAL,
    heliofania_efectiva           REAL,
    heliofania_relativa           REAL,

    -- Columnas adicionales del parquet completo
    temperatura_abrigo_150cm      REAL,
    temperatura_abrigo_150cm_maxima REAL,
    temperatura_abrigo_150cm_minima REAL,
    temperatura_intemperie_5cm_minima REAL,
    temperatura_intemperie_50cm_minima REAL,
    temperatura_suelo_5cm_media   REAL,
    temperatura_suelo_10cm_media  REAL,
    temperatura_inte_5cm          REAL,
    temperatura_intemperie_150cm_minima REAL,
    humedad_suelo                 REAL,
    precipitacion_cronologica     REAL,
    precipitacion_maxima_30minutos REAL,
    heliofania_efectiva_full      REAL,
    heliofania_relativa_full      REAL,
    tesion_vapor_media_full       REAL,
    humedad_media_full            REAL,
    humedad_media_8_14_20         REAL,
    rocio_medio_full              REAL,
    duracion_follaje_mojado       REAL,
    velocidad_viento_200cm_media  REAL,
    direccion_viento_200cm        TEXT,
    velocidad_viento_1000cm_media REAL,
    direccion_viento_1000cm       TEXT,
    velocidad_viento_maxima       REAL,
    presion_media                 REAL,
    radiacion_global_full         REAL,
    horas_frio                    REAL,
    unidades_frio                 REAL,
    granizo                       REAL,
    nieve                         REAL,
    radiacion_neta                REAL,
    evaporacion_tanque            REAL,
    evapotranspiracion_potencial  REAL,
    profundidad_napa              REAL,
    unidad_frio                   REAL,

    PRIMARY KEY (IdEstacion, IdFecha),
    FOREIGN KEY (IdEstacion) REFERENCES estaciones(IdEstacion) ON DELETE CASCADE,
    FOREIGN KEY (IdFecha)    REFERENCES calendario(IdFecha)    ON DELETE CASCADE
);

-- Contagios (por localidad, semana epidemiológica y grupo de edad)
CREATE TABLE IF NOT EXISTS contagios (
    IdLocalidad           INTEGER NOT NULL,
    anio                  INTEGER NOT NULL,
    semana_epidemiologica INTEGER NOT NULL,
    IdGrupo               INTEGER NOT NULL,
    casos                 INTEGER NOT NULL DEFAULT 0,
    poblacion             INTEGER,

    PRIMARY KEY (IdLocalidad, anio, semana_epidemiologica, IdGrupo),
    FOREIGN KEY (IdLocalidad) REFERENCES localidades(IdLocalidad) ON DELETE RESTRICT,
    FOREIGN KEY (IdGrupo)     REFERENCES grupoEdad(IdGrupo)       ON DELETE RESTRICT
);

-- --------------- Índices ---------------
CREATE INDEX IF NOT EXISTS idx_calendario_fecha         ON calendario(fecha);
CREATE INDEX IF NOT EXISTS idx_localidades_prov         ON localidades(IdProvincia);
CREATE INDEX IF NOT EXISTS idx_estaciones_loc           ON estaciones(IdLocalidad);
CREATE INDEX IF NOT EXISTS idx_clima_idfecha            ON clima(IdFecha);
CREATE INDEX IF NOT EXISTS idx_contagios_loc_sem        ON contagios(IdLocalidad, anio, semana_epidemiologica);
"""

# 3) Ejecutar DDL
print("Creando esquema de base de datos...")
with engine.begin() as conn:
    for stmt in ddl.strip().split(";"):
        s = stmt.strip()
        if s:
            conn.execute(text(s))
print("Esquema creado exitosamente.")