# main.py
from gramatica import lexico, gramatica
from utils import lexer, imprimir_arbol
from parser_dcg import obtener_definiciones, parse_abstracto, obtener_arbol_parcial
from ambiguedad import resolver_ambiguedad
from atn import recorrer_atn
from generador_respuestas import manejar_fuera_de_dominio, generar_recomendacion

# ============================================================
# ORQUESTADOR PRINCIPAL
# ============================================================

def parse_oracion(tokens):
    """
    Pipeline completo:
      1. Pre-validación léxica (Desvío de dominio)
      2. Parser DCG          → uno o más árboles válidos
      3. AF                  → selecciona árbol ganador si hay ambigüedad
      4. ATN                 → recorre el árbol y extrae registros semánticos
      5. Recomendador        → Consulta la BD simulada y responde al usuario
    """
    # ── 1. Pre-validación léxica ─────────────────────────────
    tokens_desconocidos = []
    for token in tokens:
        en_lexico    = obtener_definiciones(token) != []
        en_gramatica = any(token in prod for prods in gramatica.values() for prod in prods)
        if not en_lexico and not en_gramatica:
            tokens_desconocidos.append(token)
        
    # Si hay palabras que no pertenecen al ecosistema, interceptamos
    if tokens_desconocidos:
        respuesta_out = manejar_fuera_de_dominio(tokens)
        print(f"\n{respuesta_out}")
        return None

    # ── 2. Parser DCG ────────────────────────────────────────
    tracker      = {'max_pos': 0, 'errores': set()}
    resultados_s = parse_abstracto('S', tokens, 0, tracker)
    dags_validos = [
        arbol for arbol, _, pos_final in resultados_s
        if pos_final == len(tokens)
    ]

    # Fallo DCG
    if not dags_validos:
        # Evaluamos si falló por estructura pero sigue siendo un tema ajeno
        respuesta_out = manejar_fuera_de_dominio(tokens)
        if "🤖" in respuesta_out and not respuesta_out.startswith("🤖 Hum... Temo"):
            print(f"\n{respuesta_out}")
            return None
        
        print("[Error Estructural o de Concordancia] detectado.\n")
        arbol_parcial, pos_alcanzada = obtener_arbol_parcial(tokens)
        print("--- ÁRBOL PARCIAL ALCANZADO ANTES DEL ERROR ---")
        imprimir_arbol(arbol_parcial)
        tokens_sobrantes = tokens[pos_alcanzada:]
        print(f"\n[!] Tokens sin procesar a partir del fallo: {tokens_sobrantes}\n")
        
        print("[MOTIVO DEL FALLO]:")
        if tracker['errores']:
            for err in tracker['errores']:
                print(f"   > {err}")
        else:
            tok_prob = tokens[min(tracker['max_pos'], len(tokens) - 1)]
            print(
                f"   > La sintaxis se rompió al intentar procesar: '{tok_prob}'. "
                "O faltan palabras, o la estructura gramatical no lo permite aquí."
            )
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

    # ── 5. CONSULTA Y RESPUESTA FINAL (SISTEMA EXPERTO) ──────
    respuesta_final = generar_recomendacion(contexto)
    print("\n" + "=" * 54)
    print(respuesta_final)
    print("=" * 54)

    return arbol_final, contexto


def analizar_oracion(oracion):
    """Punto de entrada público. Tokeniza, analiza e imprime resultado."""
    tokens = lexer(oracion)
    print(f"\n{'=' * 54}")
    print(f"Frase : '{oracion}'")
    print(f"Tokens: {tokens}")
    print(f"{'=' * 54}")

    resultado = parse_oracion(tokens)

    if resultado is None:
        print("\nResultado: None (la oración no fue procesada por el ecosistema)")
        return None

    arbol_final, contexto = resultado
    print(f"\n[ÉXITO] Árbol válido seleccionado\n")
    print("--- ÁRBOL DCG FINAL ---")
    imprimir_arbol(arbol_final)
    print()
    return arbol_final, contexto


# ============================================================
# CASOS DE PRUEBA
# ============================================================

