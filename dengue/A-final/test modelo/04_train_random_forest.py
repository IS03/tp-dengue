#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrena Random Forest para predecir casos t+1 por id_uta (rápido)
- Lee data/features.parquet
- Entrena un único RF con configuración ligera
- Reentrena en train+val
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
	print("[RF] Cargando features...")
	df = pd.read_parquet(paths["feat"])
	train_df = df[df["split"] == "train"].copy()
	val_df = df[df["split"] == "val"].copy()
	test_df = df[df["split"] == "test"].copy()

	X_tr, y_tr = train_df[FEATURES], train_df[TARGET]
	X_val, y_val = val_df[FEATURES], val_df[TARGET]
	X_tv = pd.concat([X_tr, X_val], axis=0)
	y_tv = pd.concat([y_tr, y_val], axis=0)
	X_test, y_test = test_df[FEATURES], test_df[TARGET]

	# Configuración ligera para velocidad
	params = {"n_estimators": 200, "max_depth": 12, "min_samples_leaf": 40, "max_features": "sqrt", "random_state": 42, "n_jobs": -1}
	print("[RF] Entrenando en train...")
	model = RandomForestRegressor(**params)
	model.fit(X_tr, y_tr)
	pred_val = model.predict(X_val)
	val_mae = float(mean_absolute_error(y_val, pred_val))
	val_rmsle = rmsle(y_val, pred_val)
	print(f"[RF] Validación -> MAE={val_mae:.4f} RMSLE={val_rmsle:.4f}")

	print("[RF] Reentrenando en train+val...")
	final_model = RandomForestRegressor(**params)
	final_model.fit(X_tv, y_tv)
	pred_test = final_model.predict(X_test)
	test_mae = float(mean_absolute_error(y_test, pred_test))
	test_rmsle = rmsle(y_test, pred_test)
	metrics = {"val": {"mae": val_mae, "rmsle": val_rmsle}, "test": {"mae": test_mae, "rmsle": test_rmsle}, "params": params}

	print("[RF] Guardando artefactos...")
	joblib.dump(final_model, paths["models"] / "random_forest.pkl")
	with open(paths["models"] / "feature_columns.json", "w", encoding="utf-8") as f:
		json.dump({"features": FEATURES, "target": TARGET}, f, ensure_ascii=False, indent=2)
	with open(paths["reports"] / "rf_metrics.json", "w", encoding="utf-8") as f:
		json.dump(metrics, f, ensure_ascii=False, indent=2)
	print("[RF] Listo.")


if __name__ == "__main__":
	main()
