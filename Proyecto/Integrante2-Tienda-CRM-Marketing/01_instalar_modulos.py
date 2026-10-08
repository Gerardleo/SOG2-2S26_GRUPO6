"""
Paso 1 - Instala en Odoo los modulos de tienda en linea, CRM y email marketing.
Es idempotente: los modulos ya instalados se omiten.

Uso:  python 01_instalar_modulos.py
"""

import time
import xmlrpc.client

from common import conectar

MODULOS = [
    "website",
    "website_sale",            # tienda en linea (catalogo, carrito, checkout)
    "delivery",
    "website_sale_delivery",   # costos de envio en el carrito
    "payment_demo",            # proveedor de pago de demostracion (integracion de pago)
    "payment_custom",          # transferencia bancaria
    "crm",
    "website_crm",             # formulario de contacto -> lead en el CRM
    "mass_mailing",            # email marketing
    "website_mass_mailing",    # bloque de suscripcion en la web
    "base_automation",         # reglas automaticas (envio del correo de campana)
]


def estado(odoo, nombre):
    r = odoo.search_read("ir.module.module", [["name", "=", nombre]], ["state"])
    return r[0]["state"] if r else None


def main():
    odoo, _ = conectar()
    for nombre in MODULOS:
        st = estado(odoo, nombre)
        if st is None:
            print(f"[!] {nombre}: no existe en esta version de Odoo, se omite")
            continue
        if st == "installed":
            print(f"[=] {nombre}: ya instalado")
            continue
        print(f"[+] Instalando {nombre} (puede tardar varios minutos)...")
        mid = odoo.search("ir.module.module", [["name", "=", nombre]])
        try:
            odoo.call("ir.module.module", "button_immediate_install", mid)
        except (xmlrpc.client.ProtocolError, ConnectionError, OSError) as e:
            print(f"    (la conexion se cerro mientras Odoo recargaba: {e}); verificando estado...")
        for _ in range(60):
            try:
                st = estado(odoo, nombre)
                if st == "installed":
                    break
            except Exception:
                pass
            time.sleep(5)
        print(f"    -> {nombre}: {st}")

    print("\n[OK] Listo. Corre 00_diagnostico.py para confirmar.")


if __name__ == "__main__":
    main()
