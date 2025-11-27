from flask import request, jsonify
from src.core.fusion_indexacion import SistemaFusionIndexacion

sistema_indexado = True

def configurar_rutas_indexacion(app):
    @app.route('/api/indexar-sistema', methods=['POST'])
    def indexar_sistema_completo():
        try:
            global sistema_indexado
            
            # Ejecutar indexación completa
            sistema_indexacion = SistemaFusionIndexacion(
                ruta_vectores='datos/caracteristicas/vectores_caracteristicas.npy',
                ruta_json='datos/caracteristicas/caracteristicas_completas.json', 
                directorio_salida='datos/indices'
            )
            
            exito = sistema_indexacion.ejecutar_fase_completa()
            
            if exito:
                sistema_indexado = True
                stats = sistema_indexacion.obtener_estadisticas()
                
                return jsonify({
                    "exito": True,
                    "mensaje": "Sistema indexado correctamente",
                    "estadisticas": stats
                })
            else:
                return jsonify({"error": "Error en la indexación del sistema"}), 500
                
        except Exception as e:
            return jsonify({"error": f"Error en indexación: {str(e)}"}), 500

    @app.route('/api/estado-sistema', methods=['GET'])
    def obtener_estado_sistema():
        from src.core.busqueda_similitud import SistemaBusqueda
        sistema_busqueda = SistemaBusqueda()
        stats = sistema_busqueda.obtener_estadisticas() if sistema_indexado else {}
        
        return jsonify({
            "sistema_indexado": sistema_indexado,
            "estadisticas": stats,
            "endpoints_disponibles": [
                "/api/salud",
                "/api/preprocesar", 
                "/api/extraer-caracteristicas",
                "/api/indexar-sistema",
                "/api/buscar-similares",
                "/api/estado-sistema"
            ]
        })