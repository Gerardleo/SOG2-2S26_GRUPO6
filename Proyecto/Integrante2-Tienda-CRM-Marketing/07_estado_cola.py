"""
Diagnostico de la cola de correos de Odoo (por que un correo queda en "Saliente").

  python 07_estado_cola.py            # muestra la tarea programada y los correos pendientes
  python 07_estado_cola.py --enviar   # ademas, procesa la cola ahora mismo
"""

import argparse
import time

from common import conectar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enviar", action="store_true")
    args = ap.parse_args()
    odoo, _ = conectar()

    cron = odoo.ref("mail.ir_cron_mail_scheduler_action")
    if cron:
        c = odoo.read("ir.cron", [cron], ["active", "interval_number", "interval_type", "nextcall", "lastcall"])[0]
        print(f"\nTarea 'Cola de correo': activa={c['active']} cada {c['interval_number']} {c['interval_type']} "
              f"| proxima ejecucion={c['nextcall']} | ultima={c['lastcall']}")
    print(f"Hora del servidor (UTC) ahora: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")

    pend = odoo.search_read("mail.mail", [["state", "=", "outgoing"]],
                            ["subject", "email_to", "scheduled_date", "date"], order="id desc", limit=10)
    print(f"\nCorreos pendientes (saliente): {len(pend)}")
    for m in pend:
        print(f"  - {m['subject'][:55]} | programado: {m['scheduled_date']} | creado: {m['date']}")

    if args.enviar:
        print("\nProcesando la cola...")
        odoo.call("mail.mail", "process_email_queue")
        time.sleep(3)
        restantes = odoo.call("mail.mail", "search_count", [["state", "=", "outgoing"]])
        print(f"Pendientes despues de procesar: {restantes}")


if __name__ == "__main__":
    main()
