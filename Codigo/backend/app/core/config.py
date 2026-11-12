"""
Modulo de configuracion centralizada de la aplicacion (app/core/config.py).

Proposito:
    Lee las variables de entorno definidas en el archivo '.env' (o del sistema operativo),
    valida sus tipos de datos mediante Pydantic y las expone como un objeto unico (Patron Singleton)
    para que cualquier modulo del backend pueda consultarlas sin leer el disco repetidamente.
"""

# lru_cache es un decorador estandar de Python que guarda en memoria RAM el resultado
# de una funcion. Lo usamos para implementar el Patron Singleton (una unica instancia).
from functools import lru_cache

# List nos permite indicar que una variable debe ser una lista de elementos (ej. lista de textos).
from typing import List

# BaseSettings es la clase de Pydantic disenada especificamente para leer archivos '.env'.
# SettingsConfigDict nos permite configurar como y de donde se lee ese archivo.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Clase que define el esquema y los valores por defecto de toda la configuracion.
    Si una variable existe en el archivo '.env', sobrescribira el valor por defecto aqui definido.
    """

    # --- 1. INFORMACION GENERAL DE LA APLICACION ---
    APP_NAME: str = "Analizador SAST Ciberseguridad TFG"  # Nombre publico de la API
    APP_VERSION: str = "1.0.0"                           # Version actual del software
    ENVIRONMENT: str = "development"                     # Entorno: 'development', 'testing' o 'production'
    DEBUG: bool = True                                   # Activa mensajes detallados en desarrollo

    # --- 2. SEGURIDAD Y LIMITES ANTI-DOS (Requisito RNF-06) ---
    # Tamano maximo permitido en Kilobytes para el codigo fuente enviado por el usuario.
    # Evita que un atacante sature la memoria RAM enviando archivos gigantescos.
    MAX_CODE_SIZE_KB: int = 256

    # Lista de direcciones web (origenes) que tienen permiso para hacer peticiones a esta API (CORS).
    # Por defecto permitimos Angular en local (puerto 4200) y el propio servidor FastAPI (puerto 8000).
    ALLOWED_ORIGINS: List[str] = ["http://localhost:4200", "http://127.0.0.1:8000"]

    # --- 3. BASE DE DATOS Y PERSISTENCIA ---
    # Cadena de conexion. En local usa un archivo SQLite llamado 'sast_tfg.db'.
    # En produccion puede cambiarse en '.env' a PostgreSQL sin tocar el codigo.
    DATABASE_URL: str = "sqlite:///./sast_tfg.db"

    # --- 4. MOTOR DE INTELIGENCIA ARTIFICIAL (Desacoplado) ---
    # Define que proveedor usar: 'mock' (simulado para pruebas), 'gemini' o 'ollama'.
    AI_PROVIDER: str = "mock"
    # Clave secreta de la API de IA (se deja vacia aqui y se rellena solo en '.env').
    AI_API_KEY: str = ""
    # Nombre exacto del modelo de lenguaje a utilizar.
    AI_MODEL_NAME: str = "gemini-2.5-flash"
    # Tiempo maximo en segundos que esperaremos respuesta de la IA antes de abortar (evita bloqueos).
    AI_TIMEOUT_SECONDS: int = 15

    # --- CONFIGURACION INTERNA DE PYDANTIC ---
    model_config = SettingsConfigDict(
        env_file=".env",              # Nombre del archivo del que debe leer las variables
        env_file_encoding="utf-8",    # Codificacion de caracteres para soportar tildes o simbolos
        case_sensitive=True,          # Distingue entre mayusculas y minusculas (APP_NAME != app_name)
        extra="ignore"                # Si en '.env' hay variables extra no definidas aqui, las ignora sin dar error
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Funcion fabrica con cache en memoria (Patron Singleton).

    ¿Por que usamos @lru_cache()?
    Si 1.000 usuarios hacen peticiones a la API, sin esta cache Python abriria y leeria
    el archivo '.env' del disco duro 1.000 veces. Con @lru_cache(), se lee solo la primera vez
    y las siguientes 999 veces se devuelve instantaneamente desde la memoria RAM.

    Returns:
        Settings: Instancia unica y validada con toda la configuracion del proyecto.
    """
    return Settings()