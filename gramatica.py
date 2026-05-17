gramatica = {
    "S": [
        ["INTENCION", "REQUERIMIENTO", "CARACTERISTICA", "USO_FINAL"], # busco un celular gama alta que sea rápido para minecraft
        ["INTENCION", "REQUERIMIENTO", "USO_FINAL", "CARACTERISTICA"], # busco un celular gama alta para minecraft que sea rápido
        ["INTENCION", "REQUERIMIENTO", "CARACTERISTICA"],              # busco un celular que no se caliente
        ["INTENCION", "REQUERIMIENTO", "USO_FINAL"],                   # busco un teléfono xiaomi para juegos pesados
        ["INTENCION", "REQUERIMIENTO"]                                 # quiero un teléfono gama media
    ],
    
    "INTENCION": [["busco"], ["quiero"], ["necesito"]],
    "ARTICULO": [["un"], ["una"], ["algo", "con"], ["algo"]],
    "CANTIDAD": [["mucha"], ["bastante"], ["poca"], ["bastante", "poca"], ["poco"]],
    
    "REQUERIMIENTO": [
        ["ARTICULO", "COMPONENTE", "MARCA", "GAMA"], # un teléfono samsung gama alta
        ["ARTICULO", "COMPONENTE", "MARCA"],         # un teléfono xiaomi
        ["ARTICULO", "COMPONENTE", "GAMA"],          # un teléfono gama media
        ["ARTICULO", "COMPONENTE", "ESPECIFICACION"],# un procesador mediatek
        ["ARTICULO", "COMPONENTE"],                  # un teléfono
        ["CANTIDAD", "RAM"],                         # mucha memoria
        ["CANTIDAD", "ALMACENAMIENTO"],              # mucha memoria
    ],
    
    "COMPONENTE": [["teléfono"], ["celular"], ["móvil"], ["procesador"]],
    "RAM": [["memoria"]],             
    "ALMACENAMIENTO": [["memoria"]],  
    
    "MARCA": [["samsung"], ["xiaomi"], ["motorola"], ["apple"], ["poco"], ["realme"], ["infinix"], ["rogphone"], ["redmagic"]],
    "GAMA": [["gama", "alta"], ["gama", "media"], ["gama", "baja"]],
    
    "ESPECIFICACION": [
        ["mediatek"], ["snapdragon"], ["exynos"], ["tensor"], 
        ["soporte", "magisk"], ["soporte", "root"]
    ],
    
    "CARACTERISTICA": [
        ["que", "no", "se", "caliente"], 
        ["que", "sea", "rápido"],
        ["rápido"],
        ["que", "sea", "eficiente"],
        ["que", "sea", "veloz"],
    ],
    
    "USO_FINAL": [
        ["que", "sea", "bueno", "para", "JUEGO"], 
        ["para", "JUEGO"],
        ["para", "jugar"],
    ],
    "JUEGO": [["juegos", "pesados"], ["minecraft"], ["call", "of", "duty"], ["fortnite"], ["free", "fire"], ["mobile", "legends"], ["pubg", "mobile"]]
}