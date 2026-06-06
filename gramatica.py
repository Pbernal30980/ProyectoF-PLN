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
    "INTENCION": [
        ["busco"], ["quiero"], ["necesito"], ["recomiéndame"],
        ["dime", "de"], ["busca"], ["dame"], ["muéstrame"],
        ["consígueme"], ["encuéntrame"],
    ],

    # --- REQUERIMIENTOS ---
    "REQUERIMIENTO": [
        # Con artículo
        ["ARTICULO", "SUJETO", "MODIFICADORES"],
        ["ARTICULO", "SUJETO", "VERBO_CONJUGADO", "MODIFICADORES"],
        ["ARTICULO", "SUJETO", "MODIFICADORES", "COMPLEMENTO"],
        ["ARTICULO", "SUJETO"],
        # Con adjetivo antepuesto
        ["ARTICULO", "ADJETIVO", "SUJETO", "MODIFICADORES"],
        ["ARTICULO", "ADJETIVO", "SUJETO", "VERBO_CONJUGADO", "MODIFICADORES"],
        ["ARTICULO", "ADJETIVO", "SUJETO"],
        # Con cantidad
        ["CANTIDAD", "SUJETO", "MODIFICADORES"],
        ["CANTIDAD", "SUJETO"],
        # Sin artículo
        ["SUJETO", "MODIFICADORES"],
        ["SUJETO"],                           # ← 'celular' solo
        # Solo modificador (marca/spec sin sujeto explícito)
        ["ARTICULO", "MODIFICADOR"],          # ← 'un samsung', 'un snapdragon'
        ["MODIFICADOR"],                      # ← 'samsung', 'snapdragon'
    ],

    # --- SUJETO (singular y plural) ---
    "SUJETO": [
        # Singulares
        ["teléfono"], ["celular"], ["móvil"], ["equipo"], ["dispositivo"],
        ["procesador"], ["chip"], ["memoria"], ["ram"], ["almacenamiento"],
        # Plurales (para frases tipo 'dime de celulares samsung')
        ["teléfonos"], ["celulares"], ["móviles"], ["equipos"], ["dispositivos"],
        ["procesadores"],
    ],

    # --- MODIFICADORES ---
    "MODIFICADORES": [
        ["MODIFICADOR", "MODIFICADORES"],
        ["MODIFICADOR"],
        ["CONJUNCION", "MODIFICADOR", "MODIFICADORES"],
        ["CONJUNCION", "MODIFICADOR"],
        ["CONJUNCION", "VERBO_CONJUGADO", "MODIFICADORES"],   # que tenga buena ram y mucho almacenamiento
        ["CONJUNCION", "VERBO_CONJUGADO", "COMPLEMENTO"],     # que sirva para el trabajo
        ["CONJUNCION", "VERBO", "COMPLEMENTO"],
        ["CONJUNCION", "COMPLEMENTO"],
        ["CONJUNCION", "VERBO", "MODIFICADORES"],
        ["CONJUNCION", "VERBO"],
        ["CONJUNCION", "JUEGO", "MODIFICADORES"],
        ["CONJUNCION", "JUEGO"],
    ],

    "MODIFICADOR": [
        ["MARCA"],
        ["GAMA"],
        ["ESPECIFICACION_TEC"],
        ["ADJETIVO"],
    ],

    # --- COMPLEMENTOS ---
    "COMPLEMENTO": [
        ["USO"],
        ["CONJUNCION", "USO"],
    ],

    # --- ARTÍCULOS (singular y plural) ---
    "ARTICULO": [
        ["un"], ["una"], ["el"], ["la"], ["algún"], ["alguna"],
        ["unos"], ["unas"], ["los"], ["las"], ["algunos"], ["algunas"],
    ],

    # --- CONJUNCIONES / PREPOSICIONES ---
    "CONJUNCION": [
        ["y"], ["que"], ["pero"], ["con"], ["para"], ["más"],
        ["ni"], ["o"],
    ],

    # --- CANTIDADES ---
    "CANTIDAD": [
        ["de", "8gb"], ["de", "12gb"], ["de", "16gb"],
        ["mucha"], ["mucho"], ["poca"], ["poco"], ["bastante"],
        ["suficiente"],
    ],

    # --- MARCAS ---
    "MARCA": [
        ["samsung"], ["xiaomi"], ["apple"], ["qualcomm"],
        ["mediatek"], ["motorola"], ["oneplus"], ["oppo"],
        ["realme"], ["huawei"], ["sony"], ["google"],
    ],

    # --- GAMAS ---
    "GAMA": [
        ["gama", "alta"], ["gama", "media"], ["gama", "baja"],
        ["gama", "premium"],
        ["premium"], ["barato"], ["económico"], ["caro"],
        ["asequible"], ["accesible"],
    ],

    # --- ESPECIFICACIONES TÉCNICAS ---
    "ESPECIFICACION_TEC": [
        ["snapdragon"],
        ["dimensity"], ["exynos"], ["helio"],
        ["RAM", "CANTIDAD"],
        ["ALMACENAMIENTO", "CANTIDAD"],
        ["ADJETIVO", "RAM"],            # buena ram
        ["CANTIDAD", "ALMACENAMIENTO"], # mucho almacenamiento
        ["CANTIDAD", "RAM"],            # mucha ram
        ["ocho", "nucleos"], ["4nm"], ["nanometros"], ["octa", "core"], ["nucleos"],
        ["ADJETIVO", "PROCESADOR"],     # buen procesador
        ["PROCESADOR"],
        ["RAM"],
        ["ALMACENAMIENTO"],
        ["5g"], ["4g"],                 # conectividad como spec
    ],

    # --- ADJETIVOS (singular y plural) ---
    "ADJETIVO": [
        # Singulares
        ["rápido"], ["rápida"], ["potente"], ["veloz"], ["eficiente"],
        ["fluido"], ["fluida"], ["bueno"], ["buen"], ["buena"],
        ["ligero"], ["ligera"], ["duradero"], ["duradera"],
        ["compacto"], ["compacta"], ["resistente"], ["moderno"], ["moderna"],
        # Plurales (para concordancia de número en errores)
        ["rápidos"], ["rápidas"], ["potentes"], ["fluidos"], ["fluidas"],
        ["veloces"], ["eficientes"], ["buenos"], ["buenas"],
        ["ligeros"], ["ligeras"],
    ],

    # --- VERBOS (infinitivo) ---
    "VERBO": [
        ["jugar"], ["programar"], ["desarrollar"], ["editar"],
        ["trabajar"], ["estudiar"], ["fotografiar"], ["grabar"],
        ["diseñar"], ["navegar"], ["escuchar"], ["ver"],
    ],

    # --- VERBOS CONJUGADOS ---
    "VERBO_CONJUGADO": [
        ["tenga"], ["posea"], ["corra"], ["funcione"], ["sirva"],
        ["ejecute"], ["incluya"], ["mueva"], ["sea"], ["cuente"],
        ["soporte"], ["permita"], ["ofrezca"], ["traiga"],
    ],

    # --- USOS / COMPLEMENTOS DE PROPÓSITO ---
    "USO": [
        ["desarrollo"], ["edición"], ["uso", "diario"],
        ["fotografía"], ["gaming"],
        ["ARTICULO", "AREA_USO"],
    ],

    "AREA_USO": [
        ["trabajo"], ["estudio"], ["ocio"], ["diario"],
        ["oficina"], ["universidad"], ["colegio"],
        ["viaje"], ["entretenimiento"],
    ],

    # --- JUEGOS ---
    "JUEGO": [
        ["jugar", "JUEGO"],
        ["cod"], ["fortnite"], ["minecraft"],
        ["red", "dead", "redemption"],
        ["juegos", "pesados"], ["emuladores"], ["juegos"],
        ["free", "fire"], ["pubg"], ["genshin"],
    ],

    # --- SUB-COMPONENTES ---
    "RAM":          [["ram"], ["memoria"]],
    "ALMACENAMIENTO": [["almacenamiento"], ["espacio"], ["rom"], ["memoria"]],
    "PROCESADOR":   [["procesador"], ["chip"]],
}

