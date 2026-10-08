"""
Paso 6 - Datos de ejemplo en el CRM de Odoo (para las capturas de "manejo de clientes en CRM").
Crea 12 oportunidades ligadas a clientes existentes, repartidas en las etapas del embudo.
Es idempotente: omite las oportunidades cuyo nombre ya existe.

Uso:  python 06_cargar_crm.py
"""

import random

from common import conectar

ASUNTOS = [
    "Pedido mayorista de abarrotes", "Contrato de suministro mensual", "Cotizacion de bebidas para evento",
    "Compra corporativa de limpieza", "Abastecimiento sucursal Mexico", "Abastecimiento sucursal El Salvador",
    "Canasta basica para empleados", "Pedido recurrente de lacteos", "Cotizacion de productos de higiene",
    "Compra por volumen de panaderia", "Convenio con restaurante", "Pedido para tienda de barrio",
]


def main():
    odoo, _ = conectar()
    random.seed(7)
    etapas = odoo.search("crm.stage", [], order="sequence")
    clientes = odoo.search_read("res.partner", [["customer_rank", ">", 0], ["email", "!=", False]],
                                ["name", "email", "phone"], limit=40)
    if not etapas or not clientes:
        raise SystemExit("[ERROR] No hay etapas de CRM o clientes (instala crm y corre la carga masiva)")

    creadas = 0
    for asunto in ASUNTOS:
        cli = random.choice(clientes)
        nombre = f"{asunto} - {cli['name']}"
        if odoo.search("crm.lead", [["name", "=", nombre]]):
            continue
        odoo.create("crm.lead", {
            "name": nombre, "type": "opportunity", "partner_id": cli["id"],
            "email_from": cli["email"], "phone": cli["phone"] or False,
            "expected_revenue": random.choice([250, 480, 900, 1500, 3200]),
            "probability": random.choice([10, 25, 50, 75]),
            "stage_id": random.choice(etapas),
        })
        creadas += 1
    print(f"[OK] {creadas} oportunidades creadas en el CRM")


if __name__ == "__main__":
    main()
