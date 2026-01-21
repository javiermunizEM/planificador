import json
import os
from config import ruta_paso  # ✅ usamos las rutas centralizadas

def ejecutar_paso3():
    # Asegurar carpeta de salida
    os.makedirs(os.path.dirname(ruta_paso(3)), exist_ok=True)

    # Cargar paso2.json
    with open(ruta_paso(2), "r", encoding="utf-8") as f:
        datos = json.load(f)

    # Ordenar por día y luego por tema_id
    datos_ordenados = sorted(datos, key=lambda x: (x["dia"], x["tema_id"]))

    # Guardar resultado como paso3.json
    with open(ruta_paso(3), "w", encoding="utf-8") as f:
        json.dump(datos_ordenados, f, indent=4, ensure_ascii=False)

    print("✅ paso3.json creado con éxito. Ordenado por día y tema_id.")

if __name__ == "__main__":
    ejecutar_paso3()

