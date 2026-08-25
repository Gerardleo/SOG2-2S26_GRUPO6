from __future__ import annotations

import asyncio
import os
import sys
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Silenciar advertencias internas de características experimentales de ADK
warnings.filterwarnings("ignore")

# Cargar variables de entorno desde practica_1/.env
PRACTICA_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PRACTICA_DIR / ".env")

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("\n[AVISO] No se encontró GEMINI_API_KEY en practica_1/.env.")
    print("Por favor, agregue 'GEMINI_API_KEY=su_api_key_aqui' en practica_1/.env.\n")

MCP_SERVER_SCRIPT = str(Path(__file__).resolve().parent / "mcp_server.py")
PYTHON_EXE = sys.executable

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
- Siempre responde en español con un tono profesional, claro y estructurado (usando tablas, viñetas y resaltados en negrita).
- Cuando el usuario pregunte sobre estadísticas, tendencias o segmentación, invoca las herramientas correspondientes y explica el significado del negocio.
- Si te piden recomendaciones o interpretaciones, ofrece conclusiones analíticas sólidas basadas en los datos obtenidos.
- Cuando menciones gráficos, indica el nombre del archivo (ej. `salida/graficas/g1_segmentacion_edad_venta.png`) para que el usuario sepa dónde encontrarlo.
"""


async def main():
    print("=" * 72)
    print("   AGENTE CONVERSACIONAL DE ANÁLISIS DE VENTAS ONLINE   ")
    print("=" * 72)

    try:
        from google.adk.agents import Agent
        from google.adk.runners import InMemoryRunner
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp.client.stdio import StdioServerParameters
        from google.genai import types

        # Configurar conexión MCP por Stdio hacia mcp_server.py
        server_params = StdioServerParameters(
            command=PYTHON_EXE,
            args=[MCP_SERVER_SCRIPT],
            env=dict(os.environ),
        )
        connection_params = StdioConnectionParams(server_params=server_params)

        print("[INFO] Conectando con el Servidor MCP...")
        mcp_toolset = McpToolset(connection_params=connection_params)

        # Crear el agente de Google ADK con modelo Gemini Flash
        agent = Agent(
            model="gemini-3.5-flash-lite",
            name="AnalistaVentasOnline",
            instruction=SYSTEM_PROMPT,
            tools=[mcp_toolset],
        )

        runner = InMemoryRunner(agent=agent, app_name="sog2_chat_app")

        # Crear sesión persistente de conversación
        session = await runner.session_service.create_session(
            app_name="sog2_chat_app",
            user_id="analista_junior"
        )
        session_id = session.id

        print("[INFO] Servidor MCP conectado exitosamente.")
        print("[INFO] Agente IA listo para interactuar.")
        print("💡 Escribe tu consulta o 'salir' para terminar.\n")

        # Bucle conversacional interactivo
        while True:
            try:
                pregunta = input("\n[Usuario] > ").strip()
                if not pregunta:
                    continue
                if pregunta.lower() in ("salir", "exit", "quit"):
                    print("\nSesión finalizada. ¡Éxitos en tu análisis!")
                    break

                print("\n[Analista IA pensando...]\n")
                content = types.Content(parts=[types.Part.from_text(text=pregunta)])

                async for event in runner.run_async(
                    user_id="analista_junior",
                    session_id=session_id,
                    new_message=content,
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                print(part.text, end="", flush=True)

                print()  # Salto de línea al finalizar la respuesta

            except KeyboardInterrupt:
                print("\n\nSesión interrumpida.")
                break
            except Exception as err:
                print(f"\n[Error durante la consulta]: {err}")

    except ModuleNotFoundError as e:
        print(f"\n[Error de Dependencia]: {e}")
        print("Instale dependencias con: pip install -r practica_1/requirements.txt")
    except Exception as e:
        print(f"\n[Error]: {e}")


if __name__ == "__main__":
    asyncio.run(main())
