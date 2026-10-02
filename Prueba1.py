"""Lanza la versión organizada del juego en la carpeta ORTRecicla."""

from pathlib import Path
import runpy
import sys


if __name__ == "__main__":
    carpeta_juego = Path(__file__).resolve().parent / "ORTRecicla"
    sys.path.insert(0, str(carpeta_juego))
    runpy.run_path(str(carpeta_juego / "main.py"), run_name="__main__")