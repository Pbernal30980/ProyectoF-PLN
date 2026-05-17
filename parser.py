from gramatica import gramatica

class Nodo:
    def __init__(self, etiqueta, hijos=None):
        self.etiqueta = etiqueta
        self.hijos = hijos if hijos is not None else []

    # Imprimir el árbol visualmente en la consola
    def __repr__(self, nivel=0):
        ret = "\t" * nivel + repr(self.etiqueta) + "\n"
        for hijo in self.hijos:
            if isinstance(hijo, Nodo):
                ret += hijo.__repr__(nivel + 1)
            else:
                ret += "\t" * (nivel + 1) + repr(hijo) + "\n"
        return ret
    

def tokenizar(oracion):
    return oracion.lower().split()


def parse(simbolo, tokens):
    # Si nos quedamos sin palabras para analizar
    if not tokens:
        return []
    
    # CASO BASE: Si el símbolo es una palabra final (terminal)
    if simbolo not in gramatica:
        if simbolo == tokens[0]:
            # Consumimos la palabra y devolvemos el token restante
            return [ (simbolo, tokens[1:]) ]
        else:
            return [] # No coincide, esta ruta fracasa

    # CASO RECURSIVO: Si el símbolo está en el diccionario (no terminal)
    resultados = []
    
    # Probamos cada regla posible para este símbolo
    for produccion in gramatica[simbolo]:
        # Empezamos asumiendo que tenemos los tokens completos
        rutas_actuales = [ ([], tokens) ]
        
        # Procesamos cada elemento dentro de la regla (ej: "INTENCION", "REQUERIMIENTO")
        for elemento in produccion:
            nuevas_rutas = []
            for hijos_acumulados, tokens_restantes in rutas_actuales:
                # Llamada recursiva para analizar el elemento
                sub_resultados = parse(elemento, tokens_restantes)
                
                # Si tuvo éxito, guardamos el avance
                for sub_arbol, tokens_sobrantes in sub_resultados:
                    nuevas_rutas.append( (hijos_acumulados + [sub_arbol], tokens_sobrantes) )
            
            rutas_actuales = nuevas_rutas
            
        # Si logramos procesar toda la regla, creamos el Nodo y lo guardamos
        for hijos_finales, tokens_finales in rutas_actuales:
            nuevo_nodo = Nodo(simbolo, hijos_finales)
            resultados.append( (nuevo_nodo, tokens_finales) )
            
    return resultados


def analizar_oracion(oracion):
    tokens = tokenizar(oracion)
    resultados = parse("S", tokens)

    arboles_validos = []
    for arbol, tokens_restantes in resultados:
        if len(tokens_restantes) == 0:
            arboles_validos.append(arbol)

    print(f"Se encontraron {len(arboles_validos)} árbol(es) de derivación.\n")
    for i, arbol in enumerate(arboles_validos, start=1):
        print(f"--- Árbol {i} ---")
        print(arbol)


