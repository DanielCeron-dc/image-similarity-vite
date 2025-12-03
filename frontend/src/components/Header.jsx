import unicaucaLogo from "../../assets/unicauca.png";

export function Header() {
  return (
    <header className="px-10 pt-10 pb-8 shrink-0">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          {/* Logo limpio */}
          <div className="h-25 w-32">
            <img
              src={unicaucaLogo}
              alt="Universidad del Cauca"
              className="h-full w-full object-contain"
              loading="lazy"
            />
          </div>

          <div>
            <div className="flex items-baseline gap-4">
              <h1 className="text-4xl font-black text-white drop-shadow-2xl">
                SCBIR: Huellas Latentes
              </h1>
            </div>

            <div className="mt-2">
              <p className="text-md font-medium drop-shadow-lg">
                Sistema de Recuperación por Contenido para Huellas Dactilares
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
