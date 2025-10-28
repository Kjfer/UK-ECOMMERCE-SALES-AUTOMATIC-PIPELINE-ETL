"""Configuración centralizada de logging para el proyecto."""
import logging
from typing import Optional


def configure_logging(level: Optional[str] = "INFO") -> None:
    """Configura el logging básico para consola.

    - level: nivel de logging como string (DEBUG, INFO, WARNING, ...)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        root.addHandler(handler)
    root.setLevel(numeric_level)
