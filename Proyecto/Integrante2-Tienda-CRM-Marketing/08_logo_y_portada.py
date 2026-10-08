"""
Paso 8 - Logo y portada de QuetzalMart.

  * Genera un logo (PNG) y lo pone en la tienda y en las facturas/correos (empresa)
  * Reemplaza la portada generica de Odoo por una portada de QuetzalMart
    (guarda una copia de la original en portada_original.json)

  python 08_logo_y_portada.py              # aplica
  python 08_logo_y_portada.py --restaurar  # vuelve a la portada original

Requiere:  pip install pillow
Despues puedes seguir editando todo desde Sitio web > Editar.
"""

import argparse
import base64
import io
import json

from common import BASE_DIR, conectar

BACKUP = BASE_DIR / "portada_original.json"


def generar_logo():
    from PIL import Image, ImageDraw, ImageFont

    def fuente(tam):
        for ruta in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(ruta, tam)
            except OSError:
                continue
        return ImageFont.load_default()

    img = Image.new("RGBA", (900, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 899, 259], radius=50, fill=(230, 126, 34, 255))
    d.ellipse([40, 55, 170, 185], fill=(255, 255, 255, 255))
    d.text((105, 120), "Q", fill=(192, 57, 43, 255), font=fuente(100), anchor="mm")
    d.text((200, 105), "QuetzalMart", fill=(255, 255, 255, 255), font=fuente(100), anchor="lm")
    d.text((205, 195), "Calidad a precios accesibles", fill=(255, 245, 230, 255), font=fuente(38), anchor="lm")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def arch_portada(categorias):
    tarjetas = ""
    for nombre, cid, emoji, color in categorias:
        tarjetas += f"""
          <div class="col-6 col-md-4 col-lg-3 mb-4">
            <a href="/shop/category/{cid}" class="text-decoration-none">
              <div class="rounded-4 text-white text-center p-4 h-100" style="background:{color};">
                <div style="font-size:44px;line-height:52px;">{emoji}</div>
                <div class="fw-bold fs-5 mt-2">{nombre}</div>
              </div>
            </a>
          </div>"""
    return f"""<t name="Home" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure oe_empty">
      <section class="text-white text-center" style="background:linear-gradient(135deg,#e67e22,#c0392b);padding:90px 0;">
        <div class="container">
          <div style="letter-spacing:4px;">TU SUPERMERCADO EN LINEA</div>
          <h1 class="display-3 fw-bold my-3">QuetzalMart</h1>
          <p class="lead mb-4">Alimentos, bebidas y todo para tu hogar a precios accesibles.<br/>Sucursales en Guatemala, Mexico y El Salvador.</p>
          <a href="/shop" class="btn btn-light btn-lg rounded-pill px-5 fw-bold" style="color:#c0392b;">Comprar ahora</a>
        </div>
      </section>
      <section class="py-5">
        <div class="container">
          <h2 class="text-center fw-bold mb-4">Explora por categoria</h2>
          <div class="row justify-content-center">{tarjetas}
          </div>
        </div>
      </section>
      <section class="py-5" style="background:#f4f6f8;">
        <div class="container">
          <div class="row text-center">
            <div class="col-md-4 mb-3"><div style="font-size:40px;">&#128666;</div><h4 class="fw-bold">Envio a domicilio</h4><p class="text-muted">Gratis en compras mayores a 25.</p></div>
            <div class="col-md-4 mb-3"><div style="font-size:40px;">&#128179;</div><h4 class="fw-bold">Pago seguro</h4><p class="text-muted">Paga en linea y recibe tu factura al instante por correo.</p></div>
            <div class="col-md-4 mb-3"><div style="font-size:40px;">&#127978;</div><h4 class="fw-bold">3 sucursales</h4><p class="text-muted">Guatemala, Mexico y El Salvador.</p></div>
          </div>
        </div>
      </section>
      <section class="text-center text-white py-5" style="background:#2c3e50;">
        <div class="container">
          <h3 class="fw-bold">Registrate y recibe 10% de descuento en tu proxima compra</h3>
          <a href="/web/signup" class="btn btn-warning btn-lg rounded-pill px-5 mt-3 fw-bold">Crear mi cuenta</a>
        </div>
      </section>
    </div>
  </t>
</t>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restaurar", action="store_true")
    args = ap.parse_args()
    odoo, _ = conectar()

    vistas = odoo.call("ir.ui.view", "search_read", [["key", "=", "website.homepage"]],
                       fields=["id", "arch_db"], context={"active_test": False})
    if not vistas:
        raise SystemExit("[ERROR] No encontre la vista website.homepage (esta instalado el modulo website?)")

    if args.restaurar:
        if not BACKUP.exists():
            raise SystemExit("[ERROR] No hay copia de la portada original (portada_original.json)")
        for v in json.loads(BACKUP.read_text(encoding="utf-8")):
            odoo.write("ir.ui.view", [v["id"]], {"arch_db": v["arch_db"]})
        print("[OK] Portada original restaurada")
        return

    # Logo
    logo = generar_logo()
    odoo.write("res.company", odoo.search("res.company", []), {"logo": logo})
    try:
        odoo.write("website", odoo.search("website", []), {"logo": logo})
    except Exception as e:
        print(f"    [!] logo del sitio: {str(e)[:80]}")
    print("[+] Logo aplicado a la tienda, facturas y correos")

    # Categorias reales de la tienda para los enlaces de la portada
    emojis = {"Alimentos": ("&#127834;", "#e67e22"), "Lacteos": ("&#129371;", "#2980b9"), "Bebidas": ("&#129380;", "#16a085"),
              "Carnes": ("&#129385;", "#c0392b"), "Panaderia": ("&#127838;", "#a0642d"), "Snacks": ("&#127850;", "#d35400"),
              "Cuidado": ("&#129532;", "#8e44ad"), "Limpieza": ("&#129532;", "#27ae60"), "Hogar": ("&#127968;", "#34495e")}
    cats = []
    for c in odoo.search_read("product.public.category", [], ["name"], order="id"):
        clave = c["name"].lower().translate(str.maketrans("áéíóúü", "aeiouu"))
        emoji, color = next((v for k, v in emojis.items() if k.lower() in clave), ("&#128722;", "#7f8c8d"))
        cats.append((c["name"], c["id"], emoji, color))

    BACKUP.write_text(json.dumps(vistas, ensure_ascii=False), encoding="utf-8") if not BACKUP.exists() else None
    for v in vistas:
        odoo.write("ir.ui.view", [v["id"]], {"arch_db": arch_portada(cats)})
    print("[+] Portada de QuetzalMart aplicada. Abre http://<IP>:8069/ y recarga con Ctrl+F5")


if __name__ == "__main__":
    main()
