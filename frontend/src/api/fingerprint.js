import api from "./client";
import ENDPOINTS from "./endpoints";

/**
 * Convierte un File a base64
 */
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // Remover prefijo "data:image/png;base64,"
      const base64 = reader.result.split(",")[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Verifica el estado del sistema (si esta indexado)
 */
export async function checkSystemStatus() {
  try {
    const response = await api.get(ENDPOINTS.STATUS);
    return response.data;
  } catch (error) {
    console.error("Error checking system status:", error);
    throw new Error("No se pudo verificar el estado del sistema");
  }
}

/**
 * Busca imagenes similares a la imagen subida
 *
 * @param {File} file - Archivo de imagen
 * @returns {Promise<Array>} Array de resultados con formato:
 *   {
 *     archivo: string,
 *     similitud: number,
 *     distancia: number,
 *     posicion: number,
 *     url: string (agregada por esta funcion)
 *   }
 */
export async function searchSimilarFingerprints(file) {
  try {
    // Convertir imagen a base64
    const imageBase64 = await fileToBase64(file);

    // Enviar busqueda al backend
    const response = await api.post(ENDPOINTS.SEARCH_SIMILAR, {
      imagen: imageBase64,
    });

    if (!response.data.exito) {
      throw new Error(response.data.error || "Error en la busqueda");
    }

    // Transformar resultados agregando URL de imagen
    const resultados = response.data.resultados || [];

    return resultados.map((resultado) => ({
      ...resultado,
      // Agregar URL completa para mostrar en el frontend
      url: ENDPOINTS.GET_IMAGE(resultado.archivo),
    }));
  } catch (error) {
    console.error("Error searching similar fingerprints:", error);

    if (error.response?.status === 400) {
      throw new Error(
        "El sistema no esta indexado. Ejecuta la indexacion primero."
      );
    }

    throw new Error("Error al buscar huellas similares. Intenta de nuevo.");
  }
}

/**
 * Preprocesa una imagen (opcional, para preview)
 */
export async function preprocessImage(file) {
  try {
    const imageBase64 = await fileToBase64(file);

    const response = await api.post(ENDPOINTS.PREPROCESS, {
      imagen: imageBase64,
    });

    if (!response.data.exito) {
      throw new Error("Error en preprocesamiento");
    }

    return {
      imagenProcesada: response.data.imagen_procesada,
      dimensionesOriginales: response.data.dimensiones_originales,
      dimensionesProcesadas: response.data.dimensiones_procesadas,
    };
  } catch (error) {
    console.error("Error preprocessing image:", error);
    throw new Error("Error al preprocesar imagen");
  }
}

/**
 * Extrae caracteristicas de una imagen (opcional, para debug)
 */
export async function extractFeatures(file) {
  try {
    const imageBase64 = await fileToBase64(file);

    const response = await api.post(ENDPOINTS.EXTRACT_FEATURES, {
      imagen: imageBase64,
    });

    if (!response.data.exito) {
      throw new Error("Error en extraccion");
    }

    return {
      caracteristicas: response.data.caracteristicas,
      vectorCompleto: response.data.vector_completo,
      dimensionTotal: response.data.dimension_total,
      detalleDescriptores: response.data.detalle_descriptores,
    };
  } catch (error) {
    console.error("Error extracting features:", error);
    throw new Error("Error al extraer caracteristicas");
  }
}
