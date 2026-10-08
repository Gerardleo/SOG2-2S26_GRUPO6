"""
Paso 0 - Diagnostico (solo lectura). No modifica nada en Odoo.
Muestra version, moneda, modulos relevantes, impuestos, productos, facturas y proveedores de pago.

Uso:  python 00_diagnostico.py
"""

from common import conectar

MODULOS = [
    "website", "website_sale", "website_sale_delivery", "delivery", "crm", "website_crm",
    "mass_mailing", "website_mass_mailing", "payment_demo", "payment_custom", "base_automation",
]


def main():
    odoo, _ = conectar()

    cia = odoo.search_read("res.company", [], ["name", "email", "currency_id", "country_id"])[0]
    print(f"\nEmpresa: {cia['name']} | email: {cia['email']} | moneda: {cia['currency_id'][1]} | pais: {cia['country_id']}")

    print("\nModulos:")
    for m in odoo.search_read("ir.module.module", [["name", "in", MODULOS]], ["name", "state"]):
        print(f"  {m['name']:<24} {m['state']}")

    print("\nImpuestos de venta:")
    for t in odoo.search_read("account.tax", [["type_tax_use", "=", "sale"]], ["name", "amount", "price_include", "active"]):
        print(f"  [{t['id']}] {t['name']} {t['amount']}% incluido={t['price_include']} activo={t['active']}")

    n_prod = odoo.call("product.template", "search_count", [["sale_ok", "=", True], ["default_code", "like", "PROD-"]])
    print(f"\nProductos de venta (PROD-*): {n_prod}")
    if "website_published" in odoo.call("product.template", "fields_get", attributes=["type"]):
        pub = odoo.call("product.template", "search_count", [["website_published", "=", True]])
        print(f"Productos publicados en la web: {pub}")

    for estado in ("draft", "posted"):
        n = odoo.call("account.move", "search_count", [["move_type", "=", "out_invoice"], ["state", "=", estado]])
        print(f"Facturas de venta {estado}: {n}")
    n = odoo.call("account.move", "search_count", [["move_type", "=", "in_invoice"], ["state", "=", "posted"]])
    print(f"Facturas de compra posted: {n}")

    try:
        print("\nProveedores de pago:")
        for p in odoo.search_read("payment.provider", [], ["name", "code", "state"]):
            print(f"  [{p['id']}] {p['name']} code={p['code']} estado={p['state']}")
    except Exception:
        print("\nProveedores de pago: modulo de pagos aun no instalado")

    print("\nServidores de correo saliente:")
    for s in odoo.search_read("ir.mail_server", [], ["name", "smtp_host", "smtp_user"]):
        print(f"  [{s['id']}] {s['name']} {s['smtp_host']} {s['smtp_user']}")


if __name__ == "__main__":
    main()
