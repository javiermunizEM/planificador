# config.py
import os
import sys

DEFAULT_BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
BASE_DIR = os.environ.get("APP_BASE_DIR", DEFAULT_BASE_DIR)

RUTA_PARAMETROS = os.path.join(BASE_DIR, "parametros", "parametros.json")
RUTA_MEDIA = os.path.join(BASE_DIR, "media")
RUTA_IMAGENES = os.path.join(RUTA_MEDIA, "imagenes")
RUTA_PASOS = os.path.join(BASE_DIR, "pasos")
RUTA_FIRMA = os.path.join(RUTA_IMAGENES, "firma.png")

def ruta_paso(n):
    return os.path.join(RUTA_PASOS, f"paso{n}.json")

def ruta_estadisticas():
    return os.path.join(RUTA_PASOS, "estadisticas.json")

def ruta_repasos():
    return os.path.join(RUTA_PASOS, "repasos_temas.json")

def ruta_textos():
    return os.path.join(RUTA_MEDIA, "textos.json")
