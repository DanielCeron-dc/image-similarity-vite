"""
Sistema de fusion de caracteristicas e indexacion con FAISS.
Normaliza vectores y construye indices para busqueda eficiente.
"""

import os
import numpy as np
import json
import faiss
import pickle
from tqdm import tqdm
import time

class SistemaFusionIndexacion:
    """
    - Cargar vectores de caracteristicas ya extraidos
    - Normalizar datos (Min-Max scaling)
    - Construir indice FAISS para busqueda rapida
    - Mantener mapeo entre indices FAISS y nombres de archivo
    - Persistir todo en disco
    
    Attributes:
        ruta_vectores (str): Ruta al archivo .npy con vectores
        ruta_json (str): Ruta al archivo JSON con metadatos
        directorio_salida (str): Directorio para guardar indices
        vectores_raw (np.ndarray): Vectores originales sin normalizar
        vectores_normalizados (np.ndarray): Vectores normalizados [0,1]
        metadatos (list): Lista de diccionarios con info de cada imagen
        indice_faiss (faiss.Index): Indice FAISS para busqueda
        mapeo_indices (dict): Mapeo {indice_faiss: nombre_archivo}
        scaler (dict): Parametros de normalizacion (min, max, range)
    """
    
    def __init__(self, 
                 ruta_vectores='datos/caracteristicas/vectores_caracteristicas.npy',
                 ruta_json='datos/caracteristicas/caracteristicas_completas.json', 
                 directorio_salida='datos/indices'):

        self.ruta_vectores = ruta_vectores
        self.ruta_json = ruta_json
        self.directorio_salida = directorio_salida
        
        # Inicializar estructuras de datos vacias
        self.vectores_raw = None
        self.vectores_normalizados = None
        self.metadatos = None
        self.indice_faiss = None
        self.mapeo_indices = {}
        self.scaler = {}  
        
        os.makedirs(self.directorio_salida, exist_ok=True)
    
    def cargar_datos(self):
        """
        Flujo:
        1. Carga matriz NumPy con vectores (shape: [N_imagenes, 1806])
        2. Limpia valores invalidos (inf, nan)
        3. Carga JSON con metadatos (nombres de archivo, caracteristicas por descriptor)
        4. Verifica consistencia entre vectores y metadatos
        """
        
        print("FASE 1: CARGA DE DATOS Y LIMPIEZA")
        # 1: Cargar vectores numericos
        if self.ruta_vectores and os.path.exists(self.ruta_vectores):
            print(f"Cargando vectores desde: {self.ruta_vectores}")
            self.vectores_raw = np.load(self.ruta_vectores)

            print("Aplicando limpieza de vectores...")
            self.vectores_raw = np.nan_to_num(
                self.vectores_raw, 
                nan=0.0,    
                posinf=1.0,  
                neginf=0.0    
            )
            
            print(f"Vectores cargados: {self.vectores_raw.shape}")
            print(f"Rango original: [{np.min(self.vectores_raw):.3f}, {np.max(self.vectores_raw):.3f}]")
        else:
            print("ERROR: No se encontraron vectores pre-calculados")
            return False
        
        # 2: Cargar metadatos
        if self.ruta_json and os.path.exists(self.ruta_json):
            print(f"Cargando metadatos desde: {self.ruta_json}")
            with open(self.ruta_json, 'r') as f:
                self.metadatos = json.load(f)
        else:
            print("ERROR: No se encontraron metadatos pre-calculados")
            return False
        
        #3: Verificar consistencia
        # El numero de vectores debe coincidir con el numero de metadatos
        if len(self.vectores_raw) != len(self.metadatos):
            print(f"ERROR: Inconsistencia - {len(self.vectores_raw)} vectores vs {len(self.metadatos)} metadatos")
            return False
        
        print(f"Carga exitosa: {len(self.vectores_raw)} imagenes procesadas")
        return True
    
    def normalizar_min_max(self):
        """
        Aplica normalizacion Min-Max para escalar caracteristicas al rango [0,1].
        
        Formula: X_norm = (X - X_min) / (X_max - X_min)
        
        Flujo:
        1. Calcula min y max por cada caracteristica (columna)
        2. Calcula range = max - min
        3. Aplica transformacion lineal
        4. Maneja casos especiales (caracteristicas constantes)
        
        Razon:
            - FAISS usa distancia Euclidiana L2
            - Sin normalizacion, caracteristicas con mayor magnitud dominan la distancia
            - Min-Max preserva relaciones de distancia relativa
            - Rango [0,1] evita overflow numerico
        """
        
        print("FASE 2: NORMALIZACION MIN-MAX")
        if self.vectores_raw is None:
            print("ERROR: Primero debes cargar los datos")
            return False
        
        # PASO 1: Calcular parametros de normalizacion
        # axis=0: calcula estadisticas por columna (por caracteristica)
        print("Calculando parametros de normalizacion...")
        self.scaler['min'] = np.min(self.vectores_raw, axis=0)
        self.scaler['max'] = np.max(self.vectores_raw, axis=0)
        self.scaler['range'] = self.scaler['max'] - self.scaler['min']
        
        # PASO 2: Manejar caracteristicas constantes
        # Si max == min para alguna caracteristica, range = 0
        # Division por cero -> inf/nan -> Corrupcion del indice
        # Solucion: Establecer range = 1.0 (la caracteristica permanece constante)
        self.scaler['range'][self.scaler['range'] == 0] = 1.0
        
        # PASO 3: Aplicar normalizacion Min-Max
        # Broadcasting de NumPy: resta y division se aplican elemento por elemento
        print("Aplicando normalizacion Min-Max...")
        self.vectores_normalizados = (self.vectores_raw - self.scaler['min']) / self.scaler['range']
        
        # Verificar resultados
        print(f"Rango normalizado: [{np.min(self.vectores_normalizados):.3f}, {np.max(self.vectores_normalizados):.3f}]")
        print("Normalizacion completada - Vectores en rango [0,1]")
        return True
    
    def construir_indice_faiss(self):
        """
        Flujo:
        1. Crea indice plano con distancia L2
        2. Convierte vectores a float32 (requerido por FAISS)
        3. Agrega vectores al indice
        

        Alternativas de indices:
        - IndexFlatL2: Exacto, O(n), mejor precision
        - IndexIVFFlat: Aproximado, O(log n), mas rapido
        - IndexHNSWFlat: Aproximado, mejor balance precision/velocidad
        """

        print("FASE 3: CONSTRUCCION INDICE FAISS")
        if self.vectores_normalizados is None:
            print("ERROR: Primero debes normalizar los datos")
            return False
        
        # Obtener dimensiones
        dimension = self.vectores_normalizados.shape[1]  # 1806
        num_vectores = self.vectores_normalizados.shape[0]  # 960
        
        print(f"Dimension: {dimension}, Vectores: {num_vectores}")
        
        # 1: Crear indice FAISS
        self.indice_faiss = faiss.IndexFlatL2(dimension)
        
        # 2: Convertir a float32
        print("Agregando vectores al indice FAISS...")
        vectores_float32 = self.vectores_normalizados.astype('float32')
        
        # 3: Agregar vectores al indice
        inicio = time.time()
        self.indice_faiss.add(vectores_float32)
        tiempo = time.time() - inicio
        
        print(f"Indice construido: {self.indice_faiss.ntotal} vectores")
        print(f"Tiempo de construccion: {tiempo:.2f}s")
        
        return True
    
    def crear_mapeo_indices(self):
        """
        Crea mapeo bidireccional entre indices FAISS y nombres de archivo.
        
        Razon:
        - FAISS asigna indices enteros secuenciales (0, 1, 2, ...)
        - Necesitamos recuperar el nombre de archivo original
        - Mapeo: {indice_faiss: nombre_archivo}
        
        Flujo:
        1. Itera sobre metadatos en orden
        2. Crea entrada {indice: archivo} para cada imagen
        """

        print("FASE 4: CREACION MAPEO INDICE-IMAGEN")
        if self.metadatos is None:
            print("ERROR: Primero debes cargar los metadatos")
            return False
        
        # Crear mapeo: {indice_entero: nombre_archivo}
        for idx, item in enumerate(self.metadatos):
            self.mapeo_indices[idx] = item['archivo']
        
        print(f"Mapeo creado: {len(self.mapeo_indices)} entradas")
        return True
    
    def guardar_indice(self):
        """
        Archivos generados:
        1. faiss_index.bin: Indice FAISS serializado (busqueda rapida)
        2. mapeo_indices.json: Mapeo indice-archivo (recuperacion de nombres)
        3. scaler.pkl: Parametros de normalizacion (para consultas futuras)
        
        Flujo:
        1. Serializa indice FAISS en formato binario
        2. Guarda mapeo como JSON (legible por humanos)
        3. Guarda scaler con pickle (preserva tipos NumPy)
        """

        print("FASE 5: PERSISTENCIA EN DISCO")
        
        if self.indice_faiss is None:
            print("ERROR: Primero debes construir el indice")
            return False
        
        # 1: Guardar indice FAISS
        ruta_indice = os.path.join(self.directorio_salida, 'faiss_index.bin')
        faiss.write_index(self.indice_faiss, ruta_indice)
        print(f"Indice FAISS guardado: {ruta_indice}")
        
        # 2: Guardar mapeo indices
        ruta_mapeo = os.path.join(self.directorio_salida, 'mapeo_indices.json')
        with open(ruta_mapeo, 'w') as f:
            json.dump(self.mapeo_indices, f, indent=2)
        print(f"Mapeo guardado: {ruta_mapeo}")
        
        # 3: Guardar parametros de normalizacion
        ruta_scaler = os.path.join(self.directorio_salida, 'scaler.pkl')
        with open(ruta_scaler, 'wb') as f:
            pickle.dump(self.scaler, f)
        print("Parametros de normalizacion guardados")
        
        print("Persistencia completada, Sistema listo para busquedas")
        return True
    
    def ejecutar_fase_completa(self):
        """
        Ejecuta todos los pasos de indexacion en secuencia.
        
        Pipeline completo:
        1. Cargar datos (vectores + metadatos)
        2. Normalizar (Min-Max scaling)
        3. Construir indice (FAISS)
        4. Crear mapeo (indice -> archivo)
        5. Guardar todo (persistencia)
        """

        print("INICIANDO FASE COMPLETA: FUSION E INDEXACION")

        pasos = [
            ("Carga de datos", self.cargar_datos),
            ("Normalizacion Min-Max", self.normalizar_min_max),
            ("Construccion indice FAISS", self.construir_indice_faiss),
            ("Mapeo indices", self.crear_mapeo_indices),
            ("Persistencia en disco", self.guardar_indice)
        ]
        
        for nombre_paso, metodo in pasos:
            print(f"\nEjecutando: {nombre_paso}")
            if not metodo():
                print(f"ERROR: Fase interrumpida en: {nombre_paso}")
                return False
        
        return True
    
    def obtener_estadisticas(self):
        if self.indice_faiss is None:
            return {"estado": "No indexado"}
        
        return {
            'total_vectores': self.indice_faiss.ntotal,
            'dimension': self.indice_faiss.d,
            'tipo_indice': 'IndexFlatL2',
            'mapeo_completo': len(self.mapeo_indices) == self.indice_faiss.ntotal,
            'normalizacion': 'Min-Max [0,1]',
            'metrica_similitud': 'Exponencial con escala 2.0'
        }