import os
import json
import shutil
import sys
import importlib
from pathlib import Path


def _purge_cached_modules():
    """
    Elimina del caché los módulos que capturan rutas en tiempo de import.
    Así, en cada petición, config + pasos recalculan rutas con el APP_BASE_DIR actual.
    """
    to_purge = [
        "config",          # shim microservicio/config.py
        "app.config",
        "app.funciones.paso1",
        "app.funciones.paso2",
        "app.funciones.paso3",
        "app.funciones.paso4",
        "app.funciones.paso5",
        "app.funciones.paso6",
    ]
    for name in to_purge:
        sys.modules.pop(name, None)


def run_pipeline_in_workspace(parametros: dict, workspace: str) -> str:
    # 1) Fijar APP_BASE_DIR para esta petición
    os.environ["APP_BASE_DIR"] = workspace

    ws = Path(workspace)

    # 2) Estructura esperada
    (ws / "parametros").mkdir(parents=True, exist_ok=True)
    (ws / "pasos").mkdir(parents=True, exist_ok=True)

    # 3) Copiar media al workspace (para paso6)
    here = Path(__file__).resolve().parent  # .../microservicio/app
    src_media = here / "media"
    dst_media = ws / "media"
    shutil.copytree(src_media, dst_media, dirs_exist_ok=True)

    # 4) Escribir parametros.json donde tus pasos lo esperan
    ruta_parametros = ws / "parametros" / "parametros.json"
    ruta_parametros.write_text(
        json.dumps(parametros, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )

    if not ruta_parametros.exists():
        raise RuntimeError(f"No se creó parametros.json en: {ruta_parametros}")

    # 5) MUY IMPORTANTE: purgar caché e importar de nuevo
    _purge_cached_modules()

    # Reimporta config (para que RUTA_PARAMETROS se recalculen con APP_BASE_DIR nuevo)
    importlib.import_module("config")
    importlib.import_module("app.config")

    # 6) Ejecutar pasos (recién importados)
    from app.funciones.paso1 import ejecutar_paso1
    from app.funciones.paso2 import ejecutar_paso2
    from app.funciones.paso3 import ejecutar_paso3
    from app.funciones.paso4 import ejecutar_paso4
    from app.funciones.paso5 import ejecutar_paso5
    from app.funciones.paso6 import ejecutar_paso6

    ejecutar_paso1()
    ejecutar_paso2()
    ejecutar_paso3()
    ejecutar_paso4()
    ejecutar_paso5()
    ejecutar_paso6()

    pdf_path = ws / "planificador.pdf"
    if not pdf_path.exists():
        raise RuntimeError("No se generó planificador.pdf")

    return str(pdf_path)
