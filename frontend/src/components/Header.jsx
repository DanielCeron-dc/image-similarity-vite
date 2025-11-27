export function Header() {
  return (
    <header className="px-10 pt-10 pb-8 shrink-0">
      <div className="flex items-center gap-5">
        <div className="h-16 w-16 rounded-full bg-gradient-to-br from-cyan-400 via-blue-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-cyan-500/50 border-4 border-white/20">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
          </svg>
        </div>
        <div>
          <h1 className="text-4xl font-black text-white tracking-tight drop-shadow-2xl">
            Sube la huella
          </h1>
          <p className="text-base text-purple-100 mt-1 drop-shadow-lg">Encuentra huellas similares utilizando un sistema SCBIR</p>
        </div>
      </div>
    </header>
  )
}
