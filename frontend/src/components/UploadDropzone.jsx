import { useRef } from "react";

export function UploadDropzone({ onFileSelected, disabled, previewUrl }) {
  const inputRef = useRef(null);

  const onPick = () => inputRef.current?.click();

  const handleFiles = (files) => {
    const file = files?.[0];
    if (file && file.type.startsWith("image/")) {
      onFileSelected?.(file);
    }
  };

  const onInput = (e) => handleFiles(e.target.files);

  const onDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled) return;
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "copy";
      }}
      onDrop={onDrop}
      className={`relative rounded-3xl border-4 transition-all duration-300 backdrop-blur-xl shadow-2xl ${
        disabled
          ? "border-white/10 bg-white/5"
          : "border-cyan-400/50 bg-gradient-to-br from-white/10 to-white/5 hover:from-white/15 hover:to-white/10 hover:border-cyan-300/70 hover:shadow-[0_0_40px_rgba(34,211,238,0.3)]"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onInput}
        disabled={disabled}
      />

      {previewUrl ? (
        <div className="p-8 flex items-center gap-8">
          <div className="relative shrink-0">
            <img
              src={previewUrl}
              alt="Selected preview"
              className="h-32 w-32 rounded-full object-cover shadow-2xl ring-4 ring-cyan-400/50 border-4 border-white/20"
            />
          </div>
          <div className="flex-1">
            <p className="text-xl font-extrabold text-white mb-2 drop-shadow-lg">
              Listo para buscar
            </p>
            <p className="text-sm text-purple-100 mb-4">
              Tu imagen está subida y lista
            </p>
            <button
              type="button"
              onClick={onPick}
              disabled={disabled}
              className="px-6 py-2.5 rounded-full bg-white/20 hover:bg-white/30 text-white text-sm font-bold transition border-2 border-white/30 disabled:opacity-50 backdrop-blur-md shadow-lg hover:scale-105"
            >
              Cambiar imagen
            </button>
          </div>
        </div>
      ) : (
        <div className="p-12 flex flex-col items-center text-center">
          <h3 className="text-2xl font-black text-white mb-2 drop-shadow-xl">
            Suelta tu imagen aquí
          </h3>
          <p className="text-base text-purple-100 mb-8">
            o haz clic en el botón de abajo para buscar
          </p>

          <button
            type="button"
            onClick={onPick}
            disabled={disabled}
            className="px-10 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-black text-lg hover:shadow-2xl hover:shadow-cyan-500/60 transition-all disabled:opacity-50 hover:scale-110 border-4 border-white/20"
          >
            Seleccionar imagen
          </button>
        </div>
      )}
    </div>
  );
}
