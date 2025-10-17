import pandas as pd
from sqlalchemy import create_engine, text, Integer, String, Float, Date, Boolean
import numpy as np

# 1) Conectar/crear archivo SQLite
engine = create_engine("sqlite:///dengue_clima.db", future=True)

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

# 4) Cargar datos

# Cargar calendario
print("Cargando calendario...")
df_cal = pd.read_csv("data/calendario.csv")
df_cal['fecha'] = pd.to_datetime(df_cal['fecha']).dt.date
df_cal['bisiesto'] = df_cal['bisiesto'].astype(int)
df_cal.rename(columns={'fecha': 'fecha', 'anio': 'anio', 'mes': 'mes', 'dia': 'dia',
                       'semana': 'semana', 'trimestre': 'trimestre', 'semestre': 'semestre',
                       'bisiesto': 'bisiesto', 'quincena': 'quincena'}, inplace=True)
df_cal['IdFecha'] = pd.to_datetime(df_cal['fecha']).dt.strftime('%Y%m%d').astype(int)
# Cargar calendario solo si está vacío
with engine.begin() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM calendario"))
    if result.fetchone()[0] == 0:
        df_cal[['IdFecha', 'fecha', 'dia', 'mes', 'anio', 'semana', 'trimestre', 'semestre', 'bisiesto', 'quincena']].to_sql(
            "calendario", engine, if_exists="append", index=False, chunksize=1000
        )
        print(f"Calendario cargado: {len(df_cal)} filas.")
    else:
        print("Calendario ya cargado.")
print(f"Calendario cargado: {len(df_cal)} filas.")

# Cargar estaciones y localidades/provincias
print("Cargando estaciones meteorológicas...")
with engine.begin() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM estaciones"))
    if result.fetchone()[0] == 0:
        df_est = pd.read_csv("data/estaciones-meteorologicas-inta.csv")
        df_est = df_est[df_est['Provincia'] != 'Sin asignar']  # Filtrar inválidas

        # Insertar provincias únicas
        provincias_unicas = df_est[['Provincia']].drop_duplicates().reset_index(drop=True)
        provincias_unicas['IdProvincia'] = range(1, len(provincias_unicas) + 1)
        provincias_unicas.rename(columns={'Provincia': 'provincia'}, inplace=True)
        provincias_unicas.to_sql("provincias", engine, if_exists="append", index=False, method="multi")

        # Mapear IdProvincia
        prov_map = dict(zip(provincias_unicas['provincia'], provincias_unicas['IdProvincia']))
        df_est['IdProvincia'] = df_est['Provincia'].map(prov_map)

        # Insertar localidades (usando Localidad como localidad)
        localidades_unicas = df_est[['IdProvincia', 'Localidad']].drop_duplicates().reset_index(drop=True)
        localidades_unicas['IdLocalidad'] = range(1, len(localidades_unicas) + 1)
        localidades_unicas.rename(columns={'Localidad': 'localidad'}, inplace=True)
        localidades_unicas.to_sql("localidades", engine, if_exists="append", index=False, method="multi")

        # Mapear IdLocalidad
        loc_map = {(row['IdProvincia'], row['localidad']): row['IdLocalidad'] for _, row in localidades_unicas.iterrows()}
        df_est['IdLocalidad'] = df_est.apply(lambda row: loc_map.get((row['IdProvincia'], row['Localidad'])), axis=1)

        # Insertar estaciones
        df_est.rename(columns={'Id Interno': 'id_estacion_original', 'Nombre': 'estacion', 'Latitud': 'latitud',
                               'Longitud': 'longitud', 'Altura': 'altitud'}, inplace=True)
        df_est[['id_estacion_original', 'estacion', 'IdLocalidad', 'latitud', 'longitud', 'altitud']].to_sql(
            "estaciones", engine, if_exists="append", index=False, method="multi"
        )
        print(f"Estaciones cargadas: {len(df_est)} filas.")
    else:
        print("Estaciones ya cargadas.")
        # Cargar mapas existentes
        df_est = pd.read_csv("data/estaciones-meteorologicas-inta.csv")
        df_est = df_est[df_est['Provincia'] != 'Sin asignar']
        # Cargar prov_map y loc_map desde DB
        df_prov = pd.read_sql("SELECT * FROM provincias", engine)
        prov_map = dict(zip(df_prov['provincia'], df_prov['IdProvincia']))
        df_loc = pd.read_sql("SELECT * FROM localidades", engine)
        loc_map = {(row['IdProvincia'], row['localidad']): row['IdLocalidad'] for _, row in df_loc.iterrows()}

