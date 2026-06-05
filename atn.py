from gramatica import lexico

# ── Helpers privados ─────────────────────────────────────────

def _buscar_nodo(arbol, nombre):
    if not isinstance(arbol, dict):
        return None
    for clave, hijos in arbol.items():
        if clave == '_rasgos_heredados':
            continue
        if clave == nombre:
            return arbol
        if isinstance(hijos, list):
            for hijo in hijos:
                r = _buscar_nodo(hijo, nombre)
                if r:
                    return r
    return None

def _extraer_terminales(nodo):
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
    rasgos = {}
    if not nodo_sujeto:
        return rasgos
    for hijo in nodo_sujeto.get('SUJETO', []):
        if isinstance(hijo, dict) and 'terminal' in hijo:
            lex = hijo.get('lexico', {})
            rasgos['gen']  = lex.get('gen',  '?')
            rasgos['num']  = lex.get('num',  '?')
            rasgos['tipo'] = lex.get('tipo', '?')
            break
    return rasgos

def _clasificar_modificador(nodo_modif):
    if not isinstance(nodo_modif, dict):
        return None
    for hijo in nodo_modif.get('MODIFICADOR', []):
        if not isinstance(hijo, dict):
            continue
        for tipo in ['MARCA', 'GAMA', 'ESPECIFICACION_TEC', 'ADJETIVO']:
            sub = _buscar_nodo(hijo, tipo)
            if sub:
                return {'tipo': tipo.lower(),
                        'valor': ' '.join(_extraer_terminales(sub))}
    return None

def _recolectar_modificadores(nodo_modifs):
    resultado = []
    if not isinstance(nodo_modifs, dict):
        return resultado
    for hijo in nodo_modifs.get('MODIFICADORES', []):
        if not isinstance(hijo, dict):
            continue
        if 'MODIFICADOR' in hijo:
            m = _clasificar_modificador(hijo)
            if m:
                resultado.append(m)
        if 'MODIFICADORES' in hijo:
            resultado.extend(_recolectar_modificadores(hijo))
    return resultado

# ── Motor ATN ────────────────────────────────────────────────

def recorrer_atn(arbol):
    contexto  = {}
    traza_atn = []

    def setr(clave, valor):
        contexto[clave] = valor
        traza_atn.append(f"      SETR {clave} = {valor!r}")

    def transitar(actual, siguiente, motivo=""):
        traza_atn.append(
            f"  {actual:22s} --> {siguiente:22s}  [{motivo}]"
        )
        return siguiente

    estado = "q0_inicio"
    traza_atn.append(f"  {'ESTADO INICIAL':22s} --> {'q0_inicio':22s}")

    raiz_hijos = arbol.get('S', [])
    if not raiz_hijos:
        traza_atn.append("  [ATN] Nodo S vacío — árbol malformado")
        return contexto, traza_atn

    # q1: INTENCION
    nodo_int = next(
        (h for h in raiz_hijos if isinstance(h, dict) and 'INTENCION' in h),
        None
    )
    if nodo_int:
        estado = transitar(estado, "q1_en_intencion", "INTENCION encontrada")
        token_int = (_extraer_terminales(nodo_int) or ['?'])[0]
        accion = lexico.get(token_int, {})
        if isinstance(accion, list):
            accion = accion[0]
        setr('intencion', accion.get('accion', token_int))
    else:
        estado = transitar(estado, "q1_en_intencion", "INTENCION ausente")
        setr('intencion', None)

    # q2: REQUERIMIENTO
    nodo_req = next(
        (h for h in raiz_hijos if isinstance(h, dict) and 'REQUERIMIENTO' in h),
        None
    )
    if not nodo_req:
        traza_atn.append("  [ATN] REQUERIMIENTO ausente — árbol malformado")
        return contexto, traza_atn

    estado = transitar(estado, "q2_en_requerim", "REQUERIMIENTO encontrado")
    hijos_req = nodo_req.get('REQUERIMIENTO', [])

    # q2a: ARTICULO
    nodo_art = next(
        (h for h in hijos_req if isinstance(h, dict) and 'ARTICULO' in h),
        None
    )
    if nodo_art:
        estado = transitar(estado, "q2a_en_articulo", "ARTICULO presente")
        terms = _extraer_terminales(nodo_art)
        lex_a = lexico.get(terms[0], {}) if terms else {}
        if isinstance(lex_a, list):
            lex_a = lex_a[0]
        setr('articulo', {
            'forma': terms[0] if terms else '?',
            'gen':   lex_a.get('gen', '?'),
            'num':   lex_a.get('num', '?'),
        })
    else:
        estado = transitar(estado, "q2a_en_articulo", "ARTICULO ausente (POP)")

    # q2b: SUJETO
    nodo_suj = next(
        (h for h in hijos_req if isinstance(h, dict) and 'SUJETO' in h),
        None
    ) or _buscar_nodo(nodo_req, 'SUJETO')

    estado = transitar(estado, "q2b_en_sujeto", "arco SUJETO")
    if nodo_suj:
        setr('sujeto', {
            'nucleo': ' '.join(_extraer_terminales(nodo_suj)),
            **_extraer_rasgos_sujeto(nodo_suj),
        })
    else:
        setr('sujeto', None)

    # q2c: MODIFICADORES
    nodo_modifs = next(
        (h for h in hijos_req if isinstance(h, dict) and 'MODIFICADORES' in h),
        None
    )
    estado = transitar(estado, "q2c_en_modif", "arco MODIFICADORES")
    if nodo_modifs:
        setr('modificadores', _recolectar_modificadores(nodo_modifs))
    else:
        setr('modificadores', [])
        traza_atn.append("      (sin modificadores — POP directo)")

    # q3: COMPLEMENTO
    nodo_compl = next(
        (h for h in raiz_hijos if isinstance(h, dict) and 'COMPLEMENTO' in h),
        None
    )
    if nodo_compl:
        estado = transitar(estado, "q3_en_compl", "COMPLEMENTO presente")
        nodo_uso = _buscar_nodo(nodo_compl, 'USO_FINAL')
        if nodo_uso:
            palabras = [p for p in _extraer_terminales(nodo_uso) if p != 'para']
            setr('complemento', ' '.join(palabras))
        else:
            setr('complemento', _extraer_terminales(nodo_compl))
    else:
        estado = transitar(estado, "q3_en_compl", "COMPLEMENTO ausente (POP)")
        setr('complemento', None)

    transitar(estado, "q4_aceptado", "árbol recorrido completamente")
    return contexto, traza_atn