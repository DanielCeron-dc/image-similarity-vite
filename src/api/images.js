import api from './client'

const toSeed = (file) => {
  if (!file) return Math.random().toString(36).slice(2)
  return encodeURIComponent(`${file.name}-${file.size}-${file.type}`)
}

export async function fetchSimilarImages(file) {
  const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') !== 'false'

  if (USE_MOCK) {
    const seed = toSeed(file)
    await new Promise((r) => setTimeout(r, 1200))
    return Array.from({ length: 5 }, (_, i) => `https://picsum.photos/seed/${seed}-${i}/640/640`)
  }

  const form = new FormData()
  form.append('image', file)

  const res = await api.post('/api/similar', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  // Expecting { images: string[] }
  return res.data?.images ?? []
}
