import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import glob

# =============================================================================
# Funciones de carga y preparación inicial
# =============================================================================

def load_excel_file(path_archivo):
    """
    Carga un archivo Excel (.xls o .xlsx) con manejo de errores.
    Retorna el DataFrame o None si falla.
    """
    try:
        if path_archivo.endswith('.xlsx'):
            df = pd.read_excel(path_archivo, engine='openpyxl')
        elif path_archivo.endswith('.xls'):
            try:
                df = pd.read_excel(path_archivo, engine='xlrd')
            except Exception as e:
                print(f"Error leyendo {path_archivo} con xlrd: {e}")
                # Intentar con openpyxl como fallback
                try:
                    df = pd.read_excel(path_archivo, engine='openpyxl')
                except Exception as e2:
                    print(f"Error leyendo {path_archivo} con openpyxl: {e2}")
                    return None
        else:
            print(f"Formato de archivo no soportado: {path_archivo}. Solo .xlsx y .xls")
            return None
    except Exception as e:
        print(f"Error general leyendo {path_archivo}: {e}")
        return None
    return df

def prepare_dataframe(df, path_archivo):
    """
    Prepara el DataFrame inicial: agrega id_estacion, normaliza columnas,
    selecciona variables, convierte tipos y elimina duplicados.
    """
    # Extraer id_estacion del nombre del archivo
    id_estacion = os.path.basename(path_archivo).replace('.xls', '').replace('.xlsx', '').strip()
    df['id_estacion'] = id_estacion

    # Normalizar nombres de columnas a minúsculas
    df.columns = [col.lower().strip() for col in df.columns]

    # Seleccionar variables relevantes para la propagación del dengue
    variables_dengue_ranked = [
        "fecha",
        'id_estacion',
        "precipitacion_pluviometrica",
        "temperatura_abrigo_150cm_minima",
        "temperatura_abrigo_150cm_maxima",
        "temperatura_abrigo_150cm",
        "humedad_media_8_14_20",
        "rocio_medio",
        "tesion_vapor_media",
        "radiacion_global",
        "heliofania_efectiva",
        "heliofania_relativa"
    ]
    df = df[variables_dengue_ranked]

    # Convertir columna fecha a datetime
    df.fecha = pd.to_datetime(df.fecha, errors='coerce')

    # Eliminar duplicados
    df = df.drop_duplicates(keep='first')

    # Renombrar columnas para mayor comodidad
    new_cols = {
        'temperatura_abrigo_150cm_minima': 'temperatura_minima',
        'temperatura_abrigo_150cm_maxima': 'temperatura_maxima',
        'temperatura_abrigo_150cm': 'temperatura_media',
        'humedad_media_8_14_20': 'humedad_media'
    }
    df = df.rename(columns=new_cols)

    # Ordenar por fecha
    df = df.sort_values('fecha').reset_index(drop=True)

    return df

# =============================================================================
# Funciones de transformación por columna
# =============================================================================

def transform_precipitacion(df):
    """
    Transforma la columna precipitacion_pluviometrica:
    - Logarítmica seguida de Min-Max
    - Interpolación spline cúbica para nulos
    """
    if "precipitacion_pluviometrica" not in df.columns:
        return df

    # Logarítmica seguida de Min-Max
    col_log = np.log1p(df["precipitacion_pluviometrica"])
    if col_log.max() > col_log.min():
        df["precipitacion_pluviometrica"] = (col_log - col_log.min()) / (col_log.max() - col_log.min())
    else:
        df["precipitacion_pluviometrica"] = col_log

    # Interpolación spline cúbica para valores nulos
    df["precipitacion_pluviometrica"] = df["precipitacion_pluviometrica"].interpolate(method='spline', order=3)

    return df

