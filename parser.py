import json
from gramatica import gramatica, lexico

# Excepción personalizada
class UnificationError(Exception):
    pass


class ParseResult:
    def __init__(self, dags=None, errors=None, tokens_restantes=None):
        self.dags = dags or []
        self.errors = errors or []
        self.tokens_restantes = tokens_restantes or []

    @property
    def ok(self):
        return len(self.errors) == 0

# Función de unificación
def unificar(dag1, dag2):
    resultado = dict(dag1)
    for rasgo, valor in dag2.items():
        if rasgo in resultado:
            if isinstance(resultado[rasgo], dict) and isinstance(valor, dict):
                sub = unificar(resultado[rasgo], valor)
                if sub is None:
                    return None
                resultado[rasgo] = sub
            elif resultado[rasgo] != valor:
                return None
        else:
            resultado[rasgo] = valor
    return resultado

def obtener_definiciones(palabra):
    if palabra not in lexico:
        return []
    defs = lexico[palabra]
    return defs if isinstance(defs, list) else [defs]

# Lexer: Tokenización y preprocesamiento de palabras compuestas
def lexer(oracion):
    tokens_raw = oracion.lower().split()
    tokens = []
    pos = 0
    while pos < len(tokens_raw):
        # Fusiones posibles de lexer
        if pos + 1 < len(tokens_raw):
            if tokens_raw[pos] == "gama" and tokens_raw[pos + 1] in ["alta", "media", "baja"]:
                tokens.append(f"gama_{tokens_raw[pos + 1]}")
                pos += 2
                continue
            if tokens_raw[pos] == "uso" and tokens_raw[pos + 1] == "diario":
                tokens.append("uso_diario")
                pos += 2
                continue
            if tokens_raw[pos] == "para" and tokens_raw[pos + 1] in ["jugar", "programar"]:
                tokens.append(f"para_{tokens_raw[pos + 1]}")
                pos += 2
                continue
            if tokens_raw[pos] == "para" and tokens_raw[pos + 1] == "uso" and pos + 2 < len(tokens_raw) and tokens_raw[pos + 2] == "diario":
                tokens.append("para_uso_diario")
                pos += 3
                continue

        tokens.append(tokens_raw[pos])
        pos += 1
    return tokens

# ==== ABSTRACCIONES DEL PARSER ====

def parse_intencion(tokens, pos):
    if pos >= len(tokens):
        return None, pos
    palabra = tokens[pos]
    defs = obtener_definiciones(palabra)
    if defs and defs[0].get('cat') == 'intencion':
        return defs[0], pos + 1
    return None, pos


def require_cat(palabra, categoria):
    defs = obtener_definiciones(palabra)
    if not defs:
        raise UnificationError(f"Palabra no encontrada en el léxico: '{palabra}'")
    if defs[0].get('cat') != categoria:
        raise UnificationError(f"Se esperaba '{categoria}' y se encontró '{defs[0].get('cat')}' en '{palabra}'")
    return defs

def parse_requerimiento(tokens, pos):
    if pos >= len(tokens):
        raise UnificationError("Faltan palabras para completar el requerimiento")

    palabra_1 = tokens[pos]
    defs_1 = obtener_definiciones(palabra_1)
    cat_1 = defs_1[0].get('cat') if defs_1 else None

    # Caso 1: determinante o cantidad + sujeto
    if cat_1 in ['art', 'cantidad']:
        if pos + 1 >= len(tokens):
            raise UnificationError("Faltan palabras para completar el requerimiento")

        palabra_art = palabra_1
        idx_sujeto = pos + 1
        pre_mods = []

        defs_posible_adj = obtener_definiciones(tokens[idx_sujeto])
        if defs_posible_adj and defs_posible_adj[0].get('cat') == 'adjetivo':
            pre_mods.append((tokens[idx_sujeto], defs_posible_adj[0]))
            idx_sujeto += 1
            if idx_sujeto >= len(tokens):
                raise UnificationError("Falta el sujeto después del adjetivo")

        palabra_sujeto = tokens[idx_sujeto]

        defs_art = defs_1
        defs_sujeto = [d for d in obtener_definiciones(palabra_sujeto) if d.get('cat') == 'sujeto']
        if not defs_sujeto:
            raise UnificationError(f"Se esperaba un sujeto y se encontró '{palabra_sujeto}'")

        rasgos_art = defs_art[0]
        opciones_requerimiento = []

        for rasgos_sujeto in defs_sujeto:
            concord_art = {'gen': rasgos_art.get('gen'), 'num': rasgos_art.get('num')}
            concord_sujeto = {'gen': rasgos_sujeto.get('gen'), 'num': rasgos_sujeto.get('num')}

            concordancia = unificar(concord_art, concord_sujeto)
            if concordancia is None:
                continue

            for palabra_adj, rasgos_adj in pre_mods:
                rasgos_mod = {}
                if 'gen' in rasgos_adj:
                    rasgos_mod['gen'] = rasgos_adj['gen']
                if 'num' in rasgos_adj:
                    rasgos_mod['num'] = rasgos_adj['num']
                if rasgos_mod:
                    if unificar(concordancia, rasgos_mod) is None:
                        raise UnificationError(
                            f"Error gramatical: no cuadra el género/número con el modificador '{palabra_adj}'"
                        )

            req = {
                'cat': 'REQUERIMIENTO',
                'articulo': palabra_art,
                'sujeto': palabra_sujeto,
                'rasgos_unificados': concordancia
            }
            if 'tipo' in rasgos_sujeto:
                req['tipo_sujeto'] = rasgos_sujeto['tipo']
            if 'subtipo' in rasgos_sujeto:
                req['subtipo'] = rasgos_sujeto['subtipo']
            if pre_mods:
                req['MODIFICADORES'] = [
                    {'tipo': 'adjetivo', 'valor': palabra, 'rasgos': rasgos}
                    for palabra, rasgos in pre_mods
                ]
            opciones_requerimiento.append((req, concordancia))

        if not opciones_requerimiento:
            raise UnificationError(f"Error gramatical: no cuadra el género/número entre '{palabra_art}' y '{palabra_sujeto}'")

        return opciones_requerimiento[0][0], opciones_requerimiento[0][1], idx_sujeto + 1

    # Caso 2: sujeto sin determinante
    palabra_sujeto = palabra_1
    defs_sujeto = [d for d in obtener_definiciones(palabra_sujeto) if d.get('cat') == 'sujeto']
    if not defs_sujeto:
        raise UnificationError(f"Se esperaba un sujeto y se encontró '{palabra_sujeto}'")

    rasgos_sujeto = defs_sujeto[0]
    concordancia = {'gen': rasgos_sujeto.get('gen'), 'num': rasgos_sujeto.get('num')}

    req = {
        'cat': 'REQUERIMIENTO',
        'sujeto': palabra_sujeto,
        'rasgos_unificados': concordancia
    }
    if 'tipo' in rasgos_sujeto:
        req['tipo_sujeto'] = rasgos_sujeto['tipo']
    if 'subtipo' in rasgos_sujeto:
        req['subtipo'] = rasgos_sujeto['subtipo']

    return req, concordancia, pos + 1

