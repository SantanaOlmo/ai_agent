import os
import json
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
API_KEY = os.getenv("IA_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def limpiar_respuesta(respuesta):
    if not respuesta:
        return None
    respuesta = respuesta.strip()
    if respuesta.startswith("```"):
        respuesta = respuesta.split("\n", 1)[-1]
    if respuesta.endswith("```"):
        respuesta = respuesta.rsplit("```", 1)[0]
    return respuesta.strip()

def cargar_ai_schema():
    from pathlib import Path
    import json

    schema_path = Path(__file__).parent / "config" / "ai_schema.json"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Solo para fallback, incluye type para no romper action_manager
        return {
            "instructions": "Responde SIEMPRE en JSON válido...",
            "actions_allowed": ["leer", "escribir", "crear", "borrar", "hablar"],
            "example_single_action": {"action": "crear", "ruta": "archivo.txt", "type": "file"},
            "example_multiple_actions": {
                "actions": [
                    {"action": "crear", "ruta": "carpeta/", "type": "directory"},
                    {"action": "crear", "ruta": "carpeta/archivo.py", "type": "file", "contenido": "print('Hola mundo')"},
                    {"action": "hablar", "mensaje": "Estructura base creada."}
                ]
            }
        }


def enviar_a_ia(instruccion, contexto=""):
    schema = cargar_ai_schema()
    instrucciones_ai = (
        f"{schema['instructions']}\n\n"
        f"Acciones permitidas: {', '.join(schema['actions_allowed'])}\n"
        f"Ejemplo acción individual:\n{json.dumps(schema['example_single_action'])}\n"
        f"Ejemplo acciones múltiples:\n{json.dumps(schema['example_multiple_actions'])}\n\n"
    )
    prompt = f"{instrucciones_ai}Contexto del proyecto:\n{contexto}\n\nPetición del usuario:\n{instruccion}"

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return limpiar_respuesta(response.text)
    except Exception as e:
        print("❌ Error al comunicarse con Gemini:", e)
        return None

def generar_estructura_proyecto(base_path=None):
    from pathlib import Path
    if base_path is None:
        base_path = Path.cwd()
    estructura = {}
    for ruta in base_path.rglob("*"):
        partes = ruta.relative_to(base_path).parts
        actual = estructura
        for p in partes[:-1]:
            actual = actual.setdefault(p, {})
        if ruta.is_file():
            actual[partes[-1]] = {"type": "file"}
        elif ruta.is_dir():
            actual[partes[-1]] = {"type": "directory"}
    with open(base_path / "project_structure.json", "w", encoding="utf-8") as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)
    print("📦 Estructura del proyecto actualizada en project_structure.json")
    return estructura
