#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL Dengue AR (2018-2025)
Autor: Nacho + ChatGPT
Versión mejorada con logging, validaciones y manejo robusto de encoding

Uso:
  python etl_dengue.py --input_dir ./raw --out_dir ./processed --geo_map ./ref/geo_map.csv --population ./ref/poblacion.csv

Requisitos: pandas, openpyxl, chardet
"""
import os
import sys
import argparse
import logging
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

# Importar configuraciones y utilidades
from config import (
    STANDARD_COLUMNS, COLUMN_ALIASES, PROVINCE_SYNONYMS, DENGUE_EVENTS,
    YEAR_MIN, YEAR_MAX, WEEK_MIN, WEEK_MAX, UNKNOWN_DEPT_ID, UNKNOWN_PROV_ID,
    ensure_directories, is_valid_year, is_valid_week, is_unknown_id
)
from utils import (
    setup_logging, read_csv_robust, normalize_text, normalize_series,
    validate_epidemiological_week, validate_date_range, validate_geo_consistency,
    handle_missing_values, calculate_incidence, get_data_quality_summary
)

# Configurar logging
logger = setup_logging('dengue_etl')

# Usar constantes del archivo de configuración
STD_COLS = STANDARD_COLUMNS
ALIASES = COLUMN_ALIASES
EVENTO_DENGUE = DENGUE_EVENTS
PROV_SYN = PROVINCE_SYNONYMS

# Las funciones strip_accents, norm_text, detect_sep y try_read_csv 
# ahora están en utils.py y se importan desde ahí

def try_read_excel(path: Path) -> pd.DataFrame:
    try:
        return pd.read_excel(path, dtype=str)  # primera hoja
    except Exception as e:
        raise e

def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapea las columnas del DataFrame al esquema estándar.
    
    Args:
        df: DataFrame con columnas a mapear
        
    Returns:
        DataFrame con columnas mapeadas al esquema estándar
    """
    logger.debug(f"Mapeando columnas. Columnas originales: {list(df.columns)}")
    
    # Build reverse alias map
    lower_cols = {c: normalize_text(c).lower() for c in df.columns}
    rename = {}
    
    for std, alist in ALIASES.items():
        for c, lc in lower_cols.items():
            if lc in [a.lower() for a in alist]:
                rename[c] = std
                logger.debug(f"Mapeando columna '{c}' -> '{std}'")
    
    out = df.rename(columns=rename)
    
    # Asegurar que todas las columnas estándar estén presentes
    for c in STD_COLS:
        if c not in out.columns:
            out[c] = pd.NA
            logger.debug(f"Agregando columna faltante: {c}")
    
    # Mantener solo columnas estándar
    return out[STD_COLS]

