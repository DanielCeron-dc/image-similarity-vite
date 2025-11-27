# Sistema SCBIR para Huellas Dactilares Latentes

Back dek Sistema de Recuperación de Imágenes por Contenido (SCBIR) especializado en huellas dactilares latentes.

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
   ```bash
   pip install -r requisitos.txt
   ```

## Uso

Termianl 1:
python scripts/descargar_datos.py
python app.py

Terminal 2:
python scripts/indexar_sistema.py
python scripts/probar_busqueda.py

## API Endpoints

GET /api/salud - Verificar estado del sistema
POST /api/preprocesar - Preprocesar imagen de huella
POST /api/extraer-caracteristicas - Extraer características
POST /api/indexar-sistema - Indexar sistema completo
POST /api/buscar-similares - Buscar imágenes similares
GET /api/estado-sistema - Estado del sistema indexado
