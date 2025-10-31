#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrena y evalúa baselines: Naive (y_t-1) y Promedio Móvil (MA4)
- Lee data/features.parquet
- Calcula predicciones y métricas MAE/RMSLE en val y test
- Guarda reports/baselines_metrics.json
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd


def rmsle(y_true: np.ndarray, y_pred: np.ndarray) -> float:
	return float(np.sqrt(np.mean((np.log1p(y_pred.clip(min=0))) - np.log1p(y_true.clip(min=0))) ** 2))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
	return float(np.mean(np.abs(y_true - y_pred)))


def resolve_paths() -> dict:
	base_dir = Path(__file__).resolve().parent
	feat_path = (base_dir / "data" / "features.parquet").resolve()
	reports_dir = (base_dir / "reports").resolve()
	reports_dir.mkdir(parents=True, exist_ok=True)
	out_path = reports_dir / "baselines_metrics.json"
	return {"feat_path": feat_path, "out_path": out_path}


def evaluate_baselines(df: pd.DataFrame) -> dict:
	# Naive usa lag_1
	df_naive = df.dropna(subset=["lag_1", "target_t1"]).copy()
	y = df_naive["target_t1"].to_numpy()
	yhat_naive = df_naive["lag_1"].to_numpy()

	# MA4 usa ma_4
	df_ma4 = df.dropna(subset=["ma_4", "target_t1"]).copy()
	y2 = df_ma4["target_t1"].to_numpy()
	yhat_ma4 = df_ma4["ma_4"].to_numpy()

	def split_metrics(split: str) -> dict:
		m = {}
		mask_naive = df_naive["split"] == split
		mask_ma4 = df_ma4["split"] == split
		if mask_naive.any():
			m["naive_mae"] = mae(y[mask_naive], yhat_naive[mask_naive])
			m["naive_rmsle"] = rmsle(y[mask_naive], yhat_naive[mask_naive])
		if mask_ma4.any():
			m["ma4_mae"] = mae(y2[mask_ma4], yhat_ma4[mask_ma4])
			m["ma4_rmsle"] = rmsle(y2[mask_ma4], yhat_ma4[mask_ma4])
		return m

	return {"val": split_metrics("val"), "test": split_metrics("test")}


def main() -> None:
	paths = resolve_paths()
	df = pd.read_parquet(paths["feat_path"])
	metrics = evaluate_baselines(df)
	with open(paths["out_path"], "w", encoding="utf-8") as f:
		json.dump(metrics, f, ensure_ascii=False, indent=2)
	print(f"Baselines (val/test) guardados en: {paths['out_path']}")
	print(metrics)


if __name__ == "__main__":
	main()