def clean_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y normaliza los tipos de datos del DataFrame.
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        DataFrame limpio y normalizado
    """
    logger.info(f"Iniciando limpieza de tipos. Filas iniciales: {len(df)}")
    
    # Normalizar columnas de texto
    text_columns = ["provincia_nombre", "departamento_nombre", "evento_nombre", "grupo_edad_desc"]
    for c in text_columns:
        if c in df.columns:
            df[c] = normalize_series(df[c])
            logger.debug(f"Normalizada columna de texto: {c}")

    # Aplicar sinónimos de provincias
    df["provincia_nombre"] = df["provincia_nombre"].replace(PROV_SYN)
    logger.debug("Aplicados sinónimos de provincias")

    # Conversiones numéricas
    numeric_columns = ["anio", "semana_epi", "grupo_edad_id", "cantidad_casos", "provincia_id", "departamento_id"]
    for c in numeric_columns:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            logger.debug(f"Convertida a numérico: {c}")

    # Conversión de fecha
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        logger.debug("Convertida columna fecha")

    # Filtrar solo eventos de dengue
    df["evento_nombre"] = df["evento_nombre"].fillna("DENGUE")
    initial_rows = len(df)
    df = df[df["evento_nombre"].str.contains("DENGUE", na=False)]
    logger.info(f"Filtrados eventos de dengue. Filas después del filtro: {len(df)} (eliminadas: {initial_rows - len(df)})")

    # Manejo de años
    df["anio"] = df["anio"].fillna(pd.NA)
    
    # Derivar año desde fecha si falta
    mask_no_year = df["anio"].isna() & df["fecha"].notna()
    if mask_no_year.any():
        df.loc[mask_no_year, "anio"] = df.loc[mask_no_year, "fecha"].dt.year
        logger.info(f"Derivados {mask_no_year.sum()} años desde fecha")
    
    df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")

    # Manejo de semanas epidemiológicas
    if "semana_epi" in df.columns:
        mask_no_week = df["semana_epi"].isna() & df["fecha"].notna()
        if mask_no_week.any():
            iso = df.loc[mask_no_week, "fecha"].dt.isocalendar()
            df.loc[mask_no_week, "semana_epi"] = iso.week.astype("Int64")
            logger.info(f"Derivadas {mask_no_week.sum()} semanas desde fecha")

    df["semana_epi"] = pd.to_numeric(df["semana_epi"], errors="coerce").astype("Int64")

    # Validar rangos de años y semanas
    invalid_years = df[~df["anio"].apply(is_valid_year)]
    if not invalid_years.empty:
        logger.warning(f"Encontrados {len(invalid_years)} registros con años inválidos: {invalid_years['anio'].unique()}")
    
    # Filtrar años válidos
    df = df[df["anio"].apply(is_valid_year)]
    logger.info(f"Filtrados años válidos. Filas restantes: {len(df)}")

    # Validar semanas epidemiológicas
    if "semana_epi" in df.columns:
        invalid_weeks = df[df["semana_epi"].notna() & ~df.apply(lambda x: validate_epidemiological_week(x["anio"], x["semana_epi"]), axis=1)]
        if not invalid_weeks.empty:
            logger.warning(f"Encontrados {len(invalid_weeks)} registros con semanas epidemiológicas inválidas")
        
        # Filtrar semanas válidas
        df = df[df["semana_epi"].isna() | df.apply(lambda x: validate_epidemiological_week(x["anio"], x["semana_epi"]), axis=1)]
        logger.info(f"Filtradas semanas válidas. Filas restantes: {len(df)}")

    # Manejo de casos
    df["cantidad_casos"] = pd.to_numeric(df["cantidad_casos"], errors="coerce")
    
    # Identificar y manejar datos desconocidos
    unknown_dept_mask = df["departamento_id"] == UNKNOWN_DEPT_ID
    unknown_prov_mask = df["provincia_id"] == UNKNOWN_PROV_ID
    
    if unknown_dept_mask.any():
        logger.warning(f"Encontrados {unknown_dept_mask.sum()} registros con departamento desconocido (ID: {UNKNOWN_DEPT_ID})")
    
    if unknown_prov_mask.any():
        logger.warning(f"Encontrados {unknown_prov_mask.sum()} registros con provincia desconocida (ID: {UNKNOWN_PROV_ID})")
    
    # Manejar valores faltantes en casos
    df = handle_missing_values(df, "cantidad_casos", strategy="fill", fill_value=0)
    df["cantidad_casos"] = df["cantidad_casos"].astype(int)

    # Manejo de grupo de edad
    df = handle_missing_values(df, "grupo_edad_desc", strategy="fill", fill_value="SIN ESPECIFICAR")
    
    logger.info(f"Limpieza completada. Filas finales: {len(df)}")
    return df

def deduplicate_and_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    # Clave mínima para una fila de casos
    key = ["anio","semana_epi","provincia_id","provincia_nombre",
           "departamento_id","departamento_nombre",
           "grupo_edad_id","grupo_edad_desc"]
    # Algunos datasets no tienen IDs → usamos nombres
    if df["provincia_id"].isna().all():
        key.remove("provincia_id")
    if df["departamento_id"].isna().all():
        key.remove("departamento_id")
    if df["grupo_edad_id"].isna().all():
        key.remove("grupo_edad_id")

    # Agregar por clave sumando casos
    agg = df.groupby(key, dropna=False, as_index=False)["cantidad_casos"].sum()
    return agg

def attach_geo_map(df: pd.DataFrame, geo_map_path: Optional[str]) -> pd.DataFrame:
    if not geo_map_path or not os.path.exists(geo_map_path):
        return df
    gm = pd.read_csv(geo_map_path, dtype=str)
    # columnas esperadas: provincia_nombre, provincia_id, departamento_nombre, departamento_id
    # normalizamos nombres para join robusto
    for c in ["provincia_nombre","departamento_nombre"]:
        if c in gm.columns:
            gm[c] = gm[c].apply(lambda x: normalize_text(x) if pd.notna(x) else x)
    # Join por nombre si faltan IDs
    if df["provincia_id"].isna().all() and "provincia_id" in gm.columns:
        df = df.merge(gm[["provincia_nombre","provincia_id"]].drop_duplicates(),
                      on="provincia_nombre", how="left")
    if df["departamento_id"].isna().all() and "departamento_id" in gm.columns:
        df = df.merge(gm[["provincia_nombre","departamento_nombre","departamento_id"]].drop_duplicates(),
                      on=["provincia_nombre","departamento_nombre"], how="left")
    return df

def attach_population(df: pd.DataFrame, pop_path: Optional[str]) -> pd.DataFrame:
    """
    Adjunta datos de población y calcula incidencia.
    
    Args:
        df: DataFrame con datos de dengue
        pop_path: Ruta al archivo de población
        
    Returns:
        DataFrame con datos de población e incidencia
    """
    if not pop_path or not os.path.exists(pop_path):
        logger.warning("Archivo de población no encontrado. Incidencia no calculada.")
        df["incidencia"] = np.nan
        return df
    
    logger.info(f"Cargando datos de población desde: {pop_path}")
    
    try:
        pop = read_csv_robust(Path(pop_path))
        logger.debug(f"Datos de población cargados: {len(pop)} filas")
        
        # Normalizar columnas de texto
        for c in ["provincia_nombre", "departamento_nombre"]:
            if c in pop.columns:
                pop[c] = normalize_series(pop[c])
        
        # Convertir tipos numéricos
        if "anio" in pop.columns:
            pop["anio"] = pd.to_numeric(pop["anio"], errors="coerce").astype("Int64")
        if "poblacion" in pop.columns:
            pop["poblacion"] = pd.to_numeric(pop["poblacion"], errors="coerce")
        
        # Merge con datos de dengue
        initial_rows = len(df)
        df = df.merge(pop, on=["anio", "provincia_nombre", "departamento_nombre"], how="left")
        
        # Calcular incidencia
        df["incidencia"] = calculate_incidence(df["cantidad_casos"], df["poblacion"])
        
        # Estadísticas del merge
        matched_rows = df["poblacion"].notna().sum()
        logger.info(f"Merge de población completado. Filas con población: {matched_rows}/{len(df)} ({matched_rows/len(df)*100:.1f}%)")
        
        return df
        
    except Exception as e:
        logger.error(f"Error cargando datos de población: {e}")
        df["incidencia"] = np.nan
        return df

def process_file(path: Path, quality_rows: List[Dict]) -> pd.DataFrame:
    """
    Procesa un archivo individual de datos de dengue.
    
    Args:
        path: Ruta al archivo a procesar
        quality_rows: Lista para almacenar métricas de calidad
        
    Returns:
        DataFrame procesado
    """
    logger.info(f"Procesando archivo: {path}")
    
    ext = path.suffix.lower()
    try:
        if ext in [".csv", ".txt"]:
            raw = read_csv_robust(path)
            logger.debug(f"Archivo CSV leído exitosamente: {len(raw)} filas")
        elif ext in [".xlsx", ".xls"]:
            raw = try_read_excel(path)
            logger.debug(f"Archivo Excel leído exitosamente: {len(raw)} filas")
        else:
            raise ValueError(f"Formato no soportado: {ext}")
            
    except Exception as e:
        logger.error(f"Error procesando archivo {path}: {e}")
        quality_rows.append({
            "file": str(path),
            "status": "ERROR",
            "rows_in": 0,
            "rows_out": 0,
            "error": str(e)
        })
        return pd.DataFrame(columns=STD_COLS)

    rows_in = len(raw)
    logger.debug(f"Filas leídas: {rows_in}")
    
    # Mapear columnas al esquema estándar
    df = map_columns(raw)
    logger.debug(f"Columnas mapeadas. Filas: {len(df)}")
    
    # Limpiar y normalizar tipos
    df = clean_types(df)
    rows_mid = len(df)
    logger.debug(f"Después de limpieza: {rows_mid} filas")

    # Agregación y deduplicación
    df = deduplicate_and_aggregate(df)
    rows_out = len(df)
    logger.info(f"Archivo procesado exitosamente. Filas finales: {rows_out}")

    # Registrar métricas de calidad
    quality_rows.append({
        "file": str(path),
        "status": "OK",
        "rows_in": rows_in,
        "rows_after_clean": rows_mid,
        "rows_out": rows_out,
        "dup_removed": rows_mid - rows_out
    })
    
    return df

def build_month_from_year_week(df: pd.DataFrame) -> pd.Series:
    # Aproxima el mes desde año+semana ISO → lunes de esa semana
    def week_start(y, w):
        try:
            return pd.to_datetime(f"{int(y)}-W{int(w)}-1", format="%G-W%V-%u")
        except Exception:
            return pd.NaT
    dates = [week_start(y, w) if pd.notna(y) and pd.notna(w) else pd.NaT
             for y, w in zip(df["anio"], df["semana_epi"])]
    ser = pd.Series(pd.to_datetime(dates))
    return ser.dt.month

def main():
    """
    Función principal del ETL de dengue.
    """
    logger.info("=== INICIANDO ETL DE DENGUE ===")
    
    # Configurar argumentos de línea de comandos
    ap = argparse.ArgumentParser(description="ETL para datos de dengue 2018-2025")
    ap.add_argument("--input_dir", required=True, help="Carpeta con CSV/XLSX crudos")
    ap.add_argument("--out_dir", required=True, help="Carpeta de salida")
    ap.add_argument("--geo_map", default=None, help="CSV con mapeo de provincias/deptos a IDs (opcional)")
    ap.add_argument("--population", default=None, help="CSV con poblacion por anio-prov-depto (opcional)")
    ap.add_argument("--verbose", "-v", action="store_true", help="Modo verbose para más detalles")
    
    args = ap.parse_args()
    
    # Configurar nivel de logging según verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Modo verbose activado")

    # Configurar directorios
    in_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Asegurar que todos los directorios necesarios existen
    ensure_directories()
    
    logger.info(f"Directorio de entrada: {in_dir}")
    logger.info(f"Directorio de salida: {out_dir}")

    # Buscar archivos a procesar
    files = [p for p in in_dir.glob("**/*") if p.suffix.lower() in [".csv", ".txt", ".xlsx", ".xls"]]
    logger.info(f"Archivos encontrados para procesar: {len(files)}")

    if not files:
        logger.error(f"No se encontraron archivos en {in_dir}")
        sys.exit(1)

    # Procesar archivos
    quality = []
    frames = []
    
    for p in files:
        df = process_file(p, quality)
        if not df.empty:
            frames.append(df)
            logger.debug(f"Archivo {p.name} agregado al conjunto de datos")

    if not frames:
        logger.error("No hubo datos válidos después del procesamiento")
        sys.exit(1)

    logger.info(f"Combinando {len(frames)} archivos procesados")
    all_df = pd.concat(frames, ignore_index=True)
    logger.info(f"Dataset combinado: {len(all_df)} filas, {len(all_df.columns)} columnas")

    # Validación de consistencia geográfica si se proporciona geo_map
    if args.geo_map and os.path.exists(args.geo_map):
        logger.info("Validando consistencia geográfica")
        geo_map = pd.read_csv(args.geo_map)
        geo_validation = validate_geo_consistency(all_df, geo_map)
        
        if geo_validation['warnings']:
            for warning in geo_validation['warnings']:
                logger.warning(warning)

    # Enriquecimientos opcionales
    logger.info("Aplicando enriquecimientos opcionales")
    all_df = attach_geo_map(all_df, args.geo_map)
    all_df = attach_population(all_df, args.population)

    # Generar resumen de calidad de datos
    quality_summary = get_data_quality_summary(all_df)
    logger.info(f"Resumen de calidad: {quality_summary['total_rows']} filas, {quality_summary['duplicate_rows']} duplicados")

    # Guardar archivo principal
    logger.info("Guardando archivo principal")
    all_df.to_parquet(out_dir / "dengue_2018_2025_clean.parquet", index=False)
    all_df.to_csv(out_dir / "dengue_2018_2025_clean.csv", index=False)

    # Generar agregaciones semanales por departamento
    logger.info("Generando agregación semanal por departamento")
    week_cols = ["anio", "semana_epi", "provincia_nombre", "departamento_nombre"]
    if "provincia_id" in all_df.columns: 
        week_cols.insert(2, "provincia_id")
    if "departamento_id" in all_df.columns: 
        week_cols.insert(4, "departamento_id")

    weekly = (all_df
              .groupby(week_cols, dropna=False, as_index=False)
              .agg(cantidad_casos=("cantidad_casos", "sum"),
                   poblacion=("poblacion", "first"))
             )
    
    if "poblacion" in weekly.columns:
        weekly["incidencia"] = calculate_incidence(weekly["cantidad_casos"], weekly["poblacion"])
    
    weekly.to_parquet(out_dir / "weekly_by_depto.parquet", index=False)
    weekly.to_csv(out_dir / "weekly_by_depto.csv", index=False)
    logger.info(f"Agregación semanal guardada: {len(weekly)} filas")

    # Generar agregaciones mensuales por provincia
    logger.info("Generando agregación mensual por provincia")
    all_df["mes"] = build_month_from_year_week(all_df)
    monthly = (all_df
               .groupby(["anio", "mes", "provincia_nombre"], dropna=False, as_index=False)
               .agg(cantidad_casos=("cantidad_casos", "sum"))
              )
    monthly.to_parquet(out_dir / "monthly_by_prov.parquet", index=False)
    monthly.to_csv(out_dir / "monthly_by_prov.csv", index=False)
    logger.info(f"Agregación mensual guardada: {len(monthly)} filas")

    # Generar reporte de calidad
    logger.info("Generando reporte de calidad")
    qdf = pd.DataFrame(quality)
    reports_dir = out_dir.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    qdf.to_csv(reports_dir / "quality_report.csv", index=False)
    
    # Estadísticas finales
    logger.info("=== ETL COMPLETADO EXITOSAMENTE ===")
    logger.info(f"Archivos procesados: {len(files)}")
    logger.info(f"Filas limpias totales: {len(all_df):,}")
    logger.info(f"Archivos generados en: {out_dir}")
    logger.info(f"Reporte de calidad en: {reports_dir / 'quality_report.csv'}")
    
    print("✔ ETL terminado exitosamente.")
    print(f"📊 Filas limpias totales: {len(all_df):,}")
    print(f"📁 Archivos generados en: {out_dir}")
    print(f"📋 Reporte de calidad: {reports_dir / 'quality_report.csv'}")

if __name__ == "__main__":
    main()