# Cargar grupos de edad
print("Cargando grupos de edad...")
with engine.begin() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM grupoEdad"))
    if result.fetchone()[0] == 0:
        df_dengue = pd.read_csv("dengue/A-final/dengue-final.csv")
        grupos_unicos = df_dengue[['grupo_edad_desc']].drop_duplicates().reset_index(drop=True)
        grupos_unicos['IdGrupo'] = range(1, len(grupos_unicos) + 1)
        grupos_unicos.rename(columns={'grupo_edad_desc': 'grupo'}, inplace=True)
        grupos_unicos.to_sql("grupoEdad", engine, if_exists="append", index=False, method="multi")
        print(f"Grupos de edad cargados: {len(grupos_unicos)} filas.")
    else:
        print("Grupos de edad ya cargados.")
        df_dengue = pd.read_csv("dengue/A-final/dengue-final.csv")
        # Cargar grupo_map desde DB
        df_grupo = pd.read_sql("SELECT * FROM grupoEdad", engine)
        grupo_map = dict(zip(df_grupo['grupo'], df_grupo['IdGrupo']))

# Cargar localidades de dengue (departamentos)
print("Cargando localidades de dengue...")
with engine.begin() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM localidades"))
    if result.fetchone()[0] <= len(df_est):  # Si solo hay las de estaciones, agregar las de dengue
        # Obtener provincias de dengue
        prov_dengue = df_dengue[['provincia_nombre']].drop_duplicates().reset_index(drop=True)
        prov_dengue['provincia'] = prov_dengue['provincia_nombre'].str.lower().str.strip()
        prov_dengue['IdProvincia'] = prov_dengue['provincia'].map(prov_map)

        # Para localidades no mapeadas, agregar nuevas provincias
        missing_prov = prov_dengue[prov_dengue['IdProvincia'].isna()]
        if not missing_prov.empty:
            max_id_prov = len(prov_map) + 1
            for _, row in missing_prov.iterrows():
                prov_map[row['provincia']] = max_id_prov
                pd.DataFrame({'IdProvincia': [max_id_prov], 'provincia': [row['provincia']]}).to_sql(
                    "provincias", engine, if_exists="append", index=False, method="multi"
                )
                max_id_prov += 1
            prov_dengue['IdProvincia'] = prov_dengue['provincia'].map(prov_map)

        # Localidades de dengue
        loc_dengue = df_dengue[['provincia_nombre', 'departamento_nombre']].drop_duplicates().reset_index(drop=True)
        loc_dengue['provincia'] = loc_dengue['provincia_nombre'].str.lower().str.strip()
        loc_dengue['localidad'] = loc_dengue['departamento_nombre'].str.lower().str.strip()
        loc_dengue['IdProvincia'] = loc_dengue['provincia'].map(prov_map)

        # Agregar localidades faltantes
        existing_loc = set(loc_map.keys())
        new_loc = loc_dengue[~loc_dengue.apply(lambda row: (row['IdProvincia'], row['localidad']) in existing_loc, axis=1)]
        if not new_loc.empty:
            max_id_loc = len(loc_map) + 1
            new_loc_list = []
            for _, row in new_loc.iterrows():
                loc_map[(row['IdProvincia'], row['localidad'])] = max_id_loc
                new_loc_list.append({'IdProvincia': row['IdProvincia'], 'localidad': row['localidad'], 'IdLocalidad': max_id_loc})
                max_id_loc += 1
            pd.DataFrame(new_loc_list).to_sql("localidades", engine, if_exists="append", index=False, method="multi")
        print("Localidades de dengue agregadas.")
    else:
        print("Localidades ya cargadas.")

