#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepara panel semanal de casos por id_uta (t=semana epidemiológica)
- Lee ../dengue-final.csv
- Agrega por id_uta-ano-semana sumando casos
- Completa semanas 1–52 por id_uta y año (faltantes a 0)
- Guarda data/panel.parquet
"""

from pathlib import Path
import pandas as pd
import numpy as np


def resolve_paths() -> dict:
	base_dir = Path(__file__).resolve().parent
	csv_path = (base_dir / ".." / "dengue-final.csv").resolve()
	out_dir = (base_dir / "data").resolve()
	out_dir.mkdir(parents=True, exist_ok=True)
	return {"base_dir": base_dir, "csv_path": csv_path, "out_dir": out_dir}


def load_raw(csv_path: Path) -> pd.DataFrame:
	df = pd.read_csv(csv_path)
	required = {"id_uta", "ano", "semanas_epidemiologicas", "cantidad_casos"}
	missing = required - set(df.columns)
	if missing:
		raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")
	return df


def build_weekly_panel(df: pd.DataFrame) -> pd.DataFrame:
	# Población (si existe): máximo por id_uta-año a partir del raw
	pop = None
	if "poblacion" in df.columns:
		pop = df.groupby(["id_uta", "ano"], as_index=False)["poblacion"].max()

	# Agregado semanal por id_uta
	agg = (
		df.groupby(["id_uta", "ano", "semanas_epidemiologicas"], as_index=False)["cantidad_casos"]
		.sum()
		.rename(columns={"semanas_epidemiologicas": "semana", "cantidad_casos": "casos"})
	)

	# Panel completo 1–52 por id_uta y año
	all_weeks = pd.MultiIndex.from_product(
		[
			sorted(agg["id_uta"].unique()),
			sorted(agg["ano"].unique()),
			list(range(1, 53)),
		],
		names=["id_uta", "ano", "semana"],
	)

	panel = agg.set_index(["id_uta", "ano", "semana"]).reindex(all_weeks).reset_index()

	# Merge de población si está disponible
	if pop is not None:
		panel = panel.merge(pop, on=["id_uta", "ano"], how="left")
	else:
		panel["poblacion"] = np.nan

	# Casos y población
	panel["casos"] = panel["casos"].fillna(0)
	if "poblacion" not in panel.columns:
		panel["poblacion"] = np.nan
	panel["poblacion"] = panel["poblacion"].fillna(1)

	# Orden final
	panel = panel[["id_uta", "ano", "semana", "poblacion", "casos"]].sort_values(["id_uta", "ano", "semana"]).reset_index(drop=True)
	return panel


def main() -> None:
	paths = resolve_paths()
	print(f"Leyendo: {paths['csv_path']}")
	df = load_raw(paths["csv_path"])
	print(f"Filas/columnas: {df.shape}")
	panel = build_weekly_panel(df)
	out_file = paths["out_dir"] / "panel.parquet"
	panel.to_parquet(out_file, index=False)
	print(f"Panel semanal guardado: {out_file} (filas={len(panel):,})")


if __name__ == "__main__":
	main()
