from gramatica import gramatica, lexico

# FUNCIONES DE UTILIDAD LÉXICA Y UNIFICACIÓN

def obtener_definiciones(palabra):
    if palabra not in lexico:
        return []
    defs = lexico[palabra]
    return defs if isinstance(defs, list) else [defs]

def unificar_rasgos(rasgos1, rasgos2):
    """
    Evalúa concordancia morfológica y rastrea las palabras exactas involucradas.
    """
    resultado = dict(rasgos1)
    rasgos_estrictos = ['gen', 'num']
    
    origen1 = rasgos1.get('_origen', ['???'])
    origen2 = rasgos2.get('_origen', ['???'])
    
    for rasgo, valor in rasgos2.items():
        if rasgo == '_origen':
            continue
            
        if rasgo in rasgos_estrictos:
            if rasgo in resultado and resultado[rasgo] != valor:
                r1_str = " ".join([f"{k}:{v}" for k,v in rasgos1.items() if k not in ['cat', '_origen']])
                r2_str = " ".join([f"{k}:{v}" for k,v in rasgos2.items() if k not in ['cat', '_origen']])
                palabra1 = " ".join(origen1)
                palabra2 = " ".join(origen2)
                
                error_msg = f"Discordancia en '{rasgo}': la(s) palabra(s) '{palabra1}' [{r1_str}] choca(n) con '{palabra2}' [{r2_str}]"
                return None, error_msg
            resultado[rasgo] = valor
        elif rasgo not in resultado or rasgo == 'cat':
            resultado[rasgo] = valor
            
    resultado['_origen'] = origen1 + origen2
    return resultado, None

def lexer(oracion):
    return oracion.lower().split()

# PARSER ABSTRACTO (MÁQUINA RECURSIVA DCG)

def parse_abstracto(simbolo, tokens, pos, tracker):
    resultados = []
    
    if pos > tracker['max_pos']:
        tracker['max_pos'] = pos
        tracker['errores'].clear()

    # CASO 1: Símbolo No-Terminal
    if simbolo in gramatica:
        for produccion in gramatica[simbolo]:
            res_secuencia = parse_secuencia(produccion, tokens, pos, tracker)
            
            for arbol_hijos, rasgos_hijos, nueva_pos in res_secuencia:
                nodo = {simbolo: arbol_hijos, '_rasgos_heredados': rasgos_hijos}
                resultados.append((nodo, rasgos_hijos, nueva_pos))
                
    # CASO 2: Símbolo Terminal
    elif pos < len(tokens):
        token_actual = tokens[pos]
        
        if simbolo == token_actual:
            defs_lexico = obtener_definiciones(token_actual)
            if defs_lexico:
                for def_lex in defs_lexico:
                    rasgos = dict(def_lex)
                    rasgos['_origen'] = [token_actual]
                    hoja = {'terminal': token_actual, 'lexico': rasgos}
                    resultados.append((hoja, rasgos, pos + 1))
            else:
                hoja = {'terminal': token_actual, 'lexico': {'_origen': [token_actual]}}
                resultados.append((hoja, {'_origen': [token_actual]}, pos + 1))
                
    return resultados

def parse_secuencia(produccion, tokens, pos, tracker):
    if not produccion: 
        return [([], {}, pos)]
        
    simbolo_actual = produccion[0]
    resto_produccion = produccion[1:]
    
    resultados = []
    res_simbolo = parse_abstracto(simbolo_actual, tokens, pos, tracker)
    
    for arbol_sim, rasgos_sim, pos_sim in res_simbolo:
        res_resto = parse_secuencia(resto_produccion, tokens, pos_sim, tracker)
        
        for arbol_resto, rasgos_resto, pos_final in res_resto:
            rasgos_unificados, error_unif = unificar_rasgos(rasgos_sim, rasgos_resto)
            
            if rasgos_unificados is not None:
                nuevo_arbol = [arbol_sim] + arbol_resto
                resultados.append((nuevo_arbol, rasgos_unificados, pos_final))
            else:
                if pos_final >= tracker['max_pos']:
                    tracker['max_pos'] = pos_final
                    tracker['errores'].add(error_unif)
                
    return resultados

# GENERADOR DE ÁRBOL PARCIAL

