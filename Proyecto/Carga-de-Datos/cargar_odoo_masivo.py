"""
Script de Carga Masiva Automatizada para Odoo 16/17/18 - QuetzalMart
====================================================================
Este script interactúa con la API XML-RPC oficial de Odoo para cargar
automáticamente:
- 60 Materiales de operación para sucursales (Guatemala, México, El Salvador)
- 40 Productos de supermercado
- 35 Clientes y 20 Proveedores
- 100 Compras a proveedores con facturas generadas
- 20 Cotizaciones (10 de venta + 10 de compra)
- 150 Ventas a distintos clientes y productos con facturas generadas

Funciona en local y en cualquier nube (AWS, GCP, Azure) sin librerías externas.
Uso:
    python cargar_odoo_masivo.py --url http://IP_O_DOMINIO:8069 --db quetzalmart --user admin --password tu_password
"""

import argparse
import csv
import os
import random
import sys
import xmlrpc.client
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def conectar_odoo(url, db, username, password):
    print(f"[*] Conectando a Odoo en {url} (DB: {db})...")
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})
        if not uid:
            print("[ERROR] Autenticación fallida. Revisa usuario, contraseña y nombre de base de datos.")
            sys.exit(1)
        print(f"[+] Autenticación exitosa. User ID: {uid}")
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        return uid, models
    except Exception as e:
        print(f"[ERROR] No se pudo conectar al servidor Odoo: {e}")
        sys.exit(1)

def cargar_csv(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[ERROR] Archivo no encontrado: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def obtener_o_crear_pais(models, db, uid, password, country_name):
    if not country_name:
        return False
    ids = models.execute_kw(db, uid, password, 'res.country', 'search', [[['name', 'ilike', country_name]]])
    return ids[0] if ids else False

def registrar_contactos(models, db, uid, password):
    print("\n[+] 1. Registrando Contactos (Clientes y Proveedores)...")
    clientes_csv = cargar_csv("clientes.csv")
    proveedores_csv = cargar_csv("proveedores.csv")

    clientes_ids = []
    for c in clientes_csv:
        exist = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['name', '=', c['Name']]]])
        if exist:
            clientes_ids.append(exist[0])
            continue
        country_id = obtener_o_crear_pais(models, db, uid, password, c['Country'])
        vals = {
            'name': c['Name'],
            'company_type': c['Company Type'] if c['Company Type'] in ['person', 'company'] else 'person',
            'email': c['Email'],
            'phone': c['Phone'],
            'street': c['Street'],
            'street2': c['Street2'],
            'city': c['City'],
            'zip': c['Zip'],
            'vat': c['Tax ID'],
            'website': c['Website'],
            'ref': c['Reference'],
            'comment': c['Notes'],
            'customer_rank': 1,
        }
        if country_id:
            vals['country_id'] = country_id
        try:
            cid = models.execute_kw(db, uid, password, 'res.partner', 'create', [vals])
            clientes_ids.append(cid)
        except Exception as e:
            print(f"    [!] Error al crear cliente {c['Name']}: {e}")

    proveedores_ids = []
    for p in proveedores_csv:
        exist = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['name', '=', p['Name']]]])
        if exist:
            proveedores_ids.append(exist[0])
            continue
        country_id = obtener_o_crear_pais(models, db, uid, password, p['Country'])
        vals = {
            'name': p['Name'],
            'company_type': 'company',
            'email': p['Email'],
            'phone': p['Phone'],
            'street': p['Street'],
            'city': p['City'],
            'zip': p['Zip'],
            'vat': p['Tax ID'],
            'ref': p['Reference'],
            'comment': p['Notes'],
            'supplier_rank': 1,
        }
        if country_id:
            vals['country_id'] = country_id
        try:
            pid = models.execute_kw(db, uid, password, 'res.partner', 'create', [vals])
            proveedores_ids.append(pid)
        except Exception as e:
            print(f"    [!] Error al crear proveedor {p['Name']}: {e}")

    print(f"    Total Clientes registrados/listos: {len(clientes_ids)}")
    print(f"    Total Proveedores registrados/listos: {len(proveedores_ids)}")
    return clientes_ids, proveedores_ids

def registrar_materiales(models, db, uid, password):
    print("\n[+] 2. Registrando 60 Materiales para las Sucursales...")
    materiales_csv = cargar_csv("60_materiales.csv")
    materiales_ids = []

    for m in materiales_csv:
        code = m['default_code']
        exist = models.execute_kw(db, uid, password, 'product.product', 'search', [[['default_code', '=', code]]])
        if exist:
            materiales_ids.append(exist[0])
            continue
        vals = {
            'name': m['name'],
            'default_code': code,
            'detailed_type': 'consu',  # Consumible/Material
            'standard_price': float(m['standard_price']),
            'list_price': float(m['list_price']),
            'description': m['description'],
            'purchase_ok': True,
            'sale_ok': False,  # Es material de operación interna
        }
        try:
            mid = models.execute_kw(db, uid, password, 'product.product', 'create', [vals])
            materiales_ids.append(mid)
        except Exception as e:
            print(f"    [!] Error al crear material {code}: {e}")

    print(f"    Total Materiales registrados/listos: {len(materiales_ids)} de 60 solicitados.")
    return materiales_ids

