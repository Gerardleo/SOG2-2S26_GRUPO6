from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import psycopg

# Cargar variables de entorno desde practica_1/.env
PRACTICA_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PRACTICA_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL")

# Instanciar el servidor MCP
mcp = FastMCP("sog2-ventas-analytics")


def get_db_connection():
    #Establece conexión con la base de datos PostgreSQL en la nube.
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL no está configurada en el archivo .env")
    return psycopg.connect(DATABASE_URL, prepare_threshold=None)


@mcp.tool()
def obtener_estadisticas_descriptivas() -> Dict[str, Any]:
    #Calcula estadísticas básicas (media, mediana, moda) para variables numéricas.
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Media de edad, venta_total, n_compras, monto_compra, tiempo
            cur.execute("""
                SELECT 
                    ROUND(AVG(c.edad)::numeric, 2) AS media_edad,
                    ROUND(AVG(r.venta_total)::numeric, 2) AS media_venta_total,
                    ROUND(AVG(r.n_compras)::numeric, 2) AS media_n_compras,
                    ROUND(AVG(cr.monto_compra)::numeric, 2) AS media_monto_compra,
                    ROUND(AVG(cr.tiempo)::numeric, 2) AS media_tiempo
                FROM clientes c
                INNER JOIN resumen_cliente_anual r ON c.id_cliente = r.id_cliente
                INNER JOIN compras_registradas cr ON c.id_cliente = cr.id_cliente;
            """)
            medias = cur.fetchone()

            # Medianas usando PERCENTILE_CONT
            cur.execute("""
                SELECT 
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY edad) AS mediana_edad
                FROM clientes;
            """)
            mediana_edad = cur.fetchone()[0]

            cur.execute("""
                SELECT 
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY venta_total) AS mediana_venta_total,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY n_compras) AS mediana_n_compras
                FROM resumen_cliente_anual;
            """)
            mediana_resumen = cur.fetchone()

            cur.execute("""
                SELECT 
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monto_compra) AS mediana_monto_compra,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tiempo) AS mediana_tiempo
                FROM compras_registradas;
            """)
            mediana_compras = cur.fetchone()

            # Modas
            cur.execute("""
                SELECT edad, COUNT(*) as cnt FROM clientes GROUP BY edad ORDER BY cnt DESC LIMIT 1;
            """)
            moda_edad = cur.fetchone()[0]

            cur.execute("""
                SELECT n_compras, COUNT(*) as cnt FROM resumen_cliente_anual GROUP BY n_compras ORDER BY cnt DESC LIMIT 1;
            """)
            moda_n_compras = cur.fetchone()[0]

            return {
                "variables": {
                    "edad": {"media": float(medias[0]), "mediana": float(mediana_edad), "moda": int(moda_edad)},
                    "venta_total": {"media": float(medias[1]), "mediana": float(mediana_resumen[0])},
                    "n_compras": {"media": float(medias[2]), "mediana": float(mediana_resumen[1]), "moda": int(moda_n_compras)},
                    "monto_compra": {"media": float(medias[3]), "mediana": float(mediana_compras[0])},
                    "tiempo_navegacion": {"media": float(medias[4]), "mediana": float(mediana_compras[1])}
                }
            }


