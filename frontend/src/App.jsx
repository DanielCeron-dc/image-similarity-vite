import { useEffect, useState } from 'react'
import { Header } from './components/Header'
import { UploadDropzone } from './components/UploadDropzone'
import { ImageGrid } from './components/ImageGrid'
import { fetchSimilarImages } from './api/images'

function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!file) {
      setPreviewUrl('')
      return
    }
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const onSelectFile = async (f) => {
    setError('')
    setImages([])
    setFile(f)
    setLoading(true)
    try {
      const results = await fetchSimilarImages(f)
      setImages(results)
    } catch (e) {
      setError('Failed to fetch similar images. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  const onClear = () => {
    setFile(null)
    setPreviewUrl('')
    setImages([])
    setError('')
  }

  return (
    <div className="h-screen max-h-screen overflow-hidden bg-gradient-to-br via-gray-600 to-bg-black flex flex-col relative">
      {/* Animated gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/20 via-transparent to-yellow-500/20 animate-pulse"></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-pink-500/30 via-transparent to-transparent"></div>
      <div className="relative z-10 flex flex-col h-full">
        <Header />

        <main className="flex-1 overflow-hidden px-10 pb-10 flex flex-col gap-8">
          {/* Upload Section */}
          <div className="shrink-0">
            <h2 className="text-2xl font-extrabold text-white mb-4 drop-shadow-lg">📤 Subir Imagen</h2>
            <UploadDropzone onFileSelected={onSelectFile} disabled={loading} previewUrl={previewUrl} />
            {error && (
              <div className="mt-4 px-5 py-3 rounded-3xl bg-red-500/20 border-2 border-red-400/50 text-red-200 text-sm backdrop-blur-sm shadow-xl">
                {error}
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="flex-1 overflow-hidden flex flex-col gap-5">
            <div className="flex items-center justify-between shrink-0">
              <h2 className="text-2xl font-extrabold text-white drop-shadow-lg">Huellas Similares:</h2>
              {(file || images.length > 0) && !loading && (
                <button
                  onClick={onClear}
                  className="px-6 py-2.5 gap-25 rounded-full text-sm font-bold bg-white/10 hover:bg-white/20 text-white border-2 border-white/30 transition backdrop-blur-md shadow-lg hover:shadow-xl hover:scale-105"
                >
                  Limpiar resultados
                </button>
              )}
            </div>
            <div className="flex-1 overflow-hidden">
              <ImageGrid images={images} loading={loading} />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
