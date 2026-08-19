-- Consultas para analizar los datos cargados en la base de datos.


-- 1. Ver cuántos clientes se cargaron.
SELECT COUNT(*) AS total_clientes
FROM clientes;

-- 2. Ver cuántas compras se cargaron.
SELECT COUNT(*) AS total_compras
FROM compras_registradas;

-- 3. Media de edad, venta total y número de compras.
SELECT
    AVG(c.edad) AS promedio_edad,
    AVG(r.venta_total) AS promedio_venta,
    AVG(r.n_compras) AS promedio_compras
FROM clientes c
INNER JOIN resumen_cliente_anual r
    ON c.id_cliente = r.id_cliente;

-- 4. Mediana de edad.
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY edad) AS mediana_edad
FROM clientes;

-- 5. Moda de número de compras.
SELECT n_compras, COUNT(*) AS cantidad
FROM resumen_cliente_anual
GROUP BY n_compras
ORDER BY cantidad DESC
LIMIT 1;

-- 6. Ventas por mes.
SELECT
    EXTRACT(MONTH FROM cr.fecha_compra) AS mes,
    SUM(r.venta_total) AS total_ventas
FROM compras_registradas cr
INNER JOIN resumen_cliente_anual r
    ON cr.id_cliente = r.id_cliente
GROUP BY EXTRACT(MONTH FROM cr.fecha_compra)
ORDER BY mes;

-- 7. Ventas por método de pago.
SELECT
    mp.descripcion AS metodo_pago,
    COUNT(*) AS cantidad_compras,
    SUM(r.venta_total) AS total_ventas
FROM compras_registradas cr
INNER JOIN catalogo_metodo_pago mp
    ON cr.id_metodo_pago = mp.id_metodo_pago
INNER JOIN resumen_cliente_anual r
    ON cr.id_cliente = r.id_cliente
GROUP BY mp.descripcion
ORDER BY total_ventas DESC;

-- 8. Cantidad de compras por navegador o canal.
SELECT
    cv.descripcion AS canal,
    COUNT(*) AS cantidad_compras
FROM compras_registradas cr
INNER JOIN catalogo_canal_venta cv
    ON cr.id_canal = cv.id_canal
GROUP BY cv.descripcion
ORDER BY cantidad_compras DESC;

-- 9. Clientes que usan boletín y vale.
SELECT
    recibe_boletin,
    utiliza_vale,
    COUNT(*) AS cantidad_clientes
FROM preferencias_cliente
GROUP BY recibe_boletin, utiliza_vale
ORDER BY cantidad_clientes DESC;

-- 10. Mes con mayor venta.
SELECT
    EXTRACT(MONTH FROM cr.fecha_compra) AS mes,
    SUM(r.venta_total) AS total_ventas
FROM compras_registradas cr
INNER JOIN resumen_cliente_anual r
    ON cr.id_cliente = r.id_cliente
GROUP BY EXTRACT(MONTH FROM cr.fecha_compra)
ORDER BY total_ventas DESC
LIMIT 1;

-- 11. Mes con menor venta.
SELECT
    EXTRACT(MONTH FROM cr.fecha_compra) AS mes,
    SUM(r.venta_total) AS total_ventas
FROM compras_registradas cr
INNER JOIN resumen_cliente_anual r
    ON cr.id_cliente = r.id_cliente
GROUP BY EXTRACT(MONTH FROM cr.fecha_compra)
ORDER BY total_ventas ASC
LIMIT 1;

-- 12. Navegador o canal más usado.
SELECT
    cv.descripcion AS canal,
    COUNT(*) AS cantidad_compras
FROM compras_registradas cr
INNER JOIN catalogo_canal_venta cv
    ON cr.id_canal = cv.id_canal
GROUP BY cv.descripcion
ORDER BY cantidad_compras DESC
LIMIT 1;

-- 13. Navegador o canal menos usado.
SELECT
    cv.descripcion AS canal,
    COUNT(*) AS cantidad_compras
FROM compras_registradas cr
INNER JOIN catalogo_canal_venta cv
    ON cr.id_canal = cv.id_canal
GROUP BY cv.descripcion
ORDER BY cantidad_compras ASC
LIMIT 1;

