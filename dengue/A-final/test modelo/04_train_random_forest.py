#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrena Random Forest para predecir casos t+1 por id_uta
- Lee data/features.parquet
- Selecciona hiperparámetros sencillos (grid chico)
- Entrena en train, selecciona por val, reentrena en train+val
- Guarda models/random_forest.pkl y models/feature_columns.json
- Reporta métricas en val y test a reports/rf_metrics.json
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


def train_and_select(X_tr, y_tr, X_val, y_val) -> tuple[RandomForestRegressor, dict]:
	grid = [
		{"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 20, "max_features": "sqrt"},
		{"n_estimators": 300, "max_depth": 14, "min_samples_leaf": 30, "max_features": 0.5},
		{"n_estimators": 400, "max_depth": 16, "min_samples_leaf": 40, "max_features": 0.7},
	]
	best = None
	best_metrics = {"val_mae": np.inf}
	for params in grid:
		rf = RandomForestRegressor(random_state=42, n_jobs=-1, **params)
		rf.fit(X_tr, y_tr)
		pred_val = rf.predict(X_val)
		mae_val = mean_absolute_error(y_val, pred_val)
		rmsle_val = rmsle(y_val, pred_val)
		if mae_val < best_metrics["val_mae"]:
			best = rf
			best_metrics = {"val_mae": float(mae_val), "val_rmsle": float(rmsle_val), "params": params}
	return best, best_metrics


def main() -> None:
	paths = resolve_paths()
	df = pd.read_parquet(paths["feat"])
	# Splits
	train_df = df[df["split"] == "train"].copy()
	val_df = df[df["split"] == "val"].copy()
	test_df = df[df["split"] == "test"].copy()

	X_tr, y_tr = train_df[FEATURES], train_df[TARGET]
	X_val, y_val = val_df[FEATURES], val_df[TARGET]
	X_tv = pd.concat([X_tr, X_val], axis=0)
	y_tv = pd.concat([y_tr, y_val], axis=0)
	X_test, y_test = test_df[FEATURES], test_df[TARGET]

	# Selección de modelo por validación
	model, val_metrics = train_and_select(X_tr, y_tr, X_val, y_val)

	# Reentrenar en train+val con los mejores parámetros
	best_params = val_metrics["params"]
	final_model = RandomForestRegressor(random_state=42, n_jobs=-1, **best_params)
	final_model.fit(X_tv, y_tv)

	# Evaluación final
	pred_val = model.predict(X_val)
	pred_test = final_model.predict(X_test)
	metrics = {
		"val": {"mae": float(mean_absolute_error(y_val, pred_val)), "rmsle": rmsle(y_val, pred_val)},
		"test": {"mae": float(mean_absolute_error(y_test, pred_test)), "rmsle": rmsle(y_test, pred_test)},
		"best_params": best_params,
	}

	# Persistencia
	joblib.dump(final_model, paths["models"] / "random_forest.pkl")
	with open(paths["models"] / "feature_columns.json", "w", encoding="utf-8") as f:
		json.dump({"features": FEATURES, "target": TARGET}, f, ensure_ascii=False, indent=2)
	with open(paths["reports"] / "rf_metrics.json", "w", encoding="utf-8") as f:
		json.dump(metrics, f, ensure_ascii=False, indent=2)

	print("Modelo RF guardado.")
	print(metrics)


if __name__ == "__main__":
	main()
