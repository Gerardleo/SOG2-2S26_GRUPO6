# Script para simular trafico y eventos en la tienda para Google Analytics 4

import argparse
import random
import re
import time
from urllib.parse import urlencode

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

FUENTES = [
    ("google", "organic", None, 25),
    ("(direct)", "(none)", None, 20),
    ("facebook", "social", "promo_octubre", 20),
    ("instagram", "social", "lacteos_2x1", 12),
    ("newsletter", "email", "gracias_por_tu_compra", 13),
    ("google", "cpc", "supermercado_gt", 10),
]

COMPORTAMIENTOS = [("navegar", 40), ("abandonar", 28), ("comprar", 22), ("contacto", 10)]
BUSQUEDAS = ["leche", "pan", "agua", "queso", "cafe", "jabon", "arroz", "galletas"]
NOMBRES = ["Ana", "Luis", "Maria", "Carlos", "Sofia", "Jorge", "Lucia", "Diego", "Valeria", "Pedro"]
APELLIDOS = ["Lopez", "Perez", "Garcia", "Morales", "Ramirez", "Castillo", "Mendez", "Cruz"]


def elegir(opciones):
    return random.choices([o[:-1] for o in opciones], weights=[o[-1] for o in opciones])[0]


def pausa(a=0.8, b=2.5):
    time.sleep(random.uniform(a, b))


def productos_de(page):
    hrefs = page.eval_on_selector_all("a[href]", "els => els.map(e => e.getAttribute('href'))")
    vistos = []
    for h in hrefs:
        if h and re.search(r"^/shop/[^/?#]+-\d+(\?|$)", h) and h not in vistos:
            vistos.append(h)
    return vistos


def agregar_al_carrito(page, base, cantidad):
    prods = productos_de(page)
    for href in random.sample(prods, min(cantidad, len(prods))):
        page.goto(base + href)
        pausa()
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        try:
            page.click("#add_to_cart, a#add_to_cart", timeout=6000)
            pausa(1.2, 2.5)
        except PWTimeout:
            pass
        if page.locator("#cart_products, .modal.show").count():
            page.keyboard.press("Escape")


def comprar(page, base):
    nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
    page.goto(base + "/shop/checkout?express=1")
    pausa()

    campos = {
        "name": nombre,
        "email": f"{nombre.lower().replace(' ', '.')}{random.randint(10, 999)}@example.com",
        "phone": f"{random.randint(2000, 5999)}{random.randint(1000, 9999)}",
        "street": f"{random.randint(1, 20)} avenida {random.randint(1, 30)}-{random.randint(1, 99)} zona {random.randint(1, 18)}",
        "city": "Ciudad de Guatemala",
        "zip": "01001",
    }
    for nom, val in campos.items():
        loc = page.locator(f"input[name='{nom}']")
        if loc.count():
            loc.first.fill(val)
    try:
        page.select_option("select[name='country_id']", label="Guatemala")
    except Exception:
        pass

    for _ in range(4):
        if "/shop/payment" in page.url:
            break
        boton = page.locator("a[name='website_sale_main_button'], a.a-submit:has-text('Continue'), a.a-submit:has-text('Continuar')")
        if not boton.count():
            break
        boton.first.click()
        page.wait_for_load_state("networkidle")
        pausa()

    if "/shop/payment" not in page.url:
        return False

    try:
        page.get_by_text(re.compile("demo", re.I)).first.click(timeout=4000)
    except PWTimeout:
        pass
    pausa()

    try:
        page.click("button[name='o_payment_submit_button']", timeout=6000)
        page.wait_for_url(re.compile("/shop/confirmation"), timeout=20000)
        pausa(2, 4)
        return True
    except PWTimeout:
        return False


def contacto(page, base):
    page.goto(base + "/contactus")
    pausa()
    nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
    datos = {
        "name": nombre,
        "phone": f"{random.randint(2000, 5999)}{random.randint(1000, 9999)}",
        "email_from": f"{nombre.lower().replace(' ', '.')}{random.randint(10, 999)}@example.com",
        "company": "Restaurante " + random.choice(APELLIDOS),
        "subject": random.choice(["Pedido mayorista", "Consulta de precios", "Entrega a domicilio"]),
        "description": "Hola, quisiera informacion sobre compras al por mayor. Gracias.",
    }
    for nom, val in datos.items():
        loc = page.locator(f"[name='{nom}']")
        if loc.count():
            loc.first.fill(val)
    try:
        page.click(".s_website_form_send, a.s_website_form_send", timeout=6000)
        page.wait_for_url(re.compile("contactus-thank-you"), timeout=15000)
        pausa(2, 3)
        return True
    except PWTimeout:
        return False


def sesion(pw, base, idx, visible):
    (src, med, camp), = [elegir(FUENTES)]
    movil = random.random() < 0.55
    comp, = elegir(COMPORTAMIENTOS)
    browser = pw.chromium.launch(headless=not visible)
    ctx = browser.new_context(**(pw.devices["iPhone 13"] if movil else {"viewport": {"width": 1366, "height": 768}}))
    page = ctx.new_page()
    page.set_default_timeout(15000)
    utm = {}
    if src != "(direct)":
        utm = {"utm_source": src, "utm_medium": med}
        if camp:
            utm["utm_campaign"] = camp
    print(f"[{idx}] {'movil' if movil else 'escritorio'} | {src}/{med} | {comp}")
    try:
        page.goto(base + "/" + ("?" + urlencode(utm) if utm else ""))
        pausa()
        page.goto(base + "/shop")
        pausa()
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        pausa()
        if random.random() < 0.4:
            page.goto(f"{base}/shop?{urlencode({'search': random.choice(BUSQUEDAS)})}")
            pausa()
        if comp == "navegar":
            for href in random.sample(productos_de(page) or [], min(random.randint(1, 4), len(productos_de(page)))):
                page.goto(base + href)
                pausa()
        elif comp == "abandonar":
            agregar_al_carrito(page, base, random.randint(1, 3))
            page.goto(base + "/shop/cart")
            pausa()
            if random.random() < 0.5:
                page.goto(base + "/shop/checkout?express=1")
                pausa()
        elif comp == "comprar":
            agregar_al_carrito(page, base, random.randint(1, 4))
            page.goto(base + "/shop/cart")
            pausa()
            print("    compra:", "OK" if comprar(page, base) else "FALLO")
        elif comp == "contacto":
            print("    formulario:", "OK" if contacto(page, base) else "FALLO")
    except Exception as e:
        print(f"    [!] Error en la sesion: {e}")
    finally:
        ctx.close()
        browser.close()


def main():
    ap = argparse.ArgumentParser(description="Generador de interacciones para GA4")
    ap.add_argument("--url", default="http://3.140.234.169:8069")
    ap.add_argument("--sesiones", type=int, default=60)
    ap.add_argument("--visible", action="store_true", help="Mostrar navegador")
    args = ap.parse_args()
    base = args.url.rstrip("/")
    with sync_playwright() as pw:
        for i in range(1, args.sesiones + 1):
            sesion(pw, base, i, args.visible)
    print("[OK] Sesiones finalizadas.")


if __name__ == "__main__":
    main()
