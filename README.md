# ai_agent

MCP profesional con **Google Gemini** y agente autónomo.

## Características

- Gestión de múltiples API Keys cifradas en el home del usuario.
- Menú interactivo para elegir una clave existente o ingresar una nueva.
- Validación automática de la API Key antes de usarla.
- Ejecución directa desde terminal con comando `ai_agent`.
- Agente autónomo que ejecuta acciones sobre archivos, carpetas y actualiza README automáticamente.

## Instalación

Se recomienda crear un entorno virtual antes de instalar el proyecto:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# Actualizar pip y setuptools
python -m pip install --upgrade pip setuptools
```

Luego instala el proyecto directamente desde GitHub:

```bash
pip install git+https://github.com/SantanaOlmo/ai_agent.git
```

## Uso

```bash
ai_agent
```

- Selecciona una API Key existente o ingresa una nueva.
- Se realizará una validación y el MCP estará listo.
- Luego puedes dar instrucciones a la IA para crear, leer, escribir, borrar archivos o carpetas.

## Aviso Legal

Este proyecto requiere una clave de API propia de Google Gemini.  
No se incluye ninguna clave en el repositorio.  
Todos los usuarios deben cumplir con los Términos de Servicio de Google Cloud.
