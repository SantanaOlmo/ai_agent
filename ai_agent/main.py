import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

from ai_agent.utils import enviar_a_ia, generar_estructura_proyecto
from ai_agent.core.action_manager import ejecutar_accion
from ai_agent.core.readme_manager import actualizar_readme
from ai_agent.key_manager import pedir_api_key
from ai_agent.core.updateREADME import push_readme_local_to_github

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = "gemini-2.5-flash"

def validar_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        model.generate_content("Validación de API Key")
        return True
    except Exception as e:
        print(f"❌ Error al validar la API Key: {e}")
        return False

def iniciar_mcp(api_key=None):
    if not api_key:
        api_key = pedir_api_key()
    if not validar_api_key(api_key):
        print("❌ La API Key no es válida. Intenta otra vez.")
        return None
    genai.configure(api_key=api_key)
    print("✅ API Key válida. MCP listo para usar.")
    return api_key

def main():
    print("\n=== MCP con Google Gemini ===")
    api_key = iniciar_mcp()
    if not api_key:
        return

    estructura = generar_estructura_proyecto(BASE_DIR.parent)
    historial = f"Contexto inicial del proyecto (estructura de archivos):\n{json.dumps(estructura, indent=2)}\n"

    while True:
        instruccion = input("\n¿Qué quieres que haga la IA? (escribe 'salir' para terminar): ")
        if instruccion.lower() == "salir":
            resumen = input("\nHaz un resumen de lo hablado y avances del proyecto: ")
            historial += f"\nUsuario: {resumen}\n"
            break

        historial += f"\nUsuario: {instruccion}\n"
        respuesta_ia = enviar_a_ia(instruccion, contexto=historial)
        print("\n🟢 RESPUESTA CRUDA DE LA IA:\n", respuesta_ia)

        resultado = ejecutar_accion(respuesta_ia, base_path=BASE_DIR.parent)
        print("\n🔹 Resumen de acciones ejecutadas:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        contenidos_leidos = {}
        for accion in resultado.get("acciones", []):
            if accion.get("status") == "ok" and "contenido" in accion:
                contenidos_leidos.update(accion["contenido"])

        if contenidos_leidos:
            actualizar_readme(contenidos_leidos, base_path=BASE_DIR)

        if resultado.get("status") == "ok":
            estructura = generar_estructura_proyecto(BASE_DIR.parent)
            historial += f"\n[Actualización de estructura]:\n{json.dumps(estructura, indent=2)}\n"

        historial += f"IA: {respuesta_ia}\n"

    # Preguntar si subir README a GitHub
    subir = input("\n¿Quieres subir README.md actualizado a GitHub? (s/n): ").lower()
    if subir == "s":
        try:
            push_readme_local_to_github()
        except Exception as e:
            print(f"❌ Error al subir README: {e}")

if __name__ == "__main__":
    main()
