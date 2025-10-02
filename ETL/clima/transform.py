# -*- coding: utf-8 -*-
"""
Transformaciones EDA por archivo (una estación por archivo)
-----------------------------------------------------------
Versión con manejo básico de errores, validaciones y mensajes de logging.
No usa patrones avanzados para mantenerlo simple y legible.
"""

import logging
from typing import Iterable, List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# -----------------------------------------------------------------------------
# Configuración de logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Variables y renombres
# -----------------------------------------------------------------------------
VARIABLES_SELECCIONADAS: List[str] = [
    # Control
    "fecha", "id_estacion",
    # Muy alta importancia
    "precipitacion_pluviometrica",
    "temperatura_abrigo_150cm_minima",
    "temperatura_abrigo_150cm_maxima",
    "temperatura_abrigo_150cm",
    # Alta importancia
    "humedad_media_8_14_20",
    "rocio_medio",
    "tesion_vapor_media",
    # Media
    "radiacion_global",
    "heliofania_efectiva",
    "heliofania_relativa",
]

VARIABLES_RENOMBRADAS = {
    "temperatura_abrigo_150cm_minima": "temperatura_minima",
    "temperatura_abrigo_150cm_maxima": "temperatura_maxima",
    "temperatura_abrigo_150cm": "temperatura_media",
    "humedad_media_8_14_20": "humedad_media",
}

MIN_REG_SAMPLES = 10  # mínimo de ejemplos para entrenar regresiones simples


# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------
def _coerce_list(x) -> List[str]:
    if x is None:
        return []
    if isinstance(x, (list, tuple, set)):
        return list(x)
    return [x]

def agregar_id_estacion(df, nombre_archivo):
    nombre_archivo = nombre_archivo.split('/')[-1].strip('.xls')
    df['id_estacion'] = nombre_archivo
    return df

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Pasa nombres a minúsculas, reemplaza espacios por guión bajo y trimea."""
    out = df.copy()
    out.columns = [str(col).replace(" ", "_").lower().strip() for col in out.columns]
    out
    return out


def seleccion_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona solo columnas de interés (las que existan) y avisa si faltan."""
    out = df.copy()
    existentes = [c for c in VARIABLES_SELECCIONADAS if c in out.columns]
    faltantes = [c for c in VARIABLES_SELECCIONADAS if c not in out.columns]
    if faltantes:
        log.warning(f"Columnas faltantes (se omiten): {faltantes}")
    if not existentes:
        log.error("No hay columnas útiles para procesar.")
        return out
    return out[existentes].copy()


def renombrar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=VARIABLES_RENOMBRADAS)


