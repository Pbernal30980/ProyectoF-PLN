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
        ["ARTICULO", "SUJETO", "VERBO_CONJUGADO", "MODIFICADORES"],
        ["ARTICULO", "SUJETO", "MODIFICADORES", "COMPLEMENTO"],  
        ["SUJETO", "MODIFICADORES"],
        ["ARTICULO", "SUJETO"],
        ["CANTIDAD", "SUJETO", "MODIFICADORES"],
        ["CANTIDAD", "SUJETO"],
        ["ARTICULO", "ADJETIVO", "SUJETO", "MODIFICADORES"],
        ["ARTICULO", "ADJETIVO", "SUJETO", "VERBO_CONJUGADO", "MODIFICADORES"],
        ["ARTICULO", "ADJETIVO", "SUJETO"]
    ],

    "SUJETO": [
        ["teléfono"], ["celular"], ["móvil"], ["equipo"], ["dispositivo"], 
        ["procesador"], ["chip"], ["memoria"], ["ram"], ["almacenamiento"]
    ],

    # --- MODIFICADORES Y SUS TIPOS ---
    "MODIFICADORES": [
        ["MODIFICADOR", "MODIFICADORES"],
        ["MODIFICADOR"],
        ["CONJUNCION", "MODIFICADOR", "MODIFICADORES"], 
        ["CONJUNCION", "MODIFICADOR"],
        ["CONJUNCION", "VERBO_CONJUGADO", "MODIFICADORES"],   # que tenga buena ram y mucho almacenamiento
        ["CONJUNCION", "VERBO_CONJUGADO", "COMPLEMENTO"],      # busco un dispositivo que sirva para el trabajo
        ["CONJUNCION", "VERBO", "COMPLEMENTO"],
        ["CONJUNCION", "COMPLEMENTO"],
        ["CONJUNCION", "VERBO", "MODIFICADORES"],
        ["CONJUNCION", "VERBO"],
        ["CONJUNCION", "JUEGO", "MODIFICADORES"],
        ["CONJUNCION", "JUEGO"]
    ],
    "MODIFICADOR": [
        ["MARCA"], 
        ["GAMA"], 
        ["ESPECIFICACION_TEC"], 
        ["ADJETIVO"]
    ],

    # --- COMPLEMENTOS ---
    "COMPLEMENTO": [
        ["USO"],
        ["CONJUNCION", "USO"],
    ],

    # --- PALABRAS ESTRUCTURALES Y CANTIDADES ---
    "ARTICULO": [["un"], ["una"], ["el"], ["algún"], ["la"]],
    "CONJUNCION": [["y"], ["que"], ["pero"], ["con"], ["para"], ["más"]],
    "CANTIDAD": [["de", "8gb"], ["de", "12gb"], ["mucha"], ["mucho"],["poca"], ["bastante"]],

    # --- ATRIBUTOS ESPECÍFICOS ---
    "MARCA": [["samsung"], ["xiaomi"], ["apple"], ["qualcomm"], ["mediatek"], ["motorola"]],
    "GAMA": [
        ["gama", "alta"], ["gama", "media"], ["gama", "baja"], 
        ["premium"], ["barato"], ["económico"], ["caro"]
    ],
    "ESPECIFICACION_TEC": [
        ["snapdragon"],
        #["snapdragon", "SERIE"],
        ["dimensity"], ["exynos"],
        ["RAM", "CANTIDAD"],
        ["ALMACENAMIENTO", "CANTIDAD"],
        ["ADJETIVO", "RAM"],            # ← buena ram
        ["CANTIDAD", "ALMACENAMIENTO"], # ← mucho almacenamiento
        ["ocho", "nucleos"], ["4nm"], ["nanometros"], ["octa", "core"], ["nucleos"],
        ["ADJETIVO", "PROCESADOR"],   # Permite "buen procesador"
        ["PROCESADOR"],               # Permite "con procesador"
        ["RAM"],                      # Permite "y ram" (solita)
        ["ALMACENAMIENTO"]
    ],
    "ADJETIVO": [
        ["rápido"], ["rápida"], ["potente"], ["veloz"], ["eficiente"],
        ["fluido"], ["fluida"], ["bueno"], ["buen"], ["buena"]
    ],

    "VERBO":[
        ["jugar"], ["programar"], ["desarrollar"], ["editar"], ["trabajar"], ["estudiar"]
    ],

    "VERBO_CONJUGADO": [
        ["tenga"], ["posea"], ["corra"], ["funcione"], ["sirva"], ["ejecute"], ["incluya"], ["mueva"], ["sea"]
    ],
    
    # --- USOS Y SUB-COMPONENTES ---
    "USO": [
        ["desarrollo"], ["edición"], ["uso", "diario"],
        ["ARTICULO", "AREA_USO"]
    ],

    "AREA_USO": [
        ["trabajo"], ["estudio"], ["ocio"], ["diario"], ["oficina"],
    ],

    "JUEGO": [["jugar", "JUEGO"], ["cod"], ["fortnite"], ["minecraft"], ["red", "dead", "redemption"], ["juegos", "pesados"], ["emuladores"], ["juegos"]],
    #"SERIE": [["8", "gen", "1"], ["8", "gen", "2"], ["7", "s", "gen", "2"]],
    "RAM": [["ram"], ["memoria"]],
    "ALMACENAMIENTO": [["almacenamiento"], ["espacio"], ["rom"], ["memoria"]],
    "PROCESADOR": [["procesador"], ["chip"]],
}

