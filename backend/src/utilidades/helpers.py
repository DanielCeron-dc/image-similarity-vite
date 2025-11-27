import os
import json
import numpy as np

def generar_resumen_sistema(directorio_base='datos'):

    directorios = [
        'datos/datasets',
        'datos/procesadas', 
        'datos/indices',
        'datos/caracteristicas'
    ]
    
    estadisticas = {}
    
    for directorio in directorios:
        existe = os.path.exists(directorio)
        cantidad = "No existe"
        
        if existe:
            if 'datasets' in directorio:
                subdirs = [d for d in os.listdir(directorio) if os.path.isdir(os.path.join(directorio, d))]
                cantidad = f"{len(subdirs)} datasets"
            elif 'procesadas' in directorio:
                archivos = [f for f in os.listdir(directorio) if f.endswith('.png')]
                cantidad = f"{len(archivos)} imagenes"
            elif 'indices' in directorio:
                archivos = os.listdir(directorio)
                cantidad = f"{len(archivos)} archivos"
            elif 'caracteristicas' in directorio:
                archivos = [f for f in os.listdir(directorio) if f.endswith('.json') or f.endswith('.npy')]
                cantidad = f"{len(archivos)} archivos"
        
        print(f"Directorio {directorio}: {cantidad}")
        estadisticas[directorio] = cantidad
        
    return estadisticas

def verificar_archivos_indices(directorio_indices='datos/indices'):
    archivos_requeridos = ['faiss_index.bin', 'mapeo_indices.json', 'scaler.pkl']
    
    print("\nVerificando archivos de indice...")
    
    for archivo in archivos_requeridos:
        ruta = os.path.join(directorio_indices, archivo)
        if os.path.exists(ruta):
            tamaño = os.path.getsize(ruta) / 1024  # KB
            print(f"   Archivo {archivo}: {tamaño:.2f} KB - EXISTE")
        else:
            print(f"   Archivo {archivo}: NO ENCONTRADO")
    
    # Verificar consistencia
    if all(os.path.exists(os.path.join(directorio_indices, a)) for a in archivos_requeridos):
        print("   Todos los archivos de indice estan presentes")
        return True
    else:
        print("   Faltan archivos de indice. El sistema necesita re-indexacion.")
        return False