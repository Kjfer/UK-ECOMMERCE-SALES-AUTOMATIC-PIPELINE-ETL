"""Orquestador del pipeline ETL.

Este módulo procesa todos los archivos CSV que encuentre en un directorio
`raw_dir` (por defecto `data/raw`) y escribe resultados en `out_dir`
(`data/processed` por defecto). Cada CSV de salida contiene la fecha de
ejecución en su nombre para mantener historiales diarios.

También se proporciona un pequeño CLI usado por GitHub Actions.
"""
from pathlib import Path
from datetime import datetime
from .extract import extract_csv
from .transform import transform
from .load import load_to_csv, load_to_sqlite
from .logging_config import configure_logging
import logging
import argparse

# Configurar logging por defecto al importar el módulo
configure_logging()
logger = logging.getLogger(__name__)


def run(raw_dir: str = "data/raw", out_dir: str = "data/processed", sqlite: bool = False, date_str: str | None = None) -> None:
    """Procesa todos los CSV en `raw_dir` y escribe resultados en `out_dir`.

    - raw_dir: directorio con archivos CSV de entrada.
    - out_dir: directorio donde escribir CSVs procesados.
    - sqlite: si True, además crea un archivo sqlite por fecha en out_dir.
    - date_str: cadena de fecha para usar en nombre de archivo (formato YYYY-MM-DD). Si None usa la fecha actual.
    """
    raw_path = Path(raw_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    logger.info("Iniciando pipeline: raw=%s out=%s date=%s", raw_path, out_path, date_str)

    csv_files = sorted(raw_path.glob("*.csv"))
    if not csv_files:
        logger.warning("No se encontraron CSVs en %s", raw_path)
        return

    for f in csv_files:
        try:
            logger.info("Procesando %s", f)
            df = extract_csv(f)
            df_t = transform(df)

            out_name = f.stem + "_" + date_str + ".csv"
            out_file = out_path / out_name
            load_to_csv(df_t, out_file)
            logger.info("Guardado procesado: %s", out_file)

            if sqlite:
                db_name = "sales_" + date_str + ".db"
                db_file = out_path / db_name
                load_to_sqlite(df_t, db_file)
                logger.info("Guardado sqlite: %s", db_file)
        except Exception as e:
            logger.exception("Error procesando %s: %s", f, e)


def _parse_args():
    p = argparse.ArgumentParser(description="Runner ETL que procesa todos los CSVs en un directorio raw y escribe en processed")
    p.add_argument("--raw-dir", default="data/raw", help="Directorio con CSVs de entrada")
    p.add_argument("--out-dir", default="data/processed", help="Directorio para CSVs procesados")
    p.add_argument("--sqlite", action="store_true", help="Crear además un sqlite por fecha")
    p.add_argument("--date", default=None, help="Fecha a usar en nombres (YYYY-MM-DD). Por defecto hoy")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(args.raw_dir, args.out_dir, sqlite=args.sqlite, date_str=args.date)
