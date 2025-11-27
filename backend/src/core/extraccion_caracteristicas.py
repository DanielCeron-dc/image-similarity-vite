import cv2
import numpy as np
from skimage import feature, filters
import os
from tqdm import tqdm
import json


class ExtractorLBP:
    """
    Extractor de caracteristicas LBP (Local Binary Patterns).
    
    LBP captura patrones de micro-textura local comparando cada pixel
    con sus vecinos. Es invariante a cambios monotonos de iluminacion.
    
    Attributes:
        num_puntos (int): Numero de puntos vecinos a considerar
        radio (int): Radio del circulo de vecinos
        metodo (str): Tipo de LBP ('uniform', 'default', 'ror', 'var')
    """
    
    def __init__(self, num_puntos=24, radio=8, metodo="uniform"):
        self.num_puntos = num_puntos
        self.radio = radio
        self.metodo = metodo

    def extraer(self, imagen):
        """
        Flujo:
        1. Calcula LBP en cada pixel comparando con vecinos
        2. Genera histograma de patrones LBP
        3. Normaliza histograma (suma = 1)
        """
        
        # 1: Calcular LBP en cada pixel
        # local_binary_pattern compara cada pixel con sus vecinos circulares
        lbp = feature.local_binary_pattern(
            imagen, 
            self.num_puntos, 
            self.radio, 
            method=self.metodo
        )
        
        # 2: Crear histograma de patrones LBP
        # Bins: 0 hasta num_puntos+2 (para 'uniform', incluye patrones no-uniformes)
        (hist, _) = np.histogram(
            lbp.ravel(),
            bins=np.arange(0, self.num_puntos + 3),
            range=(0, self.num_puntos + 2)
        )
        hist = hist.astype("float")
        
        # 3: Normalizar histograma 
        suma = hist.sum()
        if suma > 0:
            hist /= suma
        else:
            hist = np.ones_like(hist) / len(hist)
            
        return hist
    

class ExtractorHOG:
    """
    Extractor de caracteristicas HOG (Histogram of Oriented Gradients).
    
    HOG captura la estructura de forma mediante distribuciones de gradientes.
    Divide la imagen en celdas y calcula histogramas de orientaciones de bordes.
    
    Attributes:
        tamano_ventana (tuple): Tamano de la ventana de deteccion
        tamano_bloque (tuple): Tamano del bloque para normalizacion
        paso_bloque (tuple): Desplazamiento entre bloques consecutivos
        tamano_celda (tuple): Tamano de cada celda individual
        nbins (int): Numero de bins en histograma de orientaciones
        hog (cv2.HOGDescriptor): Descriptor HOG de OpenCV
    """
    
    def __init__(self):
        self.tamano_ventana = (64, 64)
        self.tamano_bloque = (16, 16)
        self.paso_bloque = (8, 8)
        self.tamano_celda = (8, 8)
        self.nbins = 9
        
        # Crear descriptor HOG de OpenCV
        self.hog = cv2.HOGDescriptor(
            self.tamano_ventana,
            self.tamano_bloque,
            self.paso_bloque,
            self.tamano_celda,
            self.nbins
        )

    def extraer(self, imagen):
        """
        Flujo:
        1. Redimensiona imagen a tamano de ventana (64x64)
        2. Calcula gradientes en cada pixel
        3. Agrupa gradientes en celdas y bloques
        4. Normaliza por bloques
        5. Concatena todos los histogramas
        """
        
        # 1: Redimensionar a tamano de ventana
        imagen_redimensionada = cv2.resize(imagen, self.tamano_ventana)
        
        # 2: Calcular descriptor HOG
        # compute() retorna vector de caracteristicas como matriz columna
        caracteristicas = self.hog.compute(imagen_redimensionada)
        
        # 3: Aplanar a vector unidimensional
        return caracteristicas.flatten()