CASOS_DE_PRUEBA = [
    # 0  — válida: requerimiento simple con modificador de gama
    "quiero un celular gama media",
    # 1  — válida: sujeto sin artículo + complemento de uso
    "busco mucha memoria para jugar",
    # 2  — válida: múltiples modificadores + complemento
    "necesito el teléfono rápido potente y fluido con snapdragon para programar",
    # 3  — error de concordancia: 'una celular' (fem → masc)
    "busca una celular gama alta",
    # 4  — error de concordancia: 'unos procesador' (plur → sing)
    "quiero unos procesador potente",
    # 5  — válida larga: intención + 4 modificadores + complemento
    "recomiéndame un dispositivo rápido y potente gama alta y fluido para jugar",
    # 6  — válida: género fem concordante + complemento
    "quiero una memoria rápida para programar",
    # 7  — válida: dos marcas coordinadas con 'y'
    "busco un teléfono samsung y xiaomi",
    # 8  — error de concordancia: 'teléfono rápidos' (sing → plur)
    "quiero el teléfono rápidos",
    # 9  — válida: especificación técnica + gama baja
    "necesito el celular con snapdragon gama baja",
    # 10 — válida: sin artículo + complemento de uso
    "algún buen procesador para jugar",
    # 11 — error estructural: NP incompleto (falta sujeto tras artículo)
    "recomiéndame el",
    # --- NUEVOS CASOS: FUERA DE DOMINIO Y RESPUESTAS RECIENTES ---
    # 12 — fuera de dominio: amor
    "como puedo encontrar el amor de mi vida",
    # 13 — fuera de dominio: comida
    "quiero pedir una pizza grande",
    # 14 — fuera de dominio: genérico filosófico
    "cual es el sentido de la existencia"
]


def ejecutar_casos(selector=None):
    """
    Corre los casos de prueba predefinidos.
      selector=None        → todos
      selector=int         → solo ese índice
      selector=(ini, fin)  → rango cerrado
    """
    if selector is None:
        indices = range(len(CASOS_DE_PRUEBA))
    elif isinstance(selector, int):
        indices = [selector]
    elif isinstance(selector, tuple):
        inicio, fin = selector
        indices = range(inicio, fin + 1)
    else:
        print("  selector debe ser None, un int o una tupla (inicio, fin).")
        return

    for i in indices:
        if 0 <= i < len(CASOS_DE_PRUEBA):
            print(f"\n\n\n[Caso {i}]")
            analizar_oracion(CASOS_DE_PRUEBA[i])
        else:
            print(f"  Índice {i} fuera de rango (0–{len(CASOS_DE_PRUEBA) - 1}).")


# ============================================================
# MODO INTERACTIVO
# ============================================================

BANNER = """
╔══════════════════════════════════════════════════════╗
║        Analizador de Requerimientos de Dispositivos  ║
║        DCG + ATN  ·  Universidad del Valle           ║
╚══════════════════════════════════════════════════════╝
  Escribe una frase para analizarla, por ejemplo:
    > quiero un celular gama alta para jugar

  Comandos especiales:
    casos            → ejecutar todos los casos de prueba
    caso <n>         → ejecutar el caso número n
    casos <n> <m>    → ejecutar los casos del n al m
    listar           → mostrar la lista de casos de prueba
    ayuda            → mostrar esta pantalla
    salir / exit     → terminar el programa
"""


def _mostrar_casos():
    print("\n  Casos de prueba disponibles:")
    for i, caso in enumerate(CASOS_DE_PRUEBA):
        print(f"    [{i:2d}]  {caso}")
    print()


def _parsear_comando_casos(partes):
    """
    Interpreta las variantes del comando 'casos':
      casos          → None  (todos)
      caso  <n>      → int n
      casos <n>      → int n
      casos <n> <m>  → tuple (n, m)
    """
    if len(partes) == 1:
        return None
    try:
        if len(partes) == 2:
            return int(partes[1])
        if len(partes) == 3:
            return (int(partes[1]), int(partes[2]))
    except ValueError:
        pass
    return "error"


def modo_interactivo():
    print(BANNER)

    while True:
        try:
            entrada = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Hasta luego.\n")
            break

        if not entrada:
            continue

        partes  = entrada.lower().split()
        comando = partes[0]

        # ── Salir ────────────────────────────────────────────
        if comando in ("salir", "exit", "quit"):
            print("\n  Hasta luego.\n")
            break

        # ── Ayuda ────────────────────────────────────────────
        elif comando in ("ayuda", "help"):
            print(BANNER)

        # ── Listar casos ─────────────────────────────────────
        elif comando == "listar":
            _mostrar_casos()

        # ── Ejecutar casos de prueba ─────────────────────────
        elif comando in ("casos", "caso"):
            selector = _parsear_comando_casos(partes)
            if selector == "error":
                print("  Uso: casos | caso <n> | casos <n> <m>\n")
            else:
                ejecutar_casos(selector)

        # ── Análisis de frase libre ──────────────────────────
        else:
            analizar_oracion(entrada)


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    modo_interactivo()