def transform_temperaturas(df):
    """
    Transforma las columnas de temperatura:
    - Corrige inconsistencias (min > max)
    - Imputa media como promedio de min/max
    - Imputa min/max desde media usando diferencias promedio
    - Interpolación lineal
    """
    temp_cols = ["temperatura_minima", "temperatura_maxima", "temperatura_media"]
    if not all(col in df.columns for col in temp_cols):
        return df

    # Corregir inconsistencias: mínima > máxima
    mask_min_max = df.temperatura_minima > df.temperatura_maxima
    df.loc[mask_min_max, ["temperatura_minima", "temperatura_maxima"]] = (
        df.loc[mask_min_max, ["temperatura_maxima", "temperatura_minima"]].values
    )

    # Imputar temperatura_media como promedio de min y max si faltan
    mask_temp = (
        df.temperatura_media.isna() &
        df.temperatura_minima.notna() &
        df.temperatura_maxima.notna()
    )
    df.loc[mask_temp, "temperatura_media"] = (
        (df.loc[mask_temp, "temperatura_minima"] + df.loc[mask_temp, "temperatura_maxima"]) / 2
    )

    # Imputar mínima y máxima desde media usando diferencias promedio
    with np.errstate(invalid='ignore'):
        promedio_min_media = np.abs((df.temperatura_minima - df.temperatura_media)).mean(skipna=True)
        promedio_max_media = np.abs((df.temperatura_maxima - df.temperatura_media)).mean(skipna=True)

    mask_minima = (df.temperatura_minima.isna() & df.temperatura_media.notna())
    df.loc[mask_minima, 'temperatura_minima'] = (
        df.loc[mask_minima, 'temperatura_media'] - promedio_min_media
    )

    mask_maxima = (df.temperatura_maxima.isna() & df.temperatura_media.notna())
    df.loc[mask_maxima, 'temperatura_maxima'] = (
        df.loc[mask_maxima, 'temperatura_media'] + promedio_max_media
    )

    # Interpolación lineal para valores restantes
    for col in temp_cols:
        df[col] = df[col].interpolate(method='linear')

    return df

def transform_humedad(df):
    """
    Transforma la columna humedad_media con interpolación lineal.
    """
    if "humedad_media" not in df.columns:
        return df

    df["humedad_media"] = df["humedad_media"].interpolate(method='linear')
    return df

def transform_rocio(df):
    """
    Transforma la columna rocio_medio:
    - Imputa usando diferencia promedio con temperatura_media
    - Interpolación lineal
    """
    if "rocio_medio" not in df.columns or "temperatura_media" not in df.columns:
        return df

    # Imputar usando diferencia promedio con temperatura_media
    mask_rocio_temp = (df.rocio_medio.notna() & df.temperatura_media.notna())
    if mask_rocio_temp.sum() > 0:
        diff_rocio_temp = np.abs(df.loc[mask_rocio_temp].temperatura_media - df.loc[mask_rocio_temp].rocio_medio).mean()
        mask_rocio_temp_imputar = (df.rocio_medio.isna() & df.temperatura_media.notna())
        df.loc[mask_rocio_temp_imputar, 'rocio_medio'] = df.loc[mask_rocio_temp_imputar].temperatura_media - diff_rocio_temp

    # Interpolación lineal
    df.rocio_medio = df.rocio_medio.interpolate(method='linear')

    return df

def transform_tension_vapor(df):
    """
    Transforma la columna tesion_vapor_media usando fórmula física.
    """
    if not all(col in df.columns for col in ["tesion_vapor_media", "temperatura_media", "humedad_media"]):
        return df

    def tension_vapor(temp, rh):
        return (rh / 100) * (6.11 * np.exp((17.27 * temp) / (temp + 237.3)))

    mask_tension_vapor = (
        df["tesion_vapor_media"].isna() &
        df["temperatura_media"].notna() &
        df["humedad_media"].notna()
    )
    if mask_tension_vapor.sum() > 0:
        df.loc[mask_tension_vapor, "tesion_vapor_media"] = tension_vapor(
            df.loc[mask_tension_vapor, "temperatura_media"],
            df.loc[mask_tension_vapor, "humedad_media"]
        )

    return df

def transform_radiacion_global(df):
    """
    Transforma la columna radiacion_global:
    - Regresión lineal con heliofania_efectiva
    - Interpolación lineal
    """
    if not all(col in df.columns for col in ["radiacion_global", "heliofania_efectiva"]):
        return df

    # Regresión lineal con heliofania_efectiva
    mask_rad_helio = df.radiacion_global.notna() & df.heliofania_efectiva.notna()
    if mask_rad_helio.sum() > 0:
        X = df.loc[mask_rad_helio, ["heliofania_efectiva"]]
        y = df.loc[mask_rad_helio, "radiacion_global"]
        model = LinearRegression()
        model.fit(X, y)
        mask_null = df.radiacion_global.isna() & df.heliofania_efectiva.notna()
        if mask_null.sum() > 0:
            df.loc[mask_null, "radiacion_global"] = model.predict(df.loc[mask_null, ["heliofania_efectiva"]])

    # Interpolación lineal para valores restantes
    df.radiacion_global = df.radiacion_global.interpolate(method='linear')

    return df

