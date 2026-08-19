"Subida de datos a Supabase"
from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FILE = ROOT / "sql" / "01_tablas.sql"
DATA_DIR = ROOT / "salida" / "normalizado"
ENV_FILE = ROOT / ".env"
IMPORTS = [
    ("clientes", "id_cliente, edad, id_genero"),
    ("preferencias_cliente", "id_cliente, recibe_boletin, utiliza_vale"),
    ("resumen_cliente_anual", "id_cliente, n_compras, venta_total"),
    ("compras_registradas", "id_cliente, fecha_compra, monto_compra, id_metodo_pago, id_canal, tiempo"),
]


def cargar_archivo_env(path: Path) -> None:
    """Carga variables simples KEY=VALUE sin reemplazar las del sistema."""
    if not path.exists():
        return
    for linea in path.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def main() -> None:
    cargar_archivo_env(ENV_FILE)
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("Falta DATABASE_URL. Agreguela al archivo .env en la raiz del proyecto.")

    try:
        import psycopg
    except ModuleNotFoundError as error:
        raise SystemExit("Instale dependencias: python -m pip install -r requirements.txt") from error

    # prepare_threshold=None evita prepared statements incompatibles con
    # el pooler de transacciones de Supabase.
    try:
        connection = psycopg.connect(database_url, prepare_threshold=None)
    except psycopg.OperationalError as error:
        if "failed to resolve host" in str(error):
            raise SystemExit(
                "No se pudo resolver el host. En Supabase > Connect copie la cadena "
                "Session pooler (no la conexion directa db.*.supabase.co) y actualice DATABASE_URL en .env."
            ) from error
        raise

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_FILE.read_text(encoding="utf-8"))

            for table, columns in IMPORTS:
                file_path = DATA_DIR / f"{table}.csv"
                if not file_path.exists():
                    raise FileNotFoundError(f"No existe {file_path}")
                copy_sql = f"COPY {table} ({columns}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
                with cursor.copy(copy_sql) as copy, file_path.open("r", encoding="utf-8") as source:
                    while chunk := source.read(1024 * 1024):
                        copy.write(chunk)

            cursor.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM clientes), "
                "(SELECT COUNT(*) FROM compras_registradas), "
                "(SELECT MIN(fecha_compra) FROM compras_registradas), "
                "(SELECT MAX(fecha_compra) FROM compras_registradas)"
            )
            clientes, compras, fecha_inicial, fecha_final = cursor.fetchone()

    print("Carga completada correctamente")
    print(f"Clientes: {clientes}")
    print(f"Compras registradas: {compras}")
    print(f"Rango de fechas: {fecha_inicial} a {fecha_final}")


if __name__ == "__main__":
    main()
