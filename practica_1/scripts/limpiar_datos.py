"""Limpia, valida y normaliza el CSV de ventas para la práctica SOG2.

Entrada: data/Venta_online_c.csv
Salidas: salida/venta_online_limpio.csv, salida/reporte_calidad.json,
         salida/registros_descartados.csv y salida/normalizado/*.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "Venta_online_c.csv"
OUTPUT_DIR = ROOT / "salida"
SOURCE_COLUMNS = [
    "Id_cliente", "Edad", "Genero", "Venta_total", "N_Compras", "FechaCompra",
    "MontoCompra", "MetodoPago", "Tiempo", "Navegador", "Boletin", "Vale",
]
RENAME_COLUMNS = {
    "Id_cliente": "id_cliente", "Edad": "edad", "Genero": "genero",
    "Venta_total": "venta_total", "N_Compras": "n_compras",
    "FechaCompra": "fecha_compra", "MontoCompra": "monto_compra",
    "MetodoPago": "metodo_pago", "Tiempo": "tiempo",
    "Navegador": "navegador", "Boletin": "boletin", "Vale": "vale",
}
MAX_MUESTRA = 20


def mostrar_registros(titulo: str, registros: pd.DataFrame) -> None:
    print(f"\n{titulo}: {len(registros)}")
    if registros.empty:
        print("No se encontraron registros.")
    else:
        print(registros.head(MAX_MUESTRA).to_string(index=False))
        if len(registros) > MAX_MUESTRA:
            print(f"Se muestran los primeros {MAX_MUESTRA} registros.")


def crear_tablas_normalizadas(data: pd.DataFrame, output_dir: Path) -> None:
    normalizado = output_dir / "normalizado"
    normalizado.mkdir(parents=True, exist_ok=True)
    tablas = {
        "clientes": data[["id_cliente", "edad", "genero"]].rename(
            columns={"genero": "id_genero"}
        ),
        "preferencias_cliente": data[["id_cliente", "boletin", "vale"]].rename(
            columns={"boletin": "recibe_boletin", "vale": "utiliza_vale"}
        ),
        "resumen_cliente_anual": data[["id_cliente", "n_compras", "venta_total"]],
        "compras_registradas": data[
            ["id_cliente", "fecha_compra", "monto_compra", "metodo_pago", "navegador", "tiempo"]
        ].rename(columns={"metodo_pago": "id_metodo_pago", "navegador": "id_canal"}),
    }
    for nombre, tabla in tablas.items():
        tabla.to_csv(normalizado / f"{nombre}.csv", index=False, date_format="%Y-%m-%d")
        print(f"Generado: salida/normalizado/{nombre}.csv ({len(tabla)} filas)")


def main() -> None:
    if not INPUT_FILE.exists():
        raise SystemExit(f"No se encontro el archivo de entrada: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    original = pd.read_csv(INPUT_FILE, sep=";")
    if list(original.columns) != SOURCE_COLUMNS:
        raise ValueError(f"Las columnas no coinciden con las esperadas: {list(original.columns)}")

    print("=== DIAGNOSTICO DEL ARCHIVO ===")
    print(f"Archivo de entrada: {INPUT_FILE.relative_to(ROOT)}")
    print(f"Filas originales: {len(original)}")
    print(f"Columnas: {len(original.columns)}")
    print("\nTipos originales:")
    print(original.dtypes.to_string())
    print("\nValores faltantes por columna:")
    print(original.isna().sum().to_string())

    duplicados_exactos = original[original.duplicated(keep=False)]
    mostrar_registros("Filas duplicadas exactas", duplicados_exactos)
    sin_duplicados = original.drop_duplicates().copy()

    data = sin_duplicados.rename(columns=RENAME_COLUMNS).copy()
    columnas_numericas = ["id_cliente", "edad", "genero", "venta_total", "n_compras", "monto_compra", "metodo_pago", "tiempo", "navegador", "boletin", "vale"]
    for columna in columnas_numericas:
        data[columna] = pd.to_numeric(data[columna], errors="coerce")
    data["fecha_compra"] = pd.to_datetime(data["fecha_compra"], format="%d.%m.%y", errors="coerce")

    ids_duplicados = data[data.duplicated("id_cliente", keep=False)]
    mostrar_registros("Registros con id_cliente duplicado", ids_duplicados)

    reglas_invalidas = (
        data.isna().any(axis=1)
        | ~data["edad"].between(18, 79)
        | (data["venta_total"] < 0)
        | (data["n_compras"] <= 0)
        | (data["monto_compra"] < 0)
        | (data["tiempo"] < 0)
        | ~data["genero"].isin([0, 1])
        | ~data["metodo_pago"].isin([0, 1, 2])
        | ~data["navegador"].isin([0, 1, 2, 3, 4])
        | ~data["boletin"].isin([0, 1])
        | ~data["vale"].isin([0, 1])
    )
    invalidos = data[reglas_invalidas]
    mostrar_registros("Registros con valores faltantes o invalidos", invalidos)

    # Politica de limpieza: elimina duplicados exactos e invalidos. Si un
    # cliente se repite, conserva el primer registro valido para preservar la PK.
    limpio = data.loc[~reglas_invalidas].drop_duplicates("id_cliente", keep="first").copy()
    for columna in ["id_cliente", "edad", "genero", "n_compras", "metodo_pago", "tiempo", "navegador", "boletin", "vale"]:
        limpio[columna] = limpio[columna].astype("int64")

    descartados = pd.concat([ids_duplicados, invalidos]).drop_duplicates()
    limpio.to_csv(OUTPUT_DIR / "venta_online_limpio.csv", index=False, date_format="%Y-%m-%d")
    descartados.to_csv(OUTPUT_DIR / "registros_descartados.csv", index=False, date_format="%Y-%m-%d")

    estadisticas = limpio[["edad", "venta_total", "n_compras", "monto_compra", "tiempo"]].agg(["mean", "median", "min", "max"])
    modas = limpio[["edad", "venta_total", "n_compras", "monto_compra", "tiempo"]].mode().iloc[0]
    print("\n=== ESTADISTICAS BASICAS DEL ARCHIVO LIMPIO ===")
    print(estadisticas.to_string())
    print("\nModa:")
    print(modas.to_string())

    reporte = {
        "filas_originales": len(original),
        "filas_duplicadas_exactas_eliminadas": len(original) - len(sin_duplicados),
        "registros_id_cliente_duplicado": len(ids_duplicados),
        "registros_invalidos_descartados": len(invalidos),
        "filas_finales": len(limpio),
        "valores_faltantes_finales": int(limpio.isna().sum().sum()),
        "id_cliente_duplicados_finales": int(limpio.duplicated("id_cliente").sum()),
        "rango_fechas": {"minima": str(limpio["fecha_compra"].min().date()), "maxima": str(limpio["fecha_compra"].max().date())},
        "estadisticas_basicas": estadisticas.to_dict(),
        "moda": modas.to_dict(),
    }
    (OUTPUT_DIR / "reporte_calidad.json").write_text(json.dumps(reporte, indent=2, default=str), encoding="utf-8")
    crear_tablas_normalizadas(limpio, OUTPUT_DIR)

    print("\n=== RESULTADO FINAL ===")
    print(f"CSV limpio: salida/venta_online_limpio.csv ({len(limpio)} filas)")
    print("Reporte: salida/reporte_calidad.json")
    print("El CSV limpio y las tablas normalizadas estan listos para cargar a Supabase.")


if __name__ == "__main__":
    main()
