gramatica = {
    "S": [
        ["INTENCION", "REQUERIMIENTO"],
        ["INTENCION", "REQUERIMIENTO", "COMPLEMENTO"],
        ["REQUERIMIENTO", "COMPLEMENTO"], 
        ["REQUERIMIENTO"] 
    ],
    
    "INTENCION": [["busco"], ["quiero"], ["necesito"], ["recomiéndame"], ["dime", "de"], ["busca"]],

    "REQUERIMIENTO": [
        ["ARTICULO", "SUJETO", "MODIFICADORES"],
        ["SUJETO", "MODIFICADORES"],
        ["ARTICULO", "SUJETO"]
    ],

    "SUJETO": [["teléfono"], ["celular"], ["móvil"], ["equipo"], ["dispositivo"], ["procesador"], ["chip"]],

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

    "COMPLEMENTO": [
        ["USO_FINAL"],
        ["CONJUNCION", "USO_FINAL"]
    ],

    "ARTICULO": [["un"], ["una"], ["el"], ["algún"], ["la"]],
    "CONJUNCION": [["y"], ["que"], ["pero"], ["con"], ["para"], ["más"]],

    "MARCA": [["samsung"], ["xiaomi"], ["apple"], ["qualcomm"], ["mediatek"], ["motorola"]],

    "GAMA": [
        ["gama", "alta"], ["gama", "media"], ["gama", "baja"], 
        ["premium"], ["barato"], ["económico"], ["caro"]
    ],

    "ESPECIFICACION_TEC": [
        ["snapdragon", "SERIE"], ["dimensity"], ["exynos"],
        ["RAM", "CANTIDAD"], ["ALMACENAMIENTO", "CANTIDAD"],
        ["ocho", "núcleos"], ["4nm"], ["nanómetros"],
        ["soporte", "magisk"], ["compatible", "con", "roms"]
    ],

    "ADJETIVO": [
        ["rápido"], ["potente"], ["veloz"], ["eficiente"], 
        ["que", "no", "se", "caliente"], ["fluido"], ["bueno"], ["buen"]
    ],

    "USO_FINAL": [
        ["para", "JUEGO"], ["para", "jugar"], ["para", "programar"],
        ["para", "desarrollo"], ["para", "edición"], ["para", "uso", "diario"]
    ],

    "JUEGO": [["cod"], ["fortnite"], ["minecraft"], ["red", "dead", "redemption"], ["juegos", "pesados"], ["emuladores"]],
    "CANTIDAD": [["de", "8gb"], ["de", "12gb"], ["mucha"], ["poca"], ["bastante"]],
    "SERIE": [["8", "gen", "1"], ["8", "gen", "2"], ["7", "s", "gen", "2"]],

    "RAM": [["ram"], ["memoria"]],
    "ALMACENAMIENTO": [["almacenamiento"], ["espacio"], ["rom"], ["memoria"]]

}


lexico = {
    # INTENCIONES
    'busco': {'cat': 'intencion', 'accion': 'buscar'},
    'busca': {'cat': 'intencion', 'accion': 'buscar'},
    'quiero': {'cat': 'intencion', 'accion': 'querer'},
    'necesito': {'cat': 'intencion', 'accion': 'necesitar'},
    'recomiéndame': {'cat': 'intencion', 'accion': 'recomendar'},

    # ARTÍCULOS
    'un': {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'una': {'cat': 'art', 'gen': 'fem', 'num': 'sing'},
    'el': {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'la': {'cat': 'art', 'gen': 'fem', 'num': 'sing'},
    'algún': {'cat': 'art', 'gen': 'masc', 'num': 'sing'},
    'unos': {'cat': 'art', 'gen': 'masc', 'num': 'plur'},
    'unas': {'cat': 'art', 'gen': 'fem', 'num': 'plur'},

    # CANTIDAD
    'mucha': {'cat': 'cantidad', 'gen': 'fem', 'num': 'sing'},
    'poca': {'cat': 'cantidad', 'gen': 'fem', 'num': 'sing'},
    'bastante': {'cat': 'cantidad', 'gen': 'masc', 'num': 'sing'},

    # SUJETOS
    'teléfono': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'teléfonos': {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'dispositivo'},
    'celular': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},
    'celulares': {'cat': 'sujeto', 'gen': 'masc', 'num': 'plur', 'tipo': 'dispositivo'},
    'memoria': [
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'RAM'},
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'sing', 'tipo': 'componente', 'subtipo': 'Almacenamiento'}
    ],
    'memorias': [
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'plur', 'tipo': 'componente', 'subtipo': 'RAM'},
        {'cat': 'sujeto', 'gen': 'fem', 'num': 'plur', 'tipo': 'componente', 'subtipo': 'Almacenamiento'}
    ],
    'procesador': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'componente'},
    'dispositivo': {'cat': 'sujeto', 'gen': 'masc', 'num': 'sing', 'tipo': 'dispositivo'},

    # ADJETIVOS
    'rápido': {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'rápida': {'cat': 'adjetivo', 'gen': 'fem', 'num': 'sing', 'rendimiento': 'alto'},
    'rápidos': {'cat': 'adjetivo', 'gen': 'masc', 'num': 'plur', 'rendimiento': 'alto'},
    'potente': {'cat': 'adjetivo', 'num': 'sing', 'rendimiento': 'alto'}, 
    'potentes': {'cat': 'adjetivo', 'num': 'plur', 'rendimiento': 'alto'},
    'fluido': {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'rendimiento': 'alto'},
    'buen': {'cat': 'adjetivo', 'gen': 'masc', 'num': 'sing', 'calidad': 'buena'},

    # MARCAS Y ESPECIFICACIONES
    'xiaomi': {'cat': 'marca', 'valor': 'xiaomi'},
    'samsung': {'cat': 'marca', 'valor': 'samsung'},
    'snapdragon': {'cat': 'especificacion', 'componente': 'procesador', 'marca': 'qualcomm'},
    
    # GAMA
    'gama': {'cat': 'gama'},
    'media': {'cat': 'gama_valor', 'valor': 'media'},
    'alta': {'cat': 'gama_valor', 'valor': 'alta'},
    'baja': {'cat': 'gama_valor', 'valor': 'baja'},

    # VERBOS FINALES (USO FINAL)
    'jugar': {'cat': 'uso_final', 'accion': 'jugar'},
    'programar': {'cat': 'uso_final', 'accion': 'programar'},

    # CONJUNCIONES Y PREPOSICIONES
    'y': {'cat': 'conjuncion'},
    'con': {'cat': 'preposicion'},
    'para': {'cat': 'preposicion'},
    'más': {'cat': 'conjuncion'}

}