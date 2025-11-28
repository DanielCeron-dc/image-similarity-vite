"""
Servidor principal del sistema SCBIR para huellas dactilares
"""
from flask import Flask
from flask_cors import CORS
import os

# Crear aplicación Flask
app = Flask(__name__)
# Permitir CORS para todos los orígenes (necesario para el front)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configurar rutas
from src.rutas.salud import configurar_rutas_salud
from src.rutas.preprocesamiento import configurar_rutas_preprocesamiento
from src.rutas.busqueda import configurar_rutas_busqueda
from src.rutas.indexacion import configurar_rutas_indexacion
from src.rutas.imagenes import configurar_rutas_imagenes

configurar_rutas_salud(app)
configurar_rutas_preprocesamiento(app)
configurar_rutas_busqueda(app)
configurar_rutas_indexacion(app)
configurar_rutas_imagenes(app)

# Crear directorios necesarios
def crear_directorios():
    """Crea los directorios necesarios para el sistema"""
    directorios = [
        'datos/datasets',
        'datos/procesadas',
        'datos/caracteristicas',
        'datos/indices',
        'datos/busquedas'
    ]
    
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)

if __name__ == '__main__':
    crear_directorios()
    print("Iniciando Sistema SCBIR para Huellas...")
    print("Directorios creados: datos/datasets, datos/procesadas, datos/caracteristicas, datos/indices")
    print("Servidor disponible en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
