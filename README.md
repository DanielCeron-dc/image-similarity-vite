
# SCBIR para Huellas Dactilares Latentes

## Descripción del Proyecto

Sistema de Recuperación de Imágenes por Contenido (SCBIR) especializado en huellas dactilares latentes que complementa los sistemas AFIS tradicionales mediante similitud visual global usando descriptores Gabor, LBP y HOG.

**Autores:**
- Daniel Cerón Bacares
- Andrea Realpe Muñoz

**Asignatura:** Electiva CBIR  
**Docente:** Sandra Roa  
**Universidad:** Universidad del Cauca - Facultad de Ingeniería Electrónica y Telecomunicaciones  
**Fecha:** Noviembre 2025

## Objetivo

Desarrollar un sistema SCBIR que permita la recuperación de huellas dactilares similares basándose en características de textura y patrón global, operando como herramienta complementaria para casos donde los sistemas AFIS tradicionales fallan con huellas latentes de baja calidad.

## Instalación y Configuración

### Backend

1. **Clonar el repositorio**
git clone <repository-url>
cd scbir-huellas/backend


2. **Instalar dependencias**
pip install -r requisitos.txt


3. **Preparar datos del sistema**
   
Terminal 1 - Descargar y preparar datos
python scripts/descargar_datos.py


Terminal 2 - Indexar sistema
python scripts/indexar_sistema.py


4. **Ejecutar servidor**
python app.py


### Frontend

1. **Navegar al directorio frontend**
cd frontend


2. **Instalar dependencias**
npm install


3. **Ejecutar en modo desarrollo**
npm run dev


## API Endpoints

### Backend (http://localhost:5000)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /api/salud | Verificar estado del servidor |
| GET | /api/estado-sistema | Estado del sistema indexado |
| POST | /api/preprocesar | Preprocesar imagen de huella |
| POST | /api/extraer-caracteristicas | Extraer características de imagen |
| POST | /api/indexar-sistema | Indexar sistema completo |
| POST | /api/buscar-similares | Buscar imágenes similares |
| GET | /api/imagen/<nombre> | Servir imagen procesada |

## Descriptores Implementados

**Filtros de Gabor**
- Captura textura orientada de crestas papilares
- Parámetros: 4 orientaciones, 2 frecuencias
- 16 características por imagen

**LBP (Local Binary Patterns)**
- Detecta micro-textura local
- Invariante a iluminación
- 26 características por imagen

**HOG (Histogram of Oriented Gradients)**
- Captura estructura global y patrones
- 1764 características por imagen

## Pipeline de Procesamiento

**Preprocesamiento**
- Redimensionamiento a 300×300 píxeles
- Ecualización CLAHE para mejora de contraste
- Filtrado de mediana para reducción de ruido

**Extracción de Características**
- Fusión de descriptores: Gabor + LBP + HOG
- Vector final: 1806 dimensiones

**Indexación**
- Normalización Min-Max [0,1]
- Índice FAISS con distancia Euclidiana L2
- Búsqueda eficiente de vecinos más cercanos

**Búsqueda por Similitud**
- Métrica exponencial: similitud = exp(-distancia / 20)
- Ranking por similitud descendente
- Precisión garantizada: consulta a sí misma = 1.0

## Resultados

**Dataset Utilizado**
- Fuente: FVC (Fingerprint Verification Competition)
- Ediciones: FVC2000, FVC2002, FVC2004
- Total imágenes: 960 huellas dactilares
- Características: Múltiples sensores, condiciones variables

**Métricas de Rendimiento**
- Precisión exacta: Consulta a sí misma = 1.000
- Tiempo de búsqueda: < 100ms por consulta
- Escalabilidad: 960 imágenes indexadas
- Consistencia: Normalización reproducible

## Pruebas y Validación

**Pruebas del Sistema**
Probar sistema de búsqueda
python scripts/probar_busqueda.py

Verificar estado del sistema
curl http://localhost:5000/api/estado-sistema
