# -*- coding: utf-8 -*-
"""
registro_logs.py
Configura el archivo de logs donde se guardan todos los eventos y errores
del sistema. Es el único archivo que el programa escribe en disco, ya que
el enunciado prohíbe el uso de bases de datos.
"""

import logging  # Módulo estándar de Python para registrar eventos
import os  # Módulo para trabajar con rutas y carpetas

CARPETA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")  # Ruta de la carpeta logs junto al código
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "software_fj.log")  # Ruta completa del archivo de logs


def obtener_logger():  # Función que crea (una sola vez) y devuelve el logger del sistema
    """Devuelve el logger configurado para escribir en logs/software_fj.log."""
    os.makedirs(CARPETA_LOGS, exist_ok=True)  # Crea la carpeta logs si todavía no existe
    logger = logging.getLogger("SoftwareFJ")  # Obtiene un logger con nombre propio
    if not logger.handlers:  # Evita agregar manejadores repetidos si se llama varias veces
        logger.setLevel(logging.DEBUG)  # Registra todos los niveles, desde DEBUG hasta CRITICAL
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")  # Escribe en el archivo con tildes correctas
        formato = logging.Formatter(  # Define cómo se verá cada línea del log
            "%(asctime)s | %(levelname)-8s | %(message)s",  # Fecha, nivel y mensaje
            datefmt="%Y-%m-%d %H:%M:%S",  # Formato de la fecha y hora
        )
        manejador.setFormatter(formato)  # Aplica el formato al manejador
        logger.addHandler(manejador)  # Conecta el manejador al logger
    return logger  # Devuelve el logger listo para usar
