import { useEffect, useState } from "react";
import { Header } from "./components/Header";
import { UploadDropzone } from "./components/UploadDropzone";
import { ImageGrid } from "./components/ImageGrid";
import { ImageModal } from "./components/ImageModal";
import {
  searchSimilarFingerprints,
  checkSystemStatus,
} from "./api/fingerprint";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [systemReady, setSystemReady] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);

  // Verificar estado del sistema al cargar
  useEffect(() => {
    checkSystemStatus()
      .then((status) => {
        setSystemReady(status.sistema_indexado);
        if (!status.sistema_indexado) {
          setError(
            "El sistema no esta indexado. Ejecuta: python scripts/indexar_sistema.py"
          );
        }
      })
      .catch((err) => {
        console.error("Error checking system:", err);
        setError(
          "No se pudo conectar con el servidor. Asegurate de que este corriendo."
        );
      });
  }, []);

  // Crear preview URL cuando cambia el archivo
  useEffect(() => {
    if (!file) {
      setPreviewUrl("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setUploadedImage(url); // Guardar la imagen original
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const onSelectFile = async (f) => {
    setError("");
    setResults([]);
    setFile(f);
    setSelectedResult(null);

    if (!systemReady) {
      setError("El sistema no esta listo. Verifica que este indexado.");
      return;
    }

    setLoading(true);

    try {
      console.log("Buscando huellas similares para:", f.name);
      const similarResults = await searchSimilarFingerprints(f);
      console.log("Resultados recibidos:", similarResults);
      setResults(similarResults);

      if (similarResults.length === 0) {
        setError("No se encontraron resultados similares.");
      }
    } catch (e) {
      console.error("Error en busqueda:", e);
      setError(
        e.message || "Error al buscar huellas similares. Intenta de nuevo."
      );
    } finally {
      setLoading(false);
    }
  };

  const onClear = () => {
    setFile(null);
    setPreviewUrl("");
    setUploadedImage(null);
    setResults([]);
    setError("");
    setSelectedResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br via-gray-600 to-bg-black flex flex-col relative overflow-auto">
      {/* Animated gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/20 via-transparent to-yellow-500/20 animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-pink-500/30 via-transparent to-transparent"></div>

      <div className="relative z-10 flex flex-col h-full">
        <Header />

        <main className="flex-1 overflow-hidden px-10 pb-10 flex flex-col gap-8">
          {/* Upload Section */}
          <div className="shrink-0">
            <h2 className="text-2xl font-extrabold text-white mb-4 drop-shadow-lg">
              Subir Imagen
            </h2>
            <UploadDropzone
              onFileSelected={onSelectFile}
              disabled={loading || !systemReady}
              previewUrl={previewUrl}
            />
            {error && (
              <div className="mt-4 px-5 py-3 rounded-3xl bg-red-500/20 border-2 border-red-400/50 text-red-200 text-sm backdrop-blur-sm shadow-xl">
                {error}
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="flex-1 overflow-hidden flex flex-col gap-5">
            <div className="flex items-center justify-between shrink-0">
              <h2 className="text-2xl font-extrabold text-white drop-shadow-lg">
                Huellas Similares:{" "}
                {results.length > 0 && `(${results.length} resultados)`}
              </h2>
              {(file || results.length > 0) && !loading && (
                <button
                  onClick={onClear}
                  className="px-8 py-3 rounded-full text-base font-bold bg-red-500/20 hover:bg-red-500/30 text-white border-2 border-red-400/50 transition backdrop-blur-md shadow-lg hover:shadow-xl hover:scale-105 whitespace-nowrap"
                >
                  Limpiar resultados
                </button>
              )}
            </div>
            <div className="flex-1 overflow-hidden">
              <ImageGrid
                results={results}
                loading={loading}
                onImageSelect={setSelectedResult}
              />
            </div>
          </div>
        </main>
      </div>

      {/* Modal */}
      {uploadedImage && selectedResult && (
        <ImageModal
          uploadedImage={uploadedImage}
          selectedResult={selectedResult}
          onClose={() => setSelectedResult(null)}
          allResults={results}
          currentIndex={results.findIndex((r) => r === selectedResult)}
        />
      )}
    </div>
  );
}

export default App;
