#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajuste pequeño de Random Forest (grid acotado)
- Lee data/features.parquet
- Busca en una grilla chica (rápida) usando validación 2024
- Reentrena mejor config en train+val
- Guarda models/random_forest.pkl (sobrescribe) y reports/rf_metrics.json
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

FEATURES = [
	"semana", "poblacion", "sin_semana", "cos_semana",
	"lag_1", "lag_2", "lag_3", "lag_4", "lag_8", "lag_12",
	"ma_2", "ma_4", "ma_8",
	"prov_spill_lag1",
]
TARGET = "target_t1"


def rmsle(y_true, y_pred) -> float:
	y_true = np.asarray(y_true)
	y_pred = np.asarray(y_pred)
	y_true_clip = np.clip(y_true, a_min=0, a_max=None)
	y_pred_clip = np.clip(y_pred, a_min=0, a_max=None)
	return float(np.sqrt(np.mean((np.log1p(y_pred_clip) - np.log1p(y_true_clip)) ** 2)))


def resolve_paths() -> dict:
	base_dir = Path(__file__).resolve().parent
	feat_path = (base_dir / "data" / "features.parquet").resolve()
	models_dir = (base_dir / "models").resolve()
	reports_dir = (base_dir / "reports").resolve()
	models_dir.mkdir(parents=True, exist_ok=True)
	reports_dir.mkdir(parents=True, exist_ok=True)
	return {"feat": feat_path, "models": models_dir, "reports": reports_dir}


def main() -> None:
	paths = resolve_paths()
	print("[RF-TUNE] Cargando features...")
	df = pd.read_parquet(paths["feat"])
	train_df = df[df["split"] == "train"].copy()
	val_df = df[df["split"] == "val"].copy()
	test_df = df[df["split"] == "test"].copy()

	X_tr, y_tr = train_df[FEATURES], train_df[TARGET]
	X_val, y_val = val_df[FEATURES], val_df[TARGET]
	X_tv = pd.concat([X_tr, X_val], axis=0)
	y_tv = pd.concat([y_tr, y_val], axis=0)
	X_test, y_test = test_df[FEATURES], test_df[TARGET]

	grid = [
		{"n_estimators": 300, "max_depth": 14, "min_samples_leaf": 30, "max_features": "sqrt"},
		{"n_estimators": 400, "max_depth": 16, "min_samples_leaf": 20, "max_features": 0.7},
		{"n_estimators": 500, "max_depth": 18, "min_samples_leaf": 20, "max_features": 0.5},
	]
	best = None
	best_metrics = {"val_mae": np.inf}
	print("[RF-TUNE] Probando configuraciones...")
	for i, params in enumerate(grid, start=1):
		print(f"  ({i}/{len(grid)}) {params}")
		rf = RandomForestRegressor(random_state=42, n_jobs=-1, **params)
		rf.fit(X_tr, y_tr)
		pv = rf.predict(X_val)
		mae_val = float(mean_absolute_error(y_val, pv))
		rmsle_val = rmsle(y_val, pv)
		print(f"     -> val MAE={mae_val:.4f} RMSLE={rmsle_val:.4f}")
		if mae_val < best_metrics["val_mae"]:
			best = rf
			best_metrics = {"val_mae": mae_val, "val_rmsle": rmsle_val, "params": params}

	print("[RF-TUNE] Mejor config:", best_metrics)
	best_params = best_metrics["params"]

	print("[RF-TUNE] Reentrenando en train+val con mejor config...")
	final_model = RandomForestRegressor(random_state=42, n_jobs=-1, **best_params)
	final_model.fit(X_tv, y_tv)
	pred_test = final_model.predict(X_test)
	test_mae = float(mean_absolute_error(y_test, pred_test))
	test_rmsle = rmsle(y_test, pred_test)
	metrics = {
		"val": {"mae": best_metrics["val_mae"], "rmsle": best_metrics["val_rmsle"]},
		"test": {"mae": test_mae, "rmsle": test_rmsle},
		"best_params": best_params,
	}

	print("[RF-TUNE] Guardando artefactos...")
	joblib.dump(final_model, paths["models"] / "random_forest.pkl")
	with open(paths["models"] / "feature_columns.json", "w", encoding="utf-8") as f:
		json.dump({"features": FEATURES, "target": TARGET}, f, ensure_ascii=False, indent=2)
	with open(paths["reports"] / "rf_metrics.json", "w", encoding="utf-8") as f:
		json.dump(metrics, f, ensure_ascii=False, indent=2)
	print("[RF-TUNE] Listo.")


if __name__ == "__main__":
	main()
