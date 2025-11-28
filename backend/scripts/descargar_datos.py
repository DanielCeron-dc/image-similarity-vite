import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.core.descargador_dataset import DescargadorFVC
from src.core.preprocesamiento import PreprocesadorUnificado
from src.core.extraccion_caracteristicas import ExtractorMasivo

def main():
    print("INICIANDO DESCARGA Y PREPARACIÓN DE DATOS")

    # Crear directorio de características si no existe
    os.makedirs('datos/caracteristicas', exist_ok=True)
    
    print("\1: Descargando datasets FVC...")
    descargador = DescargadorFVC()
    exitosos = descargador.descargar_todos()
    
    if exitosos == 0:
        print("No se pudieron descargar los datasets")
        return
    
    print("\2: Preprocesando imágenes...")
    preprocesador = PreprocesadorUnificado()
    ruta_dataset = descargador.obtener_ruta_dataset()
    ruta_salida = 'datos/procesadas'
    
    total_procesadas = preprocesador.preprocesar_directorio(ruta_dataset, ruta_salida)
    
    if total_procesadas == 0:
        print("No se pudieron preprocesar imágenes")
        return
    
    print("\3: Extrayendo características...")
    extractor = ExtractorMasivo()
    
    resultados, vectores = extractor.extraer_directorio(
        directorio_imagenes=ruta_salida,
        ruta_salida_json='datos/caracteristicas/caracteristicas_completas.json',
        ruta_salida_vectores='datos/caracteristicas/vectores_caracteristicas.npy'
    )
    
    print(f"\nPROCESO COMPLETADO:")
    print(f"Datasets descargados: {exitosos}")
    print(f"Imágenes preprocesadas: {total_procesadas}")
    print(f"Características extraídas: {len(resultados)}")

if __name__ == "__main__":
    main()