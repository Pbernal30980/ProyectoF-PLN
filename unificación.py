# "el" es determinante masculino singular

#definición de dags que permiten unificación
dag_el= {
    "cat": "det",
    "gen": "masc",
    "num": "sing"
}

dag_las= {
    "cat": "det",
    "gen": "fem",
    "num": "plur"
}

dag_np_complejo = {
    "cat": "np",
    "num": "sing",
    "acuerdo": {
        "gen": "masc",
        "num": "sing"
    }
}

print(f"dag_ejemplo: {dag_el}")
print(f"dag_las: {dag_las}")
print(f"dag_np_complejo: {dag_np_complejo}")


#==================
# PARTE 2: ALGORITMO DE UNIFICACIÓN
#==================

# Combinar dos Dags, en uno.
# Si los dos tienen el mismo rango con el mismo valor -> sin problema, se fusiona
# Si los dos tienen el mismo rango con distinto valor -> error, no se pueden unificar
# Si el rasgo existe en uno de los Dags pero no en el otro -> se agrega al resultado

def unificar(dag1, dag2):
    resultado = dict(dag1)

    for rasgo, valor in dag2.items():
        # Si rasgo ya existe en resultado
        if rasgo in resultado:
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                # Si ambos son sub-dags, unificamos recursivamente
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None  # No se pueden unificar
                resultado[rasgo] = sub

            elif resultado[rasgo] != valor:
                return None  # No se pueden unificar
        else:
            resultado[rasgo] = valor  # Agregamos el nuevo rasgo

    return resultado


#==================
# PARTE 3: Lexico con DAGs
#==================

#Cada palabra del vocabulario se representa como un DAG con sus rasgos gramaticales
# Cuando el parser analiza una oración, consulta el DAG de cada palabra para verificar su categoría y rasgos, y luego unifica esos DAGs con los requeridos por la gramática para construir el árbol sintáctico.

Lexico = {
    # Determinantes - Cada uno lleva su genero y número
    "el": {"cat": "det", "gen": "masc", "num": "sing"},
    "la": {"cat": "det", "gen": "fem", "num": "sing"},
    "los": {"cat": "det", "gen": "masc", "num": "plur"},
    "las": {"cat": "det", "gen": "fem", "num": "plur"},
    #Sustantivos - tambien llevan genero y numero, ademas de la categoria "sust"
    "gato": {"cat": "n", "gen": "masc", "num": "sing"},
    "gata": {"cat": "n", "gen": "fem", "num": "sing"},
    "gatos": {"cat": "n", "gen": "masc", "num": "plur"},
    "perro": {"cat": "n", "gen": "masc", "num": "sing"},
    "perros": {"cat": "n", "gen": "masc", "num": "plur"},
    "niña": {"cat": "n", "gen": "fem", "num": "sing"},
    "niñas": {"cat": "n", "gen": "fem", "num": "plur"},


    # Verbos - LLevan numero para concordar con el sujeto y accion para concordar con la intencion (busco, quiero, necesito)

    "corre": {"cat": "v", "num": "sing", "accion": "correr"},
    "corren": {"cat": "v", "num": "plur", "accion": "correr"},
    "duerme": {"cat": "v", "num": "sing", "accion": "dormir"},
    "duermen": {"cat": "v", "num": "plur", "accion": "dormir"},
    "juega": {"cat": "v", "num": "sing", "accion": "jugar"},
    "juegan": {"cat": "v", "num": "plur", "accion": "jugar"},

}

print("Lexico con DAGs:")
for palabra, rasgos in Lexico.items():
    print(f"'{palabra}': '{rasgos}'")

def parse_np(tokens, pos):
    if pos + 1 >= len(tokens):
        return None, pos
    
    palabra_det = tokens[pos]
    palabra_n = tokens[pos + 1]

    if palabra_det not in Lexico or palabra_n not in Lexico:
        print(f"{palabra_det}' o '{palabra_n}' no encontrada en el léxico.")
        return None, pos
    
    rasgos_det = Lexico[palabra_det]
    rasgos_n = Lexico[palabra_n]

    # verificamos que la palabra sea realmente un determinante y la segunda un sustantivo
    if rasgos_det.get("cat") != "det" or rasgos_n.get("cat") != "n":
        print(f"{palabra_det} no es un determinante o {palabra_n} no es un sustantivo.")
        return None, pos
    
    if rasgos_n.get("cat") != "n":
        print(f"{palabra_n} no es un sustantivo.")
        return None, pos
    
    concord_det = {"gen": rasgos_det.get("gen"), "num": rasgos_det.get("num")}
    concord_n = {"gen": rasgos_n.get("gen"), "num": rasgos_n.get("num")}

    unificado = unificar(concord_det, concord_n)
    if unificado is None:
        print(f"Error de concordancia entre '{palabra_det}' y '{palabra_n}'.")
        return None, pos
    
    np = {
        "cat": "np",
        "gen": unificado.get("gen"),
        "num": unificado.get("num"),
        "det": palabra_det,
        "n": palabra_n
    }

    print(f" NP: {palabra_det} + {palabra_n} -> {np}")

    return np, pos + 2

def parse_vp(tokens, pos):
    if pos + 1 >= len(tokens):
        return None, pos
    
    palabra_v = tokens[pos]

    if palabra_v not in Lexico:
        print(f"'{palabra_v}' no encontrada en el léxico.")
        return None, pos
    
    rasgos_v = Lexico[palabra_v]

    if rasgos_v.get("cat") != "v":
        print(f"{palabra_v} no es un verbo.")
        return None, pos
    
    vp = {
        "cat": "vp",
        "num": rasgos_v.get["num"],
        "accion": rasgos_v.get["accion"],
        "v": palabra_v
    }

    print(f" VP: {palabra_v} accion {rasgos_v.get('accion')} , num {rasgos_v.get('num')} -> {vp}")
    return vp, pos + 1

def parse_s(tokens):
    np, pos = parse_np(tokens, 0)
    if np is None:
        print("no se reconoció el np")
        return None
    
    vp, pos = parse_vp(tokens, pos)
    if vp is None:
        print("no se reconoció el vp")
        return None
    
    if pos != len(tokens):
        print("Quedaron tokens sin procesar.")
        return None
    
    concordancia = unificar({"num": np.get("num")}, {"num": vp.get("num")})
    if concordancia is None:
        print("Error de concordancia entre NP y VP.")
        return None 
    
    oracion = {
        "cat": "s",
        "np": np,
        "vp": vp,
        "accion": vp["accion"]
    }

    return oracion

def extraer_intencion(oracion):
    accion = oracion.get("accion")
    if accion == "correr":
        return "intención de correr"
    elif accion == "dormir":
        return "intención de dormir"
    elif accion == "jugar":
        return "intención de jugar"
    else:
        return "intención desconocida"  