@mcp.tool()
def analizar_distribucion_ventas() -> Dict[str, Any]:
    #Obtiene la distribución de ventas por mes, método de pago, navegador/canal, boletín y vales
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Ventas por mes
            cur.execute("""
                SELECT 
                    EXTRACT(MONTH FROM cr.fecha_compra)::int AS mes,
                    COUNT(*) AS total_transacciones,
                    ROUND(SUM(cr.monto_compra)::numeric, 2) AS monto_total_mes
                FROM compras_registradas cr
                GROUP BY EXTRACT(MONTH FROM cr.fecha_compra)
                ORDER BY mes;
            """)
            ventas_mes = [{"mes": row[0], "transacciones": row[1], "monto_total": float(row[2])} for row in cur.fetchall()]

            # Distribución por método de pago
            cur.execute("""
                SELECT 
                    mp.descripcion AS metodo_pago,
                    COUNT(*) AS total_transacciones,
                    ROUND(SUM(cr.monto_compra)::numeric, 2) AS total_ventas
                FROM compras_registradas cr
                INNER JOIN catalogo_metodo_pago mp ON cr.id_metodo_pago = mp.id_metodo_pago
                GROUP BY mp.descripcion
                ORDER BY total_ventas DESC;
            """)
            metodos_pago = [{"metodo": row[0], "transacciones": row[1], "total_ventas": float(row[2])} for row in cur.fetchall()]

            # Distribución por navegador / canal
            cur.execute("""
                SELECT 
                    cv.descripcion AS canal,
                    COUNT(*) AS total_transacciones,
                    ROUND(SUM(cr.monto_compra)::numeric, 2) AS total_ventas
                FROM compras_registradas cr
                INNER JOIN catalogo_canal_venta cv ON cr.id_canal = cv.id_canal
                GROUP BY cv.descripcion
                ORDER BY total_transacciones DESC;
            """)
            canales = [{"canal": row[0], "transacciones": row[1], "total_ventas": float(row[2])} for row in cur.fetchall()]

            # Distribución por boletín y vales
            cur.execute("""
                SELECT 
                    p.recibe_boletin,
                    p.utiliza_vale,
                    COUNT(*) AS total_clientes,
                    ROUND(AVG(r.venta_total)::numeric, 2) AS venta_promedio
                FROM preferencias_cliente p
                INNER JOIN resumen_cliente_anual r ON p.id_cliente = r.id_cliente
                GROUP BY p.recibe_boletin, p.utiliza_vale;
            """)
            boletin_vale = [
                {"recibe_boletin": row[0], "utiliza_vale": row[1], "clientes": row[2], "venta_promedio": float(row[3])}
                for row in cur.fetchall()
            ]

            return {
                "distribucion_por_mes": ventas_mes,
                "distribucion_por_metodo_pago": metodos_pago,
                "distribucion_por_canal": canales,
                "distribucion_boletin_vale": boletin_vale
            }


@mcp.tool()
def analizar_tendencias_compras() -> Dict[str, Any]:
    #Identifica tendencias clave
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Mes mayor y menor venta
            cur.execute("""
                SELECT EXTRACT(MONTH FROM fecha_compra)::int AS mes, ROUND(SUM(monto_compra)::numeric, 2) AS total
                FROM compras_registradas
                GROUP BY mes
                ORDER BY total DESC;
            """)
            meses_ordenados = cur.fetchall()
            mes_mayor = {"mes": meses_ordenados[0][0], "total_ventas": float(meses_ordenados[0][1])}
            mes_menor = {"mes": meses_ordenados[-1][0], "total_ventas": float(meses_ordenados[-1][1])}

            # Navegador más y menos usado
            cur.execute("""
                SELECT cv.descripcion, COUNT(*) AS total_compras
                FROM compras_registradas cr
                INNER JOIN catalogo_canal_venta cv ON cr.id_canal = cv.id_canal
                GROUP BY cv.descripcion
                ORDER BY total_compras DESC;
            """)
            canales_ordenados = cur.fetchall()
            canal_mas_usado = {"canal": canales_ordenados[0][0], "compras": canales_ordenados[0][1]}
            canal_menos_usado = {"canal": canales_ordenados[-1][0], "compras": canales_ordenados[-1][1]}

            # Ventas en efectivo / contra entrega (id_metodo_pago = 0)
            cur.execute("""
                SELECT COUNT(*) as transacciones, ROUND(SUM(monto_compra)::numeric, 2) as total_monto
                FROM compras_registradas
                WHERE id_metodo_pago = 0;
            """)
            ventas_efectivo = cur.fetchone()

            # Meses con mayor uso de boletín
            cur.execute("""
                SELECT EXTRACT(MONTH FROM cr.fecha_compra)::int AS mes, COUNT(*) AS compras_con_boletin
                FROM compras_registradas cr
                INNER JOIN preferencias_cliente p ON cr.id_cliente = p.id_cliente
                WHERE p.recibe_boletin = true
                GROUP BY mes
                ORDER BY compras_con_boletin DESC
                LIMIT 3;
            """)
            top_meses_boletin = [{"mes": row[0], "compras": row[1]} for row in cur.fetchall()]

            # Meses con mayor uso de vale
            cur.execute("""
                SELECT EXTRACT(MONTH FROM cr.fecha_compra)::int AS mes, COUNT(*) AS compras_con_vale
                FROM compras_registradas cr
                INNER JOIN preferencias_cliente p ON cr.id_cliente = p.id_cliente
                WHERE p.utiliza_vale = true
                GROUP BY mes
                ORDER BY compras_con_vale DESC
                LIMIT 3;
            """)
            top_meses_vale = [{"mes": row[0], "compras": row[1]} for row in cur.fetchall()]

            return {
                "mes_mayor_venta": mes_mayor,
                "mes_menor_venta": mes_menor,
                "canal_mas_popular": canal_mas_usado,
                "canal_menos_popular": canal_menos_usado,
                "ventas_efectivo_contraentrega": {
                    "transacciones": ventas_efectivo[0],
                    "total_monto": float(ventas_efectivo[1]) if ventas_efectivo[1] else 0.0
                },
                "top_meses_boletin": top_meses_boletin,
                "top_meses_vale": top_meses_vale
            }


