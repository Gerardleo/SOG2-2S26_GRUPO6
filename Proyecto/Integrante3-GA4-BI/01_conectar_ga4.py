# Script para conectar el ID de medicion de GA4 con el sitio web de Odoo

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Integrante2-Tienda-CRM-Marketing"))
from common import conectar


def main():
    ap = argparse.ArgumentParser(description="Conectar GA4 con Odoo")
    ap.add_argument("--id", required=True, help="ID de medicion G-XXXXXXXXXX")
    ap.add_argument(
        "--sin-banner-cookies",
        action="store_true",
        help="Desactiva el banner de cookies",
    )
    args = ap.parse_args()

    if not re.fullmatch(r"G-[A-Z0-9]{6,}", args.id):
        sys.exit("[ERROR] ID invalido, debe iniciar con G-")

    odoo, _ = conectar()
    sitios = odoo.search_read("website", [], ["name", "domain", "google_analytics_key", "cookies_bar"])
    if not sitios:
        sys.exit("[ERROR] No se encontraron sitios web en Odoo")

    for s in sitios:
        vals = {"google_analytics_key": args.id}
        if args.sin_banner_cookies:
            vals["cookies_bar"] = False
        odoo.write("website", [s["id"]], vals)
        nuevo = odoo.read("website", [s["id"]], ["google_analytics_key", "cookies_bar"])[0]
        print(f"[+] Sitio '{s['name']}' (id {s['id']}): GA key = {nuevo['google_analytics_key']}, cookies = {nuevo['cookies_bar']}")

    print("[OK] GA4 configurado en el sitio.")


if __name__ == "__main__":
    main()
