from flask import send_file, jsonify
import os
import base64


def configurar_rutas_imagenes(app):

    @app.route('/api/imagen/<nombre_archivo>', methods=['GET'])
    def obtener_imagen(nombre_archivo):
        """
        Retorna una imagen preprocesada por su nombre de archivo.
        
        Flujo:
        1. Valida que el nombre de archivo sea seguro
        2. Busca la imagen en el directorio de procesadas
        3. Retorna la imagen como archivo
        """
        try:
            # Validacion de seguridad: evitar path traversal
            # Elimina caracteres peligrosos como ../ o /
            nombre_archivo = os.path.basename(nombre_archivo)
            
            # Construir ruta completa
            ruta_imagen = os.path.join('datos/procesadas', nombre_archivo)
            
            # Verificar que el archivo existe
            if not os.path.exists(ruta_imagen):
                return jsonify({"error": f"Imagen no encontrada: {nombre_archivo}"}), 404
            
            # Retornar imagen como archivo
            # mimetype='image/png': indica al navegador que es una imagen PNG
            return send_file(ruta_imagen, mimetype='image/png')
            
        except Exception as e:
            return jsonify({"error": f"Error al obtener imagen: {str(e)}"}), 500
    
    
    @app.route('/api/imagen-base64/<nombre_archivo>', methods=['GET'])
    def obtener_imagen_base64(nombre_archivo):

        try:
            # Validacion de seguridad
            nombre_archivo = os.path.basename(nombre_archivo)
            ruta_imagen = os.path.join('datos/procesadas', nombre_archivo)
            
            if not os.path.exists(ruta_imagen):
                return jsonify({"error": f"Imagen no encontrada: {nombre_archivo}"}), 404
            
            # Leer imagen y codificar en base64
            with open(ruta_imagen, 'rb') as f:
                imagen_bytes = f.read()
                imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
            
            return jsonify({
                "exito": True,
                "archivo": nombre_archivo,
                "imagen_base64": imagen_base64
            })
            
        except Exception as e:
            return jsonify({"error": f"Error al obtener imagen: {str(e)}"}), 500
    
    
    @app.route('/api/imagenes-lote', methods=['POST'])
    def obtener_imagenes_lote(self):
        """
        Retorna multiples imagenes en base64 en una sola peticion.
        Optimizacion para evitar N peticiones HTTP separadas.
        """
        try:
            from flask import request
            datos = request.get_json()
            archivos = datos.get('archivos', [])
            
            if not archivos:
                return jsonify({"error": "No se proporcionaron archivos"}), 400
            
            imagenes = []
            for nombre_archivo in archivos:
                # Validacion de seguridad
                nombre_archivo = os.path.basename(nombre_archivo)
                ruta_imagen = os.path.join('datos/procesadas', nombre_archivo)
                
                if os.path.exists(ruta_imagen):
                    with open(ruta_imagen, 'rb') as f:
                        imagen_bytes = f.read()
                        imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
                    
                    imagenes.append({
                        "archivo": nombre_archivo,
                        "imagen_base64": imagen_base64,
                        "encontrada": True
                    })
                else:
                    imagenes.append({
                        "archivo": nombre_archivo,
                        "encontrada": False
                    })
            
            return jsonify({
                "exito": True,
                "total": len(imagenes),
                "imagenes": imagenes
            })
            
        except Exception as e:
            return jsonify({"error": f"Error al obtener imagenes: {str(e)}"}), 500