class ExtractorGabor:
    """
    Extractor de caracteristicas usando filtros de Gabor.
    
    Los filtros de Gabor son detectores de bordes direccionales optimos para
    analisis de textura orientada. Ideales para patrones de crestas papilares.
    
    Attributes:
        frecuencias (list): Frecuencias espaciales de los filtros
        orientaciones (int): Numero de orientaciones a evaluar
        angulos (list): Angulos en radianes para cada orientacion
    """
    
    def __init__(self, frecuencias=[0.1, 0.2], orientaciones=4):
        self.frecuencias = frecuencias
        self.orientaciones = orientaciones
        
        # Calcular angulos uniformemente distribuidos en [0, pi)
        # Por ejemplo, para 4 orientaciones: [0, pi/4, pi/2, 3pi/4]
        self.angulos = [i * np.pi / orientaciones for i in range(orientaciones)]

    def extraer(self, imagen):
        """
        Flujo:
        1. Para cada combinacion (frecuencia, orientacion):
           a. Aplica filtro Gabor
           b. Calcula magnitud de respuesta
           c. Extrae media y desviacion estandar
        2. Concatena todas las estadisticas
        """
        caracteristicas = []
        
        for frecuencia in self.frecuencias:
            for theta in self.angulos:
                
                # 1: Aplicar filtro Gabor
                filtro_real, filtro_imag = filters.gabor(
                    imagen, 
                    frequency=frecuencia, 
                    theta=theta
                )
                
                # 2: Calcular magnitud de la respuesta compleja
                magnitud = np.sqrt(filtro_real**2 + filtro_imag**2)
                
                # 3: Extraer estadisticas de la magnitud
                caracteristicas.extend([np.mean(magnitud), np.std(magnitud)])
        
        return np.array(caracteristicas)


class ExtractorMasivo:
    """
    Combina LBP, HOG y Gabor en un pipeline unificado para extraccion
    masiva de caracteristicas de huellas dactilares.
    """
    
    def __init__(self):
        self.extractores = {
            'LBP': ExtractorLBP(),
            'HOG': ExtractorHOG(),
            'GABOR': ExtractorGabor()
        }

    def extraer_imagen(self, imagen):
        """
        Flujo:
        1. Aplica cada extractor (LBP, HOG, Gabor) a la imagen
        2. Almacena caracteristicas individuales
        3. Concatena todo en un vector unificado
        """
        caracteristicas = {}
        vector_completo = []

        # Aplicar
        for nombre, extractor in self.extractores.items():
            # Extraer caracteristicas con el descriptor actual
            caracteristicas_ext = extractor.extraer(imagen)
            # Convertir a lista de floats (para serializacion JSON)
            caracteristicas[nombre] = [float(x) for x in caracteristicas_ext.tolist()]
            # Agregar al vector completo
            vector_completo.extend([float(x) for x in caracteristicas_ext])

        return {
            'caracteristicas': caracteristicas,
            'vector_completo': vector_completo
        }

    def extraer_directorio(self, directorio_imagenes, ruta_salida_json=None, ruta_salida_vectores=None):
        """
        Extrae caracteristicas de todas las imagenes en un directorio.
        
        Flujo:
        1. Lista todas las imagenes .png del directorio
        2. Para cada imagen:
           a. Lee la imagen
           b. Extrae caracteristicas
           c. Almacena resultados
        3. Guarda resultados
        
        Args:
            directorio_imagenes (str): Directorio con imagenes preprocesadas
            ruta_salida_json (str): Ruta para guardar metadatos en JSON (opcional)
            ruta_salida_vectores (str): Ruta para guardar matriz NumPy (opcional)
            
        Returns:
            tuple: (resultados, vectores_caracteristicas)
                - resultados: Lista de diccionarios con metadatos completos
                - vectores_caracteristicas: Lista de vectores numericos
        """
        
        # 1: Listar todas las imagenes preprocesadas
        archivos_imagenes = [
            f for f in os.listdir(directorio_imagenes) 
            if f.endswith('.png')
        ]
        
        print(f"Extrayendo caracteristicas de {len(archivos_imagenes)} imagenes...")

        resultados = []
        vectores_caracteristicas = []

        # 2: Procesar cada imagen
        for archivo in tqdm(archivos_imagenes, desc="Extraccion"):

            ruta_imagen = os.path.join(directorio_imagenes, archivo)
            imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)

            if imagen is not None:
                # Extraer caracteristicas
                resultado = self.extraer_imagen(imagen)
                # Agregar metadato del nombre de archivo
                resultado['archivo'] = archivo
                # Almacenar resultados
                resultados.append(resultado)
                vectores_caracteristicas.append(resultado['vector_completo'])

        # 3: Guardar resultados 
        if ruta_salida_json:
            with open(ruta_salida_json, 'w') as f:
                json.dump(resultados, f, indent=2)
            print(f"Caracteristicas guardadas en: {ruta_salida_json}")

        if ruta_salida_vectores:
            # Guardar como matriz NumPy (shape: [N_imagenes, 1806])
            np.save(ruta_salida_vectores, np.array(vectores_caracteristicas))
            print(f"Vectores guardados en: {ruta_salida_vectores}")

        print(f"Extracción completada: {len(resultados)} imagenes procesadas")
        
        return resultados, vectores_caracteristicas