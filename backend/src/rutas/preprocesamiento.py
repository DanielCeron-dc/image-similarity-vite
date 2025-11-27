from flask import request, jsonify
import base64
import cv2
import numpy as np
from src.core.preprocesamiento import PreprocesadorUnificado

preprocesador = PreprocesadorUnificado()

def configurar_rutas_preprocesamiento(app):
    @app.route('/api/preprocesar', methods=['POST'])
    def preprocesar_imagen():
        try:
            datos = request.get_json()
            if 'imagen' not in datos:
                return jsonify({"error": "No se proporcionó imagen"}), 400
            
            imagen_codificada = datos['imagen']
            
            # Decodificar imagen base64
            imagen_bytes = base64.b64decode(imagen_codificada)
            imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
            imagen = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)
            
            if imagen is None:
                return jsonify({"error": "No se pudo decodificar la imagen"}), 400
            
            # Preprocesar imagen
            imagen_procesada = preprocesador.preprocesar_imagen(imagen)
            
            # Codificar resultado
            _, buffer = cv2.imencode('.png', imagen_procesada)
            imagen_procesada_codificada = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                "exito": True,
                "imagen_procesada": imagen_procesada_codificada,
                "dimensiones_originales": f"{imagen.shape[1]}x{imagen.shape[0]}",
                "dimensiones_procesadas": f"{imagen_procesada.shape[1]}x{imagen_procesada.shape[0]}"
            })
            
        except Exception as e:
            return jsonify({"error": f"Error en preprocesamiento: {str(e)}"}), 500