def parse_modificadores_y_complementos(tokens, pos, concordancia_base):
    modificadores = []
    complemento = None

    while pos < len(tokens):
        palabra = tokens[pos]
        nexo = None
        defs_nexo = obtener_definiciones(palabra)
        if any(d.get('cat') in ['conjuncion', 'preposicion'] for d in defs_nexo):
            nexo = palabra
            pos += 1
            if pos >= len(tokens):
                break
            palabra = tokens[pos]

        if palabra.startswith('gama_'):
            parts = palabra.split('_')
            info_mod = {'tipo': 'gama', 'valor': f"gama {parts[1]}"}
            if nexo:
                info_mod['nexo'] = nexo
            pos += 1
            modificadores.append(info_mod)
            continue

        if palabra in ['uso_diario', 'para_jugar', 'para_programar', 'para_uso_diario']:
            valor = palabra
            if palabra.startswith('para_'):
                valor = palabra.replace('para_', '')
            complemento = {'tipo': 'complemento', 'valor': valor}
            if nexo:
                complemento['nexo'] = nexo
            pos += 1
            break

        defs_palabra = obtener_definiciones(palabra)
        if not defs_palabra:
            break

        mod = defs_palabra[0]
        cat = mod.get('cat')

        if cat in ['adjetivo', 'marca', 'especificacion']:
            rasgos_mod = {}
            if 'gen' in mod: rasgos_mod['gen'] = mod['gen']
            if 'num' in mod: rasgos_mod['num'] = mod['num']
            
            if rasgos_mod:
                unificado = unificar(concordancia_base, rasgos_mod)
                if unificado is None:
                    raise UnificationError(f"Error gramatical: no cuadra el género/número con el modificador '{palabra}'")
            
            info_mod = {'tipo': cat, 'valor': palabra, 'rasgos': mod}
            if nexo:
                info_mod['nexo'] = nexo
            pos += 1
            modificadores.append(info_mod)
            
        elif cat in ['uso_final', 'juego']:
            complemento = {'tipo': 'complemento', 'valor': palabra}
            if nexo:
                complemento['nexo'] = nexo
            pos += 1
            break
        else:
            break

    return modificadores, complemento, pos

def parse_s(tokens):
    print(f"\nAnalizando frase (Tokens): {tokens}")
    pos = 0

    try:
        intencion, pos = parse_intencion(tokens, pos)
        if intencion is None:
            # Rebobinamos si no hay intencion y probamos directo desde requerimiento
            pass
        requerimiento, concordancia_base, pos = parse_requerimiento(tokens, pos)
        modificadores, complemento, pos = parse_modificadores_y_complementos(tokens, pos, concordancia_base)
        
        if modificadores:
            if 'MODIFICADORES' in requerimiento:
                requerimiento['MODIFICADORES'].extend(modificadores)
            else:
                requerimiento['MODIFICADORES'] = modificadores
            
        dag_resultado = {}
        if intencion:
            dag_resultado['INTENCION'] = intencion
        dag_resultado['REQUERIMIENTO'] = requerimiento
        
        if complemento:
            dag_resultado['COMPLEMENTO'] = complemento

        resultado = ParseResult(dags=[dag_resultado])
        if pos < len(tokens):
            resultado.tokens_restantes = tokens[pos:]
        return resultado

    except UnificationError as e:
        return ParseResult(errors=[str(e)])

def analizar_oracion(oracion):
    tokens = lexer(oracion)
    resultados = parse_s(tokens)

    if not resultados.ok:
        print(f"Error: {resultados.errors[0]}")
        return

    print(f"Árbol(es) resultante(s) DAG(s) encontrados: {len(resultados.dags)}")
    for idx, dag in enumerate(resultados.dags, 1):
        print(f"\n--- INTERPRETACIÓN {idx} ---")
        print(json.dumps(dag, indent=2, ensure_ascii=False))

    if resultados.tokens_restantes:
        print(f"Tokens no procesados: {resultados.tokens_restantes}")

