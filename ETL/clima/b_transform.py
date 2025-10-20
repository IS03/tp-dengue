import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import glob

def transform_clima_data(path_archivo):
    """
    Aplica todas las transformaciones del EDA de datos climáticos para una estación específica.
    Cada archivo en 'data/datos-estaciones' representa una estación separada, por lo que
    las transformaciones se aplican directamente al DataFrame de esa estación.
    Retorna None si no se puede leer el archivo.
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
    id_estacion = path_archivo.split('/')[-1].strip('.xls').strip('.xlsx').strip()
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
    df.fecha = pd.to_datetime(df.fecha)

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

    # Ordenar por fecha (ya que es una estación específica)
    df = df.sort_values('fecha').reset_index(drop=True)

    # Creo la columna de id_estacion


    # Transformación de precipitacion_pluviometrica
    # Logarítmica seguida de Min-Max para estabilizar rangos
    col_log = np.log1p(df["precipitacion_pluviometrica"])
    df["precipitacion_pluviometrica"] = (col_log - col_log.min()) / (col_log.max() - col_log.min())
    # Interpolación spline para valores nulos
    df.precipitacion_pluviometrica = df.precipitacion_pluviometrica.interpolate(method='spline', order=2)

    # Transformaciones de temperaturas
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
    promedio_min_media = abs(np.mean(df.temperatura_minima - df.temperatura_media))
    mask_minima = (df.temperatura_minima.isna() & df.temperatura_media.notna())
    df.loc[mask_minima, 'temperatura_minima'] = (
        df.loc[mask_minima, 'temperatura_media'] - promedio_min_media
    )
    promedio_max_media = abs(np.mean(df.temperatura_maxima - df.temperatura_media))
    mask_maxima = (df.temperatura_maxima.isna() & df.temperatura_media.notna())
    df.loc[mask_maxima, 'temperatura_maxima'] = (
        df.loc[mask_maxima, 'temperatura_media'] + promedio_max_media
    )
    # Interpolación lineal para valores restantes
    df.loc[:, 'temperatura_minima'] = df.temperatura_minima.interpolate(method='linear')
    df.loc[:, 'temperatura_maxima'] = df.temperatura_maxima.interpolate(method='linear')
    df.loc[:, 'temperatura_media'] = df.temperatura_media.interpolate(method='linear')

    # Transformación de humedad_media
    # Interpolación lineal
    df.loc[:, 'humedad_media'] = df.humedad_media.interpolate(method='linear')

    # Transformación de rocio_medio
    # Imputar usando diferencia promedio con temperatura_media
    mask_rocio_temp = (df.rocio_medio.notna() & df.temperatura_media.notna())
    if mask_rocio_temp.sum() > 0:
        diff_rocio_temp = abs(df.loc[mask_rocio_temp].temperatura_media - df.loc[mask_rocio_temp].rocio_medio).mean()
        mask_rocio_temp_imputar = (df.rocio_medio.isna() & df.temperatura_media.notna())
        df.loc[mask_rocio_temp_imputar, 'rocio_medio'] = df.loc[mask_rocio_temp_imputar].temperatura_media - diff_rocio_temp
    # Interpolación lineal si quedan nulos
    df.rocio_medio = df.rocio_medio.interpolate(method='linear')

    # Transformación de tesion_vapor_media
    # Calcular usando fórmula física: e = (RH/100) * e_s(T)
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

    # Transformación de radiacion_global
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

    # Transformaciones de heliofania_efectiva y heliofania_relativa
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
    df.heliofania_efectiva = df.heliofania_efectiva.interpolate(method='linear')
    df.heliofania_relativa = df.heliofania_relativa.interpolate(method='linear')

    return df

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