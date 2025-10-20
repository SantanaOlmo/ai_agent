#ai_agent/main.py
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
BASE_DIR = Path.cwd()
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

    base_path_proyecto = BASE_DIR
    estructura = generar_estructura_proyecto(base_path_proyecto) 
    
    # 🔥 HISTORIAL MEJORADO: Ahora incluirá el contenido de archivos leídos
    historial = (
        f"Contexto inicial del proyecto (estructura de archivos):\n"
        f"{json.dumps(estructura, indent=2)}\n\n"
        "Instrucciones importantes:\n"
        "- Cuando leas un archivo, DEBES usar su contenido en las siguientes acciones.\n"
        "- Si te pido crear algo basado en un archivo leído, usa EXACTAMENTE el contenido leído.\n"
        "- Respeta el formato y estructura del contenido original.\n\n"
    )
    
    # 📁 Memoria de archivos leídos (clave: ruta, valor: contenido)
    memoria_archivos = {}
    
    print("🔹 base_path detectado (proyecto actual):", base_path_proyecto)
    print("🔹 Archivos en la raíz del proyecto:", list(base_path_proyecto.iterdir()))

    while True:
        instruccion = input("\n¿Qué quieres que haga la IA? (escribe 'salir' para terminar): ")
        
        if instruccion.lower() == "salir":
            resumen = input("\nHaz un resumen de lo hablado y avances del proyecto: ")
            historial += f"\nUsuario: {resumen}\n"
            break
            
        if not instruccion.strip():
            print("⚠️ Introduce una instrucción o escribe 'salir'.")
            continue
        
        # 🔥 PASO 1: Agregar instrucción al historial
        historial += f"\nUsuario: {instruccion}\n"
        
        # 🔥 PASO 2: Si hay archivos en memoria, inyectarlos en el contexto
        contexto_con_archivos = historial
        if memoria_archivos:
            contexto_con_archivos += "\n📂 ARCHIVOS LEÍDOS RECIENTEMENTE (USA ESTE CONTENIDO):\n"
            for ruta, contenido in memoria_archivos.items():
                # Limitar contenido si es muy largo (opcional)
                contenido_mostrar = contenido[:5000] + "..." if len(contenido) > 5000 else contenido
                contexto_con_archivos += f"\n--- {ruta} ---\n{contenido_mostrar}\n"
        
        # Enviar a la IA con el contexto enriquecido
        respuesta_ia = enviar_a_ia(instruccion, contexto=contexto_con_archivos)
        
        print("\n🟢 RESPUESTA DE LA IA:\n", respuesta_ia)

        # 🔥 PASO 3: Ejecutar acciones
        resultado = ejecutar_accion(respuesta_ia, base_path=base_path_proyecto)
        print("\n🔹 Resumen de acciones ejecutadas:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        # 🔥 PASO 4: Extraer contenidos leídos y agregarlos a la MEMORIA
        contenidos_leidos = {}
        for accion in resultado.get("acciones", []):
            if accion.get("status") == "ok" and "contenido" in accion:
                contenidos_leidos.update(accion["contenido"])
        
        # Actualizar memoria de archivos leídos
        if contenidos_leidos:
            memoria_archivos.update(contenidos_leidos)
            print(f"\n💾 {len(contenidos_leidos)} archivo(s) agregado(s) a la memoria de la IA")
            
            # 🔥 AGREGAR contenido al historial permanentemente
            historial += "\n📂 Archivos leídos (contenido disponible para uso):\n"
            for ruta, contenido in contenidos_leidos.items():
                # Guardar solo un resumen en el historial para no saturarlo
                resumen_contenido = contenido[:500] + "..." if len(contenido) > 500 else contenido
                historial += f"\n--- {ruta} ---\n{resumen_contenido}\n"
            
            # Actualizar README
            actualizar_readme(contenidos_leidos, base_path=BASE_DIR)

        # Actualizar estructura si hubo cambios
        if resultado.get("status") == "ok":
            estructura = generar_estructura_proyecto(base_path_proyecto)
            historial += f"\n[Estructura actualizada]\n{json.dumps(estructura, indent=2)}\n"

        # Guardar respuesta de IA en historial
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