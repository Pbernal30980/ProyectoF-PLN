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
    
    
    casos_a_ejecutar = (1,3)
    
    if casos_a_ejecutar is None:
        indices = range(len(casos_de_prueba))
    elif isinstance(casos_a_ejecutar, int):
        indices = [casos_a_ejecutar]
    elif isinstance(casos_a_ejecutar, tuple):
        inicio, fin = casos_a_ejecutar
        indices = range(inicio, fin + 1)
    else:
        print("Error: casos_a_ejecutar debe ser None, un número o una tupla (inicio, fin)")
        indices = []
    
    # Ejecutar casos seleccionados
    for i in indices:
        if 0 <= i < len(casos_de_prueba):
            print(f"\n\n\n[Caso {i}]")
            analizar_oracion(casos_de_prueba[i])
        else:
            print(f"Error: Índice {i} fuera de rango (0-{len(casos_de_prueba)-1})")
