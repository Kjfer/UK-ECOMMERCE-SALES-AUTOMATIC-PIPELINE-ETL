"""Módulo de carga (load).

Funciones para escribir el DataFrame transformado a destino: CSV y SQLite.
"""
from pathlib import Path
import sqlite3
import pandas as pd
from typing import Union
import logging

logger = logging.getLogger(__name__)


def load_to_csv(df: pd.DataFrame, out_path: Union[str, Path]) -> None:
	out_path = Path(out_path)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_csv(out_path, index=False)
	logger.info("Guardado CSV procesado en %s (filas=%d)", out_path, len(df))


def load_to_sqlite(df: pd.DataFrame, db_path: Union[str, Path], table_name: str = "sales") -> None:
	db_path = Path(db_path)
	db_path.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(str(db_path))
	try:
		# Reemplaza la tabla si existe (idempotencia simple)
		df.to_sql(table_name, conn, if_exists="replace", index=False)
	finally:
		conn.close()
	logger.info("Guardado SQLite en %s (tabla=%s, filas=%d)", db_path, table_name, len(df))


if __name__ == "__main__":
	# prueba rápida
	from pathlib import Path
	from .extract import extract_csv
	from .transform import transform

	p = Path(__file__).parent.parent / "data" / "raw" / "data.csv"
	df = extract_csv(p)
	t = transform(df)
	load_to_csv(t, Path(__file__).parent.parent / "data" / "processed" / "cleaned.csv")
	load_to_sqlite(t, Path(__file__).parent.parent / "data" / "processed" / "sales.db")
	print("Carga completada: CSV + SQLite")
