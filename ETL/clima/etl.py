# -*- coding: utf-8 -*-
"""
ETL Runner: Ejecuta el proceso completo de ETL
-----------------------------------------------
Script principal que coordina las fases de extracción, transformación y carga
usando las funciones de los módulos extract.py, transform.py y load.py
"""

import os
import logging
import pandas as pd

# Importar funciones de los módulos ETL
from ETL.clima.b_transform import run_eda_transformations

# -----------------------------------------------------------------------------
# Configuración de logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Configuración de rutas
# -----------------------------------------------------------------------------
INPUT_PARQUET = "data/datos-todas-estaciones.parquet"
OUTPUT_PARQUET = "data/datos_clima_transformados.parquet"

# -----------------------------------------------------------------------------
# Función principal del ETL
# -----------------------------------------------------------------------------
def run_etl():
    """
    Ejecuta el proceso completo de ETL: Extract, Transform, Load.
    """
    try:
        log.info("🚀 Iniciando proceso ETL completo...")

        # 1) Verificar que existe el archivo de datos
        if not os.path.exists(INPUT_PARQUET):
            log.error(f"❌ No se encontró el archivo de datos: {INPUT_PARQUET}")
            return False
        else:
            log.info("📦 Archivo de datos encontrado")

        # 2) Leer datos extraídos
        log.info("📖 Leyendo datos crudos...")
        df_raw = pd.read_parquet(INPUT_PARQUET)
        log.info(f"📊 Datos crudos: {len(df_raw)} filas, {len(df_raw.columns)} columnas")

        # 3) TRANSFORM: Aplicar transformaciones
        log.info("🔄 Aplicando transformaciones...")
        df_transformed = run_eda_transformations(df_raw)
        log.info(f"✨ Datos transformados: {len(df_transformed)} filas, {len(df_transformed.columns)} columnas")

        # 4) LOAD: Guardar datos transformados en Parquet
        log.info("💾 Guardando datos transformados en Parquet...")
        df_transformed.to_parquet(OUTPUT_PARQUET, index=False)
        log.info(f"✅ Datos guardados en: {OUTPUT_PARQUET}")

        # Estadísticas finales
        print("\n" + "="*50)
        print("ESTADISTICAS DEL PROCESO ETL")
        print("="*50)
        print(f"Registros transformados: {len(df_transformed)}")
        print(f"Estaciones procesadas: {df_transformed['id_estacion'].nunique()}")
        print(f"Rango de fechas: {df_transformed['fecha'].min()} - {df_transformed['fecha'].max()}")
        print(f"Archivo Parquet generado: {OUTPUT_PARQUET}")
        print("="*50)

        log.info("✅ Proceso ETL completado exitosamente!")
        return True

    except Exception as e:
        log.error(f"💥 Error crítico en ETL: {e}")
        return False

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    success = run_etl()
    exit(0 if success else 1)