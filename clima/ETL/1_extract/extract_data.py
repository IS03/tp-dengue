import pandas as pd
import json
from io import BytesIO
import requests
import time, os
from dotenv import load_dotenv

# Carga las variables desde el archivo .env
load_dotenv()

USER_AGENT = os.getenv("USER_AGENT")

def obtener_historico(id_estacion):
  headers = {
    'accept': '*/*',
    'accept-language': 'es-419,es;q=0.7',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Brave";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': USER_AGENT,
  }

  return requests.get(f'https://siga.inta.gob.ar/document/series/{id_estacion}.xls', headers=headers)

def generar_excel(response):
  if response.status_code == 200:
    try:
        return pd.read_excel(BytesIO(response.content), engine='xlrd')
    except Exception as e:
        print(f"Error con el excel: {e}")
  else:
      print(f"Hubo un error y no se pudo completar el proceso: {response.status_code}")


if __name__ == "__main__":
    try:
        # 1) Validaciones iniciales
        if not USER_AGENT:
            raise RuntimeError("La variable de entorno USER_AGENT no está definida en .env")

        ruta = "../../data/estaciones-meteorologicas-inta.csv"
        try:
            df_estaciones = pd.read_csv(ruta)
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo de estaciones: {ruta}")
        except pd.errors.ParserError as e:
            raise RuntimeError(f"Error al parsear el CSV de estaciones: {e}")

        if "id_interno" not in df_estaciones.columns:
            raise KeyError("La columna 'id_interno' no existe en el CSV de estaciones.")

        ids = df_estaciones["id_interno"].dropna().astype(str).unique()
        if len(ids) == 0:
            raise RuntimeError("No se encontraron IDs de estaciones válidos en el CSV.")

        # 2) Descarga y parsing por estación (con tolerancia a errores por estación)
        data = []
        for i, id_est in enumerate(ids, start=1):
            try:
                response = obtener_historico(id_est)
                if response is None:
                    print(f"[{i}/{len(ids)}] {id_est}: respuesta None, se salta.")
                    continue

                if response.status_code != 200:
                    print(f"[{i}/{len(ids)}] {id_est}: HTTP {response.status_code}, se salta.")
                    continue

                df = generar_excel(response)
                if df is None or df.empty:
                    print(f"[{i}/{len(ids)}] {id_est}: DataFrame vacío/None, se salta.")
                    continue

                df["id_estacion"] = id_est
                data.append(df)
                print(f"[{i}/{len(ids)}] {id_est} listo ({len(df)} filas).")

            except Exception as e:
                # Cualquier error no esperado en esta estación no detiene todo el proceso
                print(f"[{i}/{len(ids)}] {id_est}: Error inesperado → {e}")
            finally:
                # Respetar una pausa entre requests
                time.sleep(5)

        # 3) Consolidación y guardado
        if not data:
            print("No se descargaron datos de ninguna estación. No se genera el parquet.")
        else:
            try:
                full = pd.concat(data, ignore_index=True)
                out_path = "../../data/datos-todas-estaciones.parquet"
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                full.to_parquet(out_path, index=False)
                print(f"Parquet generado: {out_path} | filas={len(full)}, columnas={len(full.columns)}")
            except Exception as e:
                print(f"Error al guardar el parquet: {e}")

    except Exception as e:
        # Errores críticos que impiden correr el proceso completo
        print(f"Proceso abortado: {e}")


