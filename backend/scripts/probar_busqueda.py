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
    3. Busca una imagen que SI esta en el dataset
    4. Realiza busqueda por imagen
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
    
    # 2: Seleccionar una imagen que SÍ está en el dataset indexado
    directorio_procesadas = 'datos/procesadas'
    if not os.path.exists(directorio_procesadas):
        print(f"Error: No existe directorio {directorio_procesadas}")
        return
    
    archivos_imagen = [f for f in os.listdir(directorio_procesadas) if f.endswith('.png')]
    if not archivos_imagen:
        print("Error: No hay imagenes en datos/procesadas")
        return
    
    # Usar la primera imagen del dataset como consulta
    imagen_consulta = archivos_imagen[0]
    ruta_imagen = os.path.join(directorio_procesadas, imagen_consulta)
    
    print(f"\nPRUEBA 1: Busqueda por imagen (consulta a si misma)")
    print(f"Imagen consulta: {imagen_consulta}")
    
    # 3: Leer imagen y convertir a base64
    try:
        with open(ruta_imagen, 'rb') as f:
            imagen_bytes = f.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error leyendo imagen {ruta_imagen}: {e}")
        return
    
    # 4: Realizar busqueda por IMAGEN
    response = requests.post(
        "http://localhost:5000/api/buscar-similares",
        json={"imagen": imagen_base64}
    )
    
    # 5: Procesar y mostrar resultados
    if response.status_code == 200:
        resultados = response.json()
        print(f"Busqueda exitosa - {len(resultados.get('resultados', []))} resultados")
        
        # Mostrar top 10 
        print("\nTOP 10 RESULTADOS (ordenados por similitud):")
        for i, resultado in enumerate(resultados['resultados'][:10]):
            print(f"   {i+1:2d}. {resultado['archivo']} - "
                  f"Similitud: {resultado['similitud']:.3f} - "
                  f"Distancia: {resultado['distancia']:.2f}")
        
        # Verificacion de precision
        verificar_precision_exacta(resultados['resultados'], imagen_consulta)
            
    else:
        print(f"Error en busqueda: {response.json()}")


def probar_busqueda_aleatoria():
    print("\nPRUEBA 2: Busqueda con imagen aleatoria")
    
    # 1: Seleccionar imagen aleatoria del directorio de procesadas
    directorio_procesadas = 'datos/procesadas'
    if not os.path.exists(directorio_procesadas):
        print(f"Error: No existe directorio {directorio_procesadas}")
        return
    
    archivos_imagen = [f for f in os.listdir(directorio_procesadas) if f.endswith('.png')]
    if not archivos_imagen:
        print("Error: No hay imagenes en datos/procesadas")
        return
    
    # 2: Seleccionar imagen aleatoria
    imagen_consulta = random.choice(archivos_imagen)
    ruta_imagen = os.path.join(directorio_procesadas, imagen_consulta)
    
    print(f"Imagen de consulta aleatoria: {imagen_consulta}")
    
    # 3: Leer imagen y convertir a base64
    try:
        with open(ruta_imagen, 'rb') as f:
            imagen_bytes = f.read()
            imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error leyendo imagen {ruta_imagen}: {e}")
        return
    
    # 4: Realizar busqueda por IMAGEN
    response = requests.post(
        "http://localhost:5000/api/buscar-similares",
        json={"imagen": imagen_base64}
    )
    
    # 5: Mostrar resultados
    if response.status_code == 200:
        resultados = response.json()
        print(f"Resultados obtenidos: {len(resultados.get('resultados', []))}")
        
        print("\nTOP 5 RESULTADOS ALEATORIOS:")
        for i, resultado in enumerate(resultados['resultados'][:5]):
            print(f"   {i+1}. {resultado['archivo']} - "
                  f"Similitud: {resultado['similitud']:.3f} - "
                  f"Distancia: {resultado['distancia']:.2f}")
        
        # Verificar si la consulta aparece en los resultados
        consulta_encontrada = any(r['archivo'] == imagen_consulta for r in resultados['resultados'])
        if consulta_encontrada:
            print("   CONSULTA ENCONTRADA EN RESULTADOS")
        else:
            print("   CONSULTA NO ENCONTRADA (normal para imagen nueva)")
            
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