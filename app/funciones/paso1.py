import json
from collections import deque
from config import RUTA_PARAMETROS, ruta_paso  # 👈 Importamos las rutas centralizadas

def ordenar_temas(parametros):
    temas = parametros["temas"]

    # Normalizar y validar el modo de ordenación
    try:
        modo_orden = int(parametros.get("ordenar_temas", 0))
    except (TypeError, ValueError):
        raise ValueError(
            "El parámetro 'ordenar_temas' debe tener uno de estos valores: 0, 1 o 2."
        )

    if modo_orden not in (0, 1, 2):
        raise ValueError(
            f"Valor no válido para 'ordenar_temas': {modo_orden}. "
            "Debe ser 0, 1 o 2."
        )

    # Normalizar y validar los temas
    lista_temas = []

    for k, v in temas.items():
        try:
            dificultad = int(v["dificultad"])
        except (KeyError, TypeError, ValueError):
            raise ValueError(
                f"La dificultad del tema {k} no es válida: "
                f"{v.get('dificultad')!r}"
            )

        if dificultad not in (1, 2, 3):
            raise ValueError(
                f"La dificultad del tema {k} debe ser 1, 2 o 3. "
                f"Valor recibido: {dificultad}"
            )

        lista_temas.append({
            "original_id": int(k),
            "titulo": v["titulo"],
            "grupo": v["grupo"],
            "dificultad": dificultad
        })

    # 0: mantener el orden original
    if modo_orden == 0:
        lista_temas.sort(key=lambda x: x["original_id"])

    # 1: ordenar por grupo
    elif modo_orden == 1:
        lista_temas.sort(key=lambda x: (x["grupo"], x["original_id"]))

    # 2: intercalar por dificultad
    elif modo_orden == 2:
        faciles = deque(
            t for t in lista_temas if t["dificultad"] == 1
        )
        medias = deque(
            t for t in lista_temas if t["dificultad"] == 2
        )
        dificiles = deque(
            t for t in lista_temas if t["dificultad"] == 3
        )

        resultado = []

        while faciles or medias or dificiles:
            if faciles:
                resultado.append(faciles.popleft())

            if medias:
                resultado.append(medias.popleft())

            if dificiles:
                resultado.append(dificiles.popleft())

        lista_temas = resultado

    # Reasignar tema_id según el nuevo orden
    for idx, tema in enumerate(lista_temas, start=1):
        tema["tema_id"] = idx
        del tema["original_id"]

    return lista_temas

def guardar_resultado(lista_temas, output_path=None):
    if output_path is None:
        output_path = ruta_paso(1)  # Guardamos en pasos/paso1.json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lista_temas, f, indent=4, ensure_ascii=False)

def ejecutar_paso1():
    with open(RUTA_PARAMETROS, "r", encoding="utf-8") as f:
        parametros = json.load(f)

    temas_ordenados = ordenar_temas(parametros)
    guardar_resultado(temas_ordenados)
