import pandas as pd
from sqlalchemy import create_engine, text

# 1) conectar/crear archivo SQLite
engine = create_engine("sqlite:///database.db", future=True)

# 2) esquema (dimensiones + hechos) — SQLite
ddl = """
PRAGMA foreign_keys = ON;

-- --------------- Dimensiones ---------------

-- Calendario (surrogate key IdFecha; fecha ISO única)
CREATE TABLE IF NOT EXISTS calendario (
    IdFecha          INTEGER PRIMARY KEY,         -- p.ej. 20250103
    fecha            DATE NOT NULL UNIQUE,        -- 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'
    dia              INTEGER,
    mes              INTEGER,
    anio             INTEGER,
    semana           INTEGER,
    trimestre        INTEGER,
    semestre         INTEGER,
    bisiesto         INTEGER,                     -- 0/1 en SQLite
    quincena         INTEGER
);

-- Provincias
CREATE TABLE IF NOT EXISTS provincias (
    IdProvincia        INTEGER PRIMARY KEY,
    provincia          TEXT NOT NULL,
    latitud            REAL,
    longitud           REAL,
    altitud            REAL,
    cantidadHabitantes INTEGER
);

-- Localidades
CREATE TABLE IF NOT EXISTS localidades (
    IdLocalidad   INTEGER PRIMARY KEY,
    IdProvincia   INTEGER NOT NULL,
    localidad     TEXT NOT NULL,
    latitud       REAL,
    longitud      REAL,
    altitud       REAL,
    habitantes    INTEGER,
    FOREIGN KEY (IdProvincia) REFERENCES provincias(IdProvincia) ON DELETE RESTRICT
);

-- Estaciones
CREATE TABLE IF NOT EXISTS estaciones (
    IdEstacion   INTEGER PRIMARY KEY,
    estacion     TEXT,
    IdLocalidad  INTEGER NOT NULL,
    latitud      REAL,
    longitud     REAL,
    altitud      REAL,
    FOREIGN KEY (IdLocalidad) REFERENCES localidades(IdLocalidad) ON DELETE RESTRICT
);

-- Grupo de Edad
CREATE TABLE IF NOT EXISTS grupoEdad (
    IdGrupo   INTEGER PRIMARY KEY,
    grupo     TEXT NOT NULL
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

    PRIMARY KEY (IdEstacion, IdFecha),
    FOREIGN KEY (IdEstacion) REFERENCES estaciones(IdEstacion) ON DELETE CASCADE,
    FOREIGN KEY (IdFecha)    REFERENCES calendario(IdFecha)    ON DELETE CASCADE
);

-- Contagios (por localidad, semana y grupo)
CREATE TABLE IF NOT EXISTS contagios (
    IdLocalidad           INTEGER NOT NULL,
    anio                  INTEGER NOT NULL,
    semana_epidemiologica INTEGER NOT NULL,
    IdGrupo               INTEGER NOT NULL,
    casos                 INTEGER NOT NULL DEFAULT 0,
    IdPoblacion           INTEGER,  -- opcional

    PRIMARY KEY (IdLocalidad, anio, semana_epidemiologica, IdGrupo),
    FOREIGN KEY (IdLocalidad) REFERENCES localidades(IdLocalidad) ON DELETE RESTRICT,
    FOREIGN KEY (IdGrupo)     REFERENCES grupoEdad(IdGrupo)       ON DELETE RESTRICT
);

-- Población (serie por localidad y año)
CREATE TABLE IF NOT EXISTS poblacion (
    IdPoblacion  INTEGER PRIMARY KEY,
    IdLocalidad  INTEGER NOT NULL,
    anio         INTEGER NOT NULL,
    poblacion    INTEGER NOT NULL,
    UNIQUE (IdLocalidad, anio),
    FOREIGN KEY (IdLocalidad) REFERENCES localidades(IdLocalidad) ON DELETE RESTRICT
);

-- --------------- Índices ---------------
CREATE INDEX IF NOT EXISTS idx_calendario_fecha         ON calendario(fecha);
CREATE INDEX IF NOT EXISTS idx_localidades_prov         ON localidades(IdProvincia);
CREATE INDEX IF NOT EXISTS idx_estaciones_loc           ON estaciones(IdLocalidad);
CREATE INDEX IF NOT EXISTS idx_clima_idfecha            ON clima(IdFecha);
CREATE INDEX IF NOT EXISTS idx_contagios_loc_sem        ON contagios(IdLocalidad, anio, semana_epidemiologica);
"""

# 3) ejecutar DDL
with engine.begin() as conn:
    for stmt in ddl.strip().split(";"):
        s = stmt.strip()
        if s:
            conn.execute(text(s))

# 4) (opcional) cargar ESTACIONES desde CSV (ajustá ruta/columnas reales)
#   columnas esperadas mínimas: IdEstacion, IdLocalidad
#   si además tenés estacion, latitud, longitud, altitud ⇒ se insertan también.
try:
    df_est = pd.read_csv("data/estaciones.csv")
    keep_est = [c for c in ["IdEstacion","IdLocalidad","estacion","latitud","longitud","altitud"] if c in df_est.columns]
    if keep_est:
        df_est[keep_est].to_sql("estaciones", engine, if_exists="append", index=False, method="multi")
        print(f"↳ estaciones insertadas: {len(df_est)}")
except FileNotFoundError:
    print("⚠️  data/estaciones.csv no encontrado (salteando carga de estaciones)")

# 5) (opcional) cargar CLIMA desde Parquet/CSV
#   Debe contener: IdEstacion, fecha (o IdFecha) y las métricas.
#   Si viene con 'fecha', mapeamos a IdFecha = YYYYMMDD (int) para la FK.
try:
    try:
        df_med = pd.read_parquet("data/mediciones.parquet")
    except Exception:
        df_med = pd.read_csv("data/mediciones.csv")
    # asegurar fecha → IdFecha (YYYYMMDD int)
    if "IdFecha" not in df_med.columns and "fecha" in df_med.columns:
        dt = pd.to_datetime(df_med["fecha"], errors="coerce")
        df_med["IdFecha"] = dt.dt.strftime("%Y%m%d").astype("Int64")