"""
Paso 5 - Genera la carpeta con las facturas en PDF (minimo 50) desde Odoo.

Las facturas que crea la carga masiva quedan en BORRADOR; un borrador no tiene numero
y el PDF dice "Factura borrador". Con --publicar-borradores se publican (action_post)
las que hagan falta para llegar a --cantidad. Sin esa bandera no se modifica nada.

  python 05_exportar_facturas_pdf.py                         # solo exporta las ya publicadas
  python 05_exportar_facturas_pdf.py --publicar-borradores   # publica borradores si faltan
  python 05_exportar_facturas_pdf.py --cantidad 60

Salida: Proyecto/Facturas-PDF/Factura_<numero>.pdf
"""

import argparse
import json
import re
import urllib.request
from http.cookiejar import CookieJar

from common import BASE_DIR, conectar

SALIDA = BASE_DIR.parent / "Facturas-PDF"


def abrir_sesion_web(url, db, user, password):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    cuerpo = json.dumps({"jsonrpc": "2.0", "method": "call",
                         "params": {"db": db, "login": user, "password": password}}).encode()
    req = urllib.request.Request(f"{url}/web/session/authenticate", cuerpo, {"Content-Type": "application/json"})
    resp = json.load(opener.open(req, timeout=60))
    if not resp.get("result", {}).get("uid"):
        raise SystemExit("[ERROR] No se pudo abrir sesion web para descargar los PDF")
    return opener


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cantidad", type=int, default=55, help="facturas a exportar (default 55, minimo pedido 50)")
    ap.add_argument("--publicar-borradores", action="store_true")
    args = ap.parse_args()

    odoo, env = conectar()
    dominio = [["move_type", "=", "out_invoice"], ["state", "=", "posted"]]
    publicadas = odoo.search("account.move", dominio, order="id")
    print(f"[=] Facturas de venta publicadas: {len(publicadas)}")

    if len(publicadas) < args.cantidad:
        faltan = args.cantidad - len(publicadas)
        borradores = odoo.search("account.move", [["move_type", "=", "out_invoice"], ["state", "=", "draft"]],
                                 order="id", limit=faltan)
        if borradores and args.publicar_borradores:
            print(f"[+] Publicando {len(borradores)} facturas en borrador...")
            for bid in borradores:
                try:
                    odoo.call("account.move", "action_post", [bid])
                except Exception as e:
                    print(f"    [!] factura {bid}: {str(e)[:120]}")
            publicadas = odoo.search("account.move", dominio, order="id")
        elif borradores:
            print(f"[!] Hay {len(borradores)} borradores utilizables; repite con --publicar-borradores")

    if len(publicadas) < 50:
        print(f"[!] Solo hay {len(publicadas)} facturas publicadas, el requisito es 50.")

    SALIDA.mkdir(parents=True, exist_ok=True)
    opener = abrir_sesion_web(odoo.url, odoo.db, odoo.user, odoo.password)
    guardadas = 0
    for fac in odoo.read("account.move", publicadas[:args.cantidad], ["name"]):
        nombre = re.sub(r"[^A-Za-z0-9_-]", "_", fac["name"])
        ruta = SALIDA / f"Factura_{nombre}.pdf"
        try:
            datos = opener.open(f"{odoo.url}/report/pdf/account.report_invoice/{fac['id']}", timeout=120).read()
        except Exception as e:
            print(f"    [!] {fac['name']}: {e}")
            continue
        if not datos.startswith(b"%PDF"):
            print(f"    [!] {fac['name']}: la respuesta no es un PDF")
            continue
        ruta.write_bytes(datos)
        guardadas += 1
    print(f"\n[OK] {guardadas} PDF guardados en {SALIDA}")


if __name__ == "__main__":
    main()
