from reglas.alturas import cantidad_plantas
from reglas.planta_baja import altura_planta_baja
from reglas.retiros import retiros
from reglas.subsuelos import subsuelos

def analizar_lote(lote):
    plantas = cantidad_plantas(lote["zona"])
    m2_edificables = plantas * lote["area_edificable_planta"]

    # Descuento 8,30% si aplica
    m2_netos = m2_edificables * 0.917

    # Vendibles
    m2_vendibles = m2_netos * 0.79

    return {
        "direccion": lote["direccion"],
        "zona": lote["zona"],
        "plantas": plantas,
        "m2_edificables": round(m2_netos, 2),
        "m2_vendibles": round(m2_vendibles, 2),
        "planta_baja": altura_planta_baja(),
        "retiros": retiros(lote["zona"]),
        "subsuelos": subsuelos()
    }
