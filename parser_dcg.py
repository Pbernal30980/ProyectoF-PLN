from gramatica import gramatica, lexico
from unificacion import unificar_rasgos

def obtener_definiciones(palabra):
    if palabra not in lexico:
        return []
    defs = lexico[palabra]
    return defs if isinstance(defs, list) else [defs]

def parse_abstracto(simbolo, tokens, pos, tracker):
    resultados = []
    if pos > tracker['max_pos']:
        tracker['max_pos'] = pos
        tracker['errores'].clear()

    if simbolo in gramatica:
        for produccion in gramatica[simbolo]:
            for arbol_hijos, rasgos_hijos, nueva_pos in \
                    parse_secuencia(produccion, tokens, pos, tracker):
                nodo = {simbolo: arbol_hijos,
                        '_rasgos_heredados': rasgos_hijos}
                resultados.append((nodo, rasgos_hijos, nueva_pos))

    elif pos < len(tokens):
        token_actual = tokens[pos]
        if simbolo == token_actual:
            defs = obtener_definiciones(token_actual)
            if defs:
                for d in defs:
                    rasgos = dict(d)
                    rasgos['_origen'] = [token_actual]
                    hoja = {'terminal': token_actual, 'lexico': rasgos}
                    resultados.append((hoja, rasgos, pos + 1))
            else:
                hoja = {'terminal': token_actual,
                        'lexico': {'_origen': [token_actual]}}
                resultados.append((hoja, {'_origen': [token_actual]}, pos + 1))
    return resultados

def parse_secuencia(produccion, tokens, pos, tracker):
    if not produccion:
        return [([], {}, pos)]
    simbolo_actual   = produccion[0]
    resto_produccion = produccion[1:]
    resultados = []

    for arbol_sim, rasgos_sim, pos_sim in \
            parse_abstracto(simbolo_actual, tokens, pos, tracker):
        for arbol_resto, rasgos_resto, pos_final in \
                parse_secuencia(resto_produccion, tokens, pos_sim, tracker):
            rasgos_unif, error = unificar_rasgos(rasgos_sim, rasgos_resto)
            if rasgos_unif is not None:
                resultados.append(
                    ([arbol_sim] + arbol_resto, rasgos_unif, pos_final)
                )
            elif pos_final >= tracker['max_pos']:
                tracker['max_pos'] = pos_final
                tracker['errores'].add(error)
    return resultados

def obtener_arbol_parcial(tokens):
    arbol_parcial = []
    pos = 0
    tracker_dummy = {'max_pos': 0, 'errores': set()}
    for comp in ['INTENCION', 'REQUERIMIENTO', 'COMPLEMENTO']:
        if pos >= len(tokens):
            break
        res = parse_abstracto(comp, tokens, pos, tracker_dummy)
        if res:
            mejor = max(res, key=lambda x: x[2])
            arbol_parcial.append(mejor[0])
            pos = mejor[2]
        else:
            break
    return {'S (Arbol Parcial hasta el error)': arbol_parcial}, pos