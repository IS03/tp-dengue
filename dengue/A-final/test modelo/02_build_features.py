#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera features para predicción t+1 por id_uta (Random Forest)
- Lee data/panel.parquet
- Crea estacionalidad (semana, sin/cos), lags (1,2,3,4,8,12), medias móviles (2,4,8)
- Agrega spillover provincial: total provincial (excl. propio) con lag 1
- Define splits temporales: train (<=2023), val (=2024), test (>=2025)
- Guarda data/features.parquet
"""

from pathlib import Path
import pandas as pd
import numpy as np


LAGS = [1, 2, 3, 4, 8, 12]
MAS = [2, 4, 8]


def resolve_paths() -> dict:
	base_dir = Path(__file__).resolve().parent
	panel_path = (base_dir / "data" / "panel.parquet").resolve()
	out_path = (base_dir / "data" / "features.parquet").resolve()
	raw_csv = (base_dir / ".." / "dengue-final.csv").resolve()
	return {"base_dir": base_dir, "panel_path": panel_path, "out_path": out_path, "raw": raw_csv}


def make_time_features(df: pd.DataFrame) -> pd.DataFrame:
	df["sin_semana"] = np.sin(2 * np.pi * df["semana"] / 52.0)
	df["cos_semana"] = np.cos(2 * np.pi * df["semana"] / 52.0)
	return df


def make_lags(df: pd.DataFrame) -> pd.DataFrame:
	df = df.sort_values(["id_uta", "ano", "semana"]).copy()
	for lag in LAGS:
		df[f"lag_{lag}"] = df.groupby("id_uta")["casos"].shift(lag)
	for w in MAS:
		# MA calculada sobre series desplazadas para evitar usar t en la ventana
		df[f"ma_{w}"] = (
			df.groupby("id_uta")["casos"].shift(1).rolling(w).mean().reset_index(level=0, drop=True)
		)
	return df


def add_spillover(df: pd.DataFrame, paths: dict) -> pd.DataFrame:
	# Mapear id_uta -> provincia desde el CSV original
	try:
		raw = pd.read_csv(paths["raw"], usecols=["id_uta", "provincia_nombre"]) 
		prov_map = raw.drop_duplicates("id_uta")
		df = df.merge(prov_map, on="id_uta", how="left")
		# Total provincial por (provincia, año, semana)
		total_prov = (
			df.groupby(["provincia_nombre", "ano", "semana"], as_index=False)["casos"].sum()
			.rename(columns={"casos": "prov_total"})
		)
		df = df.merge(total_prov, on=["provincia_nombre", "ano", "semana"], how="left")
		# Spillover = total provincia menos los casos del propio id_uta
		df["prov_spill"] = (df["prov_total"] - df["casos"]).clip(lower=0)
		# Lag 1 del spillover por id_uta
		df["prov_spill_lag1"] = df.groupby("id_uta")["prov_spill"].shift(1)
		# Limpieza
		df.drop(columns=["prov_total"], inplace=True)
	except Exception:
		# Si falla, dejar columna nula para que no rompa el pipeline
		df["prov_spill_lag1"] = np.nan
	return df


def add_split_labels(df: pd.DataFrame) -> pd.DataFrame:
	conditions = [df["ano"] <= 2023, df["ano"] == 2024, df["ano"] >= 2025]
	choices = ["train", "val", "test"]
	df["split"] = np.select(conditions, choices, default="train").astype(str)
	return df


def main() -> None:
	paths = resolve_paths()
	panel = pd.read_parquet(paths["panel_path"])
	# Features temporales y lags
	feat = make_time_features(panel.copy())
	feat = make_lags(feat)
	# Spillover provincial (lag)
	feat = add_spillover(feat, paths)
	# Objetivo t+1
	feat["target_t1"] = feat.groupby("id_uta")["casos"].shift(-1)
	# Splits temporales
	feat = add_split_labels(feat)
	# Filtrar filas con NaN en features críticas o en objetivo
	feature_cols = [
		"semana", "poblacion", "sin_semana", "cos_semana",
		*[f"lag_{l}" for l in LAGS], *[f"ma_{w}" for w in MAS],
		"prov_spill_lag1"
	]
	needed = feature_cols + ["target_t1", "split", "id_uta", "ano"]
	feat = feat[needed].dropna()
	feat.to_parquet(paths["out_path"], index=False)
	print(f"Features guardadas en: {paths['out_path']} (filas={len(feat):,})")


if __name__ == "__main__":
	main()
