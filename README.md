# SCBIR para Huellas Dactilares Latentes

## Descripción del Proyecto

Sistema de Recuperación de Imágenes por Contenido (SCBIR) especializado en huellas dactilares latentes que complementa sistemas AFIS tradicionales mediante similitud visual global usando descriptores Gabor, LBP y HOG.

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

### Requisitos
- Python 3.11+ (recomendado)
- Node.js 18+ y npm
- Git

### Backend


1) Crear entorno virtual e instalar dependencias
```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requisitos.txt
```

2) Arranque recomendado (prepara datos e inicia el servidor)
```bash
python run_backend.py # o: python3 run_backend.py
```
- Usa `BACKEND_PORT/PORT/FLASK_RUN_PORT` (por defecto 5001).
- Ejecuta `scripts/setup_inicial.py` si faltan datos/índice; este paso puede tardar por la descarga y procesado del dataset FVC.

3) Alternativa manual
- Preparar datos en un solo paso:
  ```bash
  python scripts/setup_inicial.py
  ```
- O por pasos (dos terminales o secuencial):
  - Terminal 1 – Descargar y preparar datos
    ```bash
    python scripts/descargar_datos.py
    ```
  - Terminal 2 – Indexar sistema
    ```bash
    python scripts/indexar_sistema.py
    ```
- Levantar servidor manualmente
  ```bash
  FLASK_APP=app FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=5001 flask run
  # o: python app.py
  ```
  Backend disponible en `http://localhost:5001`.

### Frontend

1) Navegar al directorio frontend
```bash
cd ../frontend
```

2) Crear archivo de entorno (si no existe)
```bash
echo "VITE_API_BASE_URL=http://localhost:5001" > .env.local
```

3) Instalar dependencias
```bash
npm install
```

4) Ejecutar en modo desarrollo
```bash
npm run dev -- --host --port 5173
```
Abrir `http://localhost:5173` y verificar que el backend esté corriendo en `5001`.

## API Endpoints (http://localhost:5001)

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
- Características: múltiples sensores, condiciones variables

**Métricas de Rendimiento**
- Precisión exacta: consulta a sí misma = 1.000
- Tiempo de búsqueda: < 100 ms por consulta
- Escalabilidad: 960 imágenes indexadas
- Consistencia: normalización reproducible

## Pruebas y Validación

**Pruebas del Sistema**
- Probar sistema de búsqueda
  ```bash
  python scripts/probar_busqueda.py
  ```
- Verificar estado del sistema
  ```bash
  curl http://localhost:5001/api/estado-sistema
  ```