lexico = {
    # --- INTENCIONES ---
    'busco':        {'cat': 'intencion', 'accion': 'buscar'},
    'busca':        {'cat': 'intencion', 'accion': 'buscar'},
    'quiero':       {'cat': 'intencion', 'accion': 'querer'},
    'necesito':     {'cat': 'intencion', 'accion': 'necesitar'},
    'recomiéndame': {'cat': 'intencion', 'accion': 'recomendar'},
    'dime':         {'cat': 'intencion', 'accion': 'decir'},

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
    'mucho':    {'cat': 'cantidad', 'gen': 'masc', 'num': 'sing'},
    '8gb':      {'cat': 'cantidad', 'valor': '8gb'},
    '12gb':     {'cat': 'cantidad', 'valor': '12gb'},

    # --- SUJETOS ---
    'teléfono':   {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'celular':    {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'dispositivo':{'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'procesador': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'móvil':      {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'equipo':     {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'chip':       {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'ram':        {'cat': 'sujeto', 'gen': 'fem',  'num': 'sing', 'tipo': 'componente'},
    'almacenamiento': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'espacio':    {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'},
    'rom':        {'cat': 'sujeto', 'gen': 'fem',  'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'},

    # memoria ya existía; se conserva con sus dos acepciones (RAM / Almacenamiento)
    'memoria': [
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'RAM'},
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'}
    ],

    # --- ADJETIVOS ---
    'rápido':  {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'rápida':  {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing', 'rendimiento': 'alto'},
    'potente': {'cat': 'adjetivo', 'num': 'sing', 'rendimiento': 'alto'},
    'fluido':  {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'buen':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'calidad': 'buena'},
    'bueno':   {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'calidad': 'buena'},
    'buena':   {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing', 'calidad': 'buena'},
    'veloz':   {'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing', 'rendimiento': 'alto'},
    'eficiente': {'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing', 'rendimiento': 'alto'},
    'pesados': {'cat': 'adjetivo', 'gen': 'masc', 'num': 'plur'},
    'diario':  {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing'},

    # --- MARCAS Y ESPECIFICACIONES ---
    'xiaomi':     {'cat': 'marca', 'valor': 'xiaomi'},
    'samsung':    {'cat': 'marca', 'valor': 'samsung'},
    'apple':      {'cat': 'marca', 'valor': 'apple'},
    'qualcomm':   {'cat': 'marca', 'valor': 'qualcomm'},
    'mediatek':   {'cat': 'marca', 'valor': 'mediatek'},
    'motorola':   {'cat': 'marca', 'valor': 'motorola'},
    'snapdragon': {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'qualcomm'},
    'dimensity':  {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'mediatek'},
    'exynos':     {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'samsung'},
    'nucleos':    {'cat': 'especificacion', 'tipo': 'nucleos'},
    '4nm':        {'cat': 'especificacion', 'tipo': 'litografia'},
    'nanometros': {'cat': 'especificacion', 'tipo': 'medida'},
    'octa':       {'cat': 'especificacion', 'tipo': 'prefijo'},
    'core':       {'cat': 'especificacion', 'tipo': 'nucleos'},
    'gen':        {'cat': 'especificacion', 'tipo': 'generacion'},
    's':          {'cat': 'especificacion', 'tipo': 'variante'},

    # --- GAMAS ---
    'gama':      {'cat': 'gama'},
    'media':     {'cat': 'gama_valor', 'valor': 'media'},
    'alta':      {'cat': 'gama_valor', 'valor': 'alta'},
    'baja':      {'cat': 'gama_valor', 'valor': 'baja'},
    'premium':   {'cat': 'gama_valor', 'valor': 'premium'},
    'barato':    {'cat': 'gama_valor', 'valor': 'barato'},
    'económico': {'cat': 'gama_valor', 'valor': 'economico'},
    'caro':      {'cat': 'gama_valor', 'valor': 'caro'},

# --- Verbos

    'jugar':      {'cat': 'verbo', 'accion': 'jugar'},
    'programar':  {'cat': 'verbo', 'accion': 'programar'},
    'desarrollar': {'cat': 'verbo', 'accion': 'desarrollar'},
    'editar':     {'cat': 'verbo', 'accion': 'editar'},
    'trabajar':    {'cat': 'verbo', 'accion': 'trabajar'},
    'estudiar':    {'cat': 'verbo', 'accion': 'estudiar'},

 # --- USOS FINALES Y JUEGOS ---
    'desarrollo': {'cat': 'uso', 'accion': 'desarrollar'},
    'edición':    {'cat': 'uso', 'accion': 'editar'},
    'uso':        {'cat': 'uso', 'accion': 'usar'},
    'juegos':     {'cat': 'uso', 'accion': 'jugar'},
    'cod':        {'cat': 'juego', 'nombre': 'cod'},
    'fortnite':   {'cat': 'juego', 'nombre': 'fortnite'},
    'minecraft':  {'cat': 'juego', 'nombre': 'minecraft'},
    'red':        {'cat': 'juego', 'nombre': 'rdr'},
    'dead':       {'cat': 'juego', 'nombre': 'rdr'},
    'redemption': {'cat': 'juego', 'nombre': 'rdr'},
    'emuladores': {'cat': 'juego', 'tipo': 'emulador'},
    'trabajo':     {'cat': 'uso', 'accion': 'trabajar'},
    'diario':     {'cat': 'uso', 'accion': 'uso diario'},

    # --- CONJUNCIONES Y PREPOSICIONES ---
    'y':    {'cat': 'conjuncion'},
    'que':  {'cat': 'conjuncion'},
    'pero': {'cat': 'conjuncion'},
    'más':  {'cat': 'conjuncion'},
    'con':  {'cat': 'preposicion'},
    'para': {'cat': 'preposicion'},
    'de':   {'cat': 'preposicion'},

    # --- VERBOS CONJUGADOS ---
    'tenga':    {'cat': 'verbo_conjugado', 'gen': 'fem', 'accion': 'tener'},
    'posea':    {'cat': 'verbo_conjugado', 'accion': 'poseer'},
    'corra':    {'cat': 'verbo_conjugado', 'accion': 'correr'},
    'funcione': {'cat': 'verbo_conjugado', 'accion': 'funcionar'},
    'sirva':    {'cat': 'verbo_conjugado', 'accion': 'servir'},
    'ejecute':  {'cat': 'verbo_conjugado', 'accion': 'ejecutar'},
    'incluya':  {'cat': 'verbo_conjugado', 'accion': 'incluir'},
    'mueva':    {'cat': 'verbo_conjugado', 'accion': 'mover'},
    
    # --- NÚMEROS ---
    'ocho': {'cat': 'numero', 'valor': 8},
    '8':    {'cat': 'numero', 'valor': 8},
    '1':    {'cat': 'numero', 'valor': 1},
    '2':    {'cat': 'numero', 'valor': 2},
    '7':    {'cat': 'numero', 'valor': 7}
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