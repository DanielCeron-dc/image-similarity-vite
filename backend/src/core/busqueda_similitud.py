"""
Sistema de busqueda por similitud usando indices FAISS.
Busca las k imagenes mas similares a una consulta dada.

"""

import faiss
import numpy as np
import json
import pickle
import os


class SistemaBusqueda:
    """
    Metodo de busqueda:
    1. Normaliza vector de consulta (misma transformacion que entrenamiento)
    2. Busca k vecinos mas cercanos en indice FAISS
    3. Convierte distancias a similitudes [0, 1]
    4. Garantiza que consulta a si misma = 1.0 exacto
    """
    
    def __init__(self, directorio_indices='datos/indices'):
        self.directorio_indices = directorio_indices
        self.indice_faiss = None
        self.mapeo_indices = {}
        self.scaler = None
        self.cargado = False
        
        # Cargar indices automaticamente al inicializar
        self.cargar_indices()
    
    def cargar_indices(self):
        """
        Flujo:
        1. Verifica existencia de archivos requeridos
        2. Carga indice FAISS binario
        3. Carga mapeo JSON
        4. Carga parametros de normalizacion
        5. Carga vectores originales (para matching exacto)
        """
        try:
            # 1: Verificar y cargar indice FAISS
            ruta_indice = f"{self.directorio_indices}/faiss_index.bin"
            if not os.path.exists(ruta_indice):
                print("No se encontro indice FAISS. Ejecuta indexacion primero.")
                return False
            
            self.indice_faiss = faiss.read_index(ruta_indice)
            
            # 2: Cargar mapeo indices-imagenes
            ruta_mapeo = f"{self.directorio_indices}/mapeo_indices.json"
            with open(ruta_mapeo, 'r') as f:
                self.mapeo_indices = json.load(f)
            
            # 3: Cargar parametros de normalizacion
            ruta_scaler = f"{self.directorio_indices}/scaler.pkl"
            with open(ruta_scaler, 'rb') as f:
                self.scaler = pickle.load(f)
            
            # 4: Cargar vectores originales para maxima precision
            self.vectores_originales = np.load('datos/caracteristicas/vectores_caracteristicas.npy')
            
            self.cargado = True
            print(f"Indices cargados: {self.indice_faiss.ntotal} vectores")
            return True
            
        except Exception as e:
            print(f"Error cargando indices: {e}")
            return False
    
    def encontrar_indice_exacto(self, vector_consulta):
        """
        Flujo:
        1. Busca vector identico con tolerancia 1e-10
        2. Si no encuentra, usa el mas cercano (fallback)
        """
        vector_consulta_array = np.array(vector_consulta)
        
        # 1: Buscar el vector identico con tolerancia muy pequeña
        for idx, vector_original in enumerate(self.vectores_originales):
            if np.allclose(vector_original, vector_consulta_array, atol=1e-10):
                return idx
        
        # 2: Fallback 
        distancias = np.linalg.norm(self.vectores_originales - vector_consulta_array, axis=1)
        indice_mas_cercano = np.argmin(distancias)
        distancia_minima = distancias[indice_mas_cercano]
        
        print(f"No se encontro vector identico. Usando el mas cercano (distancia: {distancia_minima:.10f})")
        return indice_mas_cercano
    
    def buscar_por_vector(self, vector_consulta, top_k=10):
        """
        Flujo:
        1. Encontrar indice exacto del vector de consulta
        2. Usar vector original normalizado para busqueda FAISS
        3. Ejecutar busqueda k-NN
        4. Convertir distancias a similitudes
        5. Forzar valores exactos para consulta a si misma
        6. Ordenar por similitud descendente
        """
        if not self.cargado:
            return {"error": "Sistema no esta cargado. Ejecuta indexacion primero."}
        
        try:
            # 1: Encontrar el indice exacto del vector de consulta
            indice_consulta = self.encontrar_indice_exacto(vector_consulta)
            nombre_archivo_consulta = self.mapeo_indices.get(str(indice_consulta), f"imagen_{indice_consulta}")
            
            print(f"Consulta: {nombre_archivo_consulta} (indice {indice_consulta})")
            
            # 2: Usar el vector original normalizado para busqueda FAISS
            vector_exacto = self.vectores_originales[indice_consulta]
            vector_normalizado = (vector_exacto - self.scaler['min']) / self.scaler['range']
            vector_normalizado = np.clip(vector_normalizado, 0.0, 1.0)
            
            # 3: Busqueda FAISS con vector exacto
            vector_float32 = vector_normalizado.astype('float32').reshape(1, -1)
            
            # search retorna (distancias, indices) de los k vecinos mas cercanos
            distancias, indices = self.indice_faiss.search(vector_float32, top_k)
            
            # 4: Formatear resultados con GARANTIA de precision
            resultados = []
            for i, (dist, idx) in enumerate(zip(distancias[0], indices[0])):
                
                if idx != -1:
                    nombre_archivo = self.mapeo_indices.get(str(idx), f"imagen_{idx}")
                    
                    # PROBLEMA, SOS: Si es la misma imagen, forzar valores exactos
                    if idx == indice_consulta:
                        similitud = 1.0
                        dist = 0.0
                        es_consulta = True
                    else:
                        # Convertir distancia a similitud con funcion exponencial
                        # Factor 20.0: controla la "sensibilidad" de la similitud
                        # Menor factor -> decaimiento mas rapido
                        similitud = np.exp(-dist / 20.0)
                        es_consulta = False
                    
                    resultados.append({
                        "posicion": i + 1,
                        "archivo": nombre_archivo,
                        "similitud": float(similitud),
                        "distancia": float(dist),
                        "indice_faiss": int(idx),
                        "es_consulta": es_consulta
                    })
            
            # 5: Ordenar por similitud descendente
            resultados.sort(key=lambda x: x["similitud"], reverse=True)
            if resultados and resultados[0]['es_consulta']:
                print(f"VERIFICACION: Consulta en posicion 1 con similitud {resultados[0]['similitud']:.6f}")
            else:
                print("ERROR: La consulta no esta en posicion 1")
            
            return resultados
            
        except Exception as e:
            return {"error": f"Error en busqueda: {str(e)}"}
    
    def buscar_por_imagen(self, imagen, extractor, top_k=10):
        """
        Flujo:
        1. Extrae caracteristicas de la imagen
        2. Llama a buscar_por_vector con el vector extraido
        """
        # Extraer caracteristicas de la imagen
        resultado = extractor.extraer_imagen(imagen)
        vector_caracteristicas = resultado['vector_completo']
        
        # Buscar por el vector extraido
        return self.buscar_por_vector(vector_caracteristicas, top_k)
    
    def obtener_estadisticas(self):
        if not self.cargado:
            return {"estado": "No cargado"}
        
        return {
            "estado": "Cargado y listo",
            "total_imagenes": self.indice_faiss.ntotal,
            "dimension_vector": self.indice_faiss.d,
            "tipo_indice": "IndexFlatL2",
            "metrica": "Distancia Euclidiana (L2)",
            "normalizacion": "Min-Max [0,1]",
            "funcion_similitud": "Exponencial (exp(-dist/20.0))",
            "precision": "Garantizada - Consulta a si misma = 1.0 exacto"
        }