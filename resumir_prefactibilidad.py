import json
from pathlib import Path

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def round1(x):
    try:
        return round(float(x), 1)
    except:
        return x

def main(input_file: str):
    p = Path(input_file)
    data = load_json(p)

    edif = (data.get("cur3d") or {}).get("seccion_edificabilidad") or {}
    fot = edif.get("fot") or {}
    links = edif.get("link_imagen") or {}
    afect = edif.get("afectaciones") or {}
    plus = edif.get("plusvalia") or {}
    coords = data.get("coords") or {}
    du = data.get("datos_utiles") or {}

    sup_parcela = edif.get("superficie_parcela")
    fot_base = fot.get("fot_medianera") or fot.get("fot_perim_libre") or fot.get("fot_semi_libre")

    m2_fot = None
    if sup_parcela is not None and fot_base is not None:
        try:
            m2_fot = float(sup_parcela) * float(fot_base)
        except:
            pass

    resumen = {
        "direccion": (data.get("normalizada_elegida") or {}).get("direccion") or (data.get("input") or {}).get("address"),
        "smp": (data.get("cur3d") or {}).get("smp"),
        "coords": {"x": coords.get("x"), "y": coords.get("y")},
        "comuna": du.get("comuna"),
        "barrio": du.get("barrio"),
        "superficie_parcela_m2": round1(sup_parcela),
        "altura_max_plano_limite_m": round1(edif.get("altura_max_plano_limite")),
        "fot": {
            "medianera": fot.get("fot_medianera"),
            "semi_libre": fot.get("fot_semi_libre"),
            "perim_libre": fot.get("fot_perim_libre"),
        },
        "m2_estimados_por_fot": round1(m2_fot),
        "distrito_cpu_historico": plus.get("distrito_cpu"),
        "afectaciones": {
            "riesgo_hidrico": afect.get("riesgo_hidrico"),
            "ensanche": afect.get("ensanche"),
            "apertura": afect.get("apertura"),
            "lep": afect.get("lep"),
            "ci_digital": afect.get("ci_digital"),
        },
        "observaciones": {
            "adps": edif.get("adps"),
            "irregular": edif.get("irregular"),
            "tipica": edif.get("tipica"),
            "rivolta": edif.get("rivolta"),
        },
        "links": {
            "croquis_parcela_pdf": links.get("croquis_parcela"),
            "plano_indice_pdf": links.get("plano_indice"),
            "perimetro_manzana_img": links.get("perimetro_manzana"),
        }
    }

    out = p.with_name(p.stem + "_RESUMEN.json")
    out.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK resumen guardado en:", out)

if __name__ == "__main__":
    carpeta = Path("salida_prefactibilidad")
    archivos = list(carpeta.glob("prefactibilidad_*.json"))

    if not archivos:
        raise FileNotFoundError("No se encontró ningún prefactibilidad_*.json en salida_prefactibilidad")

    main(str(archivos[0]))

