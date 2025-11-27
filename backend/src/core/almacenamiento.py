"""
Gestion de almacenamiento y recuperacion de datos del sistema SCBIR.
Guarda resultados de busquedas para analisis posterior.
"""

import json
import numpy as np
import os
from datetime import datetime


class GestorAlmacenamiento:
    
    def __init__(self, directorio_base='datos'):
        """
        Estructura de directorios creada:
            datos/
            ├── busquedas/         # Resultados de busquedas
            ├── caracteristicas/   # Vectores y metadatos
            ├── indices/           # Indices FAISS
            ├── procesadas/        # Imagenes preprocesadas
            └── datasets/          # Datasets originales
        """
        self.directorio_base = directorio_base
        # Crear directorio base si no existe
        os.makedirs(directorio_base, exist_ok=True)
    
    def guardar_resultados_busqueda(self, resultados, consulta_info=None):
        """
        Flujo:
        1. Genera timestamp unico
        2. Construye diccionario con todos los datos
        3. Serializa a JSON con formato legible
        4. Guarda en directorio de busquedas
        """
        
        # 1: Generar timestamp unico
        # Formato: YYYYMMDD_HHMMSS (Año Mes Dia _ Hora Minuto Segundo)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 2: Construir nombre de archivo
        ruta_archivo = f"{self.directorio_base}/busquedas/busqueda_{timestamp}.json"
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        
        # 3: Preparar datos a guardar
        datos_guardar = {
            "timestamp": timestamp,
            "consulta": consulta_info or {},  
            "resultados": resultados,
            "total_resultados": len(resultados)
        }
        
        # PASO 4: Serializar y guardar
        with open(ruta_archivo, 'w') as f:
            json.dump(datos_guardar, f, indent=2)
        
        return ruta_archivo
    
    def cargar_ultima_busqueda(self):
        """
        Flujo:
        1. Lista todos los archivos JSON en directorio de busquedas
        2. Identifica el mas reciente por nombre (ordenamiento lexicografico)
        3. Carga y retorna el contenido
        """
        
        # Ruta del directorio de busquedas
        directorio_busquedas = f"{self.directorio_base}/busquedas"
        if not os.path.exists(directorio_busquedas):
            return None
        
        # 1: Listar todos los archivos JSON
        archivos = [f for f in os.listdir(directorio_busquedas) if f.endswith('.json')]
        if not archivos:
            return None
        
        # 2: Obtener el archivo mas reciente
        archivo_reciente = max(archivos)
        ruta_completa = os.path.join(directorio_busquedas, archivo_reciente)
        
        # 3: Cargar y retornar contenido
        with open(ruta_completa, 'r') as f:
            return json.load(f)