# ─────────────────────────────────────────────────────────────
lexico = {
    # --- INTENCIONES ---
    'busco':        {'cat': 'intencion', 'accion': 'buscar'},
    'busca':        {'cat': 'intencion', 'accion': 'buscar'},
    'quiero':       {'cat': 'intencion', 'accion': 'querer'},
    'necesito':     {'cat': 'intencion', 'accion': 'necesitar'},
    'recomiéndame': {'cat': 'intencion', 'accion': 'recomendar'},
    'dime':         {'cat': 'intencion', 'accion': 'decir'},
    'dame':         {'cat': 'intencion', 'accion': 'dar'},
    'muéstrame':    {'cat': 'intencion', 'accion': 'mostrar'},
    'consígueme':   {'cat': 'intencion', 'accion': 'conseguir'},
    'encuéntrame':  {'cat': 'intencion', 'accion': 'encontrar'},

    # --- ARTÍCULOS singulares ---
    'un':     {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'una':    {'cat': 'art', 'gen': 'fem',  'num': 'sing'},
    'el':     {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'la':     {'cat': 'art', 'gen': 'fem',  'num': 'sing'},
    'algún':  {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'alguna': {'cat': 'art', 'gen': 'fem',  'num': 'sing'},
    # --- ARTÍCULOS plurales ---
    'unos':    {'cat': 'art', 'gen': 'masc', 'num': 'plur'},
    'unas':    {'cat': 'art', 'gen': 'fem',  'num': 'plur'},
    'los':     {'cat': 'art', 'gen': 'masc', 'num': 'plur'},
    'las':     {'cat': 'art', 'gen': 'fem',  'num': 'plur'},
    'algunos': {'cat': 'art', 'gen': 'masc', 'num': 'plur'},
    'algunas': {'cat': 'art', 'gen': 'fem',  'num': 'plur'},

    # --- CANTIDADES ---
    'mucha':     {'cat': 'cantidad', 'gen': 'fem',  'num': 'sing'},
    'mucho':     {'cat': 'cantidad', 'gen': 'masc', 'num': 'sing'},
    'poca':      {'cat': 'cantidad', 'gen': 'fem',  'num': 'sing'},
    'poco':      {'cat': 'cantidad', 'gen': 'masc', 'num': 'sing'},
    'bastante':  {'cat': 'cantidad', 'gen': 'inv',  'num': 'sing'},
    'suficiente':{'cat': 'cantidad', 'gen': 'inv',  'num': 'sing'},
    '8gb':       {'cat': 'cantidad', 'valor': '8gb'},
    '12gb':      {'cat': 'cantidad', 'valor': '12gb'},
    '16gb':      {'cat': 'cantidad', 'valor': '16gb'},

    # --- SUJETOS singulares ---
    'teléfono':    {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'celular':     {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'móvil':       {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'equipo':      {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'dispositivo': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'procesador':  {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'chip':        {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'ram':         {'cat': 'sujeto', 'gen': 'fem',  'num': 'sing', 'tipo': 'componente'},
    'almacenamiento': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'espacio':     {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'},
    'rom':         {'cat': 'sujeto', 'gen': 'fem',  'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'},
    'memoria': [
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'RAM'},
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'},
    ],
    # --- SUJETOS plurales ---
    'teléfonos':    {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'dispositivo'},
    'celulares':    {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'dispositivo'},
    'móviles':      {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'dispositivo'},
    'equipos':      {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'dispositivo'},
    'dispositivos': {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'dispositivo'},
    'procesadores': {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'componente'},

    # --- ADJETIVOS singulares ---
    'rápido':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'rápida':    {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing', 'rendimiento': 'alto'},
    'potente':   {'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing', 'rendimiento': 'alto'},
    'fluido':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'fluida':    {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing', 'rendimiento': 'alto'},
    'buen':      {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'calidad': 'buena'},
    'bueno':     {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'calidad': 'buena'},
    'buena':     {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing', 'calidad': 'buena'},
    'veloz':     {'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing', 'rendimiento': 'alto'},
    'eficiente': {'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing', 'rendimiento': 'alto'},
    'ligero':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing'},
    'ligera':    {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing'},
    'duradero':  {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing'},
    'duradera':  {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing'},
    'compacto':  {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing'},
    'compacta':  {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing'},
    'resistente':{'cat': 'adjetivo', 'gen': 'inv',  'num': 'sing'},
    'moderno':   {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing'},
    'moderna':   {'cat': 'adjetivo', 'gen': 'fem',  'num': 'sing'},
    'pesados':   {'cat': 'adjetivo', 'gen': 'masc', 'num': 'plur'},
    'diario':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing'},
    # --- ADJETIVOS plurales (para detectar discordancias) ---
    'rápidos':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'plur', 'rendimiento': 'alto'},
    'rápidas':    {'cat': 'adjetivo', 'gen': 'fem',  'num': 'plur', 'rendimiento': 'alto'},
    'potentes':   {'cat': 'adjetivo', 'gen': 'inv',  'num': 'plur', 'rendimiento': 'alto'},
    'fluidos':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'plur', 'rendimiento': 'alto'},
    'fluidas':    {'cat': 'adjetivo', 'gen': 'fem',  'num': 'plur', 'rendimiento': 'alto'},
    'veloces':    {'cat': 'adjetivo', 'gen': 'inv',  'num': 'plur', 'rendimiento': 'alto'},
    'eficientes': {'cat': 'adjetivo', 'gen': 'inv',  'num': 'plur', 'rendimiento': 'alto'},
    'buenos':     {'cat': 'adjetivo', 'gen': 'masc', 'num': 'plur', 'calidad': 'buena'},
    'buenas':     {'cat': 'adjetivo', 'gen': 'fem',  'num': 'plur', 'calidad': 'buena'},
    'ligeros':    {'cat': 'adjetivo', 'gen': 'masc', 'num': 'plur'},
    'ligeras':    {'cat': 'adjetivo', 'gen': 'fem',  'num': 'plur'},

    # --- MARCAS ---
    'samsung':    {'cat': 'marca', 'valor': 'samsung'},
    'xiaomi':     {'cat': 'marca', 'valor': 'xiaomi'},
    'apple':      {'cat': 'marca', 'valor': 'apple'},
    'qualcomm':   {'cat': 'marca', 'valor': 'qualcomm'},
    'mediatek':   {'cat': 'marca', 'valor': 'mediatek'},
    'motorola':   {'cat': 'marca', 'valor': 'motorola'},
    'oneplus':    {'cat': 'marca', 'valor': 'oneplus'},
    'oppo':       {'cat': 'marca', 'valor': 'oppo'},
    'realme':     {'cat': 'marca', 'valor': 'realme'},
    'huawei':     {'cat': 'marca', 'valor': 'huawei'},
    'sony':       {'cat': 'marca', 'valor': 'sony'},
    'google':     {'cat': 'marca', 'valor': 'google'},

    # --- ESPECIFICACIONES ---
    'snapdragon': {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'qualcomm'},
    'dimensity':  {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'mediatek'},
    'exynos':     {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'samsung'},
    'helio':      {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'mediatek'},
    'nucleos':    {'cat': 'especificacion', 'tipo': 'nucleos'},
    '4nm':        {'cat': 'especificacion', 'tipo': 'litografia'},
    'nanometros': {'cat': 'especificacion', 'tipo': 'medida'},
    'octa':       {'cat': 'especificacion', 'tipo': 'prefijo'},
    'core':       {'cat': 'especificacion', 'tipo': 'nucleos'},
    'gen':        {'cat': 'especificacion', 'tipo': 'generacion'},
    's':          {'cat': 'especificacion', 'tipo': 'variante'},
    '5g':         {'cat': 'especificacion', 'tipo': 'conectividad', 'valor': '5g'},
    '4g':         {'cat': 'especificacion', 'tipo': 'conectividad', 'valor': '4g'},

    # --- GAMAS ---
    'gama':       {'cat': 'gama'},
    'alta':       {'cat': 'gama_valor', 'valor': 'alta'},
    'media':      {'cat': 'gama_valor', 'valor': 'media'},
    'baja':       {'cat': 'gama_valor', 'valor': 'baja'},
    'premium':    {'cat': 'gama_valor', 'valor': 'premium'},
    'barato':     {'cat': 'gama_valor', 'valor': 'barato'},
    'económico':  {'cat': 'gama_valor', 'valor': 'economico'},
    'caro':       {'cat': 'gama_valor', 'valor': 'caro'},
    'asequible':  {'cat': 'gama_valor', 'valor': 'economico'},
    'accesible':  {'cat': 'gama_valor', 'valor': 'economico'},

    # --- VERBOS (infinitivo) ---
    'jugar':       {'cat': 'verbo', 'accion': 'jugar'},
    'programar':   {'cat': 'verbo', 'accion': 'programar'},
    'desarrollar': {'cat': 'verbo', 'accion': 'desarrollar'},
    'editar':      {'cat': 'verbo', 'accion': 'editar'},
    'trabajar':    {'cat': 'verbo', 'accion': 'trabajar'},
    'estudiar':    {'cat': 'verbo', 'accion': 'estudiar'},
    'fotografiar': {'cat': 'verbo', 'accion': 'fotografiar'},
    'grabar':      {'cat': 'verbo', 'accion': 'grabar'},
    'diseñar':     {'cat': 'verbo', 'accion': 'diseñar'},
    'navegar':     {'cat': 'verbo', 'accion': 'navegar'},
    'escuchar':    {'cat': 'verbo', 'accion': 'escuchar'},
    'ver':         {'cat': 'verbo', 'accion': 'ver'},

    # --- VERBOS CONJUGADOS ---
    # IMPORTANTE: sin rasgo 'gen' para no contaminar la unificación
    'tenga':    {'cat': 'verbo_conjugado', 'accion': 'tener'},
    'posea':    {'cat': 'verbo_conjugado', 'accion': 'poseer'},
    'corra':    {'cat': 'verbo_conjugado', 'accion': 'correr'},
    'funcione': {'cat': 'verbo_conjugado', 'accion': 'funcionar'},
    'sirva':    {'cat': 'verbo_conjugado', 'accion': 'servir'},
    'ejecute':  {'cat': 'verbo_conjugado', 'accion': 'ejecutar'},
    'incluya':  {'cat': 'verbo_conjugado', 'accion': 'incluir'},
    'mueva':    {'cat': 'verbo_conjugado', 'accion': 'mover'},
    'sea':      {'cat': 'verbo_conjugado', 'accion': 'ser'},
    'cuente':   {'cat': 'verbo_conjugado', 'accion': 'contar'},
    'soporte':  {'cat': 'verbo_conjugado', 'accion': 'soportar'},
    'permita':  {'cat': 'verbo_conjugado', 'accion': 'permitir'},
    'ofrezca':  {'cat': 'verbo_conjugado', 'accion': 'ofrecer'},
    'traiga':   {'cat': 'verbo_conjugado', 'accion': 'traer'},

    # --- USOS ---
    'desarrollo':  {'cat': 'uso', 'accion': 'desarrollar'},
    'edición':     {'cat': 'uso', 'accion': 'editar'},
    'fotografía':  {'cat': 'uso', 'accion': 'fotografiar'},
    'gaming':      {'cat': 'uso', 'accion': 'jugar'},
    'uso':         {'cat': 'uso', 'accion': 'usar'},
    'juegos':      {'cat': 'uso', 'accion': 'jugar'},
    'trabajo':     {'cat': 'uso', 'accion': 'trabajar'},
    'diario':      {'cat': 'uso', 'accion': 'uso diario'},

    # --- ÁREAS DE USO ---
    'estudio':        {'cat': 'area_uso', 'accion': 'estudiar'},
    'ocio':           {'cat': 'area_uso', 'accion': 'ocio'},
    'oficina':        {'cat': 'area_uso', 'accion': 'trabajar'},
    'universidad':    {'cat': 'area_uso', 'accion': 'estudiar'},
    'colegio':        {'cat': 'area_uso', 'accion': 'estudiar'},
    'viaje':          {'cat': 'area_uso', 'accion': 'viajar'},
    'entretenimiento':{'cat': 'area_uso', 'accion': 'ocio'},

    # --- JUEGOS ---
    'cod':        {'cat': 'juego', 'nombre': 'cod'},
    'fortnite':   {'cat': 'juego', 'nombre': 'fortnite'},
    'minecraft':  {'cat': 'juego', 'nombre': 'minecraft'},
    'red':        {'cat': 'juego', 'nombre': 'rdr'},
    'dead':       {'cat': 'juego', 'nombre': 'rdr'},
    'redemption': {'cat': 'juego', 'nombre': 'rdr'},
    'emuladores': {'cat': 'juego', 'tipo': 'emulador'},
    'free':       {'cat': 'juego', 'nombre': 'free fire'},
    'fire':       {'cat': 'juego', 'nombre': 'free fire'},
    'pubg':       {'cat': 'juego', 'nombre': 'pubg'},
    'genshin':    {'cat': 'juego', 'nombre': 'genshin impact'},

    # --- CONJUNCIONES / PREPOSICIONES ---
    'y':    {'cat': 'conjuncion'},
    'que':  {'cat': 'conjuncion'},
    'pero': {'cat': 'conjuncion'},
    'más':  {'cat': 'conjuncion'},
    'con':  {'cat': 'preposicion'},
    'para': {'cat': 'preposicion'},
    'de':   {'cat': 'preposicion'},
    'ni':   {'cat': 'conjuncion'},
    'o':    {'cat': 'conjuncion'},

    # --- NÚMEROS ---
    'ocho': {'cat': 'numero', 'valor': 8},
    '8':    {'cat': 'numero', 'valor': 8},
    '1':    {'cat': 'numero', 'valor': 1},
    '2':    {'cat': 'numero', 'valor': 2},
    '7':    {'cat': 'numero', 'valor': 7},
}

# ─────────────────────────────────────────────────────────────
def _normalizar_clave(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.strip()

# Normalizar léxico
lexico = {_normalizar_clave(k): v for k, v in lexico.items()}

# Normalizar terminales de la gramática
gramatica = {
    simbolo: [
        [_normalizar_clave(token) if isinstance(token, str) and token[0].islower() else token
         for token in produccion]
        for produccion in producciones
    ]
    for simbolo, producciones in gramatica.items()
}