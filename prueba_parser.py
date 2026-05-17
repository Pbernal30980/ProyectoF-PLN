from parser import analizar_oracion


if __name__ == "__main__":
    casos_de_prueba = [
        # Casos básicos correctos
        "quiero un celular gama media",
        "busco mucha memoria para jugar",
        
        # 1. Acumulando adjetivos y especificando marcas (Larga y compleja)
        "necesito el teléfono rápido potente y fluido con snapdragon para programar",
        
        # 2. Conflicto de género/número intencional (una celular -> fem vs masc)
        "busca una celular gama alta",
        
        # 3. Conflicto de número con otro sujeto (unos procesador -> plur vs sing)
        "quiero unos procesador potente",
        
        # 4. Modificadores con conjunciones redundantes
        "recomiéndame un dispositivo rápido y potente gama alta y fluido para jugar",
        
        # 5. Adjetivo femenino que concuerde con memoria (Correcto)
        "quiero una memoria rápida para programar",
        
        # 6. Múltiples marcas y modelos
        "busco un teléfono samsung y xiaomi",

        # 7. Adjetivos en plural que fallen el número con el artículo singular
        "quiero el teléfono rápidos",
        
        # 8. Modificadores sin unificación estricta (snapdragon no tiene genero pero teléfono sí)
        "necesito el celular con snapdragon gama baja",
        
        # 9. Omisión de intención (La sintaxis depende del parser, veremos si asume que empieza por req)
        "un procesador para jugar",
        
        # 10. Frase truncada
        "recomiéndame el",
    ]
    
    for caso in casos_de_prueba:
        print("-" * 50)
        analizar_oracion(caso)
