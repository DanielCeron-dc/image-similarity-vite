"""
Descarga automatica de datasets FVC (Fingerprint Verification Competition).
Descarga y extrae bases de datos publicas de huellas dactilares.
"""

import os
import urllib.request
import zipfile
from tqdm import tqdm


class DescargadorFVC:
    
    def __init__(self):
        # Patron de URL: http://bias.csr.unibo.it/fvc{AÃ'O}/downloads/DB{NUM}_B.zip
        # {AÃ'O}: 2000, 2002, 2004
        # {NUM}: 1, 2, 3, 4
        # _B: Indica "Base" (version completa del dataset)
        self.url_base = "http://bias.csr.unibo.it/fvc{}/downloads/DB{}_B.zip"        
        self.directorio_base = 'datos/datasets'
        os.makedirs(self.directorio_base, exist_ok=True)

        # Cada tupla: (año, numero_db)
        self.configuracion_datasets = [
            # FVC2000: 4 bases de datos
            (2000, 1), (2000, 2), (2000, 3), (2000, 4),
            # FVC2002: 4 bases de datos
            (2002, 1), (2002, 2), (2002, 3), (2002, 4),
            # FVC2004: 4 bases de datos
            (2004, 1), (2004, 2), (2004, 3), (2004, 4)
        ]

    def descargar_y_extraer(self, año, db_num):
        """
        Flujo:
        1. Construye URL del archivo ZIP
        2. Descarga con progreso visual
        3. Extrae contenido a directorio especifico
        4. Elimina archivo ZIP temporal
        """
        
        # 1: Construir nombres y rutas
        url = self.url_base.format(año, db_num)
        nombre_zip = f'FVC{año}_DB{db_num}_B.zip'
        ruta_extraccion = os.path.join(self.directorio_base, f'FVC{año}_DB{db_num}')

        print(f"\nDescargando dataset FVC{año} DB{db_num}: ")

        try:
            # 2: Descargar archivo ZIP con barra de progreso
            def mostrar_progreso(bloque_num, bloque_tam, tam_total):
                """
                Callback para mostrar progreso de descarga.
                
                Args:
                    bloque_num (int): Numero de bloque descargado
                    bloque_tam (int): Tamaño de cada bloque en bytes
                    tam_total (int): Tamaño total del archivo en bytes
                """
                if tam_total > 0:
                    # Calcular porcentaje descargado
                    porcentaje = min(1.0, (bloque_num * bloque_tam) / tam_total)
                    # Mostrar en misma linea (carriage return \r)
                    print(f"\r{porcentaje:.1%}", end="", flush=True)

            urllib.request.urlretrieve(url, nombre_zip, mostrar_progreso)
            print()  # Nueva linea despues del progreso

            # 3: Extraer contenido del ZIP
            with zipfile.ZipFile(nombre_zip, 'r') as zip_ref:
                # extractall descomprime todos los archivos al directorio destino
                zip_ref.extractall(ruta_extraccion)

            # 4: Limpiar archivo ZIP temporal
            os.remove(nombre_zip)
            
            print(f"Dataset FVC{año}_DB{db_num} extraido exitosamente")
            return True

        except Exception as e:
            print(f"Error con {nombre_zip}: {e}")
            return False

    def descargar_todos(self):
        print("Inicio de descarga de todos los datasets FVC...")
        exitosos = 0

        for año, db_num in tqdm(self.configuracion_datasets, desc="Descargando datasets"):
            if self.descargar_y_extraer(año, db_num):
                exitosos += 1

        print(f"Descargados: {exitosos}/{len(self.configuracion_datasets)} datasets.")
        return exitosos

    def obtener_ruta_dataset(self):
        return self.directorio_base