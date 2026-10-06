-- ============================================================================
-- PROYECTO QUETZALMART - CONSULTAS SQL DE COMPROBACIÓN (POSTGRESQL / ODOO)
-- Evaluador / Auxiliar: Consultas para verificar los requerimientos del ERP
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. VENTAS
-- Requerimiento 1.a: Al menos 150 ventas con distintos productos y clientes.
-- ----------------------------------------------------------------------------

-- Conteo total de órdenes de venta confirmadas (estado 'sale' o 'done'):
SELECT COUNT(*) AS total_ventas_confirmadas
FROM sale_order
WHERE state IN ('sale', 'done');

-- Verificación de variedad de clientes en las ventas:
SELECT COUNT(DISTINCT partner_id) AS clientes_distintos_con_compras
FROM sale_order
WHERE state IN ('sale', 'done');

-- Verificación de variedad de productos vendidos:
SELECT COUNT(DISTINCT sol.product_id) AS productos_distintos_vendidos
FROM sale_order_line sol
JOIN sale_order so ON so.id = sol.order_id
WHERE so.state IN ('sale', 'done');

-- Listado de las 150 ventas con cliente, fecha y monto total (muestra las primeras 20):
SELECT 
    so.name AS codigo_orden,
    rp.name AS cliente,
    so.date_order AS fecha_venta,
    so.state AS estado,
    so.amount_total AS total_venta
FROM sale_order so
JOIN res_partner rp ON rp.id = so.partner_id
WHERE so.state IN ('sale', 'done')
ORDER BY so.date_order DESC
LIMIT 20;


-- ----------------------------------------------------------------------------
-- 2. COTIZACIONES
-- Requerimiento 1.b: Al menos 20 cotizaciones realizadas a clientes y proveedores.
-- ----------------------------------------------------------------------------

-- Conteo de cotizaciones a Clientes (estado 'draft' o 'sent'):
SELECT COUNT(*) AS cotizaciones_clientes
FROM sale_order
WHERE state IN ('draft', 'sent');

-- Conteo de solicitudes de cotización a Proveedores (estado 'draft' o 'sent'):
SELECT COUNT(*) AS cotizaciones_proveedores
FROM purchase_order
WHERE state IN ('draft', 'sent');

-- Total consolidado de cotizaciones (debe ser >= 20):
SELECT 
    (SELECT COUNT(*) FROM sale_order WHERE state IN ('draft', 'sent')) AS cotizaciones_clientes,
    (SELECT COUNT(*) FROM purchase_order WHERE state IN ('draft', 'sent')) AS cotizaciones_proveedores,
    ((SELECT COUNT(*) FROM sale_order WHERE state IN ('draft', 'sent')) + 
     (SELECT COUNT(*) FROM purchase_order WHERE state IN ('draft', 'sent'))) AS total_cotizaciones;


-- ----------------------------------------------------------------------------
-- 3. COMPRAS Y FACTURAS
-- Requerimiento 3.a: Al menos 100 compras realizadas y facturas correspondientes.
-- ----------------------------------------------------------------------------

-- Conteo de órdenes de compra confirmadas:
SELECT COUNT(*) AS total_compras_realizadas
FROM purchase_order
WHERE state IN ('purchase', 'done');

-- Verificación de compras con sus facturas asociadas en account_move:
SELECT 
    po.name AS orden_compra,
    rp.name AS proveedor,
    po.date_order AS fecha_compra,
    po.amount_total AS total_compra,
    am.name AS numero_factura,
    am.state AS estado_factura
FROM purchase_order po
JOIN res_partner rp ON rp.id = po.partner_id
LEFT JOIN account_move_purchase_order_rel am_rel ON am_rel.purchase_order_id = po.id
LEFT JOIN account_move am ON am.id = am_rel.account_move_id
WHERE po.state IN ('purchase', 'done')
ORDER BY po.date_order DESC
LIMIT 20;

-- Conteo total de facturas de compra generadas en contabilidad:
SELECT COUNT(*) AS total_facturas_proveedor
FROM account_move
WHERE move_type = 'in_invoice';


-- ----------------------------------------------------------------------------
-- 4. MATERIALES DE SUCURSAL
-- Requerimiento 3.b: Al menos 60 materiales utilizados para las sucursales.
-- ----------------------------------------------------------------------------

-- Conteo de materiales operativos registrados (prefijo 'MAT-'):
SELECT COUNT(*) AS total_materiales_sucursales
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code LIKE 'MAT-%';

-- Listado de los materiales con código, nombre y tipo:
SELECT 
    pp.default_code AS codigo_material,
    pt.name AS nombre_material,
    pt.detailed_type AS tipo,
    pt.list_price AS precio
FROM product_product pp
JOIN product_template pt ON pt.id = pp.product_tmpl_id
WHERE pp.default_code LIKE 'MAT-%'
ORDER BY pp.default_code ASC;


-- ----------------------------------------------------------------------------
-- 5. RESUMEN EJECUTIVO GENERAL DEL ERP (AUDITORÍA COMPLETA)
-- ----------------------------------------------------------------------------
SELECT 
    (SELECT COUNT(*) FROM sale_order WHERE state IN ('sale', 'done')) AS ventas_confirmadas,
    (SELECT COUNT(*) FROM purchase_order WHERE state IN ('purchase', 'done')) AS compras_confirmadas,
    ((SELECT COUNT(*) FROM sale_order WHERE state IN ('draft', 'sent')) + 
     (SELECT COUNT(*) FROM purchase_order WHERE state IN ('draft', 'sent'))) AS cotizaciones_totales,
    (SELECT COUNT(*) FROM product_product pp JOIN product_template pt ON pt.id = pp.product_tmpl_id WHERE pp.default_code LIKE 'MAT-%') AS materiales_sucursales,
    (SELECT COUNT(*) FROM res_partner WHERE customer_rank > 0) AS clientes_totales,
    (SELECT COUNT(*) FROM res_partner WHERE supplier_rank > 0) AS proveedores_totales;
