from gramatica import gramatica, lexico
import unicodedata
import re

def obtener_definiciones(palabra):
    """Devuelve lista de definiciones léxicas de una palabra."""
    if palabra not in lexico:
        return []
    defs = lexico[palabra]
    return defs if isinstance(defs, list) else [defs]


def unificar_rasgos(rasgos1, rasgos2):
    """
    Unifica dos conjuntos de rasgos morfológicos.
    Falla con mensaje de error si hay discordancia en género o número.
    Los adjetivos invariables (gen='inv') nunca generan discordancia.
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
                # Adjetivos invariables en género nunca chocan
                if 'inv' in (resultado[rasgo], valor):
                    continue
                r1_str  = " ".join([f"{k}:{v}" for k, v in rasgos1.items() if k not in ['cat', '_origen']])
                r2_str  = " ".join([f"{k}:{v}" for k, v in rasgos2.items() if k not in ['cat', '_origen']])
                palabra1 = " ".join(origen1)
                palabra2 = " ".join(origen2)
                error_msg = (
                    f"Discordancia en '{rasgo}': "
                    f"'{palabra1}' [{r1_str}] choca con '{palabra2}' [{r2_str}]"
                )
                return None, error_msg
            resultado[rasgo] = valor
        elif rasgo not in resultado or rasgo == 'cat':
            resultado[rasgo] = valor

    resultado['_origen'] = origen1 + origen2
    return resultado, None



def normalizar(texto):
    """
    Quita tildes/diacríticos, elimina puntuación y normaliza espacios.
    Ejemplo: "Recomiéndame, un teléfono." → "recomiendame un telefono"
    """
    # 1. Minúsculas
    texto = texto.lower()
    # 2. Descomponer caracteres Unicode (é → e + acento) y quedarse solo
    #    con los caracteres base (categoría 'Mn' = marca no espaciadora = tilde)
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # 3. Eliminar puntuación (comas, puntos, signos de interrogación, etc.)
    texto = re.sub(r'[^\w\s]', '', texto)
    # 4. Colapsar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def lexer(oracion):
    return normalizar(oracion).split()


# ── Máquina recursiva DCG ────────────────────────────────────

def parse_abstracto(simbolo, tokens, pos, tracker):
    """
    Intenta hacer coincidir 'simbolo' a partir de 'pos'.
    Devuelve lista de (arbol, rasgos, nueva_pos).
    """
    resultados = []

    if pos > tracker['max_pos']:
        tracker['max_pos'] = pos
        tracker['errores'].clear()

    # CASO 1: No-terminal → expandir todas sus producciones
    if simbolo in gramatica:
        for produccion in gramatica[simbolo]:
            for arbol_hijos, rasgos_hijos, nueva_pos in parse_secuencia(produccion, tokens, pos, tracker):
                nodo = {simbolo: arbol_hijos, '_rasgos_heredados': rasgos_hijos}
                resultados.append((nodo, rasgos_hijos, nueva_pos))

    # CASO 2: Terminal → cotejar token actual con léxico
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
    """
    Intenta hacer coincidir una producción completa (lista de símbolos).
    Unifica rasgos símbolo a símbolo.
    """
    if not produccion:
        return [([], {}, pos)]

    simbolo_actual  = produccion[0]
    resto_produccion = produccion[1:]
    resultados = []

    for arbol_sim, rasgos_sim, pos_sim in parse_abstracto(simbolo_actual, tokens, pos, tracker):
        for arbol_resto, rasgos_resto, pos_final in parse_secuencia(resto_produccion, tokens, pos_sim, tracker):
            rasgos_unificados, error_unif = unificar_rasgos(rasgos_sim, rasgos_resto)
            if rasgos_unificados is not None:
                resultados.append(([arbol_sim] + arbol_resto, rasgos_unificados, pos_final))
            else:
                if pos_final >= tracker['max_pos']:
                    tracker['max_pos'] = pos_final
                    tracker['errores'].add(error_unif)

    return resultados


# ── Árbol parcial para diagnóstico de errores ────────────────

def obtener_arbol_parcial(tokens):
    """
    Construye las partes del árbol que sí fueron válidas antes del fallo.
    Útil para mostrar hasta dónde llegó el parser.
    """
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


# ── Impresión visual del árbol ───────────────────────────────

def imprimir_arbol(nodo, prefijo="", es_ultimo=True, es_raiz=True):
    marcador = "" if es_raiz else ("└── " if es_ultimo else "├── ")

    if isinstance(nodo, dict) and 'terminal' in nodo:
        lex = nodo.get('lexico', {})
        cat = lex.get('cat', 'Desconocido').upper()
        rasgos_extra = ", ".join([f"{k}:{v}" for k, v in lex.items() if k not in ['cat', '_origen']])
        info_rasgos  = f" [{rasgos_extra}]" if rasgos_extra else ""
        print(f"{prefijo}{marcador}'{nodo['terminal']}' (Cat: {cat}){info_rasgos}")
        return

    if isinstance(nodo, dict):
        llaves = [k for k in nodo.keys() if k != '_rasgos_heredados']
        if not llaves:
            return
        simbolo = llaves[0]
        hijos   = nodo[simbolo]
        print(f"{prefijo}{marcador}{simbolo}")
        nuevo_prefijo = prefijo if es_raiz else prefijo + ("    " if es_ultimo else "│   ")
        for i, hijo in enumerate(hijos):
            imprimir_arbol(hijo, nuevo_prefijo, es_ultimo=(i == len(hijos) - 1), es_raiz=False)


#####################################################################################
## ATN

def _buscar_nodo(arbol, nombre_simbolo):
    """
    Búsqueda en profundidad: devuelve el primer nodo cuya
    clave principal coincide con nombre_simbolo.
    """
    if not isinstance(arbol, dict):
        return None
    for clave, hijos in arbol.items():
        if clave == '_rasgos_heredados':
            continue
        if clave == nombre_simbolo:
            return arbol
        if isinstance(hijos, list):
            for hijo in hijos:
                resultado = _buscar_nodo(hijo, nombre_simbolo)
                if resultado:
                    return resultado
    return None


def _extraer_terminales(nodo):
    """
    Recoge todos los tokens terminales de un subárbol,
    en orden de izquierda a derecha.
    """
    palabras = []
    if isinstance(nodo, dict):
        if 'terminal' in nodo:
            palabras.append(nodo['terminal'])
        else:
            for clave, hijos in nodo.items():
                if clave == '_rasgos_heredados':
                    continue
                if isinstance(hijos, list):
                    for hijo in hijos:
                        palabras.extend(_extraer_terminales(hijo))
    return palabras


def _extraer_rasgos_sujeto(nodo_sujeto):
    """
    Extrae los rasgos morfológicos del núcleo del SUJETO
    para incluirlos en el contexto.
    """
    rasgos = {}
    if not nodo_sujeto:
        return rasgos
    hijos = nodo_sujeto.get('SUJETO', [])
    for hijo in hijos:
        if isinstance(hijo, dict) and 'terminal' in hijo:
            lex = hijo.get('lexico', {})
            rasgos['gen']  = lex.get('gen',  '?')
            rasgos['num']  = lex.get('num',  '?')
            rasgos['tipo'] = lex.get('tipo', '?')
            break
    return rasgos


def _clasificar_modificador(nodo_modif):
    """
    Dado un nodo MODIFICADOR, determina su tipo semántico
    (marca, gama, especificacion_tec, adjetivo) y su valor textual.
    """
    if not isinstance(nodo_modif, dict):
        return None

    hijos = nodo_modif.get('MODIFICADOR', [])
    for hijo in hijos:
        if not isinstance(hijo, dict):
            continue
        for tipo in ['MARCA', 'GAMA', 'ESPECIFICACION_TEC', 'ADJETIVO']:
            sub = _buscar_nodo(hijo, tipo)
            if sub:
                palabras = _extraer_terminales(sub)
                return {'tipo': tipo.lower(), 'valor': ' '.join(palabras)}
    return None


def _recolectar_modificadores(nodo_modifs):
    """
    Recorre recursivamente el árbol MODIFICADORES
    y devuelve una lista plana de dicts clasificados.
    """
    resultado = []
    if not isinstance(nodo_modifs, dict):
        return resultado

    hijos = nodo_modifs.get('MODIFICADORES', [])
    for hijo in hijos:
        if not isinstance(hijo, dict):
            continue

        # Nodo MODIFICADOR individual
        if 'MODIFICADOR' in hijo:
            m = _clasificar_modificador(hijo)
            if m:
                resultado.append(m)

        # Recursión para MODIFICADORES anidados
        if 'MODIFICADORES' in hijo:
            resultado.extend(_recolectar_modificadores(hijo))

    return resultado


# ── Motor ATN principal ──────────────────────────────────────

def recorrer_atn(arbol):
    """
    Segunda pasada sobre el árbol producido por el DCG.
    Recorre con estados explícitos y acumula registros semánticos.

    Devuelve:
        contexto  → dict con intencion, sujeto, modificadores, complemento
        traza_atn → lista de strings describiendo cada transición de estado
    """
    contexto  = {}
    traza_atn = []

    def setr(clave, valor):
        """SETR: escribe un registro en el contexto."""
        contexto[clave] = valor
        traza_atn.append(f"      SETR {clave} = {valor!r}")

    def getr(clave):
        """GETR: lee un registro del contexto."""
        return contexto.get(clave)

    def transitar(estado_actual, estado_siguiente, motivo=""):
        traza_atn.append(f"  {estado_actual:22s} --> {estado_siguiente:22s}  [{motivo}]")
        return estado_siguiente

    # ── q0: inicio ───────────────────────────────────────────
    estado = "q0_inicio"
    traza_atn.append(f"  {'ESTADO INICIAL':22s} --> {'q0_inicio':22s}")

    raiz_hijos = arbol.get('S', [])
    if not raiz_hijos:
        traza_atn.append("  [ATN] No se encontró nodo raíz S — árbol vacío")
        return contexto, traza_atn

    # ── q1: intentar encontrar INTENCION ─────────────────────
    nodo_intencion = None
    for hijo in raiz_hijos:
        if isinstance(hijo, dict) and 'INTENCION' in hijo:
            nodo_intencion = hijo
            break

    if nodo_intencion:
        estado = transitar(estado, "q1_en_intencion", "nodo INTENCION encontrado")
        terminales_int = _extraer_terminales(nodo_intencion)
        token_int = terminales_int[0] if terminales_int else '?'
        # SETR accion: buscar en léxico la acción asociada
        accion = lexico.get(token_int, {})
        if isinstance(accion, list):
            accion = accion[0]
        setr('intencion', accion.get('accion', token_int))
    else:
        estado = transitar(estado, "q1_en_intencion", "INTENCION ausente (oración sin verbo de intención)")
        setr('intencion', None)

    # ── q2: REQUERIMIENTO ────────────────────────────────────
    nodo_requerim = None
    for hijo in raiz_hijos:
        if isinstance(hijo, dict) and 'REQUERIMIENTO' in hijo:
            nodo_requerim = hijo
            break

    if not nodo_requerim:
        traza_atn.append("  [ATN] No se encontró REQUERIMIENTO — árbol malformado")
        return contexto, traza_atn

    estado = transitar(estado, "q2_en_requerim", "nodo REQUERIMIENTO encontrado")
    hijos_req = nodo_requerim.get('REQUERIMIENTO', [])

    # ── q2a: ARTICULO (opcional) ─────────────────────────────
    nodo_art = None
    for h in hijos_req:
        if isinstance(h, dict) and 'ARTICULO' in h:
            nodo_art = h
            break

    if nodo_art:
        estado = transitar(estado, "q2a_en_articulo", "arco ARTICULO presente")
        terminales_art = _extraer_terminales(nodo_art)
        lex_art = lexico.get(terminales_art[0], {}) if terminales_art else {}
        if isinstance(lex_art, list):
            lex_art = lex_art[0]
        setr('articulo', {
            'forma': terminales_art[0] if terminales_art else '?',
            'gen':   lex_art.get('gen', '?'),
            'num':   lex_art.get('num', '?'),
        })
    else:
        estado = transitar(estado, "q2a_en_articulo", "arco ARTICULO ausente (POP, sin artículo)")

    # ── q2b: SUJETO ──────────────────────────────────────────
    nodo_sujeto = None
    for h in hijos_req:
        if isinstance(h, dict) and 'SUJETO' in h:
            nodo_sujeto = h
            break
    # También puede estar anidado (si el árbol tiene más profundidad)
    if not nodo_sujeto:
        nodo_sujeto = _buscar_nodo(nodo_requerim, 'SUJETO')

    estado = transitar(estado, "q2b_en_sujeto", "arco SUJETO")
    if nodo_sujeto:
        terminales_suj = _extraer_terminales(nodo_sujeto)
        rasgos_suj     = _extraer_rasgos_sujeto(nodo_sujeto)
        setr('sujeto', {
            'nucleo': ' '.join(terminales_suj),
            **rasgos_suj,
        })
    else:
        setr('sujeto', None)

    # ── q2c: MODIFICADORES (puede haber 0 o más) ─────────────
    nodo_modifs = None
    for h in hijos_req:
        if isinstance(h, dict) and 'MODIFICADORES' in h:
            nodo_modifs = h
            break

    estado = transitar(estado, "q2c_en_modif", "arco MODIFICADORES")
    if nodo_modifs:
        lista_modifs = _recolectar_modificadores(nodo_modifs)
        setr('modificadores', lista_modifs)
    else:
        setr('modificadores', [])
        traza_atn.append("      (sin modificadores — POP directo)")

    # ── q3: COMPLEMENTO (opcional) ───────────────────────────
    nodo_compl = None
    for hijo in raiz_hijos:
        if isinstance(hijo, dict) and 'COMPLEMENTO' in hijo:
            nodo_compl = hijo
            break

    if nodo_compl:
        estado = transitar(estado, "q3_en_compl", "arco COMPLEMENTO presente")
        nodo_uso = _buscar_nodo(nodo_compl, 'USO_FINAL')
        if nodo_uso:
            palabras_uso = _extraer_terminales(nodo_uso)
            # Filtrar preposiciones ('para') para quedarse con el uso real
            uso_limpio = [p for p in palabras_uso if p not in ('para',)]
            setr('complemento', ' '.join(uso_limpio))
        else:
            setr('complemento', _extraer_terminales(nodo_compl))
    else:
        estado = transitar(estado, "q3_en_compl", "COMPLEMENTO ausente (POP, oración sin uso final)")
        setr('complemento', None)

    # ── q4: aceptado ─────────────────────────────────────────
    estado = transitar(estado, "q4_aceptado", "árbol recorrido completamente")
    return contexto, traza_atn


# ============================================================
# Ambiguedad

def resolver_ambiguedad(lista_arboles):
    """
    Dado un conjunto de árboles válidos, usa un AF para
    seleccionar el más específico/informativo.

    Devuelve:
        ganador     → el árbol elegido
        traza_af    → lista de strings con la traza del AF
        puntajes    → dict {índice: puntaje} para diagnóstico
    """
    traza_af = []
    puntajes  = {}

    def transitar_af(estado_actual, estado_siguiente, motivo=""):
        traza_af.append(f"  {estado_actual:22s} --> {estado_siguiente:22s}  [{motivo}]")
        return estado_siguiente

    traza_af.append(f"\n[AF] {len(lista_arboles)} candidatos recibidos para desambiguación")
    estado = "q_start"

    for idx, arbol in enumerate(lista_arboles):
        puntaje = 0
        traza_af.append(f"\n  -- Evaluando candidato #{idx + 1} --")

        # q_evaluar_compl
        estado = transitar_af(estado, "q_evaluar_compl", f"candidato #{idx + 1}")
        raiz_hijos = arbol.get('S', [])
        tiene_compl = any(isinstance(h, dict) and 'COMPLEMENTO' in h for h in raiz_hijos)
        if tiene_compl:
            puntaje += 3
            traza_af.append("      COMPLEMENTO presente    → +3")
        else:
            traza_af.append("      COMPLEMENTO ausente     → +0")

        # q_evaluar_modifs
        estado = transitar_af(estado, "q_evaluar_modifs", "contar modificadores")
        nodo_req = next((h for h in raiz_hijos if isinstance(h, dict) and 'REQUERIMIENTO' in h), None)
        n_modifs = 0
        if nodo_req:
            nodo_m = _buscar_nodo(nodo_req, 'MODIFICADORES')
            if nodo_m:
                n_modifs = len(_recolectar_modificadores(nodo_m))
        puntaje += n_modifs
        traza_af.append(f"      Modificadores: {n_modifs}          → +{n_modifs}")

        # q_evaluar_intent
        estado = transitar_af(estado, "q_evaluar_intent", "verificar intención")
        tiene_intent = any(isinstance(h, dict) and 'INTENCION' in h for h in raiz_hijos)
        if tiene_intent:
            puntaje += 2
            traza_af.append("      INTENCION presente       → +2")
        else:
            traza_af.append("      INTENCION ausente        → +0")

        # q_evaluar_sujeto
        estado = transitar_af(estado, "q_evaluar_sujeto", "riqueza léxica del sujeto")
        nodo_suj = _buscar_nodo(arbol, 'SUJETO') if nodo_req else None
        if nodo_suj:
            terminales_suj = _extraer_terminales(nodo_suj)
            token_suj = terminales_suj[0] if terminales_suj else ''
            lex_suj = lexico.get(token_suj, {})
            if isinstance(lex_suj, list):
                lex_suj = lex_suj[0]
            rasgos_presentes = sum(1 for k in ['gen', 'num', 'tipo'] if k in lex_suj)
            puntaje += rasgos_presentes
            traza_af.append(f"      Rasgos sujeto: {rasgos_presentes}           → +{rasgos_presentes}")

        # q_puntuar
        estado = transitar_af(estado, "q_puntuar", f"puntaje total = {puntaje}")
        puntajes[idx] = puntaje
        traza_af.append(f"      Puntaje candidato #{idx + 1}: {puntaje}")

        # Volver a q_start para el siguiente candidato
        estado = "q_start"

    # q_comparar → q_aceptar
    estado = transitar_af(estado, "q_comparar", "seleccionar máximo puntaje")
    idx_ganador = max(puntajes, key=lambda i: puntajes[i])
    estado = transitar_af(estado, "q_aceptar", f"candidato #{idx_ganador + 1} elegido (puntaje={puntajes[idx_ganador]})")

    traza_af.append(f"\n[AF] Ganador: candidato #{idx_ganador + 1} con puntaje {puntajes[idx_ganador]}")
    return lista_arboles[idx_ganador], traza_af, puntajes


# ============================================================
# ORQUESTADOR PRINCIPAL

def parse_oracion(tokens):
    """
    Pipeline completo:
      1. Pre-validación léxica
      2. Parser DCG  → uno o más árboles
      3. AF          → selecciona árbol ganador (si hay ambigüedad)
      4. ATN         → recorre árbol y extrae registros semánticos
    """
    # ── 1. Pre-validación léxica ─────────────────────────────
    for token in tokens:
        en_lexico    = obtener_definiciones(token) != []
        en_gramatica = any(token in prod for prods in gramatica.values() for prod in prods)
        if not en_lexico and not en_gramatica:
            print(f"[Error Lexico] La palabra '{token}' no existe en el diccionario ni en las reglas.")
            return None

    # ── 2. Parser DCG ────────────────────────────────────────
    tracker = {'max_pos': 0, 'errores': set()}
    resultados_s = parse_abstracto('S', tokens, 0, tracker)
    dags_validos  = [arbol for arbol, _, pos_final in resultados_s if pos_final == len(tokens)]

    # Fallo DCG
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
            tok_prob = tokens[min(tracker['max_pos'], len(tokens) - 1)]
            print(f"   > La sintaxis se rompió al intentar procesar: '{tok_prob}'. "
                  "O faltan palabras, o la estructura gramatical no lo permite aquí.")
        return None

    # ── 3. AF — resolución de ambigüedad ────────────────────
    if len(dags_validos) > 1:
        print(f"[AF] Ambigüedad detectada: {len(dags_validos)} árboles válidos. Iniciando AF...\n")
        arbol_final, traza_af, puntajes = resolver_ambiguedad(dags_validos)
        print("\n--- TRAZA DEL AUTÓMATA FINITO ---")
        for linea in traza_af:
            print(linea)
        print()
    else:
        arbol_final = dags_validos[0]

    # ── 4. ATN — recorrido semántico ─────────────────────────
    print("\n--- TRAZA ATN ---")
    contexto, traza_atn = recorrer_atn(arbol_final)
    for linea in traza_atn:
        print(linea)

    print("\n--- REGISTROS SEMÁNTICOS (GETR) ---")
    for clave, valor in contexto.items():
        print(f"   GETR {clave:15s} = {valor!r}")

    return arbol_final, contexto


# -----------------------------

def analizar_oracion(oracion):
    tokens = lexer(oracion)
    print(f"\n{'=' * 54}")
    print(f"Frase : '{oracion}'")
    print(f"Tokens: {tokens}")
    print(f"{'=' * 54}")

    resultado = parse_oracion(tokens)
    if resultado is None:
        print("\nResultado: None (la oración no es válida)")
        return None

    arbol_final, contexto = resultado

    print(f"\n[ÉXITO] Árbol válido seleccionado\n")
    print("--- ÁRBOL DCG FINAL ---")
    imprimir_arbol(arbol_final)
    print()
    return arbol_final, contexto