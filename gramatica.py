import unicodedata
import re


gramatica = {
    # --- REGLAS PRINCIPALES ---
    "S": [
        ["INTENCION", "REQUERIMIENTO"],
        ["INTENCION", "REQUERIMIENTO", "COMPLEMENTO"],
        ["REQUERIMIENTO", "COMPLEMENTO"], 
        ["REQUERIMIENTO"] 
    ],
    
    # --- INTENCIONES ---
    "INTENCION": [["busco"], ["quiero"], ["necesito"], ["recomiéndame"], ["dime", "de"], ["busca"]],

    # --- REQUERIMIENTOS Y SUJETOS ---
    "REQUERIMIENTO": [
        ["ARTICULO", "SUJETO", "MODIFICADORES"],
        ["SUJETO", "MODIFICADORES"],
        ["ARTICULO", "SUJETO"],
        ["CANTIDAD", "SUJETO", "MODIFICADORES"],
        ["CANTIDAD", "SUJETO"],
        ["ARTICULO", "ADJETIVO", "SUJETO", "MODIFICADORES"],
        ["ARTICULO", "ADJETIVO", "SUJETO"]
    ],

    "SUJETO": [
        ["teléfono"], ["celular"], ["móvil"], ["equipo"], ["dispositivo"], 
        ["procesador"], ["chip"], ["memoria"], ["ram"], ["almacenamiento"]
    ],

    # --- MODIFICADORES Y SUS TIPOS ---
    "MODIFICADORES": [
        ["MODIFICADOR"],
        ["MODIFICADOR", "MODIFICADORES"], 
        ["CONJUNCION", "MODIFICADOR", "MODIFICADORES"], 
        ["CONJUNCION", "MODIFICADOR"]
    ],
    "MODIFICADOR": [
        ["MARCA"], 
        ["GAMA"], 
        ["ESPECIFICACION_TEC"], 
        ["ADJETIVO"]
    ],

    # --- COMPLEMENTOS ---
    "COMPLEMENTO": [
        ["USO_FINAL"],
        ["CONJUNCION", "USO_FINAL"]
    ],

    # --- PALABRAS ESTRUCTURALES Y CANTIDADES ---
    "ARTICULO": [["un"], ["una"], ["el"], ["algún"], ["la"]],
    "CONJUNCION": [["y"], ["que"], ["pero"], ["con"], ["para"], ["más"]],
    "CANTIDAD": [["de", "8gb"], ["de", "12gb"], ["mucha"], ["poca"], ["bastante"]],

    # --- ATRIBUTOS ESPECÍFICOS ---
    "MARCA": [["samsung"], ["xiaomi"], ["apple"], ["qualcomm"], ["mediatek"], ["motorola"]],
    "GAMA": [
        ["gama", "alta"], ["gama", "media"], ["gama", "baja"], 
        ["premium"], ["barato"], ["económico"], ["caro"]
    ],
    "ESPECIFICACION_TEC": [
        ["snapdragon"],
        ["snapdragon", "SERIE"],
        ["dimensity"], ["exynos"],
        ["RAM", "CANTIDAD"], ["ALMACENAMIENTO", "CANTIDAD"],
        ["ocho", "núcleos"], ["4nm"], ["nanómetros"],
        ["soporte", "magisk"], ["compatible", "con", "roms"]
    ],
    "ADJETIVO": [
        ["rápido"], ["potente"], ["veloz"], ["eficiente"], 
        ["fluido"], ["bueno"], ["buen"]
    ],
    
    # --- USOS Y SUB-COMPONENTES ---
    "USO_FINAL": [
        ["para", "JUEGO"], ["para", "jugar"], ["para", "programar"],
        ["para", "desarrollo"], ["para", "edición"], ["para", "uso", "diario"]
    ],
    "JUEGO": [["cod"], ["fortnite"], ["minecraft"], ["red", "dead", "redemption"], ["juegos", "pesados"], ["emuladores"]],
    "SERIE": [["8", "gen", "1"], ["8", "gen", "2"], ["7", "s", "gen", "2"]],
    "RAM": [["ram"], ["memoria"]],
    "ALMACENAMIENTO": [["almacenamiento"], ["espacio"], ["rom"], ["memoria"]]
}