def obtener_arbol_parcial(tokens):
    """Construye las partes del árbol que sí fueron válidas antes del fallo general."""
    arbol_parcial = []
    pos = 0
    tracker_dummy = {'max_pos': 0, 'errores': set()}
    
    componentes = ['INTENCION', 'REQUERIMIENTO', 'COMPLEMENTO']
    
    for comp in componentes:
        if pos >= len(tokens): break
        res = parse_abstracto(comp, tokens, pos, tracker_dummy)
        if res:
            mejor = max(res, key=lambda x: x[2])
            arbol_parcial.append(mejor[0])
            pos = mejor[2]
        else:
            break
            
    return {'S (Arbol Parcial hasta el error)': arbol_parcial}, pos

# ORQUESTADOR PRINCIPAl

def parse_oracion(tokens):
    # 1. PRE-VALIDACIÓN LÉXICA
    for token in tokens:
        esta_en_lexico = obtener_definiciones(token) != []
        esta_en_gramatica = any(token in prod for prods in gramatica.values() for prod in prods)
        
        if not esta_en_lexico and not esta_en_gramatica:
            print(f"[Error Lexico] La palabra '{token}' no existe en el diccionario ni en las reglas.")
            return None

    # 2. ANÁLISIS SINTÁCTICO
    tracker = {'max_pos': 0, 'errores': set()}
    resultados_s = parse_abstracto('S', tokens, 0, tracker)
    dags_validos = []
    
    for arbol, rasgos, pos_final in resultados_s:
        if pos_final == len(tokens):
            dags_validos.append(arbol)
            
    # 3. GESTIÓN DEL FALLO
    if not dags_validos:
        print("[Error Estructural o de Concordancia] detectado.\n")
        
        arbol_parcial, pos_alcanzada = obtener_arbol_parcial(tokens)
        
        print("--- ARBOL PARCIAL ALCANZADO ANTES DEL ERROR ---")
        imprimir_arbol(arbol_parcial)
        
        tokens_sobrantes = tokens[pos_alcanzada:]
        print(f"\n[!] Tokens sin procesar a partir del fallo: {tokens_sobrantes}\n")
        
        print("[MOTIVO DEL FALLO]:")
        if tracker['errores']:
            for err in tracker['errores']:
                print(f"   > {err}")
        else:
            token_problematico = tokens[min(tracker['max_pos'], len(tokens)-1)]
            print(f"   > La sintaxis se rompio al intentar procesar: '{token_problematico}'. " 
                  "O faltan palabras, o la estructura gramatical no lo permite aqui.")
                  
        return None 
    
    return dags_validos

# IMPRESIÓN VISUAL DEL ÁRBOL

def imprimir_arbol(nodo, prefijo="", es_ultimo=True, es_raiz=True):
    marcador = "" if es_raiz else ("└── " if es_ultimo else "├── ")
    
    if isinstance(nodo, dict) and 'terminal' in nodo:
        lex = nodo.get('lexico', {})
        cat = lex.get('cat', 'Desconocido').upper()
        rasgos_extra = ", ".join([f"{k}:{v}" for k, v in lex.items() if k not in ['cat', '_origen']])
        info_rasgos = f" [{rasgos_extra}]" if rasgos_extra else ""
        
        print(f"{prefijo}{marcador}'{nodo['terminal']}' (Cat: {cat}){info_rasgos}")
        return

    if isinstance(nodo, dict):
        llaves = [k for k in nodo.keys() if k != '_rasgos_heredados']
        if not llaves: return
        
        simbolo = llaves[0]
        hijos = nodo[simbolo]
        
        print(f"{prefijo}{marcador}{simbolo}")
        
        nuevo_prefijo = prefijo if es_raiz else prefijo + ("    " if es_ultimo else "│   ")
        for i, hijo in enumerate(hijos):
            imprimir_arbol(hijo, nuevo_prefijo, es_ultimo=(i == len(hijos) - 1), es_raiz=False)

def analizar_oracion(oracion):
    tokens = lexer(oracion)
    print(f"\n==============================================")
    print(f"Frase: '{oracion}'")
    print(f"Tokens: {tokens}")
    print(f"==============================================")
    
    dags = parse_oracion(tokens)

    if dags is None:
        print("\nResultado devuelto a la consola: None")
        return None

    print(f"[EXITO] Arbol(es) valido(s) encontrado(s): {len(dags)}\n")
    for idx, dag in enumerate(dags, 1):
        print(f"--- INTERPRETACION {idx} ---")
        imprimir_arbol(dag)
        print()