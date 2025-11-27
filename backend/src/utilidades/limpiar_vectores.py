import numpy as np

def limpiar_vector(vector):
    """
    Limpia valores infinitos y NaN de un vector de características
    """
    vector_limpio = []
    for valor in vector:
        if np.isinf(valor) or np.isnan(valor):
            vector_limpio.append(0.0)
        elif abs(valor) > 1e100:  # Valores extremadamente grandes
            vector_limpio.append(0.0)
        else:
            vector_limpio.append(float(valor))
    return vector_limpio

def limpiar_vectores_lote(vectores):
    return [limpiar_vector(vector) for vector in vectores]

def verificar_problemas_division(vector):
    problemas = []
    if len(vector) >= 26:
        lbp_segment = vector[:26]
        suma_lbp = sum(lbp_segment)
        if suma_lbp == 0:
            problemas.append("LBP suma cero")
    
    return problemas