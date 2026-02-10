import json
from tabla_canonica.tabla import analizar_lote

def ejecutar(path_json):
    with open(path_json, "r", encoding="utf-8") as f:
        lotes = json.load(f)

    resultados = []
    for lote in lotes:
        resultados.append(analizar_lote(lote))

    return resultados
