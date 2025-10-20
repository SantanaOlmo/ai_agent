import os
import sys
import json
import getpass
from pathlib import Path
from cryptography.fernet import Fernet

HOME = Path.home()
KEYS_FILE = HOME / ".mcp_gemini_keys.enc"
KEYS_SECRET_FILE = HOME / ".mcp_gemini_secret.key"

def generar_clave_secreta():
    key = Fernet.generate_key()
    with open(KEYS_SECRET_FILE, "wb") as f:
        f.write(key)
    return key

def cargar_clave_secreta():
    if KEYS_SECRET_FILE.exists():
        return KEYS_SECRET_FILE.read_bytes()
    return generar_clave_secreta()

SECRET_KEY = cargar_clave_secreta()
CIPHER = Fernet(SECRET_KEY)

def guardar_claves(claves):
    data = json.dumps(claves).encode()
    encrypted = CIPHER.encrypt(data)
    with open(KEYS_FILE, "wb") as f:
        f.write(encrypted)

def cargar_claves():
    if KEYS_FILE.exists():
        try:
            encrypted = KEYS_FILE.read_bytes()
            decrypted = CIPHER.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception:
            return []
    return []

def ingresar_nueva_clave():
    api_key = getpass.getpass("Introduce tu nueva API Key de Google Gemini: ").strip()
    if not api_key or len(api_key) < 20:
        print("❌ La clave no parece válida.")
        sys.exit(1)
    claves = cargar_claves()
    if api_key not in claves:
        claves.append(api_key)
        guardar_claves(claves)
    return api_key

def pedir_api_key():
    claves = cargar_claves()
    if claves:
        print("\n🔑 Claves guardadas:")
        for i, _ in enumerate(claves, 1):
            print(f"{i}. Clave #{i}")
        print(f"{len(claves)+1}. Ingresar una nueva clave")
        opcion = input("Selecciona una opción: ").strip()
        if opcion.isdigit():
            opcion = int(opcion)
            if 1 <= opcion <= len(claves):
                return claves[opcion-1]
            elif opcion == len(claves) + 1:
                return ingresar_nueva_clave()
    return ingresar_nueva_clave()