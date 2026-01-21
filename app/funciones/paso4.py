import json
import os
from datetime import datetime, timedelta
from config import RUTA_PARAMETROS, ruta_paso  # ✅ Importamos rutas centralizadas

def es_dia_libre(fecha_str, dias_libres):
    return fecha_str in dias_libres

def es_dia_descanso(fecha, dias_descanso):
    return fecha.weekday() in dias_descanso

def es_dia_imprevisto(fecha, dia_imprevistos):
    return fecha.weekday() in dia_imprevistos

def generar_calendario_real(parametros, plan_logico):
    fecha_inicio = datetime.strptime(parametros["fecha_inicio"], "%Y-%m-%d")
    fecha_examen = datetime.strptime(parametros["fecha_examen"], "%Y-%m-%d")
    fecha_limite = fecha_examen - timedelta(weeks=2)

    dias_descanso = parametros.get("dias_descanso", [])
    dia_imprevistos = parametros.get("dia_imprevistos_semana", [])
    dias_libres = parametros.get("dias_libres", [])

    calendario_final = []
    dia_logico_actual = 1
    max_dia_logico = max(entry["dia"] for entry in plan_logico)

    contador_dia = 1
    contador_semana = 1
    contador_mes = 1
    mes_actual = fecha_inicio.month
    primer_dia = True

    while fecha_inicio < fecha_limite:
        fecha_str = fecha_inicio.strftime("%Y-%m-%d")
        dia_semana = fecha_inicio.weekday()

        if not primer_dia and dia_semana == 0:
            contador_semana += 1

        if fecha_inicio.month != mes_actual:
            contador_mes += 1
            mes_actual = fecha_inicio.month

        primer_dia = False

        if es_dia_libre(fecha_str, dias_libres):
            calendario_final.append({
                "dia": contador_dia,
                "fecha": fecha_str,
                "dia_semana": dia_semana,
                "semana": contador_semana,
                "mes": contador_mes,
                "titulo": "Libre",
                "grupo": 101,
                "dificultad": 0,
                "tema_id": 0,
                "vuelta": 0,
                "tipo": "descanso"
            })

        elif es_dia_descanso(fecha_inicio, dias_descanso):
            calendario_final.append({
                "dia": contador_dia,
                "fecha": fecha_str,
                "dia_semana": dia_semana,
                "semana": contador_semana,
                "mes": contador_mes,
                "titulo": "Descanso",
                "grupo": 100,
                "dificultad": 0,
                "tema_id": 0,
                "vuelta": 0,
                "tipo": "descanso"
            })

        elif es_dia_imprevisto(fecha_inicio, dia_imprevistos):
            calendario_final.append({
                "dia": contador_dia,
                "fecha": fecha_str,
                "dia_semana": dia_semana,
                "semana": contador_semana,
                "mes": contador_mes,
                "titulo": "Imprevisto",
                "grupo": 102,
                "dificultad": 0,
                "tema_id": 0,
                "vuelta": 0,
                "tipo": "descanso"
            })

        else:
            entradas_dia = [entry for entry in plan_logico if entry["dia"] == dia_logico_actual]

            for entrada in entradas_dia:
                nueva_entrada = {
                    "dia": contador_dia,
                    "fecha": fecha_str,
                    "dia_semana": dia_semana,
                    "semana": contador_semana,
                    "mes": contador_mes,
                    "titulo": entrada["titulo"],
                    "grupo": entrada["grupo"],
                    "dificultad": entrada["dificultad"],
                    "tema_id": entrada["tema_id"],
                    "vuelta": entrada["vuelta"],
                    "tipo": entrada.get("tipo", "estudio")
                }
                calendario_final.append(nueva_entrada)

            dia_logico_actual += 1

        fecha_inicio += timedelta(days=1)
        contador_dia += 1

        if dia_logico_actual > max_dia_logico:
            break

    return calendario_final

def ejecutar_paso4():
    os.makedirs(os.path.dirname(ruta_paso(4)), exist_ok=True)

    with open(RUTA_PARAMETROS, "r", encoding="utf-8") as f:
        parametros = json.load(f)

    with open(ruta_paso(3), "r", encoding="utf-8") as f:
        plan_logico = json.load(f)

    calendario_real = generar_calendario_real(parametros, plan_logico)

    with open(ruta_paso(4), "w", encoding="utf-8") as f:
        json.dump(calendario_real, f, indent=4, ensure_ascii=False)

    print("✅ paso4.json creado con éxito. Fechas reales y estructura uniforme añadidas.")
