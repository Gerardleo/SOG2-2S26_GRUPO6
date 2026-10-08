"""
Paso 3 - Correo saliente + campana de marketing automatica.

  * Crea/actualiza el servidor SMTP saliente en Odoo (datos en .env)
  * Fija el remitente (empresa, plantillas de factura y confirmacion) para que NO salga de un correo personal
  * Crea la plantilla HTML de la campana "QuetzalMart - Campana de Marketing"
  * Crea una regla automatica: cuando una factura de la tienda web queda pagada,
    se encola el correo de marketing (1 min despues, para que llegue DESPUES del correo de compra)
  * Baja el intervalo de la cola de correo a 1 minuto

Uso:  python 03_configurar_correo.py
"""

import sys
import time

from common import conectar

NOMBRE_PLANTILLA = "QuetzalMart - Campana de Marketing"
NOMBRE_REGLA = "QuetzalMart - Enviar campana tras compra web"

CODIGO_ACCION = """
tmpl = env['mail.template'].search([('name', '=', '%s')], limit=1)
if tmpl and record.partner_id.email:
    when = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).strftime('%%Y-%%m-%%d %%H:%%M:%%S')
    tmpl.send_mail(record.id, force_send=False, email_values={'scheduled_date': when})
""" % NOMBRE_PLANTILLA


def cuerpo_html(base_url, productos):
    # Sin fotos remotas: clientes como temp-mail bloquean imagenes http. Tarjetas con emoji + color se ven siempre.
    tarjetas = ""
    for emoji, titulo, color, texto in [
        ("&#127834;", "Alimentos", "#e67e22", "Abarrotes, granos y despensa"),
        ("&#129371;", "Bebidas", "#16a085", "Jugos, aguas y gaseosas"),
        ("&#129472;", "Lacteos", "#2980b9", "Leche, quesos y yogurt"),
    ]:
        tarjetas += f"""
        <td style="width:33%;padding:6px;text-align:center;vertical-align:top;">
          <a href="{base_url}/shop" style="text-decoration:none;display:block;background:{color};border-radius:14px;padding:18px 6px;color:#ffffff;">
            <div style="font-size:42px;line-height:48px;">{emoji}</div>
            <div style="font-weight:bold;font-size:16px;margin-top:6px;">{titulo}</div>
            <div style="font-size:12px;margin-top:4px;opacity:.9;">{texto}</div>
          </a>
        </td>"""
    return f"""
<div style="background:#f4f6f8;padding:24px 0;font-family:Arial,Helvetica,sans-serif;">
  <table align="center" cellpadding="0" cellspacing="0" style="width:600px;max-width:100%;background:#ffffff;border-radius:14px;overflow:hidden;">
    <tr><td style="background:linear-gradient(135deg,#e67e22,#c0392b);padding:36px 24px;text-align:center;color:#ffffff;">
      <div style="font-size:15px;letter-spacing:3px;">QUETZALMART</div>
      <div style="font-size:32px;font-weight:bold;margin:10px 0;">Gracias por tu compra, <t t-out="object.partner_id.name"/>!</div>
      <div style="font-size:16px;">Calidad y precios accesibles, ahora tambien en linea.</div>
    </td></tr>
    <tr><td style="padding:28px 24px;text-align:center;">
      <div style="font-size:22px;font-weight:bold;color:#2c3e50;">Tu proxima compra con 10% de descuento</div>
      <div style="margin:16px auto;display:inline-block;border:2px dashed #e67e22;border-radius:10px;padding:10px 26px;font-size:24px;font-weight:bold;color:#e67e22;">QUETZAL10</div>
      <p style="color:#555;font-size:15px;line-height:1.5;">Alimentos, bebidas y todo lo que necesitas para tu hogar, con sucursales en
        Guatemala, Mexico y El Salvador y envio gratis en compras mayores a 25.</p>
      <a href="{base_url}/shop" style="display:inline-block;background:#e67e22;color:#ffffff;text-decoration:none;padding:14px 34px;border-radius:30px;font-weight:bold;font-size:16px;">Ir a la tienda</a>
    </td></tr>
    <tr><td style="padding:0 16px 24px;">
      <div style="font-size:18px;font-weight:bold;color:#2c3e50;text-align:center;margin-bottom:8px;">Lo que encuentras en nuestra tienda</div>
      <table width="100%" cellpadding="0" cellspacing="0"><tr>{tarjetas}</tr></table>
    </td></tr>
    <tr><td style="background:#2c3e50;color:#bdc3c7;text-align:center;padding:18px;font-size:12px;">
      QuetzalMart - Guatemala | Mexico | El Salvador<br/>Recibes este correo por tu compra en nuestra tienda en linea.
    </td></tr>
  </table>
</div>"""


