"""
Script para probar el sistema de busqueda por similitud.
Verifica precision exacta y realiza busquedas de prueba.
"""

import os
import sys
import requests
import json
import base64
import cv2
import random
import numpy as np

# Agregar directorio raiz al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utilidades.limpiar_vectores import limpiar_vector


def verificar_precision_exacta(resultados, imagen_consulta):
    
    consulta_encontrada = False
    
    # Buscar la imagen de consulta en los resultados
    for resultado in resultados:
        if resultado['archivo'] == imagen_consulta:
            consulta_encontrada = True
            similitud = resultado['similitud']
            distancia = resultado['distancia']
            
            print(f"\nVERIFICACION DE PRECISION:")
            print(f"   Imagen: {imagen_consulta}")
            print(f"   Similitud: {similitud:.6f}")
            print(f"   Distancia: {distancia:.6f}")
            
            # Evaluar precision
            if similitud == 1.0 and distancia == 0.0:
                print("   PRECISION EXACTA")
            elif similitud >= 0.999:
                print("   PRECISION ALTA")
            else:
                print("   PRECISION INACEPTABLE")
            
            break
    
    if not consulta_encontrada:
        print("   ERROR: Consulta no encontrada en resultados")


def probar_busqueda():
    """
    Flujo:
    1. Verifica que el servidor esta activo
    2. Verifica que el sistema esta indexado
    3. Carga caracteristicas de la primera imagen
    4. Realiza busqueda por vector
    5. Muestra resultados y verifica precision
    """
    print("PROBANDO SISTEMA SCBIR")

    # 1: Verificar estado del sistema
    try:
        response = requests.get("http://localhost:5000/api/estado-sistema")
        estado = response.json()
        print(f"Sistema indexado: {estado.get('sistema_indexado')}")
        
        if not estado.get('sistema_indexado'):
            print("El sistema no esta indexado")
            print("Ejecuta: python scripts/indexar_sistema.py")
            return
    except Exception as e:
        print(f"Error conectando al servidor: {e}")
        print("Asegurate de que el servidor este corriendo:")
        print("  python app.py")
        return
    
    # 2: Cargar caracteristicas pre-extraidas
    try:
        with open('datos/caracteristicas/caracteristicas_completas.json', 'r') as f:
            caracteristicas = json.load(f)
    except Exception as e:
        print(f"Error cargando caracteristicas: {e}")
        print("Ejecuta: python scripts/descargar_datos.py")
        return
    
    # 3: Probar busqueda por vector (consulta a si misma)
    print("\nPRUEBA 1: Busqueda por vector (consulta a si misma)")
    
    # Usar el vector de la primera imagen como consulta
    imagen_consulta = caracteristicas[0]['archivo']
    vector_prueba = caracteristicas[0]['vector_completo']
    
    # Limpiar vector
    vector_limpio = limpiar_vector(vector_prueba)

    print(f"Imagen consulta: {imagen_consulta}")
    print(f"Dimension del vector: {len(vector_limpio)}")
    
    # 4: Realizar busqueda via API
    response = requests.post(
        "http://localhost:5000/api/buscar-similares",
        json={"vector_caracteristicas": vector_limpio}
    )
    
    # 5: Procesar y mostrar resultados
    if response.status_code == 200:
        resultados = response.json()
        print(f"Busqueda exitosa - {len(resultados.get('resultados', []))} resultados")
        
        # Mostrar top 10 
        print("\nTOP 10 RESULTADOS (ordenados por similitud):")
        for i, resultado in enumerate(resultados['resultados'][:10]):
            # Marcar cual es la consulta original
            marca_consulta = " [CONSULTA]" if resultado.get('es_consulta', False) else ""
            print(f"   {i+1:2d}. {resultado['archivo']} - "
                  f"Similitud: {resultado['similitud']:.3f} - "
                  f"Distancia: {resultado['distancia']:.2f}{marca_consulta}")
        
        # Verificacion de precision
        verificar_precision_exacta(resultados['resultados'], imagen_consulta)
            
    else:
        print(f"Error en busqueda: {response.json()}")


def probar_busqueda_aleatoria():
    print("PRUEBA 2: Busqueda con imagen aleatoria")
    # 1: Cargar caracteristicas
    try:
        with open('datos/caracteristicas/caracteristicas_completas.json', 'r') as f:
            caracteristicas = json.load(f)
    except Exception as e:
        print(f"Error cargando caracteristicas: {e}")
        return
    
    # 2: Seleccionar imagen aleatoria como consulta
    indice_aleatorio = random.randint(0, len(caracteristicas) - 1)
    imagen_consulta = caracteristicas[indice_aleatorio]['archivo']
    vector_consulta = caracteristicas[indice_aleatorio]['vector_completo']
    vector_limpio = limpiar_vector(vector_consulta)
    
    print(f"Imagen de consulta aleatoria: {imagen_consulta}")
    
    # 3: Realizar busqueda
    response = requests.post(
        "http://localhost:5000/api/buscar-similares",
        json={"vector_caracteristicas": vector_limpio}
    )
    
    # 4: Mostrar resultados
    if response.status_code == 200:
        resultados = response.json()
        print(f"Resultados obtenidos: {len(resultados.get('resultados', []))}")
        
        print("\nTOP 5 RESULTADOS ALEATORIOS:")
        for i, resultado in enumerate(resultados['resultados'][:5]):
            marca_consulta = " [CONSULTA]" if resultado.get('es_consulta', False) else ""
            print(f"   {i+1}. {resultado['archivo']} - "
                  f"Similitud: {resultado['similitud']:.3f}{marca_consulta}")
        
        # Verificacion de precision
        verificar_precision_exacta(resultados['resultados'], imagen_consulta)
    else:
        print(f"Error en busqueda: {response.json()}")


def mostrar_interpretacion():
    """
    Muestra guia de interpretacion de resultados de similitud.
    """
    print("\n" + "="*60)
    print("PRUEBAS COMPLETADAS")
    print("="*60)
    print("\nInterpretacion de resultados:")
    print("  1.000: IDENTICO (misma imagen)")
    print("  0.900-0.999: MUY SIMILAR (posible mismo dedo)")
    print("  0.700-0.899: SIMILAR (caracteristicas compartidas)")
    print("  0.400-0.699: MODERADAMENTE SIMILAR")
    print("  0.000-0.399: POCO SIMILAR")


if __name__ == "__main__":
    probar_busqueda()
    probar_busqueda_aleatoria()
    mostrar_interpretacion()