# Cargar contagios
print("Cargando contagios...")
with engine.begin() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM contagios"))
    if result.fetchone()[0] == 0:
        df_dengue['provincia'] = df_dengue['provincia_nombre'].str.lower().str.strip()
        df_dengue['localidad'] = df_dengue['departamento_nombre'].str.lower().str.strip()
        df_dengue['IdProvincia'] = df_dengue['provincia'].map(prov_map)
        df_dengue['IdLocalidad'] = df_dengue.apply(lambda row: loc_map.get((row['IdProvincia'], row['localidad'])), axis=1)

        # Mapear grupos
        df_grupo = pd.read_sql("SELECT * FROM grupoEdad", engine)
        grupo_map = dict(zip(df_grupo['grupo'], df_grupo['IdGrupo']))
        df_dengue['IdGrupo'] = df_dengue['grupo_edad_desc'].map(grupo_map)

        df_dengue['casos'] = df_dengue['cantidad_casos'].fillna(0).astype(int)
        df_dengue['semana_epidemiologica'] = df_dengue['semanas_epidemiologicas'].fillna(0).astype(int)

        # Agrupar por las claves únicas y sumar casos
        df_dengue_agg = df_dengue.groupby(['IdLocalidad', 'ano', 'semana_epidemiologica', 'IdGrupo']).agg({
            'casos': 'sum',
            'poblacion': 'first'  # Tomar el primer valor de población
        }).reset_index()

        df_dengue_agg[['IdLocalidad', 'ano', 'semana_epidemiologica', 'IdGrupo', 'casos', 'poblacion']].rename(columns={'ano': 'anio'}).to_sql(
            "contagios", engine, if_exists="append", index=False, chunksize=1000
        )
        print(f"Contagios cargados: {len(df_dengue)} filas.")
    else:
        print("Contagios ya cargados.")

# Cargar clima transformado
print("Cargando clima transformado...")
with engine.begin() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM clima"))
    if result.fetchone()[0] == 0:
        df_clima_trans = pd.read_parquet("data/datos_clima_transformados.parquet")
        df_clima_trans['fecha'] = pd.to_datetime(df_clima_trans['fecha']).dt.date
        df_clima_trans['IdFecha'] = pd.to_datetime(df_clima_trans['fecha']).dt.strftime('%Y%m%d').astype(int)

        # Mapear estaciones
        df_est_db = pd.read_sql("SELECT * FROM estaciones", engine)
        est_map = dict(zip(df_est_db['id_estacion_original'], df_est_db['IdEstacion']))
        df_clima_trans['IdEstacion'] = df_clima_trans['id_estacion'].map(est_map)

        # Filtrar filas con IdEstacion válido
        df_clima_trans = df_clima_trans.dropna(subset=['IdEstacion'])
        df_clima_trans['IdEstacion'] = df_clima_trans['IdEstacion'].astype(int)

        df_clima_trans.rename(columns={
            'precipitacion_pluviometrica': 'precipitacion_pluviometrica',
            'temperatura_minima': 'temperatura_minima',
            'temperatura_maxima': 'temperatura_maxima',
            'temperatura_media': 'temperatura_promedio',
            'humedad_media': 'humedad_media',
            'rocio_medio': 'rocio_medio',
            'tesion_vapor_media': 'tension_vapor_medio',
            'radiacion_global': 'radiacion_global',
            'heliofania_efectiva': 'heliofania_efectiva',
            'heliofania_relativa': 'heliofania_relativa'
        }, inplace=True)

        df_clima_trans[['IdEstacion', 'IdFecha', 'precipitacion_pluviometrica', 'temperatura_minima',
                        'temperatura_maxima', 'temperatura_promedio', 'humedad_media', 'rocio_medio',
                        'tension_vapor_medio', 'radiacion_global', 'heliofania_efectiva', 'heliofania_relativa']].to_sql(
            "clima", engine, if_exists="append", index=False, method="multi"
        )
        print(f"Clima transformado cargado: {len(df_clima_trans)} filas.")
    else:
        print("Clima ya cargado.")

