"""
Paso 2 - Configura la tienda en linea de QuetzalMart sobre Odoo.

  * Categorias de la tienda a partir de productos_venta.csv
  * Publica los 40 productos con imagen, descripcion y precio (imagenes generadas con Pillow)
  * Impuesto IVA 12% (se crea si no existe) asignado a los productos
  * Metodo de envio (tarifa fija, gratis sobre cierto monto)
  * Proveedores de pago: demo (integracion de pago) y transferencia bancaria
  * Facturacion automatica al pagar + registro libre de usuarios (portal)

Requiere:  pip install pillow
Uso:       python 02_configurar_tienda.py
"""

import base64
import csv
import io
import textwrap

from common import BASE_DIR, conectar

CSV_PRODUCTOS = BASE_DIR.parent / "Carga-de-Datos" / "productos_venta.csv"

COLORES = {
    "Alimentos": (214, 137, 16),
    "Lacteos": (41, 128, 185),
    "Bebidas": (22, 160, 133),
    "Carnes": (192, 57, 43),
    "Panaderia": (160, 100, 50),
    "Snacks": (230, 126, 34),
    "Cuidado": (142, 68, 173),
    "Limpieza": (39, 174, 96),
    "Hogar": (52, 73, 94),
}


def color_para(categoria):
    sin_tildes = categoria.lower().translate(str.maketrans("áéíóú", "aeiou"))
    for clave, color in COLORES.items():
        if clave.lower() in sin_tildes:
            return color
    return (44, 62, 80)


def generar_imagen(nombre, precio, categoria):
    """Tarjeta 800x800 con el nombre del producto (no hay fotos reales; sirve para el catalogo)."""
    from PIL import Image, ImageDraw, ImageFont

    color = color_para(categoria)
    img = Image.new("RGB", (800, 800), color)
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, 760, 760], outline=(255, 255, 255), width=6)

    def fuente(tam):
        for ruta in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
            try:
                return ImageFont.truetype(ruta, tam)
            except OSError:
                continue
        return ImageFont.load_default()

    d.text((400, 130), "QuetzalMart", fill=(255, 255, 255), font=fuente(48), anchor="mm")
    y = 330
    for linea in textwrap.wrap(nombre, 18):
        d.text((400, y), linea, fill=(255, 255, 255), font=fuente(64), anchor="mm")
        y += 80
    d.rounded_rectangle([250, 640, 550, 720], radius=30, fill=(255, 255, 255))
    d.text((400, 680), f"{precio:.2f}", fill=color, font=fuente(56), anchor="mm")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def grupo(fila):
    """Categoria principal de la tienda (primer nivel de 'Grupo / Subgrupo')."""
    return fila["Category"].split("/")[0].strip()


def categorias_tienda(odoo, filas):
    ids = {}
    for fila in filas:
        nombre = grupo(fila)
        if nombre in ids:
            continue
        existe = odoo.search("product.public.category", [["name", "=", nombre]], limit=1)
        ids[nombre] = existe[0] if existe else odoo.create("product.public.category", {"name": nombre})
    print(f"[+] Categorias de tienda: {', '.join(ids)}")
    return ids


def asegurar_iva(odoo):
    ya = odoo.search("account.tax", [["type_tax_use", "=", "sale"], ["amount", "=", 12]], limit=1)
    if ya:
        return ya[0]
    iva = odoo.create("account.tax", {
        "name": "IVA 12%", "amount": 12, "amount_type": "percent",
        "type_tax_use": "sale", "price_include": True,
    })
    print("[+] Impuesto IVA 12% creado")
    return iva


