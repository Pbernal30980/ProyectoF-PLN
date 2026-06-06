# Analizador de Requerimientos de Dispositivos — DCG + ATN
 — *Universidad del Valle, Procesamiento de Lenguaje Natural*.
 
Presentado por Pedro Bernal y Santiago Reyes

Este es un sistema de procesamiento de lenguaje natural para interpretar requerimientos de dispositivos tecnológicos (teléfonos, procesadores, memoria, etc.) y generar recomendaciones de compra al usuario.


## Requisitos

- Python 3.10 o superior
- No requiere librerías externas (solo `unicodedata`, `re` y `random`, todos del *standard library*)

## Cómo ejecutar

```bash
python main.py
```

Se abrirá un modo interactivo donde puedes escribir frases como:

```
> quiero un celular gama alta para jugar
> busco mucha memoria para programar
> necesito el teléfono rápido potente y fluido con snapdragon
```

Comandos especiales disponibles dentro del modo interactivo:

| Comando         | Descripción                                     |
|-----------------|-------------------------------------------------|
| `casos`         | Ejecuta todos los casos de prueba predefinidos  |
| `caso <n>`      | Ejecuta un caso de prueba específico            |
| `casos <n> <m>` | Ejecuta casos desde `<n>` hasta `<m>`           |
| `listar`        | Muestra la lista de casos de prueba             |
| `ayuda` / `help`| Muestra la pantalla de ayuda                    |
| `salir` / `exit`| Termina el programa                             |

## Arquitectura del sistema

El pipeline de análisis consta de 5 etapas secuenciales:

```
Entrada → 1. Léxico → 2. DCG → 3. AF → 4. ATN → 5. Recomendador → Salida
```

### 1. `gramatica.py` — Léxico y gramática

Define el **léxico** (diccionario `lexico`) con categorías gramaticales, rasgos morfológicos (género, número) y semánticos de cada palabra, y la **gramática DCG** (diccionario `gramatica`) con reglas de producción para formar oraciones del dominio tecnológico. Soporta concordancia de género y número.

### 2. `parser_dcg.py` — Parser DCG

Implementa un parser descendente recursivo basado en **DCG (Definite Clause Grammar)** que, dada una oración tokenizada, produce todos los árboles sintácticos válidos aplicando las reglas de `gramatica.py`. Realiza unificación de rasgos en cada derivación.

### 3. `unificacion.py` — Unificación de rasgos

Función `unificar_rasgos` que valida la compatibilidad entre rasgos morfológicos (género, número) durante el parseo. Detecta discordancias como "una celular" (fem + masc) y las reporta como errores, permitiendo tolerancias controladas (ej. invariantes o componentes mixtos).

### 4. `ambiguedad.py` — Autómata Finito (AF) desambiguador

Cuando el DCG produce múltiples árboles sintácticos válidos para una misma oración, este módulo ejecuta un **Autómata Finito** que asigna puntajes a cada candidato según heurísticas (presencia de complemento, cantidad de modificadores, riqueza de rasgos del sujeto) y selecciona el ganador.

### 5. `atn.py` — Red de Transición Aumentada (ATN)

Recorre el árbol sintáctico ganador mediante una **ATN (Augmented Transition Network)** y extrae registros semánticos estructurados: intención, artículo, sujeto, modificadores (marca, gama, especificaciones técnicas, adjetivos) y complemento de uso. Produce una traza de las transiciones de estado.

### 6. `generador_respuestas.py` — Sistema recomendador

Toma los registros semánticos del ATN y consulta la base de datos de dispositivos, asignando puntajes a cada producto según qué tan bien coincide con los requerimientos del usuario. Devuelve una respuesta en lenguaje natural con las mejores opciones. También incluye detección de **fuera de dominio** (preguntas sobre amor, comida, filosofía) con respuestas ingeniosas.

### 7. `base_datos.py` — Catálogo de dispositivos

Contiene la base de datos simulada (`DISPOSITIVOS`) con ~40+ entradas de smartphones, procesadores y componentes de RAM/almacenamiento. Cada entrada incluye nombre, marca, gama, atributos, procesador, RAM, almacenamiento, descripción y usos óptimos.

### 8. `utils.py` — Utilidades

Funciones auxiliares de normalización de texto (eliminación de tildes, lowercasing, limpieza de caracteres especiales), tokenización (`lexer`) e impresión formateada de árboles sintácticos.

### 9. `main.py` — Orquestador principal

Punto de entrada del sistema. Coordina el pipeline completo y ofrece un **modo interactivo** donde el usuario puede escribir frases libremente, ejecutar casos de prueba predefinidos o listarlos. Contiene 15 casos de prueba que cubren oraciones válidas, errores de concordancia, errores estructurales y consultas fuera de dominio.
