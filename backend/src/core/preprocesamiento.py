"""
    Realiza conversion a escala de grises, mejora de contraste y normalizacion.
"""

import cv2
import numpy as np
import os
from tqdm import tqdm


class PreprocesadorUnificado:
    
    def __init__(self, tamano_objetivo=(300, 300)):

        self.tamano_objetivo = tamano_objetivo
        
        # CLAHE: Contrast Limited Adaptive Histogram Equalization
        # clipLimit: Limita el contraste para evitar amplificacion excesiva de ruido
        # tileGridSize: Tamano de las regiones para ecualizacion local (8x8 pixeles)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def preprocesar_imagen(self, imagen):
        """
        Flujo de procesamiento:
        1. Conversion a escala de grises
        2. Redimensionamiento a tamano estandar
        3. Mejora de contraste con CLAHE
        4. Suavizado con filtro de mediana
        
        Args:
            imagen (numpy.ndarray): Imagen de entrada (BGR o escala de grises)
            
        Returns:
            numpy.ndarray: Imagen preprocesada en escala de grises
        """
        
        # 1: Conversion a escala de grises
        # Verifica si la imagen tiene 3 canales (BGR) o ya esta en escala de grises
        if len(imagen.shape) == 3:
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        else:
            gris = imagen

        # 2: Redimensionamiento
        h, w = gris.shape
        
        # Redimensionar solo si las dimensiones no coinciden con el objetivo
        if h != self.tamano_objetivo[0] or w != self.tamano_objetivo[1]:
            # INTER_AREA: Interpolacion recomendada para reduccion de tamano
            # Resultados mas suaves y evita aliasing
            gris = cv2.resize(gris, self.tamano_objetivo, interpolation=cv2.INTER_AREA)

        # 3: Mejora de contraste con CLAHE
        # CLAHE mejora el contraste local sin amplificar demasiado el ruido
        # Util para huellas latentes con iluminacion irregular
        mejorada = self.clahe.apply(gris)

        # 4: Suavizado para reducir ruido
        # Filtro de mediana con kernel 3x3
        # Efectivo para eliminar ruido de tipo "sal y pimienta" sin difuminar bordes
        suavizada = cv2.medianBlur(mejorada, 3)

        return suavizada

    def preprocesar_directorio(self, directorio_entrada, directorio_salida):
        """
        Preprocesa todas las imagenes de un directorio y guarda los resultados.
        
        Flujo:
        1. Escanea recursivamente el directorio de entrada
        2. Identifica archivos de imagen por extension
        3. Preprocesa cada imagen encontrada
        4. Guarda con nombre (proc_XXXXXX.png)
        """
        
        # Crear directorio de salida
        os.makedirs(directorio_salida, exist_ok=True)

        # 1: Encontrar todas las imagenes en el directorio
        formatos_imagen = ['.tif', '.tiff', '.png', '.jpg', '.jpeg']
        rutas_imagenes = []
        
        for root, dirs, files in os.walk(directorio_entrada):
            for file in files:
                if any(file.lower().endswith(fmt) for fmt in formatos_imagen):
                    ruta_completa = os.path.join(root, file)
                    rutas_imagenes.append(ruta_completa)

        # 2: Preprocesar cada imagen encontrada
        contador = 0
        print(f"Preprocesando {len(rutas_imagenes)} imagenes...")

        # tqdm: Barra de progreso visual
        for ruta_entrada in tqdm(rutas_imagenes, desc="Preprocesamiento"):
            
            # Leer imagen original
            img_original = cv2.imread(ruta_entrada)
            
            if img_original is not None:
                # Preprocesar y guardar imagen
                img_procesada = self.preprocesar_imagen(img_original)
                nombre_salida = f"proc_{contador:06d}.png"
                ruta_salida = os.path.join(directorio_salida, nombre_salida)
                
                cv2.imwrite(ruta_salida, img_procesada)
                
                contador += 1

        print(f"Preprocesamiento completado: {contador} imagenes procesadas")
        return contador