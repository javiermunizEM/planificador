import json
import os
from datetime import datetime, date, timedelta
from collections import defaultdict

from config import (
    RUTA_PARAMETROS,
    ruta_paso,
    ruta_repasos,
    ruta_estadisticas,
)

DIAS_SEMANA_ES = [
    "Lunes", "Martes", "Miércoles", "Jueves",
    "Viernes", "Sábado", "Domingo"
]

INDICE_DIA = {
    "Lunes": 0, "Martes": 1, "Miércoles": 2,
    "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6
}


def formatear_fecha(fecha_iso: str):
    dt = datetime.strptime(fecha_iso, "%Y-%m-%d")
    return dt.strftime("%d-%m-%Y"), dt.strftime("%d"), DIAS_SEMANA_ES[dt.weekday()]


def formatear_tiempo(minutos: int) -> str:
    horas = minutos // 60
    minutos_restantes = minutos % 60
    return f"{horas}h {minutos_restantes}m" if horas else f"{minutos_restantes}m"


def construir_calendario_por_semanas(entradas, horas_diarias):
    horas_diarias_array = horas_diarias if isinstance(horas_diarias, list) else [horas_diarias] * 7

    agrupado_por_fecha = defaultdict(list)
    estudio_repaso_por_tema = defaultdict(lambda: {"estudio": [], "repaso": []})

    for entrada in entradas:
        agrupado_por_fecha[entrada["fecha"]].append(entrada)

    semanas = defaultdict(list)

    for fecha_iso in sorted(agrupado_por_fecha.keys()):
        entradas_dia = agrupado_por_fecha[fecha_iso]
        fecha, dia_mes, dia_semana = formatear_fecha(fecha_iso)
        semana = entradas_dia[0]["semana"]
        dia = entradas_dia[0]["dia"]

        indice_dia_semana = INDICE_DIA[dia_semana]
        horas_dia_actual = horas_diarias_array[indice_dia_semana]
        minutos_disponibles = int(horas_dia_actual * 60)

        estudiar = ""
        repasar = []
        minutos_estudiar = 0
        minutos_repasar = []

        peso_estudio = 0
        pesos_repasos = []
        tema_id_estudio = None

        for entrada in entradas_dia:
            if entrada["titulo"] in ["Descanso", "Libre", "Imprevisto"]:
                estudiar = entrada["titulo"]
                repasar = []
                minutos_disponibles = 0
                break

            if entrada["tipo"] == "estudio":
                estudiar = f'{entrada["titulo"]} [{entrada["vuelta"]}]'
                tema_id_estudio = entrada["tema_id"]
                peso_estudio = 3

            elif entrada["tipo"] == "repaso":
                peso = 5 if entrada["vuelta"] == 2 else 3 if entrada["vuelta"] == 3 else 1
                repasar.append((f'{entrada["titulo"]} [{entrada["vuelta"]}]', peso, entrada["tema_id"]))
                pesos_repasos.append((peso, entrada["tema_id"]))

        peso_total = peso_estudio + sum(p for p, _ in pesos_repasos)
        repasar_con_tiempo = []

        if peso_estudio > 0:
            minutos_estudiar = int(minutos_disponibles * 0.5)

            if tema_id_estudio is not None:
                estudiar += f" [{formatear_tiempo(minutos_estudiar)}]"
                estudio_repaso_por_tema[tema_id_estudio]["estudio"].append(minutos_estudiar)

            resto_minutos = minutos_disponibles - minutos_estudiar
            peso_total_repasos = sum(p for p, _ in pesos_repasos)

            for (titulo, peso, tema_id), (peso_val, tema_id_r) in zip(repasar, pesos_repasos):
                minutos = int((peso / peso_total_repasos) * resto_minutos) if peso_total_repasos else 0
                repasar_con_tiempo.append(f"{titulo} [{formatear_tiempo(minutos)}]")
                minutos_repasar.append(minutos)
                estudio_repaso_por_tema[tema_id]["repaso"].append(minutos)

        elif peso_total > 0:
            for (titulo, peso, tema_id), (peso_val, tema_id_r) in zip(repasar, pesos_repasos):
                minutos = int((peso / peso_total) * minutos_disponibles)
                repasar_con_tiempo.append(f"{titulo} [{formatear_tiempo(minutos)}]")
                minutos_repasar.append(minutos)
                estudio_repaso_por_tema[tema_id]["repaso"].append(minutos)

        semanas[semana].append({
            "dia": dia,
            "fecha": fecha,
            "dia_mes": dia_mes,
            "dia_semana": dia_semana,
            "estudiar": estudiar,
            "repasar": repasar_con_tiempo,
            "minutos_estudiar": minutos_estudiar,
            "minutos_repasar": minutos_repasar,
            "horas_disponibles": horas_dia_actual
        })

    calendario = [{"semana": s, "dias": semanas[s]} for s in sorted(semanas)]

    total_estudio_general = 0
    total_repaso_general = 0

    resumen = {}
    for tema_id, valores in estudio_repaso_por_tema.items():
        total_estudio = sum(valores["estudio"])
        total_repaso = sum(valores["repaso"])

        resumen[tema_id] = {
            "total_estudio": total_estudio,
            "total_repaso": total_repaso,
            "estudio": valores["estudio"],
            "repaso": valores["repaso"]
        }

        total_estudio_general += total_estudio
        total_repaso_general += total_repaso

    resumen["__resumen_global__"] = {
        "total_estudio": total_estudio_general,
        "total_repaso": total_repaso_general,
        "total_general": total_estudio_general + total_repaso_general
    }

    # ✅ Guardar resumen (repasos_temas.json) usando ruta_repasos()
    os.makedirs(os.path.dirname(ruta_repasos()), exist_ok=True)
    with open(ruta_repasos(), "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=4, ensure_ascii=False)

    return calendario, resumen


def guardar_estadisticas(calendario, parametros, resumen):
    fecha_hoy = date.today()
    fecha_examen = datetime.strptime(parametros["fecha_examen"], "%Y-%m-%d").date()
    fecha_limite = fecha_examen - timedelta(weeks=2)

    dias_restantes = (fecha_examen - fecha_hoy).days
    dias_planificables = (fecha_limite - fecha_hoy).days

    horas_diarias = parametros.get("horas_diarias", [4, 4, 4, 4, 4, 4, 4])

    # Obtener fecha y día del fin de la primera vuelta
    fecha_fin_primera_vuelta = ""
    dia_ultima_vuelta1 = 0

    for semana in calendario:
        for entrada in semana["dias"]:
            if entrada.get("estudiar") and "[1]" in entrada["estudiar"]:
                fecha_fin_primera_vuelta = entrada["fecha"]
                dia_ultima_vuelta1 = entrada["dia"]

    # Calcular cuántos días faltan desde hoy hasta fin de primera vuelta
    dias_hasta_fin_primera_vuelta = 0
    if fecha_fin_primera_vuelta:
        fecha_fin_vuelta = datetime.strptime(fecha_fin_primera_vuelta, "%d-%m-%Y").date()
        dias_hasta_fin_primera_vuelta = (fecha_fin_vuelta - fecha_hoy).days

    dias_estudio = sum(
        1
        for semana in calendario
        for dia_ in semana["dias"]
        if dia_["estudiar"] not in ["Descanso", "Libre", "Imprevisto"]
    )
    dias_total = sum(len(semana["dias"]) for semana in calendario)
    dias_descanso = dias_total - dias_estudio

    total_estudio = resumen["__resumen_global__"]["total_estudio"]
    total_repaso = resumen["__resumen_global__"]["total_repaso"]

    # === Leer planificacion de paso4.json usando ruta_paso(4)
    with open(ruta_paso(4), "r", encoding="utf-8") as f:
        planificacion_dias = json.load(f)

    # === Calcular vueltas completas (robusto)
    temas_ids_totales = sorted(int(k) for k in parametros["temas"].keys()) if parametros.get("temas") else []
    estudios_por_tema = defaultdict(int)

    for entrada in planificacion_dias:
        if entrada.get("tipo") == "estudio":
            tid = int(entrada["tema_id"])
            if tid in temas_ids_totales:
                estudios_por_tema[tid] += 1

    # Asegurar que todos los temas existen en el contador
    for tid in temas_ids_totales:
        estudios_por_tema.setdefault(tid, 0)

    vueltas_completas = min(estudios_por_tema.values()) if temas_ids_totales else 0

    datos = {
        "dias_restantes": dias_restantes,
        "dias_planificables": dias_planificables,
        "dias_hasta_fin_primera_vuelta": dias_hasta_fin_primera_vuelta,
        "horas_diarias": horas_diarias,
        "vueltas_completas": vueltas_completas,
        "fin_primera_vuelta": fecha_fin_primera_vuelta,
        "duracion_primera_vuelta": dia_ultima_vuelta1,
        "tiempo_estudio_total": formatear_tiempo(total_estudio),
        "tiempo_repaso_total": formatear_tiempo(total_repaso),
        "tiempo_total": formatear_tiempo(total_estudio + total_repaso),
        "dias_estudio": dias_estudio,
        "dias_descanso": dias_descanso
    }

    # ✅ Guardar estadísticas usando ruta_estadisticas()
    os.makedirs(os.path.dirname(ruta_estadisticas()), exist_ok=True)
    with open(ruta_estadisticas(), "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    print("✅ estadisticas.json generado correctamente.")


def ejecutar_paso5():
    os.makedirs(os.path.dirname(ruta_paso(5)), exist_ok=True)

    with open(ruta_paso(4), "r", encoding="utf-8") as f:
        entradas = json.load(f)

    with open(RUTA_PARAMETROS, "r", encoding="utf-8") as f:
        parametros = json.load(f)

    horas_diarias = parametros.get("horas_diarias", [4, 4, 4, 4, 4, 4, 4])

    calendario, resumen = construir_calendario_por_semanas(entradas, horas_diarias)

    with open(ruta_paso(5), "w", encoding="utf-8") as f:
        json.dump(calendario, f, indent=4, ensure_ascii=False)

    # (Ya se guarda dentro de construir_calendario_por_semanas, pero lo dejamos por compatibilidad)
    with open(ruta_repasos(), "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=4, ensure_ascii=False)

    guardar_estadisticas(calendario, parametros, resumen)
    print("✅ paso5.json, repasos_temas.json y estadísticas generadas correctamente.")


if __name__ == "__main__":
    ejecutar_paso5()
