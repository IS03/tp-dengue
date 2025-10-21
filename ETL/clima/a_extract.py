import pandas as pd
import json
from io import BytesIO
import requests
import time
from fake_useragent import UserAgent
import os, sys

ua = UserAgent()


ruta_actual = os.path.dirname(__file__)
ruta_dos_atras = os.path.abspath(os.path.join(ruta_actual, "..", ".."))
sys.path.append(ruta_dos_atras)


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
    'user-agent': ua.random,
  }

  return requests.get(f'https://siga.inta.gob.ar/document/series/{id_estacion}.xls', headers=headers)

def generar_excel(response):
  if response.status_code == 200:
    try:
        return response.content
    except Exception as e:
        return None
  else:
      return None


def proceso(ids_estaciones):
    carpeta = 'C:/Documents/Proyectos/casos-dengue/tp-dengue/data/datos-estaciones'
    errores_carpeta = 'C:/Documents/Proyectos/casos-dengue/tp-dengue/data/estaciones-errores'
    errores_archivo = os.path.join(errores_carpeta, "errores.txt")

    # Crear carpetas si no existen
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    if not os.path.exists(errores_carpeta):
        os.makedirs(errores_carpeta)

    # verificar si el proceso ya se realizo
    if len(os.listdir(carpeta)) > 5:
        print('Ya existen los archivos de las estaciones. El proceso se realizo anteriormente.')
    
    else:
        for index, id in enumerate(ids_estaciones):
            path = f"{carpeta}/{id}.xls"

            if not os.path.exists(path):
                try:
                    response = obtener_historico(id)
                    contenido = generar_excel(response)

                    if contenido is not None:
                        with open(path, 'wb') as excel:
                            excel.write(contenido)
                    else:
                        # Guardar el id fallido
                        with open(errores_archivo, "a") as f:
                            f.write(f"{id}/n")

                except Exception as e:
                    # Cualquier error inesperado también lo guardamos
                    with open(errores_archivo, "a") as f:
                        f.write(f"{id}/n")
                    print(f"Error con {id}: {e}")


def run():
    ruta = "C:/Documents/Proyectos/casos-dengue/tp-dengue/data/estaciones-meteorologicas-inta.csv"
    df_estaciones = pd.read_csv(ruta)
    df_estaciones.columns = [col.lower().replace(' ', '_').strip() for col in df_estaciones.columns]

    ids_estaciones = list(df_estaciones.id_interno.unique())
    proceso(ids_estaciones)


if __name__ == '__main__':
    run()