export function ImageGrid({ images = [], loading = false }) {
  const total = 5
  const placeholders = Array.from({ length: total })

  return (
    <div className="h-full w-full flex items-stretch gap-4">
      {placeholders.map((_, i) => {
        const src = images[i]
        return (
          <div key={i} className="group relative" style={{ width: 'calc((100% - 64px) / 5)' }}>
            {src ? (
              <div className="relative h-full w-full rounded-3xl overflow-hidden shadow-2xl hover:shadow-[0_0_50px_rgba(34,211,238,0.6)] transition-all duration-300 hover:scale-105 border-4 border-cyan-400/40">
                <img
                  src={src}
                  alt={`Result ${i + 1}`}
                  className="h-full w-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-purple-900/80 via-transparent to-cyan-500/20" />
                <div className="absolute top-3 right-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-black shadow-xl border-4 border-white/30">
                    {i + 1}
                  </div>
                </div>
                <div className="absolute bottom-3 left-3 right-3">
                  <div className="flex items-center justify-between">
                    <div className="px-4 py-2 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 text-white text-xs font-bold shadow-xl border-2 border-white/30">
                      ✓ Match
                    </div>
                    <div className="px-3 py-1.5 rounded-full bg-white/20 backdrop-blur-md text-white text-xs font-semibold border border-white/30">
                      {Math.floor(Math.random() * 15 + 85)}%
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div
                className={`h-full w-full rounded-3xl flex flex-col items-center justify-center border-4 transition-all backdrop-blur-xl ${
                  loading
                    ? 'animate-pulse bg-gradient-to-br from-cyan-500/20 via-blue-500/20 to-purple-600/20 border-cyan-400/50'
                    : 'bg-gradient-to-br from-white/5 to-white/10 border-dashed border-white/30 hover:from-white/10 hover:to-white/15 hover:border-cyan-400/50'
                }`}
              >
                {loading ? (
                  <div className="flex flex-col items-center gap-4">
                    <div className="h-12 w-12 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin"></div>
                    <span className="text-base font-bold text-white/70">Loading...</span>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="h-16 w-16 rounded-full bg-white/10 flex items-center justify-center mb-4 border-2 border-white/20">
                      <span className="text-3xl font-black text-white/30">{i + 1}</span>
                    </div>
                    <div className="text-sm text-white/50 font-bold">Empty Slot</div>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
