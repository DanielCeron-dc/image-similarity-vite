# Fases del sistema SCBIR

## Fase 1: Preprocesamiento
Ubicación: `backend/src/core/preprocesamiento.py`

Objetivo: estandarizar las huellas de entrada para que los descriptores trabajen sobre imágenes comparables. Convierte a escala de grises, normaliza tamaño y mejora contraste/ruido para estabilizar la extracción posterior.

- **Pipeline** (`PreprocesadorUnificado.preprocesar_imagen`)
```python
if len(imagen.shape) == 3:
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
else:
    gris = imagen

# Redimensionar a tamaño objetivo
gris = cv2.resize(gris, self.tamano_objetivo, interpolation=cv2.INTER_AREA)

# Mejora de contraste y suavizado
mejorada = self.clahe.apply(gris)
suavizada = cv2.medianBlur(mejorada, 3)
```
- **Procesamiento masivo** (`preprocesar_directorio`): recorre recursivamente un directorio (tif/jpg/png), aplica el pipeline y guarda salidas como `proc_XXXXXX.png` en el directorio destino.

Resultado de la fase: huellas preprocesadas y homogéneas (mismo tamaño, contraste mejorado y ruido reducido), listas para extracción de características.

## Fase 2: Extractores (Gabor, LBP, HOG)
Ubicación: `backend/src/core/extraccion_caracteristicas.py`

Objetivo: a partir de una huella preprocesada (escala de grises), generar una representación vectorial unificada combinando tres descriptores complementarios. Cada extractor captura un aspecto específico de la textura papilar y sus resultados se concatenan en `vector_completo`, que será la base para la indexación y la búsqueda.

- **Gabor** (`ExtractorGabor.extraer`)
```python
for frecuencia in self.frecuencias:
    for theta in self.angulos:
        filtro_real, filtro_imag = filters.gabor(
            imagen, frequency=frecuencia, theta=theta
        )
        magnitud = np.sqrt(filtro_real**2 + filtro_imag**2)
        caracteristicas.extend([np.mean(magnitud), np.std(magnitud)])
```
- **LBP** (`ExtractorLBP.extraer`)
```python
lbp = feature.local_binary_pattern(imagen, self.num_puntos, self.radio, method=self.metodo)
(hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, self.num_puntos + 3), range=(0, self.num_puntos + 2))
hist = hist.astype("float")
hist /= hist.sum() if hist.sum() > 0 else len(hist)
```
- **HOG** (`ExtractorHOG.extraer`)
```python
imagen_redimensionada = cv2.resize(imagen, self.tamano_ventana)
caracteristicas = self.hog.compute(imagen_redimensionada)
return caracteristicas.flatten()
```
- **Fusión de descriptores** (`ExtractorMasivo.extraer_imagen`)
```python
caracteristicas = {}
vector_completo = []
for nombre, extractor in self.extractores.items():
    caracteristicas_ext = extractor.extraer(imagen)
    caracteristicas[nombre] = [float(x) for x in caracteristicas_ext.tolist()]
    vector_completo.extend([float(x) for x in caracteristicas_ext])
return {"caracteristicas": caracteristicas, "vector_completo": vector_completo}
```
Resultado de la fase: un vector numérico por huella (concatenación LBP+HOG+Gabor) y un diccionario por descriptor para trazabilidad, inspección y depuración.

## Fase 3: Fusión e Indexación
Ubicación: `backend/src/core/fusion_indexacion.py`

Objetivo: consolidar todos los vectores extraídos, limpiarlos y normalizarlos, y construir un índice FAISS para consultas eficientes de vecinos más cercanos. Se persisten en disco el índice, el mapeo FAISS→archivo y los parámetros de normalización para garantizar reproducibilidad entre entrenamiento e inferencia.

- **Normalización Min–Max** (`normalizar_min_max`)
```python
self.scaler['min'] = np.min(self.vectores_raw, axis=0)
self.scaler['max'] = np.max(self.vectores_raw, axis=0)
self.scaler['range'] = self.scaler['max'] - self.scaler['min']
self.scaler['range'][self.scaler['range'] == 0] = 1.0
self.vectores_normalizados = (self.vectores_raw - self.scaler['min']) / self.scaler['range']
```
- **Construcción índice FAISS** (`construir_indice_faiss`)
```python
self.indice_faiss = faiss.IndexFlatL2(dimension)
vectores_float32 = self.vectores_normalizados.astype('float32')
self.indice_faiss.add(vectores_float32)
```
- **Persistencia** (`guardar_indices`)
```python
faiss.write_index(self.indice_faiss, os.path.join(self.directorio_salida, 'faiss_index.bin'))
json.dump(self.mapeo_indices, open(...,'w'), indent=2)
pickle.dump(self.scaler, open(...,'wb'))
```
Resultado de la fase: `faiss_index.bin`, `mapeo_indices.json` y `scaler.pkl` en `datos/indices/`, listos para carga en tiempo de consulta.

