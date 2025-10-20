from pathlib import Path
from datetime import datetime

def actualizar_readme(contenidos, mensaje_inicial="Documentación generada automáticamente", base_path="."):
    """
    Actualiza README.md con los contenidos de archivos.
    contenidos: dict de la forma { "archivo": "contenido" }
    """
    if not contenidos:
        print("⚠️ No hay contenidos para actualizar README.")
        return

    readme_path = Path(base_path) / "README.md"

    lines = [f"# Proyecto actualizado automáticamente ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n",
             f"{mensaje_inicial}\n\n"]

    for archivo, contenido in contenidos.items():
        lines.append(f"## {archivo}\n")
        lines.append("```python\n" if archivo.endswith(".py") else "```\n")
        lines.append((contenido or "") + "\n")
        lines.append("```\n\n")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"📄 README.md actualizado con {len(contenidos)} archivos.")
