# generador_respuestas.py
import random
from base_datos import DISPOSITIVOS

# Sinónimos de gama: 'economico' / 'barato' / 'caro' no son gamas canónicas
# en el catálogo, pero el usuario las usa como tal. Las mapeamos a la gama
# más cercana para que el matching funcione.
GAMA_SINONIMOS = {
    'economico': 'baja',
    'barato':    'baja',
    'caro':      'alta',
}

# Sinónimos de adjetivo: la apócope 'buen' (masc sing ante sustantivo) y
# la forma femenina 'buena' se normalizan a 'bueno' para matchear contra
# la lista de atributos del dispositivo.
ADJ_SINONIMOS = {
    'buen':  'bueno',
    'buena': 'bueno',
}


def manejar_fuera_de_dominio(tokens):
    """
    Heurística para interceptar temas fuera del ecosistema tecnológico
    y dar respuestas ingeniosas en lugar de un error frío de compilador.
    """
    palabras_clave = set(tokens)
    
    amor = {"amor", "novia", "novio", "pareja", "amar", "corazon", "vida"}
    comida = {"pizza", "hamburguesa", "comida", "almuerzo", "restaurante", "hambre"}
    filosofia = {"existencia", "dios", "creo", "humano", "sentimientos", "siento", "vivir"}
    
    if palabras_clave.intersection(amor):
        return ("🤖 Como recomendador experto en hardware de telefonos, el único 'amor' "
                "que entiendo es el que le tengo a un Snapdragon bien refrigerado. "
                "¡Pero te aseguro que un celular gama alta te ayudará a responder más rápido en Tinder!")
        
    if palabras_clave.intersection(comida):
        return ("🤖 ¡Uff, una comida suena excelente! Pero mi sistema operativo solo digiere "
                "datos. Si me dices tu presupuesto, te busco un celular genial para que "
                "pidas todas las pizzas que quieras por delivery.")
                
    if palabras_clave.intersection(filosofia):
        return ("🤖 Interesante dilema existencial... pero mis circuitos están limitados a la tecnología. "
                "¿Qué tal si volvemos a la tierra y buscamos un smartphone potente para ti?")
    
    # Fallback genérico si no encaja en las anteriores pero es claramente fuera de tema
    return ("🤖 Hum... Temo que mi especialidad es estrictamente la recomendación de teléfonos, "
            "procesadores y hardware. Intenta preguntarme algo como: 'quiero un celular potente para jugar'.")


def generar_recomendacion(contexto):
    """
    Toma los registros semánticos del ATN y puntúa los dispositivos del catálogo.
    """
    if not contexto or not contexto.get('sujeto'):
        return "🤖 No logré comprender qué tipo de dispositivo estás buscando. ¿Podrías ser más específico?"

    modificadores = contexto.get('modificadores', [])
    # Extraer complementos (pueden venir como lista o string según el ATN)
    comp = contexto.get('complemento', '')
    complemento_str = " ".join(comp) if isinstance(comp, list) else (comp or '')

    mejores_opciones = []

    for dispositivo in DISPOSITIVOS:
        puntaje = 0
        
        # 1. Validar coincidencia de Marca si fue solicitada (Soporta 'tipo' o 'type')
        marcas_solicitadas = [
            m['valor'] for m in modificadores 
            if m.get('tipo') == 'marca' or m.get('type') == 'marca'
        ]
        if marcas_solicitadas and dispositivo['marca'] in marcas_solicitadas:
            puntaje += 5  # Alto peso a la marca explícita
            
        # 2. Validar coincidencia de Gama (Soporta 'tipo' o 'type')
        gamas_solicitadas = [
            g['valor'] for g in modificadores
            if g.get('tipo') == 'gama' or g.get('type') == 'gama'
        ]
        if gamas_solicitadas:
            gama_dispositivo = dispositivo['gama']
            atributos       = dispositivo.get('atributos', [])
            for g in gamas_solicitadas:
                # 2a. Match exacto (gama canónica)
                if gama_dispositivo == g:
                    puntaje += 4
                    break
                # 2b. Match por sinónimo: 'economico'/'barato' → 'baja', 'caro' → 'alta'
                if GAMA_SINONIMOS.get(g) == gama_dispositivo:
                    puntaje += 4
                    break
                # 2c. Match contra atributos: el dispositivo declara 'economico'/'barato'
                if g in atributos:
                    puntaje += 4
                    break

        # 3. Validar adjetivos y especificaciones técnicas en los atributos del dispositivo
        for m in modificadores:
            if m.get('tipo') in ['adjetivo', 'especificacion_tec']:
                valor = m['valor']
                # 3a. Match directo
                if valor in dispositivo['atributos'] or valor in dispositivo['procesador']:
                    puntaje += 2
                # 3b. Match por sinónimo (p.ej. 'buen' → 'bueno')
                elif ADJ_SINONIMOS.get(valor) in dispositivo.get('atributos', []):
                    puntaje += 2

        # 4. Validar concordancia con el Complemento de uso o juegos
        for uso in dispositivo['usos_optimos']:
            if uso in complemento_str:
                puntaje += 3

        if puntaje > 0:
            mejores_opciones.append((dispositivo, puntaje))

    # Ordenar dispositivos de mayor a menor puntaje
    mejores_opciones.sort(key=lambda x: x[1], reverse=True)

    if not mejores_opciones:
        return ("🤖 Encontré los parámetros en mi gramática, pero ningún dispositivo de mi catálogo "
                "cumple con esas características exactas actualmente. ¡Prueba buscando otras especificaciones!")

    # Diversificar por marca cuando el usuario pidió varias (p.ej. "samsung y xiaomi"):
    # mostrar la mejor opción de cada marca solicitada en vez de los 2 mejores globales.
    if len(marcas_solicitadas) > 1:
        opciones_a_mostrar = []
        for marca in marcas_solicitadas:
            candidatos = [(d, p) for d, p in mejores_opciones if d['marca'] == marca]
            if candidatos:
                opciones_a_mostrar.append(candidatos[0])
    else:
        opciones_a_mostrar = mejores_opciones[:2]

    # Construir respuesta con las mejores opciones encontradas
    respuesta = "😁 Aquí tienes mis recomendaciones basadas en tu análisis semántico:\n\n"
    for i, (disp, pts) in enumerate(opciones_a_mostrar):
        respuesta += f"{i+1}. {disp['nombre']} (Gama {disp['gama'].capitalize()}) ⭐\n"
        respuesta += f"   • Su Hardware: Procesador {disp['procesador'].upper()} | {disp['ram'].upper()} RAM | {disp['almacenamiento'].upper()}\n"
        respuesta += f"   • Te diré las razónes: {disp['descripcion']}\n\n"
        
    return respuesta