#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evalúa el modelo entrenado:
- Carga models/random_forest.pkl y data/features.parquet
- Calcula predicciones en VAL y TEST
- Reporta MAE/RMSLE global y por deciles de población
- (Opcional) Reporta por provincia si está disponible desde el CSV original
- Guarda reports/metrics_global.json y reports/metrics_by_pop_decile.csv
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib


def rmsle(y_true, y_pred) -> float:
	y_true = np.asarray(y_true)
	y_pred = np.asarray(y_pred)
	y_true_clip = np.clip(y_true, a_min=0, a_max=None)
	y_pred_clip = np.clip(y_pred, a_min=0, a_max=None)
	return float(np.sqrt(np.mean((np.log1p(y_pred_clip) - np.log1p(y_true_clip)) ** 2)))


def mae(y_true, y_pred) -> float:
	return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def resolve_paths() -> dict:
	base_dir = Path(__file__).resolve().parent
	feat = (base_dir / "data" / "features.parquet").resolve()
	model = (base_dir / "models" / "random_forest.pkl").resolve()
	feature_cols = (base_dir / "models" / "feature_columns.json").resolve()
	reports_dir = (base_dir / "reports").resolve()
	reports_dir.mkdir(parents=True, exist_ok=True)
	csv_raw = (base_dir / ".." / "dengue-final.csv").resolve()
	return {"feat": feat, "model": model, "feature_cols": feature_cols, "reports": reports_dir, "raw": csv_raw}


def try_load_province_map(raw_path: Path) -> pd.DataFrame | None:
	try:
		df_raw = pd.read_csv(raw_path, usecols=["id_uta", "provincia_nombre"])  # columnas presentes según dataset
		mp = df_raw.drop_duplicates("id_uta")
		return mp
	except Exception:
		return None


def main() -> None:
	paths = resolve_paths()
	feat = pd.read_parquet(paths["feat"]) 
	with open(paths["feature_cols"], "r", encoding="utf-8") as f:
		meta = json.load(f)
	features = meta["features"]
	model = joblib.load(paths["model"]) 

	out_global = {}
	out_by_decile = []
	for split in ["val", "test"]:
		df = feat[feat["split"] == split].copy()
		X = df[features]
		y = df["target_t1"].to_numpy()
		pred = model.predict(X)
		out_global[split] = {"mae": mae(y, pred), "rmsle": rmsle(y, pred)}

		# Por deciles de población
		df = df.copy()
		df["pred"] = pred
		df["decile"] = pd.qcut(df["poblacion"].rank(method="first"), 10, labels=False) + 1
		grp = df.groupby("decile").apply(lambda g: pd.Series({
			"mae": mae(g["target_t1"], g["pred"]),
			"rmsle": rmsle(g["target_t1"], g["pred"]),
			"count": int(len(g))
		})).reset_index()
		grp.insert(0, "split", split)
		out_by_decile.append(grp)

	# Guardar global
	with open(paths["reports"] / "metrics_global.json", "w", encoding="utf-8") as f:
		json.dump(out_global, f, ensure_ascii=False, indent=2)

	# Guardar por decil de población
	pd.concat(out_by_decile, ignore_index=True).to_csv(paths["reports"] / "metrics_by_pop_decile.csv", index=False, encoding="utf-8")

	# Si hay provincias disponibles, generar reporte adicional
	prov_map = try_load_province_map(paths["raw"]) 
	if prov_map is not None and "id_uta" in feat.columns:
		rows = []
		for split in ["val", "test"]:
			df = feat[feat["split"] == split].copy()
			X = df[features]
			y = df["target_t1"].to_numpy()
			pred = model.predict(X)
			df_local = df[["id_uta"]].copy()
			df_local["target_t1"] = y
			df_local["pred"] = pred
			df_local = df_local.merge(prov_map, on="id_uta", how="left")
			grp = df_local.groupby("provincia_nombre").apply(lambda g: pd.Series({
				"mae": mae(g["target_t1"], g["pred"]),
				"rmsle": rmsle(g["target_t1"], g["pred"]),
				"count": int(len(g))
			})).reset_index()
			grp.insert(0, "split", split)
			rows.append(grp)
		if rows:
			pd.concat(rows, ignore_index=True).to_csv(paths["reports"] / "metrics_by_province.csv", index=False, encoding="utf-8")

	print("Evaluación completada. Reportes en carpeta reports/.")


if __name__ == "__main__":
	main()
