from atn import _buscar_nodo, _extraer_terminales, _recolectar_modificadores
from gramatica import lexico

def resolver_ambiguedad(lista_arboles):
    traza_af = []
    puntajes  = {}

    def transitar_af(actual, siguiente, motivo=""):
        traza_af.append(f"  {actual:22s} --> {siguiente:22s}  [{motivo}]")
        return siguiente

    traza_af.append(f"\n[AF] {len(lista_arboles)} candidatos para desambiguación")
    estado = "q_start"

    for idx, arbol in enumerate(lista_arboles):
        puntaje = 0
        traza_af.append(f"\n  -- Candidato #{idx + 1} --")
        raiz_hijos = arbol.get('S', [])

        estado = transitar_af(estado, "q_evaluar_compl", f"candidato #{idx+1}")
        if any(isinstance(h, dict) and 'COMPLEMENTO' in h for h in raiz_hijos):
            puntaje += 3
            traza_af.append("      COMPLEMENTO presente    → +3")
        else:
            traza_af.append("      COMPLEMENTO ausente     → +0")

        estado = transitar_af(estado, "q_evaluar_modifs", "contar modificadores")
        nodo_req = next(
            (h for h in raiz_hijos if isinstance(h, dict) and 'REQUERIMIENTO' in h),
            None
        )
        n_modifs = 0
        if nodo_req:
            nodo_m = _buscar_nodo(nodo_req, 'MODIFICADORES')
            if nodo_m:
                n_modifs = len(_recolectar_modificadores(nodo_m))
        puntaje += n_modifs
        traza_af.append(f"      Modificadores: {n_modifs}          → +{n_modifs}")

        estado = transitar_af(estado, "q_evaluar_intent", "verificar intención")
        if any(isinstance(h, dict) and 'INTENCION' in h for h in raiz_hijos):
            puntaje += 2
            traza_af.append("      INTENCION presente       → +2")
        else:
            traza_af.append("      INTENCION ausente        → +0")

        estado = transitar_af(estado, "q_evaluar_sujeto", "rasgos del sujeto")
        nodo_suj = _buscar_nodo(nodo_req, 'SUJETO') if nodo_req else None
        if nodo_suj:
            token_suj = (_extraer_terminales(nodo_suj) or [''])[0]
            lex_suj = lexico.get(token_suj, {})
            if isinstance(lex_suj, list):
                lex_suj = lex_suj[0]
            rasgos = sum(1 for k in ['gen', 'num', 'tipo'] if k in lex_suj)
            puntaje += rasgos
            traza_af.append(f"      Rasgos sujeto: {rasgos}           → +{rasgos}")

        estado = transitar_af(estado, "q_puntuar", f"puntaje = {puntaje}")
        puntajes[idx] = puntaje
        traza_af.append(f"      Puntaje candidato #{idx+1}: {puntaje}")
        estado = "q_start"

    estado = transitar_af(estado, "q_comparar", "seleccionar máximo")
    idx_ganador = max(puntajes, key=lambda i: puntajes[i])
    transitar_af(estado, "q_aceptar",
                 f"candidato #{idx_ganador+1} (puntaje={puntajes[idx_ganador]})")
    traza_af.append(
        f"\n[AF] Ganador: #{idx_ganador+1} con puntaje {puntajes[idx_ganador]}"
    )
    return lista_arboles[idx_ganador], traza_af, puntajes