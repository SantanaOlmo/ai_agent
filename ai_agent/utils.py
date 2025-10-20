#ai_agent/utils.py
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
    schema_path = Path.cwd() / "config" / "ai_schema.json"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
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
    
    # 🔥 INSTRUCCIONES MEJORADAS: Enfatizar el uso del contenido leído
    instrucciones_ai = (
        f"{schema['instructions']}\n\n"
        f"🔥 REGLA CRÍTICA: Si en el contexto hay archivos leídos (sección '📂 ARCHIVOS LEÍDOS'),\n"
        f"DEBES usar EXACTAMENTE ese contenido cuando crees o modifiques archivos relacionados.\n"
        f"NO inventes contenido nuevo si ya existe contenido leído relevante.\n\n"
        f"Acciones permitidas: {', '.join(schema['actions_allowed'])}\n"
        f"Ejemplo acción individual:\n{json.dumps(schema['example_single_action'], indent=2)}\n"
        f"Ejemplo acciones múltiples:\n{json.dumps(schema['example_multiple_actions'], indent=2)}\n\n"
    )
    
    prompt = (
        f"{instrucciones_ai}"
        f"Contexto del proyecto:\n{contexto}\n\n"
        f"Petición del usuario:\n{instruccion}"
    )

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return limpiar_respuesta(response.text)
    except Exception as e:
        print("❌ Error al comunicarse con Gemini:", e)
        return None

def generar_estructura_proyecto(base_path: Path):
    """
    Genera la estructura del proyecto en un formato de diccionario, 
    excluyendo directorios y archivos comunes irrelevantes (venv, .git, etc.).
    """
    EXCLUIR_DIR = ['.git', '__pycache__', 'venv', 'node_modules', '.vscode', '.idea']
    EXCLUIR_ARCHIVOS = ['.DS_Store', 'project_structure.json', 'README.md', '.env', 'Pipfile.lock']

    estructura = {}
    
    if not base_path.is_dir():
        return {"error": "Ruta base no es un directorio válido."}

    def _recorrer_directorio(ruta_actual: Path):
        elementos = {}
        for item in ruta_actual.iterdir():
            if item.is_dir() and item.name in EXCLUIR_DIR:
                continue
            if item.is_file() and item.name in EXCLUIR_ARCHIVOS:
                continue

            if item.is_dir():
                elementos[item.name] = _recorrer_directorio(item)
            else:
                elementos[item.name] = "file" 

        return elementos

    estructura[base_path.name] = _recorrer_directorio(base_path)

    output_path = base_path / "project_structure.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(estructura, f, indent=2, ensure_ascii=False)
    
    return estructura