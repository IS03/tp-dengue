# -*- coding: utf-8 -*-
"""
EDA de datos climáticos — Transformaciones sin gráficos
------------------------------------------------------
Este script implementa, de forma modular y ordenada, las transformaciones
definidas durante el EDA: normalización de nombres, tratamiento de nulos,
correcciones lógicas y diversas estrategias de imputación (interpolación,
regresión simple y reglas físicas) para variables meteorológicas típicas.

Notas:
- No se realizan agrupamientos por estación (id_estacion) en esta versión EDA.
- No se incluyen gráficos.
- Pensado para ser ejecutado como script o importado como módulo.

Autor: (tu nombre)
Fecha: (completa si querés)
"""

from __future__ import annotations

import os
from typing import List, Optional, Dict

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


# =============================================================================
# Configuración
# =============================================================================

COLUMNS_ORDER: list[str] = [
    "fecha", "id_estacion",
    "precipitacion_pluviometrica",
    "temperatura_abrigo_150cm_minima",
    "temperatura_abrigo_150cm_maxima",
    "temperatura_abrigo_150cm",
    "humedad_media_8_14_20",
    "rocio_medio",
    "tesion_vapor_media",
    "radiacion_global",
    "heliofania_efectiva",
    "heliofania_relativa",
]

RENAME_MAP: Dict[str, str] = {
    "temperatura_abrigo_150cm_minima": "temperatura_minima",
    "temperatura_abrigo_150cm_maxima": "temperatura_maxima",
    "temperatura_abrigo_150cm": "temperatura_media",
    "humedad_media_8_14_20": "humedad_media",
}

DAY_HOURS = range(7, 19)   # 7..18 como “día”
RAD_MAX_FISICO = 60        # MJ/m² — tope razonable para EDA (ajustable)
MIN_REG_SAMPLES = 30       # mínimo de muestras para entrenar regresiones


# =============================================================================
# Utilidades
# =============================================================================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte nombres de columnas a minúsculas y sin espacios extremos."""
    out = df.copy()
    out.columns = [c.lower().strip() for c in out.columns]
    return out


