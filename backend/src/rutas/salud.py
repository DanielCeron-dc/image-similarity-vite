from flask import jsonify

def configurar_rutas_salud(app):
    @app.route('/api/salud', methods=['GET'])
    def verificar_salud():
        return jsonify({
            "estado": "Sistema SCBIR funcionando correctamente",
        })