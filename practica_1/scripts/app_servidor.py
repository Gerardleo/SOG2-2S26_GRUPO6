from __future__ import annotations

import asyncio
import os
import re
import sys
import warnings
from pathlib import Path
from typing import AsyncGenerator, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Silenciar advertencias internas de Google ADK
warnings.filterwarnings("ignore")

# Asegurar que el directorio de scripts esté en sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Cargar variables de entorno desde practica_1/.env
ROOT = SCRIPTS_DIR.parent
load_dotenv(ROOT / ".env")

MCP_SERVER_SCRIPT = str(Path(__file__).resolve().parent / "mcp_server.py")
PYTHON_EXE = sys.executable

app = FastAPI(title="SOG2 Sales Analytics AI Assistant", version="1.0.0")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
STATIC_DIR = ROOT / "web" / "static"
TEMPLATES_DIR = ROOT / "web" / "templates"
GRAFICAS_DIR = ROOT / "salida" / "graficas"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if GRAFICAS_DIR.exists():
    app.mount("/graficas", StaticFiles(directory=str(GRAFICAS_DIR)), name="graficas")


# Esquema de solicitud del chat
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "sesion_predeterminada"


# Estado global del Agente y Runner de ADK
_runner = None
_agent = None


async def get_agent_runner():
    """Inicializa de forma diferida el Agente Google ADK y el McpToolset."""
    global _runner, _agent
    if _runner is not None:
        return _runner

    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp.client.stdio import StdioServerParameters

    SYSTEM_PROMPT = """Eres un Analista de Datos Senior experto en inteligencia de negocios y ventas online para la empresa de la Práctica 1 (SOG2).
Tu misión es asistir a los directivos y analistas respondiendo consultas en lenguaje natural basándote en los datos de la base de datos SQL y análisis realizados.

Tienes acceso a un conjunto de herramientas del Servidor MCP que te permiten:
1. 'obtener_estadisticas_descriptivas': Estadísticas básicas (media, mediana, moda) de variables numéricas (Punto 2.b).
2. 'analizar_distribucion_ventas': Distribución de ventas por mes, método de pago, canales y boletines (Punto 2.c).
3. 'analizar_tendencias_compras': Meses extremos, canales populares, ventas en efectivo y uso de vales/boletines (Punto 3).
4. 'segmentar_clientes': Segmentación por edad, género, y uso de boletines/vales (Punto 4).
5. 'calcular_correlaciones': Correlación edad-venta, género-método de pago y boletín-vales (Punto 5).
6. 'consultar_graficas': Consultar las 7 gráficas disponibles y sus rutas/descripciones (Punto 6).
7. 'ejecutar_consulta_sql': Ejecutar consultas SELECT personalizadas en Supabase cuando se requieran datos específicos adicionales.

Instrucciones:
- Siempre responde en español con un tono profesional, claro y estructurado (usando tablas markdown, viñetas y resaltados en negrita).
- Cuando el usuario pregunte sobre estadísticas, tendencias o segmentación, invoca las herramientas correspondientes y explica el significado del negocio.
- Si te piden recomendaciones o interpretaciones, ofrece conclusiones analíticas sólidas basadas en los datos obtenidos.
- Cuando menciones o sugieras gráficos, incluye el nombre del archivo de la imagen (ejemplo: `salida/graficas/g1_segmentacion_edad_venta.png` o `g1_segmentacion_edad_venta.png`) para que el sistema web renderice automáticamente la gráfica en la interfaz.
"""

    server_params = StdioServerParameters(
        command=PYTHON_EXE,
        args=[MCP_SERVER_SCRIPT],
        env=dict(os.environ),
    )
    connection_params = StdioConnectionParams(server_params=server_params)
    mcp_toolset = McpToolset(connection_params=connection_params)

    _agent = Agent(
        model="gemini-3.5-flash-lite",
        name="AnalistaVentasOnline",
        instruction=SYSTEM_PROMPT,
        tools=[mcp_toolset],
    )

    _runner = InMemoryRunner(agent=_agent, app_name="sog2_web_app")
    return _runner


@app.get("/")
async def serve_home():
    """Sirve la página principal del chat web."""
    index_path = TEMPLATES_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html no encontrado")
    return FileResponse(str(index_path))


@app.get("/api/graficas")
async def list_graficas():
    """Retorna la lista de gráficas disponibles para la galería del frontend."""
    from mcp_server import consultar_graficas
    try:
        return consultar_graficas()
    except Exception as e:
        return {"error": str(e), "graficas": []}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Endpoint de chat con streaming de respuesta para el frontend."""
    from google.genai import types

    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío.")

    runner = await get_agent_runner()
    session_id = request.session_id or "sesion_predeterminada"

    # Asegurar que la sesión exista en el SessionService
    session = await runner.session_service.get_session(
        app_name="sog2_web_app",
        user_id="usuario_web",
        session_id=session_id,
    )
    if session is None:
        session = await runner.session_service.create_session(
            app_name="sog2_web_app",
            user_id="usuario_web",
            session_id=session_id,
        )

    content = types.Content(parts=[types.Part.from_text(text=user_message)])

    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            async for event in runner.run_async(
                user_id="usuario_web",
                session_id=session_id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield part.text
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                match = re.search(r"retry in ([\d\.]+)s", err_str) or re.search(r"retryDelay': '(\d+)s'", err_str)
                delay = float(match.group(1)) if match else 40.0
                yield f"\n\n**Límite de cuota alcanzado (Rate Limit 429):** La API gratuita de Gemini requiere una pausa de **{int(delay)} segundos** antes de procesar más peticiones."
            else:
                yield f"\n\n[Error al procesar la respuesta: {err_str}]"

    return StreamingResponse(stream_generator(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("  INICIANDO INTERFAZ WEB DE ANALÍTICA (SOG2 Grupo 6)")
    print("  Abra su navegador en: http://localhost:8000")
    print("=" * 65 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