def select_and_rename(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona columnas de interés y aplica renombrados convenientes."""
    out = df[[c for c in COLUMNS_ORDER if c in df.columns]].copy()
    out = out.rename(columns=RENAME_MAP)
    return out


def fix_types_and_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Ajusta tipos básicos y elimina duplicados exactos."""
    out = df.copy()
    if "fecha" in out.columns:
        out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce")
    out = out.drop_duplicates(keep="first")
    return out


# =============================================================================
# Transformaciones por variable
# =============================================================================

def transform_precipitacion(df: pd.DataFrame, col: str = "precipitacion_pluviometrica") -> pd.DataFrame:
    """
    Precipitación: log1p -> min-max -> interpolación suave (spline).
    Nota: en EDA se deja normalizado para estabilizar rangos y nulos.
    """
    out = df.copy()
    if col not in out.columns:
        return out
    safe = out[col].clip(lower=0)
    col_log = np.log1p(safe)
    denom = (col_log.max() - col_log.min())
    if denom == 0 or np.isnan(denom):
        out[col] = safe
        return out
    norm = (col_log - col_log.min()) / denom
    out[col] = pd.Series(norm, index=out.index).interpolate(method="spline", order=2)
    return out


def transform_temperaturas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Temperaturas:
      1) Corrige inconsistencia mínima > máxima (swap).
      2) Imputa media con (min+max)/2 si ambas existen.
      3) Imputa mínima y máxima desde media con diferencia promedio global.
      4) Interpolación lineal para rezagos.
    """
    out = df.copy()

    cols_needed = {"temperatura_minima", "temperatura_maxima", "temperatura_media"}
    if not cols_needed.issubset(out.columns):
        return out

    # 1) swap si mínima > máxima
    mask_swap = out["temperatura_minima"] > out["temperatura_maxima"]
    out.loc[mask_swap, ["temperatura_minima", "temperatura_maxima"]] = (
        out.loc[mask_swap, ["temperatura_maxima", "temperatura_minima"]].to_numpy()
    )

    # 2) media = (min+max)/2 si falta
    mask_tmed = (
        out["temperatura_media"].isna()
        & out["temperatura_minima"].notna()
        & out["temperatura_maxima"].notna()
    )
    out.loc[mask_tmed, "temperatura_media"] = (
        out.loc[mask_tmed, "temperatura_minima"] + out.loc[mask_tmed, "temperatura_maxima"]
    ) / 2

    # 3) dif promedio |min-media| y |max-media|
    with np.errstate(invalid="ignore"):
        dmin = (out["temperatura_minima"] - out["temperatura_media"]).abs().mean(skipna=True)
        dmax = (out["temperatura_maxima"] - out["temperatura_media"]).abs().mean(skipna=True)

    mask_min = out["temperatura_minima"].isna() & out["temperatura_media"].notna()
    out.loc[mask_min, "temperatura_minima"] = out.loc[mask_min, "temperatura_media"] - dmin

    mask_max = out["temperatura_maxima"].isna() & out["temperatura_media"].notna()
    out.loc[mask_max, "temperatura_maxima"] = out.loc[mask_max, "temperatura_media"] + dmax

    # 4) interpolaciones lineales
    for c in ["temperatura_minima", "temperatura_maxima", "temperatura_media"]:
        out[c] = out[c].interpolate(method="linear")

    return out


def transform_humedad(df: pd.DataFrame, col: str = "humedad_media") -> pd.DataFrame:
    """Interpolación lineal simple para humedad media."""
    out = df.copy()
    if col in out.columns:
        out[col] = out[col].interpolate(method="linear")
    return out


def transform_rocio(df: pd.DataFrame, col_rocio: str = "rocio_medio", col_temp: str = "temperatura_media") -> pd.DataFrame:
    """
    Rocío: imputar desde temperatura usando diferencia promedio global |T - Td|.
    Luego interpolación lineal si quedara rezago.
    """
    out = df.copy()
    if col_rocio not in out.columns or col_temp not in out.columns:
        return out

    mask_rt = out[col_rocio].notna() & out[col_temp].notna()
    if mask_rt.any():
        diff_rt = (out.loc[mask_rt, col_temp] - out.loc[mask_rt, col_rocio]).abs().mean()
    else:
        diff_rt = 0.0

    mask_imp = out[col_rocio].isna() & out[col_temp].notna()
    out.loc[mask_imp, col_rocio] = out.loc[mask_imp, col_temp] - diff_rt
    out[col_rocio] = out[col_rocio].interpolate(method="linear")
    return out


def transform_tension_vapor(df: pd.DataFrame, col_tv: str = "tesion_vapor_media",
                            col_temp: str = "temperatura_media", col_rh: str = "humedad_media") -> pd.DataFrame:
    """
    Tensión de vapor: derivada física desde temperatura y humedad relativa.
      e = (RH/100) * e_s(T)
      e_s(T) = 6.11 * exp(17.27*T/(T+237.3))
    """
    out = df.copy()
    if not {col_tv, col_temp, col_rh}.issubset(out.columns):
        return out

    def tension_vapor(temp: pd.Series, rh: pd.Series) -> pd.Series:
        return (rh / 100.0) * (6.11 * np.exp((17.27 * temp) / (temp + 237.3)))

    mask = out[col_tv].isna() & out[col_temp].notna() & out[col_rh].notna()
    if mask.any():
        out.loc[mask, col_tv] = tension_vapor(out.loc[mask, col_temp], out.loc[mask, col_rh])
    return out


def transform_radiacion_global(df: pd.DataFrame,
                               col_rad: str = "radiacion_global",
                               col_helio: str = "heliofania_efectiva",
                               col_fecha: str = "fecha",
                               day_hours: range = DAY_HOURS,
                               rad_max_fisico: Optional[float] = RAD_MAX_FISICO,
                               min_reg_samples: int = MIN_REG_SAMPLES) -> pd.DataFrame:
    """
    Radiación global (versión EDA sin agrupar por estación):
      1) Regresión lineal simple (heliofania -> radiación) SOLO horario diurno.
      2) Mediana por (mes, hora) SOLO horario diurno.
      3) Mediana móvil centrada SOLO horario diurno.
      - No se aplica 'cero final'.
      - Los valores nocturnos se respetan (0 puede ser real).
    """
    out = df.copy()
    if not {col_rad, col_helio, col_fecha}.issubset(out.columns):
        return out

    out[col_fecha] = pd.to_datetime(out[col_fecha], errors="coerce")
    out.sort_values(col_fecha, inplace=True)
    out["_hora"] = out[col_fecha].dt.hour
    out["_mes"] = out[col_fecha].dt.month

    day_mask = out["_hora"].isin(day_hours)
    cero_sospechoso = (out[col_rad] == 0) & day_mask
    faltante = out[col_rad].isna() | cero_sospechoso

    # 1) Regresión global en diurno
    can_train = day_mask & out[col_rad].notna() & (out[col_rad] > 0) & out[col_helio].notna()
    can_predict = day_mask & faltante & out[col_helio].notna()
    if can_train.sum() >= min_reg_samples and can_predict.any():
        X = out.loc[can_train, [col_helio]].to_numpy()
        y = out.loc[can_train, col_rad].to_numpy()
        reg = LinearRegression().fit(X, y)
        yhat = reg.predict(out.loc[can_predict, [col_helio]].to_numpy())
        if rad_max_fisico is not None:
            yhat = np.clip(yhat, 0, rad_max_fisico)
        else:
            yhat = np.clip(yhat, 0, None)
        out.loc[can_predict, col_rad] = yhat

    # 2) Mediana (mes, hora) en diurno
    faltante = (out[col_rad].isna() | ((out[col_rad] == 0) & day_mask)) & day_mask
    valid_diurno = day_mask & out[col_rad].notna() & (out[col_rad] > 0)
    med_map = (
        out.loc[valid_diurno]
           .groupby(["_mes", "_hora"])[col_rad]
           .median()
    )

    if faltante.any() and len(med_map) > 0:
        def fill_mes_hora(row):
            return med_map.get((row["_mes"], row["_hora"]), np.nan)
        to_fill = out.loc[faltante].apply(fill_mes_hora, axis=1)
        idx_ok = to_fill.index[to_fill.notna()]
        vals = to_fill.loc[idx_ok].values
        if rad_max_fisico is not None:
            vals = np.clip(vals, 0, rad_max_fisico)
        out.loc[idx_ok, col_rad] = vals

    # 3) Mediana móvil centrada (diurno)
    faltante = (out[col_rad].isna() | ((out[col_rad] == 0) & day_mask)) & day_mask
    if faltante.any():
        serie = out[col_rad].copy()
        serie.loc[(serie == 0) & day_mask] = np.nan
        rolling_med = serie.rolling(window=7, min_periods=1, center=True).median()
        idx_fill = faltante & rolling_med.notna()
        vals = rolling_med.loc[idx_fill].values
        if rad_max_fisico is not None:
            vals = np.clip(vals, 0, rad_max_fisico)
        out.loc[idx_fill, col_rad] = vals

    # saneo final solo diurno
    if rad_max_fisico is not None:
        out.loc[day_mask, col_rad] = out.loc[day_mask, col_rad].clip(lower=0, upper=rad_max_fisico)
    else:
        out.loc[day_mask, col_rad] = out.loc[day_mask, col_rad].clip(lower=0)

    out.drop(columns=["_hora", "_mes"], inplace=True, errors="ignore")
    return out


def transform_heliofania_cruzada(df: pd.DataFrame,
                                 col_eff: str = "heliofania_efectiva",
                                 col_rel: str = "heliofania_relativa",
                                 min_reg_samples: int = MIN_REG_SAMPLES) -> pd.DataFrame:
    """
    Imputaciones cruzadas:
      - Imputa heliofania_efectiva usando regresión con heliofania_relativa.
      - Imputa heliofania_relativa usando regresión con heliofania_efectiva.
      - Luego interpolación lineal.
    """
    out = df.copy()
    if not {col_eff, col_rel}.issubset(out.columns):
        return out

    # a) efectiva ~ relativa
    mask_valid = out[col_eff].notna() & out[col_rel].notna()
    mask_null = out[col_eff].isna() & out[col_rel].notna()
    if mask_valid.sum() >= min_reg_samples and mask_null.any():
        X = out.loc[mask_valid, [col_rel]].to_numpy()
        y = out.loc[mask_valid, col_eff].to_numpy()
        reg = LinearRegression().fit(X, y)
        out.loc[mask_null, col_eff] = reg.predict(out.loc[mask_null, [col_rel]].to_numpy())

    # b) relativa ~ efectiva
    mask_valid = out[col_rel].notna() & out[col_eff].notna()
    mask_null = out[col_rel].isna() & out[col_eff].notna()
    if mask_valid.sum() >= min_reg_samples and mask_null.any():
        X = out.loc[mask_valid, [col_eff]].to_numpy()
        y = out.loc[mask_valid, col_rel].to_numpy()
        reg = LinearRegression().fit(X, y)
        out.loc[mask_null, col_rel] = reg.predict(out.loc[mask_null, [col_eff]].to_numpy())

    # interpolación lineal de rezagos
    out[col_eff] = out[col_eff].interpolate(method="linear")
    out[col_rel] = out[col_rel].interpolate(method="linear")
    return out


# =============================================================================
# Pipeline principal
# =============================================================================

def run_eda_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta todo el pipeline EDA de transformaciones sin gráficos."""
    df0 = normalize_columns(df)
    df1 = select_and_rename(df0)
    df2 = fix_types_and_duplicates(df1)

    df3 = transform_precipitacion(df2)
    df4 = transform_temperaturas(df3)
    df5 = transform_humedad(df4)
    df6 = transform_rocio(df5)
    df7 = transform_tension_vapor(df6)
    df8 = transform_radiacion_global(df7)
    df9 = transform_heliofania_cruzada(df8)

    return df9


# =============================================================================
# Main (ejemplo de uso)
# =============================================================================

def main(input_path: str,
         output_path: Optional[str] = None) -> pd.DataFrame:
    """
    Carga el dataset, aplica transformaciones EDA y opcionalmente guarda salida.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"No existe el archivo de entrada: {input_path}")

    df_in = pd.read_parquet(input_path) if input_path.lower().endswith(".parquet") else pd.read_csv(input_path)
    df_out = run_eda_transformations(df_in)

    if output_path:
        if output_path.lower().endswith(".parquet"):
            df_out.to_parquet(output_path, index=False)
        else:
            df_out.to_csv(output_path, index=False)
        print(f"✅ Transformaciones EDA guardadas en: {output_path}")

    return df_out