def transform_heliofania(df):
    """
    Transforma las columnas heliofania_efectiva y heliofania_relativa:
    - Regresión cruzada
    - Interpolación lineal
    """
    helio_cols = ["heliofania_efectiva", "heliofania_relativa"]
    if not all(col in df.columns for col in helio_cols):
        return df

    # Regresión cruzada
    # Imputar efectiva desde relativa
    mask_valid = (df["heliofania_efectiva"].notna() & df["heliofania_relativa"].notna())
    mask_null = (df["heliofania_efectiva"].isna() & df["heliofania_relativa"].notna())
    if mask_valid.sum() > 0 and mask_null.sum() > 0:
        X = df.loc[mask_valid, ["heliofania_relativa"]].values
        y = df.loc[mask_valid, "heliofania_efectiva"].values
        model = LinearRegression()
        model.fit(X, y)
        df.loc[mask_null, "heliofania_efectiva"] = model.predict(
            df.loc[mask_null, ["heliofania_relativa"]].values
        )

    # Imputar relativa desde efectiva
    mask_valid = df["heliofania_relativa"].notna() & df["heliofania_efectiva"].notna()
    mask_null = df["heliofania_relativa"].isna() & df["heliofania_efectiva"].notna()
    if mask_valid.sum() > 0 and mask_null.sum() > 0:
        X = df.loc[mask_valid, ["heliofania_efectiva"]].values
        y = df.loc[mask_valid, "heliofania_relativa"].values
        model = LinearRegression()
        model.fit(X, y)
        df.loc[mask_null, "heliofania_relativa"] = model.predict(
            df.loc[mask_null, ["heliofania_efectiva"]].values
        )

    # Interpolación lineal para valores restantes
    for col in helio_cols:
        df[col] = df[col].interpolate(method='linear')

    return df

# =============================================================================
# Función principal de transformación
# =============================================================================

def transform_clima_data(path_archivo):
    """
    Aplica todas las transformaciones del EDA de datos climáticos para una estación específica.
    Cada archivo en 'data/datos-estaciones' representa una estación separada.
    Retorna None si no se puede leer el archivo.
    """
    # Cargar archivo
    df = load_excel_file(path_archivo)
    if df is None:
        return None

    # Preparar DataFrame
    df = prepare_dataframe(df, path_archivo)

    # Aplicar transformaciones por columna
    df = transform_precipitacion(df)
    df = transform_temperaturas(df)
    df = transform_humedad(df)
    df = transform_rocio(df)
    df = transform_tension_vapor(df)
    df = transform_radiacion_global(df)
    df = transform_heliofania(df)

    # Eliminar filas con valores nulos restantes
    df = eliminar_nulos(df)

    return df

def eliminar_nulos(df: pd.DataFrame, columnas: list = None):
    """
    Elimina filas que contienen valores nulos en las columnas especificadas.
    Si no se especifican columnas, elimina filas con nulos en cualquier columna.
    """
    if columnas is None:
        return df.dropna()
    else:
        return df.dropna(subset=columnas)

def process_all_station_files(data_folder):
    """
    Procesa todos los archivos en la carpeta data/datos-estaciones,
    aplica transformaciones a cada uno y agrupa todos los datos en un solo DataFrame.
    """
    # Obtener lista de archivos (parquet o csv)
    files = list(os.path.join(data_folder, archivo) for archivo in os.listdir(data_folder))
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos en {data_folder}")

    transformed_dfs = []

    for file_path in files:
        print(f"Procesando archivo: {file_path}")

        # Aplicar transformaciones
        df_transformed = transform_clima_data(file_path)
        if df_transformed is not None:
            transformed_dfs.append(df_transformed)
        else:
            print(f"Saltando archivo {file_path} debido a errores de lectura")

    # Concatenar todos los DataFrames transformados
    if transformed_dfs:
        combined_df = pd.concat(transformed_dfs, ignore_index=True)
        # Ordenar final por id_estacion y fecha
        combined_df = combined_df.sort_values(['id_estacion', 'fecha']).reset_index(drop=True)
        return combined_df
    else:
        raise ValueError("No se pudieron procesar archivos válidos")
    
def guardar_datos(df_combined):
    try:
        df_combined.to_parquet('data/datos_climaticos.parquet', index=False)
        print('✅ Archivo guardado con exito.')
    except Exception as e:
        print('🔴 Hubo en error al intentar guardar los datos.\n\n', e)

# Ejemplo de uso (puedes adaptar para tu ETL)
if __name__ == "__main__":
    # Procesar todos los archivos en data/datos-estaciones y combinar
    try:
        df_combined = process_all_station_files('data/datos-estaciones')
        guardar_datos(df_combined)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Asegúrate de que la carpeta 'data/datos-estaciones' existe y contiene archivos .parquet o .csv")