lexico = {
    # --- INTENCIONES ---
    'busco':        {'cat': 'intencion', 'accion': 'buscar'},
    'busca':        {'cat': 'intencion', 'accion': 'buscar'},
    'quiero':       {'cat': 'intencion', 'accion': 'querer'},
    'necesito':     {'cat': 'intencion', 'accion': 'necesitar'},
    'recomiéndame': {'cat': 'intencion', 'accion': 'recomendar'},

    # --- ARTÍCULOS ---
    'un':    {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'una':   {'cat': 'art', 'gen': 'fem',  'num': 'sing'},
    'el':    {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'la':    {'cat': 'art', 'gen': 'fem',  'num': 'sing'},
    'algún': {'cat': 'art', 'gen': 'masc', 'num': 'sing'},

    # --- CANTIDADES ---
    'mucha':    {'cat': 'cantidad', 'gen': 'fem',  'num': 'sing'},
    'poca':     {'cat': 'cantidad', 'gen': 'fem',  'num': 'sing'},
    'bastante': {'cat': 'cantidad', 'gen': 'masc', 'num': 'sing'},

    # --- SUJETOS ---
    'teléfono':   {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'celular':    {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'dispositivo':{'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'procesador': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},

    'móvil':          {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'equipo':         {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'chip':           {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'ram':            {'cat': 'sujeto', 'gen': 'fem',  'num': 'sing', 'tipo': 'componente'},
    'almacenamiento': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},

    'veloz':     {'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing', 'rendimiento': 'alto'},
    'eficiente': {'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing', 'rendimiento': 'alto'},
    'bueno':     {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'calidad': 'buena'},

    # memoria ya existía; se conserva con sus dos acepciones (RAM / Almacenamiento)
    'memoria': [
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'RAM'},
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'}
    ],

    # --- ADJETIVOS (entradas previas, sin cambios) ---
    'rápido':  {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'rápida':  {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing', 'rendimiento': 'alto'},
    'potente': {'cat': 'adjetivo', 'num': 'sing', 'rendimiento': 'alto'},
    'fluido':  {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'buen':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'calidad': 'buena'},

    # --- MARCAS Y ESPECIFICACIONES ---
    'xiaomi':     {'cat': 'marca', 'valor': 'xiaomi'},
    'samsung':    {'cat': 'marca', 'valor': 'samsung'},
    'snapdragon': {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'qualcomm'},

    # --- GAMAS ---
    'gama':  {'cat': 'gama'},
    'media': {'cat': 'gama_valor', 'valor': 'media'},
    'alta':  {'cat': 'gama_valor', 'valor': 'alta'},
    'baja':  {'cat': 'gama_valor', 'valor': 'baja'},

    # --- USOS FINALES ---
    'jugar':    {'cat': 'uso_final', 'accion': 'jugar'},
    'programar':{'cat': 'uso_final', 'accion': 'programar'},

    # --- CONJUNCIONES Y PREPOSICIONES ---
    'y':    {'cat': 'conjuncion'},
    'con':  {'cat': 'preposicion'},
    'para': {'cat': 'preposicion'},
    'más':  {'cat': 'conjuncion'}
}


def _normalizar_clave(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.strip()

# Normalizar léxico
lexico = {_normalizar_clave(k): v for k, v in lexico.items()}

# Normalizar terminales en la gramática
gramatica = {
    simbolo: [
        [_normalizar_clave(token) if isinstance(token, str) and token[0].islower() else token
         for token in produccion]
        for produccion in producciones
    ]
    for simbolo, producciones in gramatica.items()
}