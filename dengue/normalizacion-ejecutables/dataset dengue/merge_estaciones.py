import pandas as pd
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    dengue_csv = base_dir / "dengue" / "A-final" / "dengue-final.csv"
    depto_csv = base_dir / "estaciones" / "departamentos_con_estacion.csv"

    # Leer datos
    dengue = pd.read_csv(dengue_csv, dtype={"id_uta": "Int64"}, encoding="utf-8")
    deptos = pd.read_csv(
        depto_csv,
        dtype={"departamento_id": "string", "estacion_id_interno": "string"},
        encoding="utf-8",
    )

    # Normalizar departamento_id (coercer no numéricos a NaN y eliminar)
    before_rows = len(deptos)
    deptos["departamento_id"] = pd.to_numeric(deptos["departamento_id"].str.strip(), errors="coerce").astype("Int64")
    dropped_bad_ids = deptos["departamento_id"].isna().sum()
    if dropped_bad_ids:
        print(f"WARNING: Filas en mapping con departamento_id no numérico: {dropped_bad_ids} (se descartan)")
    deptos = deptos.dropna(subset=["departamento_id"]).copy()

    # Chequeos de duplicados en mapping
    dup_map = deptos.groupby("departamento_id")["estacion_id_interno"].nunique().reset_index()
    dup_map = dup_map[dup_map["estacion_id_interno"] > 1]

    if not dup_map.empty:
        print("WARNING: Existen departamento_id con múltiples estacion_id_interno:")
        print(dup_map.to_string(index=False))
    else:
        print("OK: No hay departamento_id con múltiples estacion_id_interno.")

    # Merge (left join)
    merged = dengue.merge(
        deptos[["departamento_id", "estacion_id_interno"]],
        how="left",
        left_on="id_uta",
        right_on="departamento_id",
    )

    # Contar sin match
    sin_match = merged["estacion_id_interno"].isna().sum()
    total = len(merged)
    print(f"Filas sin match: {sin_match} de {total}")

    # Dejar solo columnas originales + estacion_id_interno
    cols_originales = list(dengue.columns)
    resultado = merged[cols_originales + ["estacion_id_interno"]]

    # Sobrescribir archivo
    resultado.to_csv(dengue_csv, index=False, encoding="utf-8")
    print("Archivo sobrescrito: dengue-final.csv (con columna estacion_id_interno)")


if __name__ == "__main__":
    main()


