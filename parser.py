from gramatica import gramatica, lexico
from unificación import unificar

def obtener_definiciones(palabra):
    if palabra not in lexico:
        return []
    defs = lexico[palabra]
    return defs if isinstance(defs, list) else [defs]

def parse_modificadores_y_complementos(tokens, pos, concordancia_base):
    if pos >= len(tokens):
        return [], None, pos

    modificadores = []
    complemento = None

    while pos < len(tokens):
        palabra = tokens[pos]

        # Verificar si es una conjunción
        is_conj = False
        defs_conj = obtener_definiciones(palabra)
        es_nexo = any(d.get('cat') in ['conjuncion', 'preposicion'] for d in defs_conj)
        
        if es_nexo:
            is_conj = True
            palabra_real = tokens[pos+1] if pos+1 < len(tokens) else None
        else:
            palabra_real = palabra

        if not palabra_real:
            break

        defs_palabra_real = obtener_definiciones(palabra_real)
        if not defs_palabra_real:
            break

        # Tomamos la primera definición que encaje para modificadores (simplificación)
        # Aquí también se podría bifurcar si los modificadores fueran polisémios
        mod = defs_palabra_real[0]
        cat = mod.get('cat')

        if cat in ['adjetivo', 'marca', 'especificacion']:
            # Es un modificador individual
            
            # Intentar unificar si tiene rasgos de género y número
            rasgos_mod = {}
            if 'gen' in mod: rasgos_mod['gen'] = mod['gen']
            if 'num' in mod: rasgos_mod['num'] = mod['num']
            
            if rasgos_mod:
                unificado = unificar(concordancia_base, rasgos_mod)
                if unificado is None:
                    # En lugar de abortar silenciosamente, retornamos el error para propagarlo
                    return [], None, f"Error gramatical: no cuadra el género/número con el modificador '{palabra_real}'"
            
            info_mod = {'tipo': cat, 'valor': palabra_real, 'rasgos': mod}
            if is_conj:
                info_mod['nexo'] = palabra
                pos += 2
            else:
                pos += 1
                
            modificadores.append(info_mod)
            
        elif cat == 'gama':
            # Revisar la siguiente palabra para conformar "gama media/alta/baja"
            if is_conj:
                pos_next = pos + 2
            else:
                pos_next = pos + 1

            defs_next = obtener_definiciones(tokens[pos_next]) if pos_next < len(tokens) else []
            if defs_next and defs_next[0].get('cat') == 'gama_valor':
                valor_gama = tokens[pos_next]
                info_mod = {'tipo': 'gama', 'valor': f'gama {valor_gama}'}
                if is_conj:
                    info_mod['nexo'] = palabra
                pos = pos_next + 1
                modificadores.append(info_mod)
            else:
                info_mod = {'tipo': 'gama', 'valor': 'gama'}
                if is_conj:
                    info_mod['nexo'] = palabra
                pos = pos_next
                modificadores.append(info_mod)
                
        elif cat == 'uso_final' or cat == 'juego' or (is_conj and palabra == 'para'):
            # Lógica simplificada de complemento
            info_comp = {'tipo': 'complemento'}
            if is_conj:
                info_comp['nexo'] = palabra
                info_comp['valor'] = palabra_real
                pos += 2
            else:
                info_comp['valor'] = palabra_real
                pos += 1
                
            complemento = info_comp
            # Usualmente los complementos van al final
            break
        else:
            # Desconocido o no corresponde a esta regla
            break

    return modificadores, complemento, pos

def parse_oracion(tokens):
    print(f"\nAnalizando frase: '{' '.join(tokens)}'")
    pos = 0
    
    # 1. Intentamos sacar la INTENCION
    palabra_intencion = tokens[pos]
    intencion = None
    defs_intencion = obtener_definiciones(palabra_intencion)
    if defs_intencion and defs_intencion[0].get('cat') == 'intencion':
        intencion = defs_intencion[0]
        pos += 1
        
    # 2. Pasamos al REQUERIMIENTO (Articulo + Sujeto)
    if pos + 1 >= len(tokens):
        return ["Faltan palabras para completar el requerimiento"]
        
    palabra_art = tokens[pos]
    palabra_sujeto = tokens[pos + 1]
    
    defs_art = obtener_definiciones(palabra_art)
    defs_sujeto = obtener_definiciones(palabra_sujeto)
    
    if not defs_art or not defs_sujeto:
        return [f"Palabras no encontradas en el léxico: {palabra_art} o {palabra_sujeto}"]
        
    # Aquí soportaremos múltiples significados para el sujeto (como memoria)
    resultados_finales = []
    
    # Tomamos el primer significado del artículo (usualmete es 1 solo)
    rasgos_art = defs_art[0]
    
    # RAMIFICACION: Iteramos por cada posible significado del sujeto
    for rasgos_sujeto in defs_sujeto:
        # Aquí ocurre la magia de la unificación para esta rama
        concordancia = unificar({'gen': rasgos_art.get('gen'), 'num': rasgos_art.get('num')}, 
                                {'gen': rasgos_sujeto.get('gen'), 'num': rasgos_sujeto.get('num')})
                                
        if concordancia is None:
            resultados_finales.append(f"Error gramatical: no cuadra el género/número entre '{palabra_art}' y '{palabra_sujeto}' (Interpretación: {rasgos_sujeto.get('subtipo', 'General')})")
            continue
            
        requerimiento_base = {
            'cat': 'REQUERIMIENTO',
            'articulo': palabra_art,
            'sujeto': palabra_sujeto,
            'rasgos_unificados': concordancia
        }
        
        # Agregamos los rasgos extra de esta interpretación al requerimiento
        if 'tipo' in rasgos_sujeto: requerimiento_base['tipo_sujeto'] = rasgos_sujeto['tipo']
        if 'subtipo' in rasgos_sujeto: requerimiento_base['subtipo'] = rasgos_sujeto['subtipo']
        
        pos_actual = pos + 2
        
        resultado_mods = parse_modificadores_y_complementos(tokens, pos_actual, concordancia)
        if isinstance(resultado_mods[2], str): # Retornó un string de error
            resultados_finales.append(resultado_mods[2])
            continue
            
        modificadores, complemento, pos_final = resultado_mods
        
        if modificadores:
            requerimiento_base['MODIFICADORES'] = modificadores
        
        # Ensamblamos el DAG para esta interpretación
        dag_resultado = {
            'INTENCION': intencion,
            'REQUERIMIENTO': requerimiento_base,
        }
        
        if complemento:
            dag_resultado['COMPLEMENTO'] = complemento
            
        if pos_final < len(tokens):
            dag_resultado['tokens_restantes_no_procesados'] = tokens[pos_final:]
            
        resultados_finales.append(dag_resultado)
        
    return resultados_finales

def analizar_oracion(oracion):
    tokens = oracion.lower().split()
    resultados = parse_oracion(tokens)
    
    import json
    
    if not resultados:
        print("La oración no pudo ser analizada.")
        return
        
    # Si todo devuelve strings (errores), imprimimos el primero
    if all(isinstance(r, str) for r in resultados):
        print(resultados[0])
        return

    # Filtramos solo los DAGs válidos para mostrarlos
    dags_validos = [r for r in resultados if not isinstance(r, str)]
    
    print(f"Árbol(es) resultante(s) DAG(s) encontrados: {len(dags_validos)}")
    for idx, dag in enumerate(dags_validos, 1):
        print(f"\n--- INTERPRETACIÓN {idx} ---")
        print(json.dumps(dag, indent=2, ensure_ascii=False))


