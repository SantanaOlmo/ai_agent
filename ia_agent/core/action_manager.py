import json
from pathlib import Path

def ejecutar_accion(respuesta_json, base_path=None):
    """
    Ejecuta las acciones indicadas por la IA.
    Soporta:
      - Acciones simples o listas múltiples.
      - Rutas como str o lista de strings.
      - Crear, escribir, leer, borrar y hablar.
    Usa el campo 'type' ('file' o 'directory') para las acciones de creación.
    """
    resultado = {"status": "ok", "acciones": []}

    if base_path is None:
        base_path = Path(__file__).resolve().parent.parent

    if not respuesta_json:
        print("⚠️ No se recibió respuesta de la IA.")
        return {"status": "error", "acciones": []}

    try:
        data = json.loads(respuesta_json) if isinstance(respuesta_json, str) else respuesta_json
    except json.JSONDecodeError:
        print(f"💬 IA dice (texto plano): {respuesta_json}")
        return {"status": "ok", "acciones": [{"status": "ok", "mensaje": respuesta_json, "contenido": {}}]}

    # Soporta formato con "actions", lista directa o acción única
    if isinstance(data, dict) and "actions" in data:
        acciones = data["actions"]
    elif isinstance(data, list):
        acciones = data
    else:
        acciones = [data]

    for accion in acciones:
        accion_res = {"status": "ok", "mensaje": "", "contenido": {}}
        tipo = accion.get("action")
        rutas = accion.get("ruta")
        contenido = accion.get("contenido", "")
        tipo_elemento = accion.get("type")  # 'file' o 'directory'

        if isinstance(rutas, str):
            rutas = [rutas]
        elif not isinstance(rutas, list):
            rutas = []

        if tipo in ["leer", "crear", "escribir", "borrar"]:
            for ruta in rutas:
                ruta_final = (base_path / Path(ruta)).resolve()
                try:
                    if tipo == "leer":
                        if ruta_final.exists():
                            with open(ruta_final, "r", encoding="utf-8") as f:
                                contenido_archivo = f.read()
                            accion_res["contenido"][str(ruta_final)] = contenido_archivo
                            print(f"📖 Archivo leído: {ruta_final}")
                        else:
                            raise FileNotFoundError(f"Archivo no encontrado: {ruta_final}")

                    elif tipo in ["crear", "escribir"]:
                        if not tipo_elemento:
                            raise ValueError(f"La acción '{tipo}' requiere 'type' ('file' o 'directory').")

                        ruta_final.parent.mkdir(parents=True, exist_ok=True)

                        if tipo_elemento == "directory":
                            ruta_final.mkdir(parents=True, exist_ok=True)
                            accion_res["mensaje"] = f"📁 Carpeta creada: {ruta_final}"

                        elif tipo_elemento == "file":
                            with open(ruta_final, "w", encoding="utf-8") as f:
                                f.write(contenido or "")
                            accion_res["mensaje"] = f"📝 Archivo {'actualizado' if tipo=='escribir' else 'creado'}: {ruta_final}"

                        else:
                            raise ValueError(f"Tipo desconocido: {tipo_elemento}")

                        print(accion_res["mensaje"])

                    elif tipo == "borrar":
                        if ruta_final.exists():
                            if ruta_final.is_dir():
                                for sub in ruta_final.rglob("*"):
                                    if sub.is_file():
                                        sub.unlink()
                                ruta_final.rmdir()
                                accion_res["mensaje"] = f"🗑️ Carpeta borrada: {ruta_final}"
                            else:
                                ruta_final.unlink()
                                accion_res["mensaje"] = f"🗑️ Archivo borrado: {ruta_final}"
                            print(accion_res["mensaje"])
                        else:
                            raise FileNotFoundError(f"No encontrado: {ruta_final}")

                except Exception as e:
                    accion_res["status"] = "error"
                    accion_res["mensaje"] = str(e)
                    print(f"❌ Error en acción '{tipo}': {e}")

        elif tipo == "hablar":
            mensaje = accion.get("mensaje") or contenido
            print(f"💬 IA dice: {mensaje}")
            accion_res["mensaje"] = mensaje

        else:
            accion_res["status"] = "error"
            accion_res["mensaje"] = f"Acción desconocida: {tipo}"
            print(f"❌ {accion_res['mensaje']}")

        resultado["acciones"].append(accion_res)

    return resultado
