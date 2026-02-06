import json
import re
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

OUT_DIR = Path("salida_prefactibilidad")
OUT_DIR.mkdir(exist_ok=True)

SMP_FALLBACK = "044-097A-032A"  # tu SMP conocido (si catastroinformal no lo devuelve)


def slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", s)[:120]


def find_smp(obj):
    """Busca un SMP en cualquier parte de un JSON."""
    if isinstance(obj, dict):
        for _, v in obj.items():
            if isinstance(v, str) and re.match(r"^\d{3}-\d{3}[A-Z]-\d{3}[A-Z]$", v):
                return v
            r2 = find_smp(v)
            if r2:
                return r2
    elif isinstance(obj, list):
        for it in obj:
            r2 = find_smp(it)
            if r2:
                return r2
    return None


def pick_caba_normalized(norm_json):
    """Elige la opción correcta: CABA."""
    dns = norm_json.get("direccionesNormalizadas", [])
    for d in dns:
        if (d.get("cod_partido") or "").lower() == "caba":
            return d
    return dns[0] if dns else None


def run(address: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1) Normalizar + geocodificar
        norm_url = (
            "https://servicios.usig.buenosaires.gob.ar/normalizar/"
            f"?direccion={quote(address)}&geocodificar=true&srid=4326"
        )
        norm = page.request.get(norm_url).json()

        d = pick_caba_normalized(norm)
        if not d:
            raise RuntimeError("No hubo direccionesNormalizadas en la respuesta de normalizar().")

        calle = d.get("nombre_calle")
        puerta = d.get("altura")
        coords = d.get("coordenadas") or {}
        x = coords.get("x")
        y = coords.get("y")

        # 2) Catastroinformal (con URL encoding correcto)
        cat = {}
        smp = None
        if calle and puerta:
            cat_url = (
                "https://epok.buenosaires.gob.ar/catastroinformal/direccioninformal/"
                f"?calle={quote(str(calle))}&puerta={quote(str(puerta))}"
            )
            cat = page.request.get(cat_url).json()
            smp = find_smp(cat)

        # 3) Datos útiles (comuna/barrio/sección etc.)
        datos_utiles = None
        if x is not None and y is not None:
            du_url = f"https://ws.usig.buenosaires.gob.ar/datos_utiles?x={x}&y={y}"
            datos_utiles = page.request.get(du_url).json()

        # 4) Si no encontramos SMP por catastroinformal, usamos fallback
        if not smp:
            smp = SMP_FALLBACK

        # 5) CUR3D por SMP
        cur3d = {
            "smp": smp,
            "parcelas_plausibles_a_enrase": page.request.get(
                f"https://epok.buenosaires.gob.ar/cur3d/parcelas_plausibles_a_enrase/?smp={smp}"
            ).json(),
            "constitucion_estado_parcelario": page.request.get(
                f"https://epok.buenosaires.gob.ar/cur3d/constitucion_estado_parcelario/?smp={smp}"
            ).json(),
            "seccion_edificabilidad": page.request.get(
                f"https://epok.buenosaires.gob.ar/cur3d/seccion_edificabilidad/?smp={smp}"
            ).json(),
        }

        browser.close()

    resultado = {
        "input": {"address": address},
        "normalizar": norm,
        "normalizada_elegida": d,
        "catastroinformal": cat,
        "coords": {"x": x, "y": y},
        "datos_utiles": datos_utiles,
        "cur3d": cur3d,
    }

    fname = OUT_DIR / f"prefactibilidad_{slug(smp)}.json"
    fname.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK, guardado:", fname.resolve())


if __name__ == "__main__":
    run("Dávila 1172, CABA")
