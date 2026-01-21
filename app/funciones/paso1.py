import json
from collections import deque
from config import RUTA_PARAMETROS, ruta_paso  # 👈 Importamos las rutas centralizadas

def ordenar_temas(parametros):
    temas = parametros["temas"]
    ordenar_temas = parametros["ordenar_temas"]

    # Convertimos los temas en una lista con sus campos completos
    lista_temas = [
        {
            "original_id": int(k),  # Guardamos el ID original por si hiciera falta después
            "titulo": v["titulo"],
            "grupo": v["grupo"],
            "dificultad": v["dificultad"]
        }
        for k, v in temas.items()
    ]

    if ordenar_temas == 0:
        lista_temas.sort(key=lambda x: x["original_id"])
    elif ordenar_temas == 1:
        lista_temas.sort(key=lambda x: (x["grupo"], x["original_id"]))
    elif ordenar_temas == 2:
        # Intercalar dificultad: patrón [fácil, media, difícil]
        faciles = deque([t for t in lista_temas if t["dificultad"] == 1])
        medias = deque([t for t in lista_temas if t["dificultad"] == 2])
        dificiles = deque([t for t in lista_temas if t["dificultad"] == 3])
        
        patron = [1, 2, 3]
        resultado = []

        while faciles or medias or dificiles:
            for nivel in patron:
                if nivel == 1 and faciles:
                    resultado.append(faciles.popleft())
                elif nivel == 2 and medias:
                    resultado.append(medias.popleft())
                elif nivel == 3 and dificiles:
                    resultado.append(dificiles.popleft())
        lista_temas = resultado

    # Reasignar tema_id según nuevo orden
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
