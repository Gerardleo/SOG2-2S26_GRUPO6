"""
Paso 9 - Toma automaticamente las capturas de pantalla para el Manual 1 (seccion Integrante 2).

Guarda PNG en  Proyecto/Manual1/imagenes/integrante2/
  * Paginas publicas (portada, tienda, producto, carrito): sin iniciar sesion
  * Paginas de administracion: inicia sesion con ODOO_USER / ODOO_PASSWORD de tu .env

Instalacion (una sola vez):
    pip install playwright
    playwright install chromium

Uso:  python 09_capturas_manual.py
No se capturan los correos de temp-mail: esas 3 capturas se toman a mano
(ver la lista al final del Manual1_Seccion_Integrante2.md).
"""

import sys

from common import BASE_DIR, cargar_env

SALIDA = BASE_DIR.parent / "Manual1" / "imagenes" / "integrante2"
VIEWPORT = {"width": 1440, "height": 900}

# (archivo, ruta de Odoo, nota)  -- rutas por modelo, funcionan sin conocer los ids de las acciones
ADMIN = [
    ("10-productos-catalogo", "/web#model=product.template&view_type=kanban"),
    ("11-metodos-envio", "/web#model=delivery.carrier&view_type=list"),
    ("12-proveedores-pago", "/web#model=payment.provider&view_type=kanban"),
    ("13-pedidos-venta", "/web#model=sale.order&view_type=list"),
    ("14-facturas", "/web#model=account.move&view_type=list"),
    ("15-servidor-correo", "/web#model=ir.mail_server&view_type=list"),
    ("16-correos-enviados", "/web#model=mail.mail&view_type=list"),
    ("17-plantillas-correo", "/web#model=mail.template&view_type=list"),
    ("18-regla-automatica", "/web#model=base.automation&view_type=list"),
    ("19-crm-embudo", "/web#model=crm.lead&view_type=kanban"),
    ("20-crm-lista", "/web#model=crm.lead&view_type=list"),
    ("21-contactos-clientes", "/web#model=res.partner&view_type=list"),
]


def esperar(page, ms=2500):
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(ms)


def foto(page, nombre, completa=False):
    ruta = SALIDA / f"{nombre}.png"
    page.screenshot(path=str(ruta), full_page=completa)
    print(f"  [+] {ruta.name}")


def publicas(browser, base):
    print("\nPaginas publicas...")
    ctx = browser.new_context(viewport=VIEWPORT)
    page = ctx.new_page()
    page.goto(f"{base}/")
    esperar(page)
    foto(page, "01-portada", completa=True)

    page.goto(f"{base}/shop")
    esperar(page)
    foto(page, "02-catalogo")

    enlace = page.locator("a[href^='/shop/']:has(img)").first
    if enlace.count():
        enlace.click()
        esperar(page)
        foto(page, "03-detalle-producto")
        boton = page.locator("#add_to_cart, a:has-text('Añadir al carrito'), a:has-text('Agregar al carrito')").first
        if boton.count():
            boton.click()
            esperar(page, 3000)
    page.goto(f"{base}/shop/cart")
    esperar(page)
    foto(page, "04-carrito")
    ctx.close()


def administracion(browser, base, env):
    print("\nAdministracion (con sesion)...")
    ctx = browser.new_context(viewport=VIEWPORT)
    page = ctx.new_page()
    page.goto(f"{base}/web/login")
    page.fill("input[name=login]", env["ODOO_USER"])
    page.fill("input[name=password]", env["ODOO_PASSWORD"])
    page.click("button[type=submit]")
    esperar(page, 4000)
    if "/login" in page.url:
        sys.exit("[ERROR] No se pudo iniciar sesion; revisa ODOO_USER / ODOO_PASSWORD en .env")

    for nombre, ruta in ADMIN:
        page.goto(f"{base}{ruta}")
        esperar(page)
        foto(page, nombre)

    # Detalle de la primera factura publicada y del primer pedido
    for nombre, ruta, filtro in [("22-detalle-factura", "/web#model=account.move&view_type=list", "INV/"),
                                 ("23-detalle-pedido", "/web#model=sale.order&view_type=list", "S0")]:
        page.goto(f"{base}{ruta}")
        esperar(page)
        fila = page.locator(f".o_data_row:has-text('{filtro}')").first
        if fila.count():
            fila.locator("td").nth(1).click()
            esperar(page, 3500)
            foto(page, nombre)
    ctx.close()


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("[ERROR] Falta playwright:  pip install playwright  y luego  playwright install chromium")
    env = cargar_env()
    if not env.get("ODOO_PASSWORD"):
        sys.exit("[ERROR] Llena ODOO_PASSWORD en .env")
    base = env["ODOO_URL"].rstrip("/")
    SALIDA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        publicas(browser, base)
        administracion(browser, base, env)
        browser.close()
    print(f"\n[OK] Capturas guardadas en {SALIDA}")


if __name__ == "__main__":
    main()
