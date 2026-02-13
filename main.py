from scripts.analizar_lote import ejecutar

if __name__ == "__main__":
    resultados = ejecutar("datos/lotes.json")

    for r in resultados:
        print("\n📍", r["direccion"])
        print("Zona:", r["zona"])
        print("Plantas:", r["plantas"])
        print("m² edificables:", r["m2_edificables"])
        print("m² vendibles:", r["m2_vendibles"])
