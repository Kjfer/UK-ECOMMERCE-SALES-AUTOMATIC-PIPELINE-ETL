"""Módulo de extracción.

Proporciona una función simple que lee un CSV y devuelve un DataFrame.
"""
from pathlib import Path
import pandas as pd
from typing import Union
import logging

logger = logging.getLogger(__name__)


def extract_csv(path: Union[str, Path]) -> pd.DataFrame:
	"""Lee un CSV desde `path` y devuelve un pandas.DataFrame.

	- Intenta leer con inferencia de tipos mínima (todo como string para que
	  la transformación decida los tipos).
	- Lanza FileNotFoundError si el archivo no existe.
	"""
	path = Path(path)
	if not path.exists():
		raise FileNotFoundError(f"Archivo de datos no encontrado: {path}")

	# Leer todo como string para evitar conversiones prematuras
	logger.debug("Leyendo CSV desde %s", path)
	try:
		df = pd.read_csv(path, dtype=str, keep_default_na=False)
	except UnicodeDecodeError:
		# Algunos CSVs (símbolos £ etc) vienen en latin-1/cp1252
		logger.debug("UnicodeDecodeError con UTF-8, intentando latin-1 para %s", path)
		try:
			df = pd.read_csv(path, dtype=str, encoding="latin-1", keep_default_na=False)
		except Exception:
			# último recurso
			logger.debug("Fallo con latin-1, intentando cp1252 para %s", path)
			df = pd.read_csv(path, dtype=str, encoding="cp1252", keep_default_na=False)

	logger.info("CSV cargado: %d filas desde %s", len(df), path)
	return df


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Extraer CSV a DataFrame (prueba)")
	parser.add_argument("input", help="Ruta al CSV de entrada")
	args = parser.parse_args()

	print("FASE 1: EXTRACCIÓN DE DATOS DESDE CSV")
	print("=" * 80)
	df = extract_csv(args.input)
	print(f"Filas leídas: {len(df)}")