-- 14. Total de ventas pagadas en efectivo.
SELECT SUM(r.venta_total) AS ventas_efectivo
FROM compras_registradas cr
INNER JOIN resumen_cliente_anual r
    ON cr.id_cliente = r.id_cliente
WHERE cr.id_metodo_pago = 0;

-- 15. Meses donde más se usó el boletín.
SELECT
    EXTRACT(MONTH FROM cr.fecha_compra) AS mes,
    COUNT(*) AS clientes_con_boletin
FROM compras_registradas cr
INNER JOIN preferencias_cliente p
    ON cr.id_cliente = p.id_cliente
WHERE p.recibe_boletin = true
GROUP BY EXTRACT(MONTH FROM cr.fecha_compra)
ORDER BY clientes_con_boletin DESC;

-- 16. Meses donde más se usó el vale.
SELECT
    EXTRACT(MONTH FROM cr.fecha_compra) AS mes,
    COUNT(*) AS clientes_con_vale
FROM compras_registradas cr
INNER JOIN preferencias_cliente p
    ON cr.id_cliente = p.id_cliente
WHERE p.utiliza_vale = true
GROUP BY EXTRACT(MONTH FROM cr.fecha_compra)
ORDER BY clientes_con_vale DESC;

-- 17. Clientes agrupados por edad.
SELECT
    CASE
        WHEN c.edad <= 25 THEN '18 a 25'
        WHEN c.edad <= 35 THEN '26 a 35'
        WHEN c.edad <= 45 THEN '36 a 45'
        WHEN c.edad <= 55 THEN '46 a 55'
        ELSE '56 o mas'
    END AS rango_edad,
    COUNT(*) AS cantidad_clientes,
    AVG(r.venta_total) AS promedio_venta
FROM clientes c
INNER JOIN resumen_cliente_anual r
    ON c.id_cliente = r.id_cliente
GROUP BY rango_edad
ORDER BY rango_edad;

-- 18. Comportamiento de compra por género.
SELECT
    g.descripcion AS genero,
    COUNT(*) AS cantidad_clientes,
    AVG(r.n_compras) AS promedio_compras,
    AVG(r.venta_total) AS promedio_venta
FROM clientes c
INNER JOIN catalogo_genero g
    ON c.id_genero = g.id_genero
INNER JOIN resumen_cliente_anual r
    ON c.id_cliente = r.id_cliente
GROUP BY g.descripcion;

-- 19. Comportamiento por boletín y vale.
SELECT
    p.recibe_boletin,
    p.utiliza_vale,
    COUNT(*) AS cantidad_clientes,
    AVG(r.venta_total) AS promedio_venta
FROM preferencias_cliente p
INNER JOIN resumen_cliente_anual r
    ON p.id_cliente = r.id_cliente
GROUP BY p.recibe_boletin, p.utiliza_vale;

-- 20. Correlación entre edad y venta total.
SELECT CORR(c.edad, r.venta_total) AS correlacion
FROM clientes c
INNER JOIN resumen_cliente_anual r
    ON c.id_cliente = r.id_cliente;

-- 21. Método de pago usado por cada género.
SELECT
    g.descripcion AS genero,
    mp.descripcion AS metodo_pago,
    COUNT(*) AS cantidad
FROM clientes c
INNER JOIN catalogo_genero g
    ON c.id_genero = g.id_genero
INNER JOIN compras_registradas cr
    ON c.id_cliente = cr.id_cliente
INNER JOIN catalogo_metodo_pago mp
    ON cr.id_metodo_pago = mp.id_metodo_pago
GROUP BY g.descripcion, mp.descripcion
ORDER BY genero, cantidad DESC;

-- 22. Relación entre boletín y vale.
SELECT
    recibe_boletin,
    utiliza_vale,
    COUNT(*) AS cantidad_clientes
FROM preferencias_cliente
GROUP BY recibe_boletin, utiliza_vale;

-- 23. Correlación entre boletín y vale.
SELECT CORR(recibe_boletin::int, utiliza_vale::int) AS correlacion_boletin_vale
FROM preferencias_cliente;

-- 24. Cliente con mayor compra acumulada.
SELECT
    r.id_cliente,
    c.edad,
    r.n_compras,
    r.venta_total
FROM resumen_cliente_anual r
INNER JOIN clientes c
    ON r.id_cliente = c.id_cliente
ORDER BY r.venta_total DESC
LIMIT 1;