# Cargar clima completo
print("Cargando clima completo...")
with engine.begin() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM clima"))
    if result.fetchone()[0] <= len(df_clima_trans):  # Si solo hay el transformado, agregar el completo
        df_clima_full = pd.read_parquet("data/datos-todas-estaciones.parquet")
        df_clima_full['Fecha'] = pd.to_datetime(df_clima_full['Fecha']).dt.date
        df_clima_full['IdFecha'] = pd.to_datetime(df_clima_full['Fecha']).dt.strftime('%Y%m%d').astype(int)
        df_clima_full['IdEstacion'] = df_clima_full['id_estacion'].map(est_map)

        # Filtrar válidos
        df_clima_full = df_clima_full.dropna(subset=['IdEstacion'])
        df_clima_full['IdEstacion'] = df_clima_full['IdEstacion'].astype(int)

        # Renombrar columnas para coincidir con el esquema
        column_mapping = {
            'Precipitacion_Pluviometrica': 'precipitacion_pluviometrica',
            'Temperatura_Abrigo_150cm': 'temperatura_abrigo_150cm',
            'Temperatura_Abrigo_150cm_Maxima': 'temperatura_abrigo_150cm_maxima',
            'Temperatura_Abrigo_150cm_Minima': 'temperatura_abrigo_150cm_minima',
            'Temperatura_Intemperie_5cm_Minima': 'temperatura_intemperie_5cm_minima',
            'Temperatura_Intemperie_50cm_Minima': 'temperatura_intemperie_50cm_minima',
            'Temperatura_Suelo_5cm_Media': 'temperatura_suelo_5cm_media',
            'Temperatura_Suelo_10cm_Media': 'temperatura_suelo_10cm_media',
            'Temperatura_Inte_5cm': 'temperatura_inte_5cm',
            'Temperatura_Intemperie_150cm_Minima': 'temperatura_intemperie_150cm_minima',
            'Humedad_Suelo': 'humedad_suelo',
            'Precipitacion_Cronologica': 'precipitacion_cronologica',
            'Precipitacion_Maxima_30minutos': 'precipitacion_maxima_30minutos',
            'Heliofania_Efectiva': 'heliofania_efectiva_full',
            'Heliofania_Relativa': 'heliofania_relativa_full',
            'Tesion_Vapor_Media': 'tesion_vapor_media_full',
            'Humedad_Media': 'humedad_media_full',
            'Humedad_Media_8_14_20': 'humedad_media_8_14_20',
            'Rocio_Medio': 'rocio_medio_full',
            'Duracion_Follaje_Mojado': 'duracion_follaje_mojado',
            'Velocidad_Viento_200cm_Media': 'velocidad_viento_200cm_media',
            'Direccion_Viento_200cm': 'direccion_viento_200cm',
            'Velocidad_Viento_1000cm_Media': 'velocidad_viento_1000cm_media',
            'Direccion_Viento_1000cm': 'direccion_viento_1000cm',
            'Velocidad_Viento_Maxima': 'velocidad_viento_maxima',
            'Presion_Media': 'presion_media',
            'Radiacion_Global': 'radiacion_global_full',
            'Horas_Frio': 'horas_frio',
            'Unidades_Frio': 'unidades_frio',
            'Granizo': 'granizo',
            'Nieve': 'nieve',
            'Radiacion_Neta': 'radiacion_neta',
            'Evaporacion_Tanque': 'evaporacion_tanque',
            'Evapotranspiracion_Potencial': 'evapotranspiracion_potencial',
            'Profundidad_Napa': 'profundidad_napa',
            'Unidad_Frio': 'unidad_frio'
        }

        df_clima_full.rename(columns=column_mapping, inplace=True)

        # Para clima completo, actualizar filas existentes o insertar nuevas
        # Usar on_conflict_do_update para SQLite (SQLAlchemy 2.0)
        from sqlalchemy.dialects.sqlite import insert

        with engine.begin() as conn:
            for _, row in df_clima_full.iterrows():
                stmt = insert(clima).values(row.to_dict()).on_conflict_do_update(
                    index_elements=['IdEstacion', 'IdFecha'],
                    set_=row.to_dict()
                )
                conn.execute(stmt)

        print(f"Clima completo cargado/actualizado: {len(df_clima_full)} filas.")
    else:
        print("Clima completo ya cargado.")

print("Base de datos creada y poblada exitosamente.")