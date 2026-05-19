from parser import analizar_oracion


if __name__ == "__main__":
    casos_de_prueba = [
        "quiero un celular gama media",
        "busco mucha memoria para jugar",
        "necesito el teléfono rápido potente y fluido con snapdragon para programar",
        "busca una celular gama alta",
        "quiero unos procesador potente",
        "recomiéndame un dispositivo rápido y potente gama alta y fluido para jugar",
        "quiero una memoria rápida para programar",
        "busco un teléfono samsung y xiaomi",
        "quiero el teléfono rápidos",
        "necesito el celular con snapdragon gama baja",
        "un buen procesador para jugar",
        "recomiéndame el",
    ]
    
    for caso in casos_de_prueba:
        print("-" * 50)
        analizar_oracion(caso)
