import json
import os
from datetime import datetime, timedelta

from config import (
    RUTA_PARAMETROS,
    RUTA_PASOS,        # ✅ para guardar plan_estado.json en el workspace correcto
    ruta_paso,
    ruta_repasos
)


def expandir_temas_con_repasos(parametros, temas_ordenados):
    dificultad_temas = parametros["dificultad_temas"]
    fecha_inicio = datetime.strptime(parametros["fecha_inicio"], "%Y-%m-%d")
    fecha_examen = datetime.strptime(parametros["fecha_examen"], "%Y-%m-%d")
    dias_libres = parametros.get("dias_libres", [])  # (lo mantengo por compatibilidad)

    dias_hasta_examen = (fecha_examen - timedelta(days=14) - fecha_inicio).days

    # (lo mantengo aunque no se use: evita cambiar comportamiento colateral)
    fin_primera_vuelta = sum([dificultad_temas[str(t["dificultad"])] for t in temas_ordenados])

    plan_dias = []
    repasos_por_tema = {}

    # -------------------------
    # Primera vuelta (estudio)
    # -------------------------
    dia_actual = 1
    for tema in temas_ordenados:
        duracion = dificultad_temas[str(tema["dificultad"])]
        for _ in range(duracion):
            plan_dias.append({
                "dia": dia_actual,
                "titulo": tema["titulo"],
                "grupo": tema["grupo"],
                "dificultad": tema["dificultad"],
                "tema_id": tema["tema_id"],
                "vuelta": 1,
                "tipo": "estudio"
            })
            dia_actual += 1

    # -------------------------
    # Verificar si la primera vuelta está incompleta
    # -------------------------
    temas_estudiados_vuelta1 = set(
        entrada["tema_id"]
        for entrada in plan_dias
        if entrada["vuelta"] == 1 and entrada["tipo"] == "estudio"
    )
    plan_incompleto = len(temas_estudiados_vuelta1) < len(temas_ordenados)

    # -------------------------
    # Patrón de repasos extendido
    # -------------------------
    for tema in temas_ordenados:
        tema_id = tema["tema_id"]

        # Último día de estudio del tema en vuelta 1
        dias_tema_v1 = [d["dia"] for d in plan_dias if d["tema_id"] == tema_id and d["vuelta"] == 1]
        if not dias_tema_v1:
            # Por seguridad, si no hay días (no debería ocurrir), saltamos
            continue
        primer_dia = dias_tema_v1[-1]

        patron_repasos = [1, 7, 28, 84]
        ultimo_repaso = patron_repasos[-1]
        while primer_dia + ultimo_repaso + 84 <= dias_hasta_examen:
            ultimo_repaso += 84
            patron_repasos.append(ultimo_repaso)

        n_vuelta = 2
        for repaso_offset in patron_repasos:
            dia_repaso = primer_dia + repaso_offset
            if dia_repaso <= dias_hasta_examen:
                plan_dias.append({
                    "dia": dia_repaso,
                    "titulo": tema["titulo"],
                    "grupo": tema["grupo"],
                    "dificultad": tema["dificultad"],
                    "tema_id": tema["tema_id"],
                    "vuelta": n_vuelta,
                    "tipo": "repaso"
                })
                n_vuelta += 1

    # -------------------------
    # Vueltas de estudio adicionales
    # -------------------------
    if dia_actual <= dias_hasta_examen:
        index = 0
        temas_len = len(temas_ordenados)
        vuelta_actual = 2

        while dia_actual <= dias_hasta_examen:
            tema = temas_ordenados[index % temas_len]
            duracion = dificultad_temas[str(tema["dificultad"])]

            for _ in range(duracion):
                if dia_actual > dias_hasta_examen:
                    break
                plan_dias.append({
                    "dia": dia_actual,
                    "titulo": tema["titulo"],
                    "grupo": tema["grupo"],
                    "dificultad": tema["dificultad"],
                    "tema_id": tema["tema_id"],
                    "vuelta": vuelta_actual,
                    "tipo": "estudio"
                })
                dia_actual += 1

            index += 1
            if index % temas_len == 0:
                vuelta_actual += 1

    return plan_dias, repasos_por_tema, plan_incompleto


def ejecutar_paso2():
    with open(RUTA_PARAMETROS, "r", encoding="utf-8") as f:
        parametros = json.load(f)

    with open(ruta_paso(1), "r", encoding="utf-8") as f:
        temas_ordenados = json.load(f)

    plan_dias, repasos_por_tema, plan_incompleto = expandir_temas_con_repasos(parametros, temas_ordenados)

    # ✅ Guardar flag adicional usando ruta del workspace (no hardcode)
    os.makedirs(RUTA_PASOS, exist_ok=True)
    ruta_plan_estado = os.path.join(RUTA_PASOS, "plan_estado.json")
    with open(ruta_plan_estado, "w", encoding="utf-8") as f:
        json.dump({"plan_incompleto": plan_incompleto}, f, indent=4, ensure_ascii=False)

    with open(ruta_paso(2), "w", encoding="utf-8") as f:
        json.dump(plan_dias, f, indent=4, ensure_ascii=False)

    with open(ruta_repasos(), "w", encoding="utf-8") as f:
        json.dump(repasos_por_tema, f, indent=4, ensure_ascii=False)

    print("✅ paso2.json generado correctamente.")
