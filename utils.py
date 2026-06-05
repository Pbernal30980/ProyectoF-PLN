import re
import unicodedata

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', '', texto)
    return re.sub(r'\s+', ' ', texto).strip()

def lexer(oracion):
    return normalizar(oracion).split()

def imprimir_arbol(nodo, prefijo="", es_ultimo=True, es_raiz=True):
    marcador = "" if es_raiz else ("└── " if es_ultimo else "├── ")
    if isinstance(nodo, dict) and 'terminal' in nodo:
        lex = nodo.get('lexico', {})
        cat = lex.get('cat', 'Desconocido').upper()
        rasgos_extra = ", ".join(
            f"{k}:{v}" for k, v in lex.items() if k not in ['cat', '_origen']
        )
        info = f" [{rasgos_extra}]" if rasgos_extra else ""
        print(f"{prefijo}{marcador}'{nodo['terminal']}' (Cat: {cat}){info}")
        return
    if isinstance(nodo, dict):
        llaves = [k for k in nodo if k != '_rasgos_heredados']
        if not llaves:
            return
        simbolo = llaves[0]
        hijos   = nodo[simbolo]
        print(f"{prefijo}{marcador}{simbolo}")
        nuevo_prefijo = prefijo if es_raiz else (
            prefijo + ("    " if es_ultimo else "│   ")
        )
        for i, hijo in enumerate(hijos):
            imprimir_arbol(hijo, nuevo_prefijo,
                           es_ultimo=(i == len(hijos) - 1), es_raiz=False)