## Fase 4: Búsqueda y Evaluación
Ubicación: `backend/src/core/busqueda_similitud.py` y rutas `backend/src/rutas/busqueda.py`

Objetivo: reutilizar el índice FAISS y el scaler entrenados para resolver consultas. El vector de la imagen de consulta se normaliza con la misma transformación, se consultan los k vecinos más cercanos y las distancias se convierten a similitudes (exp(-dist/20)). La API expone endpoints para extracción y búsqueda, consumidos por el frontend.

- **Búsqueda** (`SistemaBusqueda.buscar_por_imagen`)
```python
resultado = extractor.extraer_imagen(imagen)
vector_normalizado = (resultado['vector_completo'] - self.scaler['min']) / self.scaler['range']
vector_float32 = vector_normalizado.astype('float32').reshape(1, -1)
distancias, indices = self.indice_faiss.search(vector_float32, top_k)
similitud = np.exp(-dist / 20.0)
```
- **Endpoint de extracción** (`/api/extraer-caracteristicas`)
```python
imagen_procesada = preprocesador.preprocesar_imagen(imagen)
resultado = extractor.extraer_imagen(imagen_procesada)
return jsonify({"caracteristicas": resultado['caracteristicas'], "vector_completo": resultado['vector_completo']})
```
- **Endpoint de búsqueda** (`/api/buscar-similares`)
```python
imagen_procesada = preprocesador.preprocesar_imagen(imagen)
resultados = sistema_busqueda.buscar_por_imagen(imagen_procesada, extractor)
return jsonify({"exito": True, "resultados": resultados})
```
Resultado de la fase: respuestas HTTP que entregan vectores (extracción) o listas ordenadas de imágenes similares (búsqueda), reutilizando el índice FAISS cargado en memoria con normalización coherente.

## Métricas implementadas y justificación de las seleccionadas

- **Distancia euclidiana (L2) en FAISS**: el índice se construye con `faiss.IndexFlatL2`, apropiado para vectores densos y normalizados en [0,1]. Garantiza exactitud en vecinos más cercanos sin aproximación.
- **Conversión a similitud exponencial**: en la búsqueda se transforma la distancia a similitud con `similitud = exp(-dist/20.0)` (`backend/src/core/busqueda_similitud.py`). Es monótonamente decreciente (preserva el orden), acota el rango en (0,1] y facilita interpretación (1≈idéntico, cercano a 0≈muy diferente). El factor 20 suaviza la caída según la escala típica de distancias L2 tras la normalización min–max.
- **Normalización previa (Min–Max)**: aplicada antes de indexar para evitar que una característica domine la distancia L2 y para mantener estabilidad numérica. Referencia: `normalizar_min_max` en `backend/src/core/fusion_indexacion.py`.

Fragmentos clave:
```python
# backend/src/core/fusion_indexacion.py
self.indice_faiss = faiss.IndexFlatL2(dimension)

# backend/src/core/busqueda_similitud.py
distancias, indices = self.indice_faiss.search(vector_float32, top_k)
similitud = np.exp(-dist / 20.0)
```

## Diseño de la evaluación

Objetivo: comprobar que la cadena completa (preprocesamiento → extracción → normalización → índice FAISS) recupera la huella correcta o las más similares.

Propuesta con lo existente:
1. **Base de consulta**: usar las huellas ya preprocesadas y sus vectores (`datos/caracteristicas/caracteristicas_completas.json` y `vectores_caracteristicas.npy`).
2. **Procedimiento**: para cada huella de prueba, llamar a `/api/buscar-similares` y comprobar si la huella original aparece en el top-k. El script `backend/scripts/probar_busqueda.py` incluye `verificar_precision_exacta`, que revisa la presencia de la consulta y reporta similitud/distancia.
3. **Métricas sugeridas**:
   - *Hit@1 / Exactitud top-1*: proporción de consultas donde la imagen correcta está en primera posición.
   - *Hit@k*: proporción de consultas donde aparece en las k primeras.
   - *Similitud promedio del match correcto*: para calibrar la función `exp(-dist/20)`.
4. **Criterios de aceptación**: la huella de consulta debe recuperarse con similitud alta (cercana a 1.0) y distancia mínima, con coherencia en el top-k.
5. **Automatización**: extender `probar_busqueda.py` para iterar sobre múltiples consultas y acumular métricas (aciertos y medias de similitud/distancia), reutilizando el pipeline actual de extracción + FAISS.
