def unificar_rasgos(rasgos1, rasgos2):
    resultado = dict(rasgos1)
    rasgos_estrictos = ['gen', 'num']
    origen1 = rasgos1.get('_origen', ['???'])
    origen2 = rasgos2.get('_origen', ['???'])

    for rasgo, valor in rasgos2.items():
        if rasgo == '_origen':
            continue
            
        if rasgo in rasgos_estrictos:
            # Si el rasgo ya existe y sus valores chocan (ej. fem vs masc)
            if rasgo in resultado and resultado[rasgo] != valor:
                
                # REGLA 1: Si alguno ya es 'inv' (invariante) o 'mixto', se fusionan pacíficamente
                if 'inv' in (resultado[rasgo], valor) or 'mixto' in (resultado[rasgo], valor):
                    resultado[rasgo] = 'mixto'
                    continue
                
                # REGLA 2: Permitir unión de componentes diferentes (ej: RAM + Almacenamiento)
                es_comp1 = rasgos1.get('tipo') == 'componente' or rasgos1.get('cat') == 'especificacion'
                es_comp2 = rasgos2.get('tipo') == 'componente' or rasgos2.get('cat') == 'especificacion'
                
                if es_comp1 and es_comp2:
                    resultado[rasgo] = 'mixto' # Neutralizamos el género para que el ATN lo acepte
                    continue

                # Si no aplica la tolerancia, entonces sí es un error real de concordancia
                r1 = " ".join(f"{k}:{v}" for k, v in rasgos1.items()
                              if k not in ['cat', '_origen'])
                r2 = " ".join(f"{k}:{v}" for k, v in rasgos2.items()
                              if k not in ['cat', '_origen'])
                p1 = " ".join(origen1)
                p2 = " ".join(origen2)
                return None, (
                    f"Discordancia en '{rasgo}': "
                    f"'{p1}' [{r1}] choca con '{p2}' [{r2}]"
                )
            
            # Si no hay choque, se asigna el valor
            resultado[rasgo] = valor
            
        elif rasgo not in resultado or rasgo == 'cat':
            resultado[rasgo] = valor

    resultado['_origen'] = origen1 + origen2
    return resultado, None