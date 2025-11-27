export function ImageGrid({ results = [], loading = false, onImageSelect }) {
  const total = 10;
  const placeholders = Array.from({ length: total });

  return (
    <div className="w-full grid grid-cols-5 gap-6 auto-rows-min">
      {placeholders.map((_, i) => {
        const result = results[i];
        return (
          <div
            key={i}
            className="group relative aspect-square cursor-pointer"
            onClick={() => result && onImageSelect(result)}
          >
            {result ? (
              <div className="relative h-full w-full rounded-3xl overflow-hidden shadow-2xl hover:shadow-[0_0_50px_rgba(34,211,238,0.6)] transition-all duration-300 hover:scale-105 border-4 border-cyan-400/40">
                <img
                  src={result.url}
                  alt={`Result ${i + 1} - ${result.archivo}`}
                  className="h-full w-full object-cover"
                  onError={(e) => {
                    e.target.src =
                      'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EError%3C/text%3E%3C/svg%3E';
                  }}
                />

                {/* Solo número de posición y porcentaje */}
                <div className="absolute top-3 right-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-black shadow-xl border-4 border-white/30">
                    {result.posicion || i + 1}
                  </div>
                </div>

                <div className="absolute bottom-3 left-3 right-3">
                  <div className="px-3 py-1.5 rounded-full bg-white/20 backdrop-blur-md text-white text-xs font-semibold border border-white/30 text-center">
                    {Math.round(result.similitud * 100)}%
                  </div>
                </div>
              </div>
            ) : (
              <div
                className={`h-full w-full rounded-3xl flex flex-col items-center justify-center border-4 transition-all backdrop-blur-xl ${
                  loading
                    ? "animate-pulse bg-gradient-to-br from-cyan-500/20 via-blue-500/20 to-purple-600/20 border-cyan-400/50"
                    : "bg-gradient-to-br from-white/5 to-white/10 border-dashed border-white/30 hover:from-white/10 hover:to-white/15 hover:border-cyan-400/50"
                }`}
              >
                {loading ? (
                  <div className="flex flex-col items-center gap-4">
                    <div className="h-12 w-12 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin"></div>
                    <span className="text-base font-bold text-white/70">
                      Loading...
                    </span>
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="h-16 w-16 rounded-full bg-white/10 flex items-center justify-center mb-4 border-2 border-white/20">
                      <span className="text-3xl font-black text-white/30">
                        {i + 1}
                      </span>
                    </div>
                    <div className="text-sm text-white/50 font-bold">
                      Empty Slot
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
