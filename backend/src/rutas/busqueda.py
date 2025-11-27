from flask import request, jsonify, current_app
import base64
import cv2
import numpy as np
from src.core.preprocesamiento import PreprocesadorUnificado
from src.core.extraccion_caracteristicas import ExtractorMasivo
from src.core.busqueda_similitud import SistemaBusqueda

preprocesador = PreprocesadorUnificado()
extractor = ExtractorMasivo()
sistema_busqueda = SistemaBusqueda()

def configurar_rutas_busqueda(app):
    @app.route('/api/buscar-similares', methods=['POST'])
    def buscar_imagenes_similares():
        try:
            if not sistema_busqueda.cargado:
                return jsonify({"error": "El sistema no está indexado. Ejecuta /api/indexar-sistema primero"}), 400
        
            datos = request.get_json()
            
            if 'vector_caracteristicas' in datos:
                # Busqueda por vector existente
                vector_consulta = datos['vector_caracteristicas']
                resultados = sistema_busqueda.buscar_por_vector(vector_consulta)
                
            elif 'imagen' in datos:
                # Busqueda por imagen nueva
                imagen_codificada = datos['imagen']
                
                # Decodificar y preprocesar
                imagen_bytes = base64.b64decode(imagen_codificada)
                imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
                imagen = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)
                imagen_procesada = preprocesador.preprocesar_imagen(imagen)
                
                # Extraer características y buscar
                resultados = sistema_busqueda.buscar_por_imagen(imagen_procesada, extractor)
                
            else:
                return jsonify({"error": "Se requiere 'vector_caracteristicas' o 'imagen'"}), 400
            
            return jsonify({
                "exito": True,
                "resultados": resultados,
                "total_resultados": len(resultados)
            })
            
        except Exception as e:
            return jsonify({"error": f"Error en busqueda: {str(e)}"}), 500

    @app.route('/api/extraer-caracteristicas', methods=['POST'])
    def extraer_caracteristicas():
        try:
            datos = request.get_json()
            if 'imagen' not in datos:
                return jsonify({"error": "No se proporcionó imagen"}), 400
            
            imagen_codificada = datos['imagen']
            
            # Decodificar y preprocesar
            imagen_bytes = base64.b64decode(imagen_codificada)
            imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
            imagen = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)
            
            if imagen is None:
                return jsonify({"error": "No se pudo decodificar la imagen"}), 400
                
            imagen_procesada = preprocesador.preprocesar_imagen(imagen)
            
            # Extraer características
            resultado = extractor.extraer_imagen(imagen_procesada)
            
            return jsonify({
                "exito": True,
                "caracteristicas": resultado['caracteristicas'],
                "vector_completo": resultado['vector_completo'],
                "dimension_total": len(resultado['vector_completo']),
                "detalle_descriptores": {
                    "LBP": len(resultado['caracteristicas']['LBP']),
                    "HOG": len(resultado['caracteristicas']['HOG']),
                    "GABOR": len(resultado['caracteristicas']['GABOR'])
                }
            })
            
        except Exception as e:
            return jsonify({"error": f"Error en extracción: {str(e)}"}), 500