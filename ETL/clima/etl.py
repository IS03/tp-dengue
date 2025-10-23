import pandas as pd
import sys
from a_extract import proceso
from b_transform import process_all_station_files
from c_load import create_tables, create_calendario_table, load_estaciones_to_db, pipeline
from pathlib import Path

# Agrego la carpeta raíz del proyecto (tp-dengue)
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Ahora puedo importar sin puntos
from scripts import create_database as baseDatos

# Obtener IDs de estaciones
ruta = "data/estaciones-meteorologicas-inta.csv"
df_estaciones = pd.read_csv(ruta)
df_estaciones.columns = [col.lower().replace(' ', '_').strip() for col in df_estaciones.columns]
ids_estaciones = list(df_estaciones.id_interno.unique())

# Extraer datos
proceso(ids_estaciones)
ruta_estaciones = 'data/datos-estaciones'

# Transformar datos
df_combined = process_all_station_files(ruta_estaciones)

# Cargar datos
engine = baseDatos.engine
create_tables(engine)
create_calendario_table(engine)
load_estaciones_to_db(engine)
pipeline(engine, df_combined)