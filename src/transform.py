"""Módulo de transformación.

Contiene la función `transform` que normaliza tipos, limpia texto y calcula
campos derivados mínimos.
"""
from typing import Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def transform(df: pd.DataFrame) -> pd.DataFrame:
	"""Transforma y limpia el DataFrame de ventas.

	Reglas aplicadas (decisiones por defecto):
	- Strip de descripciones.
	- Parseo de `InvoiceDate` con dayfirst=True (formato en los datos de ejemplo).
	- Conversión de `Quantity`, `UnitPrice` y `CustomerID` a numéricos; filas
	  sin CustomerID válidos se descartan.
	- Marca `is_return` si `InvoiceNo` comienza con 'C'.
	- Calcula `TotalPrice = Quantity * UnitPrice`.

	Devuelve copia (no modifica el DataFrame original).
	"""
	df = df.copy()
	logger.debug("Starting transform on dataframe with %d rows", len(df))

	# Asegurar columnas claves existan
	expected = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
	for col in expected:
		if col not in df.columns:
			df[col] = None

	# Limpiar texto
	df["Description"] = df["Description"].astype(str).str.strip()

	# Fecha
	df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], dayfirst=True, errors="coerce")

	# Numerics
	df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
	df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
	df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")

	# is_return
	df["is_return"] = df["InvoiceNo"].astype(str).str.startswith("C")

	# Drop rows sin CustomerID
	before = len(df)
	df = df.dropna(subset=["CustomerID"]) 
	after = len(df)
	logger.info("Dropped %d rows without CustomerID", before - after)

	# Rellenar NaNs numéricos con 0 para evitar errores posteriores
	df["Quantity"] = df["Quantity"].fillna(0).astype(int)
	df["UnitPrice"] = df["UnitPrice"].fillna(0.0)

	# Campo derivado
	df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

	# Reordenar columnas de forma razonable
	cols = ["InvoiceNo", "InvoiceDate", "StockCode", "Description", "Quantity", "UnitPrice", "TotalPrice", "CustomerID", "Country", "is_return"]
	cols_existing = [c for c in cols if c in df.columns]
	logger.debug("Transform result columns: %s", cols_existing)
	return df[cols_existing]


if __name__ == "__main__":
	# pequeña prueba manual
	from pathlib import Path
	from .extract import extract_csv
	p = Path(__file__).parent.parent / "data" / "raw" / "data.csv"
	df = extract_csv(p)
	t = transform(df)
	print(t.head(3))
