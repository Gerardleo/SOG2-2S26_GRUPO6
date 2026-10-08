"""
Paso 4 - Prueba el correo saliente desde Odoo hacia una direccion temporal (temp-mail.org).

  python 04_probar_correo.py --to alguien@temp-mail.org              # correo simple
  python 04_probar_correo.py --to alguien@temp-mail.org --marketing  # envia la campana usando una factura web/venta existente

Muestra el estado final del correo en Odoo (sent / exception + motivo del fallo).
"""

import argparse
import time

from common import conectar


def estado(odoo, mail_id):
    time.sleep(3)
    m = odoo.read("mail.mail", [mail_id], ["state", "failure_reason"])
    return (m[0]["state"], m[0]["failure_reason"]) if m else ("enviado y eliminado de la cola", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--marketing", action="store_true")
    args = ap.parse_args()
    odoo, _ = conectar()

    if args.marketing:
        tmpl = odoo.search("mail.template", [["name", "=", "QuetzalMart - Campana de Marketing"]], limit=1)
        factura = odoo.search("account.move", [["move_type", "=", "out_invoice"], ["state", "=", "posted"]], limit=1)
        if not tmpl or not factura:
            raise SystemExit("[ERROR] Falta la plantilla (paso 3) o una factura de venta publicada")
        mail_id = odoo.call("mail.template", "send_mail", tmpl[0], factura[0], True, False,
                            {"email_to": args.to, "recipient_ids": []})
    else:
        mail_id = odoo.create("mail.mail", {
            "subject": "Prueba SMTP QuetzalMart", "email_to": args.to,
            "body_html": "<h2>Hola!</h2><p>Correo de prueba enviado desde Odoo - QuetzalMart.</p>",
        })
        odoo.call("mail.mail", "send", [mail_id])

    st, motivo = estado(odoo, mail_id)
    print(f"[=] Estado del correo: {st} {motivo or ''}")
    print("    Revisa la bandeja en temp-mail.org (puede tardar ~1 min; mira tambien Spam).")


if __name__ == "__main__":
    main()
