"""Flujo automatizado de preparación de datos e indexación.

Ejecuta los dos pasos necesarios para dejar el sistema listo:
1) Descargar y preprocesar datasets
2) Construir índices FAISS

Se salta el proceso si ya existe el índice principal.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INDICE_OBJETIVO = ROOT / "datos" / "indices" / "faiss_index.bin"


def ya_esta_indexado() -> bool:
    return INDICE_OBJETIVO.exists()


def ejecutar(comando: list[str]) -> None:
    print(f"\n>> Ejecutando: {' '.join(comando)}")
    resultado = subprocess.run(comando, cwd=ROOT)
    if resultado.returncode != 0:
        raise SystemExit(resultado.returncode)


def main() -> None:
    if ya_esta_indexado():
        print(f"Índice ya presente en {INDICE_OBJETIVO}. Nada que hacer.")
        return

    print("Preparando datos e índices (primer arranque)...")

    # Paso 1: descarga/preprocesamiento/extracción
    ejecutar([sys.executable, "scripts/descargar_datos.py"])

    # Paso 2: indexación
    ejecutar([sys.executable, "scripts/indexar_sistema.py"])

    if ya_esta_indexado():
        print("Proceso completo: índice disponible.")
    else:
        print("Proceso terminado, pero no se encontró el índice. Revisa los logs.")


if __name__ == "__main__":
    main()