@mcp.tool()
def segmentar_clientes(criterio: str = "todos") -> Dict[str, Any]:
    #Segmenta clientes según edad, género, o boletín y vales
    resultado = {}
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if criterio in ("edad", "todos"):
                cur.execute("""
                    SELECT 
                        CASE
                            WHEN c.edad BETWEEN 18 AND 25 THEN '18-25'
                            WHEN c.edad BETWEEN 26 AND 35 THEN '26-35'
                            WHEN c.edad BETWEEN 36 AND 45 THEN '36-45'
                            WHEN c.edad BETWEEN 46 AND 60 THEN '46-60'
                            ELSE '61-79'
                        END AS rango_edad,
                        COUNT(DISTINCT c.id_cliente) AS total_clientes,
                        ROUND(AVG(r.venta_total)::numeric, 2) AS venta_promedio,
                        ROUND(AVG(r.n_compras)::numeric, 2) AS compras_promedio
                    FROM clientes c
                    INNER JOIN resumen_cliente_anual r ON c.id_cliente = r.id_cliente
                    GROUP BY rango_edad
                    ORDER BY rango_edad;
                """)
                resultado["segmentacion_edad"] = [
                    {"rango": row[0], "clientes": row[1], "venta_promedio": float(row[2]), "compras_promedio": float(row[3])}
                    for row in cur.fetchall()
                ]

            if criterio in ("genero", "todos"):
                cur.execute("""
                    SELECT 
                        g.descripcion AS genero,
                        COUNT(DISTINCT c.id_cliente) AS total_clientes,
                        ROUND(AVG(r.venta_total)::numeric, 2) AS venta_promedio,
                        ROUND(AVG(r.n_compras)::numeric, 2) AS compras_promedio
                    FROM clientes c
                    INNER JOIN catalogo_genero g ON c.id_genero = g.id_genero
                    INNER JOIN resumen_cliente_anual r ON c.id_cliente = r.id_cliente
                    GROUP BY g.descripcion;
                """)
                resultado["segmentacion_genero"] = [
                    {"genero": row[0], "clientes": row[1], "venta_promedio": float(row[2]), "compras_promedio": float(row[3])}
                    for row in cur.fetchall()
                ]

            if criterio in ("boletin_vale", "todos"):
                cur.execute("""
                    SELECT 
                        p.recibe_boletin,
                        p.utiliza_vale,
                        COUNT(DISTINCT p.id_cliente) AS total_clientes,
                        ROUND(AVG(r.venta_total)::numeric, 2) AS venta_promedio,
                        ROUND(AVG(r.n_compras)::numeric, 2) AS compras_promedio
                    FROM preferencias_cliente p
                    INNER JOIN resumen_cliente_anual r ON p.id_cliente = r.id_cliente
                    GROUP BY p.recibe_boletin, p.utiliza_vale;
                """)
                resultado["segmentacion_boletin_vale"] = [
                    {"boletin": row[0], "vale": row[1], "clientes": row[2], "venta_promedio": float(row[3]), "compras_promedio": float(row[4])}
                    for row in cur.fetchall()
                ]

    return resultado


@mcp.tool()
def calcular_correlaciones() -> Dict[str, Any]:
    #Calcula las correlaciones estadísticas solicitadas
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Correlación edad vs venta total
            cur.execute("""
                SELECT ROUND(CORR(c.edad, r.venta_total)::numeric, 4) AS corr_edad_venta
                FROM clientes c
                INNER JOIN resumen_cliente_anual r ON c.id_cliente = r.id_cliente;
            """)
            corr_edad_venta = cur.fetchone()[0]

            # Correlación boletin vs vale
            cur.execute("""
                SELECT ROUND(CORR(recibe_boletin::int, utiliza_vale::int)::numeric, 4) AS corr_boletin_vale
                FROM preferencias_cliente;
            """)
            corr_boletin_vale = cur.fetchone()[0]

            # Relación género y método de pago
            cur.execute("""
                SELECT 
                    g.descripcion AS genero,
                    mp.descripcion AS metodo_pago,
                    COUNT(*) AS transacciones
                FROM clientes c
                INNER JOIN catalogo_genero g ON c.id_genero = g.id_genero
                INNER JOIN compras_registradas cr ON c.id_cliente = cr.id_cliente
                INNER JOIN catalogo_metodo_pago mp ON cr.id_metodo_pago = mp.id_metodo_pago
                GROUP BY g.descripcion, mp.descripcion
                ORDER BY genero, transacciones DESC;
            """)
            genero_pago = [
                {"genero": row[0], "metodo_pago": row[1], "transacciones": row[2]}
                for row in cur.fetchall()
            ]

            return {
                "correlacion_edad_venta_total": float(corr_edad_venta) if corr_edad_venta is not None else 0.0,
                "correlacion_boletin_vale": float(corr_boletin_vale) if corr_boletin_vale is not None else 0.0,
                "distribucion_genero_metodo_pago": genero_pago,
                "interpretacion": {
                    "edad_venta": "Valores cercanos a 0 indican ausencia de relación lineal fuerte entre la edad y el monto total gastado.",
                    "boletin_vale": "Mide el grado de asociación entre clientes suscritos al boletín y el canje de vales."
                }
            }