def convertir_fecha(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "fecha" not in out.columns:
        log.warning("No existe columna 'fecha'; se omite conversión y orden.")
        return out
    out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce")
    if out["fecha"].isna().any():
        n = int(out["fecha"].isna().sum())
        log.warning(f"{n} filas tienen 'fecha' inválida (NaT).")
    return out.sort_values("fecha", ascending=True)


def eliminar_duplicados(df: pd.DataFrame, subset: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """Elimina duplicados (global o por subset)."""
    out = df.copy()
    if subset is not None:
        subset = _coerce_list(subset)
    before = len(out)
    out = out.drop_duplicates(subset=subset, keep="first")
    dropped = before - len(out)
    if dropped:
        log.info(f"Eliminados {dropped} duplicados.")
    return out


def eliminar_nulos(df: pd.DataFrame, subset: Iterable[str]) -> pd.DataFrame:
    """Elimina filas con NaN en todas las columnas del subset dado."""
    out = df.copy()
    subset = _coerce_list(subset)
    before = len(out)
    out = out.dropna(subset=subset, how="any").reset_index(drop=True)
    dropped = before - len(out)
    if dropped:
        log.info(f"Eliminadas {dropped} filas con nulos en {subset}.")
    return out


# -----------------------------------------------------------------------------
# Transformaciones por variable
# -----------------------------------------------------------------------------
def transform_precipitacion_pluviometrica(df: pd.DataFrame) -> pd.DataFrame:
    if "precipitacion_pluviometrica" not in df.columns:
        return df
    out = df.copy()
    # Aseguramos no-negatividad
    safe = out["precipitacion_pluviometrica"].clip(lower=0)
    col_log = np.log1p(safe)  # log(1+x)
    denom = (col_log.max() - col_log.min())
    if pd.isna(denom) or denom == 0:
        log.warning("Precipitación: rango nulo tras log1p; se deja la serie original clippeada.")
        out["precipitacion_pluviometrica"] = safe
        return out
    out["precipitacion_pluviometrica"] = (col_log - col_log.min()) / denom
    # Interpolación suave
    try:
        out["precipitacion_pluviometrica"] = out["precipitacion_pluviometrica"].interpolate(
            method="spline", order=2
        )
    except Exception as e:
        log.warning(f"Interpolación spline falló en precipitación ({e}); se usa lineal.")
        out["precipitacion_pluviometrica"] = out["precipitacion_pluviometrica"].interpolate(method="linear")
    return out


def transform_temperatura(df: pd.DataFrame) -> pd.DataFrame:
    needed = {"temperatura_minima", "temperatura_maxima", "temperatura_media"}
    if not needed.issubset(df.columns):
        log.warning("Temperatura: faltan columnas para la transformación; se omite.")
        return df

    out = df.copy()

    # 1) Corrección de inconsistencias
    mask_min_max = out["temperatura_minima"] > out["temperatura_maxima"]
    if mask_min_max.any():
        out.loc[mask_min_max, ["temperatura_minima", "temperatura_maxima"]] = (
            out.loc[mask_min_max, ["temperatura_maxima", "temperatura_minima"]].to_numpy()
        )
        log.info(f"Temperatura: corregidas {int(mask_min_max.sum())} filas con mínima>máxima.")

    # 2) Temperatura media desde (min+max)/2
    mask_temp = out["temperatura_media"].isna() & out["temperatura_minima"].notna() & out["temperatura_maxima"].notna()
    out.loc[mask_temp, "temperatura_media"] = (
        (out.loc[mask_temp, "temperatura_minima"] + out.loc[mask_temp, "temperatura_maxima"]) / 2
    )

    # 3) Imputar min y max desde media con diferencias promedio
    with np.errstate(invalid="ignore"):
        dmin = (out["temperatura_minima"] - out["temperatura_media"]).abs().mean(skipna=True)
        dmax = (out["temperatura_maxima"] - out["temperatura_media"]).abs().mean(skipna=True)
        dmin = 0.0 if pd.isna(dmin) else float(dmin)
        dmax = 0.0 if pd.isna(dmax) else float(dmax)

    mask_minima = out["temperatura_minima"].isna() & out["temperatura_media"].notna()
    out.loc[mask_minima, "temperatura_minima"] = out.loc[mask_minima, "temperatura_media"] - dmin

    mask_maxima = out["temperatura_maxima"].isna() & out["temperatura_media"].notna()
    # OJO: bug corregido (antes restaba en vez de sumar)
    out.loc[mask_maxima, "temperatura_maxima"] = out.loc[mask_maxima, "temperatura_media"] + dmax

    # 4) Interpolación lineal
    for c in ["temperatura_minima", "temperatura_maxima", "temperatura_media"]:
        out[c] = out[c].interpolate(method="linear")

    return out


def transform_humedad_media(df: pd.DataFrame) -> pd.DataFrame:
    if "humedad_media" not in df.columns:
        return df
    out = df.copy()
    out["humedad_media"] = out["humedad_media"].interpolate(method="linear")
    return out


def transform_rocio_medio(df: pd.DataFrame) -> pd.DataFrame:
    if not {"rocio_medio", "temperatura_media"}.issubset(df.columns):
        return df
    out = df.copy()
    mask = out["rocio_medio"].notna() & out["temperatura_media"].notna()
    if mask.any():
        diff = (out.loc[mask, "temperatura_media"] - out.loc[mask, "rocio_medio"]).abs().mean()
        diff = float(diff) if not pd.isna(diff) else 0.0
    else:
        diff = 0.0
        log.info("Rocío: no hay pares válidos para estimar diferencia promedio; se asume 0.0.")

    mask_imp = out["rocio_medio"].isna() & out["temperatura_media"].notna()
    out.loc[mask_imp, "rocio_medio"] = out.loc[mask_imp, "temperatura_media"] - diff
    out["rocio_medio"] = out["rocio_medio"].interpolate(method="linear")
    return out


def transform_vapor_media(df: pd.DataFrame) -> pd.DataFrame:
    if not {"temperatura_media", "humedad_media"}.issubset(df.columns):
        return df
    out = df.copy()
    if "tesion_vapor_media" not in out.columns:
        out["tesion_vapor_media"] = np.nan

    def tension_vapor_formula(temp: pd.Series, rh: pd.Series) -> pd.Series:
        return (rh / 100.0) * (6.11 * np.exp((17.27 * temp) / (temp + 237.3)))

    mask = out["tesion_vapor_media"].isna() & out["temperatura_media"].notna() & out["humedad_media"].notna()
    out.loc[mask, "tesion_vapor_media"] = tension_vapor_formula(
        out.loc[mask, "temperatura_media"],
        out.loc[mask, "humedad_media"],
    )
    return out


def transform_radiacion_global(df: pd.DataFrame) -> pd.DataFrame:
    if "radiacion_global" not in df.columns or "heliofania_efectiva" not in df.columns:
        return df
    out = df.copy()

    mask_train = out["radiacion_global"].notna() & out["heliofania_efectiva"].notna()
    if mask_train.sum() >= MIN_REG_SAMPLES:
        X = out.loc[mask_train, ["heliofania_efectiva"]].to_numpy()
        y = out.loc[mask_train, "radiacion_global"].to_numpy()
        try:
            model = LinearRegression().fit(X, y)
            mask_null = out["radiacion_global"].isna() & out["heliofania_efectiva"].notna()
            if mask_null.any():
                out.loc[mask_null, "radiacion_global"] = model.predict(
                    out.loc[mask_null, ["heliofania_efectiva"]].to_numpy()
                )
        except Exception as e:
            log.warning(f"Radiación: regresión falló ({e}); se omite predicción.")
    else:
        log.info("Radiación: muy pocas muestras para entrenar regresión; se omite predicción.")

    out["radiacion_global"] = out["radiacion_global"].interpolate(method="linear")

    # Si a pesar de todo queda nulo, se eliminan esas filas
    if out["radiacion_global"].isna().any():
        out = eliminar_nulos(out, ["radiacion_global"])
    return out


def transform_heliofania(df: pd.DataFrame) -> pd.DataFrame:
    if not {"heliofania_efectiva", "heliofania_relativa"}.issubset(df.columns):
        return df

    out = df.copy()

    # a) efectiva ~ relativa
    mask_valid = out["heliofania_efectiva"].notna() & out["heliofania_relativa"].notna()
    mask_null = out["heliofania_efectiva"].isna() & out["heliofania_relativa"].notna()
    if mask_valid.sum() >= MIN_REG_SAMPLES and mask_null.any():
        try:
            X = out.loc[mask_valid, ["heliofania_relativa"]].to_numpy()
            y = out.loc[mask_valid, "heliofania_efectiva"].to_numpy()
            model = LinearRegression().fit(X, y)
            out.loc[mask_null, "heliofania_efectiva"] = model.predict(
                out.loc[mask_null, ["heliofania_relativa"]].to_numpy()
            )
        except Exception as e:
            log.warning(f"Heliofanía (efectiva~relativa) regresión falló: {e}")

    # b) relativa ~ efectiva
    mask_valid = out["heliofania_relativa"].notna() & out["heliofania_efectiva"].notna()
    mask_null = out["heliofania_relativa"].isna() & out["heliofania_efectiva"].notna()
    if mask_valid.sum() >= MIN_REG_SAMPLES and mask_null.any():
        try:
            X = out.loc[mask_valid, ["heliofania_efectiva"]].to_numpy()
            y = out.loc[mask_valid, "heliofania_relativa"].to_numpy()
            model = LinearRegression().fit(X, y)
            out.loc[mask_null, "heliofania_relativa"] = model.predict(
                out.loc[mask_null, ["heliofania_efectiva"]].to_numpy()
            )
        except Exception as e:
            log.warning(f"Heliofanía (relativa~efectiva) regresión falló: {e}")

    out["heliofania_efectiva"] = out["heliofania_efectiva"].interpolate(method="linear")
    out["heliofania_relativa"] = out["heliofania_relativa"].interpolate(method="linear")

    # Limpieza de duplicados exactos (global)
    out = eliminar_duplicados(out)
    return out


# -----------------------------------------------------------------------------
# Pipeline
# -----------------------------------------------------------------------------
def pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ejecuta el pipeline de transformaciones sobre un DF de una estación (un archivo).
    Incluye manejo básico de errores por etapa para no abortar todo el proceso.
    """
    def _step(name, func, data):
        try:
            return func(data)
        except Exception as e:
            log.error(f"Falla en paso '{name}': {e}. Se devuelve DF sin cambios en este paso.")
            return data

    steps = [
        ("normalizar_columnas", normalizar_columnas),
        ("seleccion_columnas", seleccion_columnas),
        ("renombrar_columnas", renombrar_columnas),
        ("convertir_fecha", convertir_fecha),
        ("eliminar_duplicados", eliminar_duplicados),
        ("transform_precipitacion_pluviometrica", transform_precipitacion_pluviometrica),
        ("transform_temperatura", transform_temperatura),
        ("transform_humedad_media", transform_humedad_media),
        ("transform_rocio_medio", transform_rocio_medio),
        ("transform_vapor_media", transform_vapor_media),
        ("transform_radiacion_global", transform_radiacion_global),
        ("transform_heliofania", transform_heliofania),
    ]

    out = df.copy()
    for name, func in steps:
        out = _step(name, func, out)
    return out
