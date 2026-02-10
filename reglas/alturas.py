ALTURAS_MAXIMAS = {
    "Corredor Alto": 38.0,
    "Corredor Medio": 31.0,
    "USAA": 22.8,
    "USAM": 17.2,
    "USAB1": 14.6,
    "USAB2": 11.6
}

ALTURA_PLANTA = 2.8

def altura_maxima(zona):
    return ALTURAS_MAXIMAS[zona]

def cantidad_plantas(zona):
    return int(ALTURAS_MAXIMAS[zona] // ALTURA_PLANTA)