@mcp.tool()
def consultar_graficas() -> Dict[str, Any]:
    #Retorna el catálogo de gráficos disponibles generados para el informe
    graficas = [
        {
            "id": "g1",
            "archivo": "salida/graficas/g1_segmentacion_edad_venta.png",
            "titulo": "Distribución de Venta Total por Rango de Edad",
            "tipo": "Boxplot",
            "descripcion": "Muestra la dispersión y mediana de compras anuales por cada grupo etario."
        },
        {
            "id": "g2",
            "archivo": "salida/graficas/g2_segmentacion_edad_compras.png",
            "titulo": "Número Promedio de Compras por Rango de Edad",
            "tipo": "Gráfico de Barras",
            "descripcion": "Compara el número promedio de compras anuales según el rango de edad."
        },
        {
            "id": "g3",
            "archivo": "salida/graficas/g3_segmentacion_genero.png",
            "titulo": "Segmentación y Comportamiento por Género",
            "tipo": "Gráfico de Barras Agrupadas",
            "descripcion": "Compara ventas promedio y frecuencia de compra entre clientes masculinos y femeninos."
        },
        {
            "id": "g4",
            "archivo": "salida/graficas/g4_segmentacion_boletin_vale.png",
            "titulo": "Impacto de Boletines y Vales en las Ventas",
            "tipo": "Gráfico de Barras",
            "descripcion": "Analiza la venta promedio según suscripción a boletín y uso de vales de descuento."
        },
        {
            "id": "g5",
            "archivo": "salida/graficas/g5_correlacion_edad_venta.png",
            "titulo": "Correlación entre Edad y Venta Total",
            "tipo": "Gráfico de Dispersión (Scatter Plot)",
            "descripcion": "Diagrama de dispersión con línea de regresión para evaluar correlación entre edad y venta total."
        },
        {
            "id": "g6",
            "archivo": "salida/graficas/g6_correlacion_genero_metodopago.png",
            "titulo": "Método de Pago Preferido por Género",
            "tipo": "Gráfico de Barras Apiladas / 100%",
            "descripcion": "Distribución porcentual de los métodos de pago preferidos por cada género."
        },
        {
            "id": "g7",
            "archivo": "salida/graficas/g7_correlacion_boletin_vale.png",
            "titulo": "Asociación entre Uso de Boletín y Canje de Vales",
            "tipo": "Mapa de Calor (Heatmap)",
            "descripcion": "Matriz de contingencia y mapa de calor de clientes según suscripción a boletín y uso de vales."
        }
    ]
    return {"total_graficas": len(graficas), "graficas": graficas}


@mcp.tool()
def ejecutar_consulta_sql(consulta_sql: str) -> Dict[str, Any]:
    #Ejecuta una consulta SQL SELECT segura en la base de datos de Supabase para responder preguntas analíticas personalizadas.
    #Solo se permiten sentencias SELECT.
    consulta_limpia = consulta_sql.strip().lower()
    if not consulta_limpia.startswith("select"):
        return {"error": "Solo se permiten consultas de lectura (SELECT)."}

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(consulta_sql)
                columnas = [desc[0] for desc in cur.description] if cur.description else []
                filas = cur.fetchall()
                # Limitar a máximo 50 filas para respuesta limpia
                resultados = [dict(zip(columnas, fila)) for fila in filas[:50]]
                return {
                    "total_filas": len(filas),
                    "filas_mostradas": len(resultados),
                    "columnas": columnas,
                    "datos": resultados
                }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Ejecuta el servidor MCP sobre stdio
    mcp.run()