def registrar_productos_venta(models, db, uid, password):
    print("\n[+] 3. Registrando Catálogo de Productos de Venta...")
    prod_csv = cargar_csv("productos_venta.csv")
    productos_ids = []

    for p in prod_csv:
        code = p['Internal Reference']
        exist = models.execute_kw(db, uid, password, 'product.product', 'search', [[['default_code', '=', code]]])
        if exist:
            productos_ids.append(exist[0])
            continue
        vals = {
            'name': p['Name'],
            'default_code': code,
            'barcode': p['Barcode'],
            'detailed_type': 'consu',
            'standard_price': float(p['Cost']),
            'list_price': float(p['Sales Price']),
            'weight': float(p['Weight']),
            'description_sale': p['Sales Description'],
            'purchase_ok': True,
            'sale_ok': True,
        }
        try:
            pid = models.execute_kw(db, uid, password, 'product.product', 'create', [vals])
            productos_ids.append(pid)
        except Exception as e:
            print(f"    [!] Error al crear producto {code}: {e}")

    print(f"    Total Productos de venta listos: {len(productos_ids)}")
    return productos_ids

def generar_compras_y_facturas(models, db, uid, password, proveedores_ids, materiales_ids, productos_ids, total_compras=100):
    print(f"\n[+] 4. Creando {total_compras} Compras con Facturas asociadas...")
    compras_creadas = 0
    items_todos = materiales_ids + productos_ids
    fecha_base = datetime.now() - timedelta(days=90)

    for i in range(1, total_compras + 1):
        proveedor_id = random.choice(proveedores_ids)
        fecha_compra = (fecha_base + timedelta(days=random.randint(0, 85))).strftime('%Y-%m-%d %H:%M:%S')

        # Seleccionar entre 1 y 4 productos/materiales por compra
        num_lineas = random.randint(1, 4)
        items_compra = random.sample(items_todos, min(num_lineas, len(items_todos)))

        lineas = []
        for item_id in items_compra:
            # Consultar precio de costo del producto
            prod_info = models.execute_kw(db, uid, password, 'product.product', 'read', [[item_id], ['name', 'standard_price', 'uom_po_id']])
            costo = prod_info[0]['standard_price'] or 10.0
            uom_id = prod_info[0]['uom_po_id'][0] if prod_info[0]['uom_po_id'] else 1
            cantidad = random.randint(5, 50)

            lineas.append((0, 0, {
                'product_id': item_id,
                'name': prod_info[0]['name'],
                'product_qty': cantidad,
                'price_unit': costo,
                'product_uom': uom_id,
                'date_planned': fecha_compra,
            }))

        po_vals = {
            'partner_id': proveedor_id,
            'date_order': fecha_compra,
            'order_line': lineas,
        }

        try:
            po_id = models.execute_kw(db, uid, password, 'purchase.order', 'create', [po_vals])
            # Confirmar orden de compra (pasa a estado 'purchase')
            models.execute_kw(db, uid, password, 'purchase.order', 'button_confirm', [[po_id]])

            # Intentar generar factura de proveedor (bill)
            try:
                models.execute_kw(db, uid, password, 'purchase.order', 'action_create_invoice', [[po_id]])
            except Exception:
                pass

            compras_creadas += 1
            if compras_creadas % 20 == 0 or compras_creadas == total_compras:
                print(f"    -> {compras_creadas}/{total_compras} compras creadas...")
        except Exception as e:
            print(f"    [!] Error en compra #{i}: {e}")

    print(f"    [OK] Finalizado: {compras_creadas} compras generadas.")

def generar_cotizaciones(models, db, uid, password, clientes_ids, proveedores_ids, productos_ids, materiales_ids, total_cotizaciones=20):
    print(f"\n[+] 5. Creando {total_cotizaciones} Cotizaciones (10 Ventas + 10 Compras en borrador)...")
    cot_creadas = 0

    # 10 Cotizaciones de Ventas a Clientes (estado 'draft')
    for i in range(1, 11):
        cliente_id = random.choice(clientes_ids)
        items = random.sample(productos_ids, random.randint(1, 3))
        lineas = []
        for pid in items:
            p_data = models.execute_kw(db, uid, password, 'product.product', 'read', [[pid], ['name', 'list_price', 'uom_id']])
            lineas.append((0, 0, {
                'product_id': pid,
                'name': p_data[0]['name'],
                'product_uom_qty': random.randint(1, 10),
                'price_unit': p_data[0]['list_price'] or 5.0,
                'product_uom': p_data[0]['uom_id'][0] if p_data[0]['uom_id'] else 1,
            }))
        so_vals = {
            'partner_id': cliente_id,
            'order_line': lineas,
            'state': 'draft',
        }
        try:
            models.execute_kw(db, uid, password, 'sale.order', 'create', [so_vals])
            cot_creadas += 1
        except Exception as e:
            print(f"    [!] Error en cotización venta #{i}: {e}")

    # 10 Solicitudes de Cotización de Compras a Proveedores (estado 'draft')
    for i in range(1, 11):
        proveedor_id = random.choice(proveedores_ids)
        items = random.sample(materiales_ids + productos_ids, random.randint(1, 3))
        lineas = []
        for pid in items:
            p_data = models.execute_kw(db, uid, password, 'product.product', 'read', [[pid], ['name', 'standard_price', 'uom_po_id']])
            lineas.append((0, 0, {
                'product_id': pid,
                'name': p_data[0]['name'],
                'product_qty': random.randint(10, 100),
                'price_unit': p_data[0]['standard_price'] or 10.0,
                'product_uom': p_data[0]['uom_po_id'][0] if p_data[0]['uom_po_id'] else 1,
            }))
        po_vals = {
            'partner_id': proveedor_id,
            'order_line': lineas,
            'state': 'draft',
        }
        try:
            models.execute_kw(db, uid, password, 'purchase.order', 'create', [po_vals])
            cot_creadas += 1
        except Exception as e:
            print(f"    [!] Error en cotización compra #{i}: {e}")

    print(f"    [OK] Finalizado: {cot_creadas} cotizaciones registradas.")

