// Default to backend port 5001 unless explicitly overridden
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";

export const ENDPOINTS = {
  // Salud del sistema
  HEALTH: `${BASE_URL}/api/salud`,

  // Estado del sistema (si esta indexado)
  STATUS: `${BASE_URL}/api/estado-sistema`,

  // Preprocesamiento
  PREPROCESS: `${BASE_URL}/api/preprocesar`,

  // Extraccion de caracteristicas
  EXTRACT_FEATURES: `${BASE_URL}/api/extraer-caracteristicas`,

  // Busqueda por similitud
  SEARCH_SIMILAR: `${BASE_URL}/api/buscar-similares`,

  // Obtener imagen por nombre
  GET_IMAGE: (filename) => `${BASE_URL}/api/imagen/${filename}`,

  // Obtener imagen en base64
  GET_IMAGE_BASE64: (filename) => `${BASE_URL}/api/imagen-base64/${filename}`,

  // Obtener multiples imagenes
  GET_IMAGES_BATCH: `${BASE_URL}/api/imagenes-lote`,
};

export default ENDPOINTS;
