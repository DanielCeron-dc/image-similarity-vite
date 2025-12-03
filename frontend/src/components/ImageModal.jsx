import { useState } from "react";
import "./ImageModal.css";

export function ImageModal({
  uploadedImage,
  selectedResult,
  onClose,
  allResults = [],
  currentIndex = 0,
}) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [lastPosition, setLastPosition] = useState({ x: 0, y: 0 });
  const [currentResultIndex, setCurrentResultIndex] = useState(currentIndex);

  const currentResult = allResults[currentResultIndex] || selectedResult;

  const goToPrevious = () => {
    setCurrentResultIndex((prev) => Math.max(0, prev - 1));
    resetZoom();
  };

  const goToNext = () => {
    setCurrentResultIndex((prev) => Math.min(allResults.length - 1, prev + 1));
    resetZoom();
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const newZoom = zoomLevel + (e.deltaY > 0 ? -0.1 : 0.1);
    setZoomLevel(Math.max(0.5, Math.min(3, newZoom)));
  };

  const handleMouseDown = (e) => {
    if (zoomLevel > 1) {
      setIsDragging(true);
      setLastPosition({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging && zoomLevel > 1) {
      const deltaX = e.clientX - lastPosition.x;
      const deltaY = e.clientY - lastPosition.y;
      setPosition((prev) => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY,
      }));
      setLastPosition({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetZoom = () => {
    setZoomLevel(1);
    setPosition({ x: 0, y: 0 });
  };

  return (
    <div className="image-modal-overlay" onClick={onClose}>
      <div className="image-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="image-modal-header">
          <h2>Comparación de Huellas</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="image-comparison-container">
          {/* Lado izquierdo - Imagen ORIGINAL del usuario SIN INFO */}
          <div className="image-side">
            <h3>Imagen Original (Consulta)</h3>
            <div className="image-zoom-container">
              <div
                className="zoomable-image"
                style={{
                  transform: `scale(${zoomLevel}) translate(${position.x}px, ${position.y}px)`,
                  cursor:
                    zoomLevel > 1
                      ? isDragging
                        ? "grabbing"
                        : "grab"
                      : "default",
                }}
                onWheel={handleWheel}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
              >
                <img src={uploadedImage} alt="Imagen original de consulta" />
              </div>
            </div>
            {/* SIN INFO - Solo el título arriba */}
          </div>

          {/* Lado derecho - Resultado del sistema CON INFO */}
          <div className="image-side">
            <h3>Imagen Resultado #{currentResultIndex + 1}</h3>
            <div className="image-zoom-container">
              <div
                className="zoomable-image"
                style={{
                  transform: `scale(${zoomLevel}) translate(${position.x}px, ${position.y}px)`,
                  cursor:
                    zoomLevel > 1
                      ? isDragging
                        ? "grabbing"
                        : "grab"
                      : "default",
                }}
                onWheel={handleWheel}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
              >
                <img
                  src={currentResult.url}
                  alt={`Resultado ${currentResultIndex + 1}`}
                />
              </div>
            </div>
            <div className="image-info">
              <div className="info-grid">
                <div className="info-item">
                  <strong>Archivo:</strong>
                  <span>{currentResult.archivo}</span>
                </div>
                <div className="info-item">
                  <strong>Similitud:</strong>
                  <span>{(currentResult.similitud * 100).toFixed(4)}%</span>
                </div>
                <div className="info-item">
                  <strong>Distancia:</strong>
                  <span>{currentResult.distancia?.toFixed(4) || "N/A"}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* CONTROLES ABAJO - Distribución horizontal */}
        <div className="modal-controls-container">
          {/* Zoom al CENTRO */}

          <div className="zoom-controls">
            <button
              onClick={goToPrevious}
              disabled={currentResultIndex === 0}
              className="nav-control-button prev-button"
            >
              ‹
            </button>
            <button
              onClick={() => setZoomLevel((prev) => Math.max(0.5, prev - 0.1))}
              className="zoom-button"
            >
              -
            </button>
            <span className="zoom-level">{Math.round(zoomLevel * 100)}%</span>
            <button
              onClick={() => setZoomLevel((prev) => Math.min(3, prev + 0.1))}
              className="zoom-button"
            >
              +
            </button>
            <button
              onClick={goToNext}
              disabled={currentResultIndex === allResults.length - 1}
              className="nav-control-button next-button"
            >
              ›
            </button>
          </div>

          {/* Navegación y Reset a la DERECHA - EN LA MISMA LÍNEA */}
          <div className="right-controls">
            <button onClick={resetZoom} className="reset-button">
              Reset Zoom
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