def configurar_smtp(odoo, env):
    host, user, pwd = env.get("SMTP_HOST"), env.get("SMTP_USER"), env.get("SMTP_PASSWORD")
    remitente = env.get("SMTP_FROM") or user
    if not (host and user and pwd):
        sys.exit("[ERROR] Llena SMTP_HOST, SMTP_USER y SMTP_PASSWORD en .env")
    vals = {
        "name": "QuetzalMart SMTP", "smtp_host": host, "smtp_port": int(env.get("SMTP_PORT", 587)),
        "smtp_encryption": "starttls", "smtp_user": user, "smtp_pass": pwd, "from_filter": False, "sequence": 1,
    }
    existe = odoo.search("ir.mail_server", [["name", "=", vals["name"]]], limit=1)
    if existe:
        odoo.write("ir.mail_server", existe, vals)
    else:
        odoo.create("ir.mail_server", vals)
    print(f"[+] Servidor SMTP '{vals['name']}' listo ({host}:{vals['smtp_port']})")

    formateado = f'"QuetzalMart" <{remitente}>'
    odoo.set_param("mail.default.from", remitente)
    cia = odoo.search("res.company", [], limit=1)
    odoo.write("res.company", cia, {"name": "QuetzalMart", "email": remitente})
    for xmlid in ("account.email_template_edi_invoice", "sale.mail_template_sale_confirmation"):
        tid = odoo.ref(xmlid)
        if tid:
            odoo.write("mail.template", [tid], {"email_from": formateado})
    print(f"[+] Remitente fijado: {formateado}")
    return remitente


def crear_plantilla(odoo, env, remitente):
    base_url = env["ODOO_URL"].rstrip("/")
    productos = odoo.search_read(
        "product.template", [["website_published", "=", True], ["image_1920", "!=", False]],
        ["name", "list_price"], limit=3, order="id")
    modelo = odoo.search("ir.model", [["model", "=", "account.move"]], limit=1)[0]
    vals = {
        "name": NOMBRE_PLANTILLA,
        "model_id": modelo,
        "subject": "QuetzalMart: gracias por tu compra, tienes 10% de descuento",
        "email_from": f'"QuetzalMart" <{remitente}>',
        "partner_to": "{{ object.partner_id.id }}",
        "body_html": cuerpo_html(base_url, productos),
        "auto_delete": False,
    }
    existe = odoo.search("mail.template", [["name", "=", NOMBRE_PLANTILLA]], limit=1)
    if existe:
        odoo.write("mail.template", existe, vals)
        print("[+] Plantilla de marketing actualizada")
    else:
        odoo.create("mail.template", vals)
        print("[+] Plantilla de marketing creada")


def crear_regla(odoo):
    modelo = odoo.search("ir.model", [["model", "=", "account.move"]], limit=1)[0]
    campo = odoo.search("ir.model.fields", [["model", "=", "account.move"], ["name", "=", "payment_state"]], limit=1)
    campos = odoo.call("base.automation", "fields_get", attributes=["type"])
    clave_accion = "action_server_ids" if "action_server_ids" in campos else "action_server_id"
    accion = {
        "name": "Enviar campana de marketing", "model_id": modelo, "state": "code",
        "code": CODIGO_ACCION, "usage": "base_automation",
    }
    vals = {
        "name": NOMBRE_REGLA,
        "model_id": modelo,
        "trigger": "on_write",
        "trigger_field_ids": [(6, 0, campo)],
        "filter_pre_domain": '[("payment_state", "not in", ["paid", "in_payment"])]',
        "filter_domain": '[("move_type", "=", "out_invoice"), ("payment_state", "in", ["paid", "in_payment"]), '
                         '("invoice_line_ids.sale_line_ids.order_id.website_id", "!=", False)]',
    }
    existe = odoo.search("base.automation", [["name", "=", NOMBRE_REGLA]], limit=1)
    if existe:
        print("[=] La regla automatica ya existe")
        return
    if clave_accion == "action_server_ids":
        vals[clave_accion] = [(0, 0, accion)]
    else:
        vals[clave_accion] = odoo.create("ir.actions.server", accion)
    odoo.create("base.automation", vals)
    print("[+] Regla automatica creada: factura web pagada -> correo de marketing")


def acelerar_cola_correo(odoo):
    cron = odoo.ref("mail.ir_cron_mail_scheduler_action")
    if cron:
        # nextcall en "ahora": si no, la tarea espera la fecha vieja (hasta 1 hora) antes de empezar a correr cada minuto
        ahora = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        odoo.write("ir.cron", [cron], {"interval_number": 1, "interval_type": "minutes", "active": True,
                                       "nextcall": ahora})
        print("[+] Cola de correo cada 1 minuto")


def main():
    odoo, env = conectar()
    # Direccion publica fija: sin esto las imagenes y enlaces de los correos apuntan a una URL que el cliente no alcanza
    odoo.set_param("web.base.url", env["ODOO_URL"].rstrip("/"))
    odoo.set_param("web.base.url.freeze", "True")
    remitente = configurar_smtp(odoo, env)
    crear_plantilla(odoo, env, remitente)
    crear_regla(odoo)
    acelerar_cola_correo(odoo)
    print("\n[OK] Siguiente paso: python 04_probar_correo.py --to tu_correo@temp-mail.org")


if __name__ == "__main__":
    main()
