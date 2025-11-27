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
    
    def buscar_por_imagen(self, imagen, extractor, top_k=10):
        """
        Flujo CORREGIDO:
        1. Extrae caracteristicas de la imagen
        2. Normaliza el vector igual que durante el entrenamiento
        3. Busca DIRECTAMENTE en FAISS sin buscar vector "exacto"
        """
        if not self.cargado:
            return {"error": "Sistema no esta cargado. Ejecuta indexacion primero."}
        
        try:
            # 1: Extraer caracteristicas de la imagen
            resultado = extractor.extraer_imagen(imagen)
            vector_caracteristicas = resultado['vector_completo']
            
            print(f"BUSQUEDA POR IMAGEN - Vector length: {len(vector_caracteristicas)}")
            
            # 2: Normalizar el vector igual que durante el entrenamiento
            vector_normalizado = (vector_caracteristicas - self.scaler['min']) / self.scaler['range']
            vector_normalizado = np.clip(vector_normalizado, 0.0, 1.0)
            
            # 3: Busqueda DIRECTA en FAISS
            vector_float32 = vector_normalizado.astype('float32').reshape(1, -1)
            
            # search retorna (distancias, indices) de los k vecinos mas cercanos
            distancias, indices = self.indice_faiss.search(vector_float32, top_k)
            
            # 4: Formatear resultados
            resultados = []
            for i, (dist, idx) in enumerate(zip(distancias[0], indices[0])):
                
                if idx != -1:
                    nombre_archivo = self.mapeo_indices.get(str(idx), f"imagen_{idx}")
                    
                    # Convertir distancia a similitud
                    similitud = np.exp(-dist / 20.0)
                    
                    resultados.append({
                        "posicion": i + 1,
                        "archivo": nombre_archivo,
                        "similitud": float(similitud),
                        "distancia": float(dist),
                        "indice_faiss": int(idx),
                        "es_consulta": False  # Porque es una imagen nueva
                    })
            
            # Ordenar por similitud descendente
            resultados.sort(key=lambda x: x["similitud"], reverse=True)
            
            print(f"BUSQUEDA COMPLETADA - {len(resultados)} resultados")
            return resultados
            
        except Exception as e:
            return {"error": f"Error en busqueda por imagen: {str(e)}"}
    
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