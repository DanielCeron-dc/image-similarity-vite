"""Lanza el backend tras preparar datos e índices si no existen.

Uso:
    python run_backend.py

Respeta las variables BACKEND_PORT, PORT o FLASK_RUN_PORT (por defecto 5001).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ubicar raíz del backend y asegurar cwd correcto
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)


def obtener_puerto() -> int:
    return int(
        os.getenv("BACKEND_PORT")
        or os.getenv("PORT")
        or os.getenv("FLASK_RUN_PORT")
        or "5001"
    )


def main() -> None:
    # Definir host/puerto antes de importar app
    port = obtener_puerto()
    os.environ.setdefault("FLASK_RUN_PORT", str(port))
    os.environ.setdefault("FLASK_RUN_HOST", "0.0.0.0")

    # Preparar datos e índices si faltan
    print("Preparando datos e índices (si faltan)...")
    from scripts import setup_inicial

    setup_inicial.main()

    # Levantar servidor Flask
    from app import app, crear_directorios

    crear_directorios()
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    print(f"Iniciando backend en http://{host}:{port}")
    app.run(debug=True, host=host, port=port)


if __name__ == "__main__":
    # Garantiza que usa el Python invocado (ej. del venv activo)
    sys.exit(main())