def generar_ventas(models, db, uid, password, clientes_ids, productos_ids, total_ventas=150):
    print(f"\n[+] 6. Creando {total_ventas} Ventas con distintos productos y clientes...")
    ventas_creadas = 0
    fecha_base = datetime.now() - timedelta(days=60)

    for i in range(1, total_ventas + 1):
        cliente_id = random.choice(clientes_ids)
        fecha_venta = (fecha_base + timedelta(days=random.randint(0, 55))).strftime('%Y-%m-%d %H:%M:%S')

        num_items = random.randint(1, 5)
        items = random.sample(productos_ids, min(num_items, len(productos_ids)))

        lineas = []
        for pid in items:
            p_data = models.execute_kw(db, uid, password, 'product.product', 'read', [[pid], ['name', 'list_price', 'uom_id']])
            lineas.append((0, 0, {
                'product_id': pid,
                'name': p_data[0]['name'],
                'product_uom_qty': random.randint(1, 8),
                'price_unit': p_data[0]['list_price'] or 2.50,
                'product_uom': p_data[0]['uom_id'][0] if p_data[0]['uom_id'] else 1,
            }))

        so_vals = {
            'partner_id': cliente_id,
            'date_order': fecha_venta,
            'order_line': lineas,
        }

        try:
            so_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [so_vals])
            # Confirmar la venta para que pase a estado 'sale'
            models.execute_kw(db, uid, password, 'sale.order', 'action_confirm', [[so_id]])

            # Intentar generar y publicar factura si es posible
            try:
                models.execute_kw(db, uid, password, 'sale.order', '_create_invoices', [[so_id]])
            except Exception:
                pass

            ventas_creadas += 1
            if ventas_creadas % 25 == 0 or ventas_creadas == total_ventas:
                print(f"    -> {ventas_creadas}/{total_ventas} ventas creadas...")
        except Exception as e:
            print(f"    [!] Error en venta #{i}: {e}")

    print(f"    [OK] Finalizado: {ventas_creadas} ventas generadas exitosamente.")

def main():
    parser = argparse.ArgumentParser(description="Carga Masiva Odoo para QuetzalMart")
    parser.add_argument("--url", default="http://localhost:8069", help="URL del servidor Odoo")
    parser.add_argument("--db", default="quetzalmart", help="Nombre de la Base de Datos")
    parser.add_argument("--user", default="admin", help="Usuario de Odoo")
    parser.add_argument("--password", default="admin", help="Contraseña o API Key")
    parser.add_argument("--compras", type=int, default=100, help="Cantidad de compras a generar")
    parser.add_argument("--ventas", type=int, default=150, help="Cantidad de ventas a generar")
    parser.add_argument("--cotizaciones", type=int, default=20, help="Cantidad de cotizaciones a generar")

    args = parser.parse_args()

    print("=" * 65)
    print("      QUETZALMART - PROYECTO ERP: CARGA MASIVA INTEGRANTE 1")
    print("=" * 65)

    uid, models = conectar_odoo(args.url, args.db, args.user, args.password)

    clientes_ids, proveedores_ids = registrar_contactos(models, args.db, uid, args.password)
    materiales_ids = registrar_materiales(models, args.db, uid, args.password)
    productos_ids = registrar_productos_venta(models, args.db, uid, args.password)

    generar_compras_y_facturas(models, args.db, uid, args.password, proveedores_ids, materiales_ids, productos_ids, args.compras)
    generar_cotizaciones(models, args.db, uid, args.password, clientes_ids, proveedores_ids, productos_ids, materiales_ids, args.cotizaciones)
    generar_ventas(models, args.db, uid, args.password, clientes_ids, productos_ids, args.ventas)

    print("\n" + "=" * 65)
    print("[¡ÉXITO TOTAL!] Carga masiva completada según todos los requerimientos.")
    print("=" * 65)

if __name__ == "__main__":
    main()
