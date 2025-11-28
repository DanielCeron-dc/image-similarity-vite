import unicaucaLogo from "../../assets/unicauca2.jpeg";

export function Header() {
  return (
    <header className="px-10 pt-10 pb-8 shrink-0">
      <div className="flex items-center gap-5">
        <div className="h-24 w-28 rounded-lg overflow-hidden bg-transparent">
          <img
            src={unicaucaLogo}
            alt="Universidad del Cauca"
            className="h-full w-full object-contain bg-transparent"
            loading="lazy"
          />
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
