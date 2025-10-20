import json
from pathlib import Path
import shutil # Necesario para la eliminación recursiva de carpetas

def ejecutar_accion(respuesta_json, base_path=None):
    """Ejecuta las acciones indicadas por la IA (crear, escribir, leer, borrar)."""

    resultado = {"status": "ok", "acciones": []}

    # 🔑 Asegurar que base_path es la ruta correcta del proyecto.
    if base_path is None:
        base_path = Path.cwd()

    if not respuesta_json:
        return {"status": "error", "acciones": []}

    # Parsear JSON y normalizar a una lista de acciones
    try:
        data = json.loads(respuesta_json) if isinstance(respuesta_json, str) else respuesta_json
    except json.JSONDecodeError:
        return {"status": "ok", "acciones": [{"status": "ok", "mensaje": respuesta_json, "contenido": {}}]}

    if isinstance(data, dict) and "actions" in data:
        acciones = data["actions"]
    elif isinstance(data, list):
        acciones = data
    else:
        acciones = [data]

    # Mapeo de acciones de inglés a español
    traducciones = {
        "read": "leer", "write": "escribir", "create": "crear",
        "delete": "borrar", "speak": "hablar"
    }

    for accion in acciones:
        accion_res = {"status": "ok", "mensaje": "", "contenido": {}}
        tipo = accion.get("action")
        tipo = traducciones.get(tipo, tipo)

        rutas = accion.get("ruta")
        contenido = accion.get("contenido", "")
        tipo_elemento = accion.get("type") 

        if isinstance(rutas, str):
            rutas = [rutas]
        elif not isinstance(rutas, list):
            rutas = []

        if tipo in ["leer", "crear", "escribir", "borrar"]:
            for ruta in rutas:
                # Crear la ruta absoluta combinando base_path con la ruta relativa
                ruta_final = (Path(base_path) / Path(ruta.strip("/\\"))).resolve()

                # Evitar escribir fuera del proyecto
                if not str(ruta_final).startswith(str(base_path)):
                    accion_res["status"] = "error"
                    accion_res["mensaje"] = f"Ruta fuera del proyecto: {ruta_final}"
                    resultado["acciones"].append(accion_res)
                    continue

                if tipo in ["crear", "escribir"] and not tipo_elemento:
                    tipo_elemento = "file" if ruta_final.suffix else "directory"

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
                        # Crear directorios padres si son necesarios
                        ruta_final.parent.mkdir(parents=True, exist_ok=True)

                        if tipo_elemento == "directory":
                            ruta_final.mkdir(parents=True, exist_ok=True)
                            accion_res["mensaje"] = f"📁 Carpeta creada: {ruta_final}"
                            # 🟢 Muestra la ruta de forma clara
                            print(f"✅ Carpeta creada en: {ruta_final}")

                        elif tipo_elemento == "file":
                            with open(ruta_final, "w", encoding="utf-8") as f:
                                f.write(contenido or "")
                            accion_res["mensaje"] = f"📝 Archivo {'actualizado' if tipo=='escribir' else 'creado'}: {ruta_final}"
                            # 🟢 Muestra la ruta de forma clara
                            print(f"✅ Archivo creado/actualizado en: {ruta_final}")
                        
                        else:
                            raise ValueError(f"Tipo desconocido: {tipo_elemento}")

                    elif tipo == "borrar":
                        if ruta_final.exists():
                            if ruta_final.is_dir():
                                # Lógica para borrar carpeta recursivamente
                                shutil.rmtree(ruta_final)
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