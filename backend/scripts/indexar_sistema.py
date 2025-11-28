"""
Script para indexar el sistema SCBIR completo
"""
import os
import sys
import requests
import json

API_BASE_URL = os.getenv("API_BASE_URL") or os.getenv("BACKEND_URL") or "http://localhost:5001"

# Agregar el directorio src al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def indexar_sistema():
    """
    Función que ejecuta la indexación del sistema a través de la API
    """
    print("Indexando sistema SCBIR...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/indexar-sistema", json={})
        
        if response.status_code == 200:
            resultado = response.json()
            print("Sistema indexado correctamente!")
            print(f"Estadísticas: {json.dumps(resultado['estadisticas'], indent=2)}")
        else:
            print(f"Error: {response.json()}")
            
    except Exception as e:
        print(f"No se pudo conectar al servidor: {e}")
        print("Asegúrate de que el servidor esté corriendo en otra terminal")

if __name__ == "__main__":
    indexar_sistema()