def publicar_productos(odoo, filas, cats, iva):
    print("\n[+] Publicando productos en la tienda...")
    ok = 0
    for fila in filas:
        tmpl = odoo.search_read("product.template", [["default_code", "=", fila["Internal Reference"]]],
                                ["id", "image_1920"], limit=1)
        if not tmpl:
            print(f"    [!] {fila['Internal Reference']} no existe en Odoo (corre la carga masiva primero)")
            continue
        categoria = grupo(fila)
        vals = {
            "website_published": True,
            "sale_ok": True,
            "public_categ_ids": [(6, 0, [cats[categoria]])],
            "description_ecommerce": f"<p>{fila['Sales Description']}</p>",
            "taxes_id": [(6, 0, [iva])],
        }
        if not tmpl[0]["image_1920"]:
            vals["image_1920"] = generar_imagen(fila["Name"], float(fila["Sales Price"]), categoria)
        try:
            odoo.write("product.template", [tmpl[0]["id"]], vals)
            ok += 1
        except Exception as e:
            print(f"    [!] {fila['Internal Reference']}: {e}")
    print(f"    {ok}/{len(filas)} productos publicados")

    # Limpia subcategorias sueltas creadas por una version anterior del script
    principales = set(cats)
    for fila in filas:
        sub = fila["Category"].split("/")[-1].strip()
        if sub not in principales:
            for cid in odoo.search("product.public.category", [["name", "=", sub]]):
                try:
                    odoo.call("product.public.category", "unlink", [cid])
                except Exception:
                    pass


def configurar_envio(odoo):
    print("\n[+] Metodo de envio...")
    if odoo.search("delivery.carrier", [["name", "=", "Envio estandar QuetzalMart"]]):
        print("    ya existe")
        return
    prod = odoo.create("product.product", {
        "name": "Envio a domicilio", "type": "service", "sale_ok": False, "purchase_ok": False, "list_price": 0,
    })
    odoo.create("delivery.carrier", {
        "name": "Envio estandar QuetzalMart",
        "delivery_type": "fixed",
        "fixed_price": 2.50,
        "free_over": True,
        "amount": 25.0,
        "product_id": prod,
        "is_published": True,
    })
    print("    creado: tarifa fija 2.50, gratis en compras mayores a 25")


def configurar_pagos(odoo):
    print("\n[+] Proveedores de pago...")
    for prov in odoo.search_read("payment.provider", [["code", "in", ["demo", "custom"]]], ["name", "code", "state"]):
        for estado in ("enabled", "test"):
            try:
                odoo.write("payment.provider", [prov["id"]], {"state": estado})
                break
            except Exception as e:
                ultimo = e
        else:
            print(f"    [!] {prov['name']}: {ultimo}")
            continue
        try:
            odoo.write("payment.provider", [prov["id"]], {"is_published": True})
        except Exception:
            pass
        print(f"    {prov['name']} ({prov['code']}) -> {estado}")


def configurar_parametros(odoo):
    print("\n[+] Facturacion automatica y registro de usuarios...")
    odoo.set_param("sale.automatic_invoice", "True")
    tmpl = odoo.ref("account.email_template_edi_invoice")
    if tmpl:
        odoo.set_param("sale.default_invoice_email_template", str(tmpl))
    odoo.set_param("auth_signup.invitation_scope", "b2c")  # cualquier visitante puede registrarse
    odoo.set_param("auth_signup.reset_password", "True")
    print("    factura automatica al pagar + registro libre (b2c) activados")
    try:  # que la tienda muestre el precio con IVA incluido (igual al de la imagen y al de Odoo)
        odoo.write("website", odoo.search("website", []), {"show_line_subtotals_tax_selection": "tax_included"})
        print("    precios de la tienda mostrados con IVA incluido")
    except Exception as e:
        print(f"    [!] No pude cambiar la vista de precios ({str(e)[:80]}); hazlo en Sitio web > Configuracion > Ajustes > Precios de tienda")


def main():
    odoo, _ = conectar()
    with open(CSV_PRODUCTOS, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    cats = categorias_tienda(odoo, filas)
    iva = asegurar_iva(odoo)
    publicar_productos(odoo, filas, cats, iva)
    configurar_envio(odoo)
    configurar_pagos(odoo)
    configurar_parametros(odoo)
    print("\n[OK] Tienda configurada. Revisa  http://<IP>:8069/shop")


if __name__ == "__main__":
    main()
