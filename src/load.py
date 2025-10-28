from pathlib import Path
import pandas as pd
from typing import Union
import logging

logger = logging.getLogger(__name__)


def load_to_csv(df: pd.DataFrame, out_path: Union[str, Path]) -> None:
	out_path = Path(out_path)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_csv(out_path, index=False)
	logger.info("Guardado CSV procesado en %s (filas=%d)", out_path, len(df))


if __name__ == "__main__":
	# prueba rápida
	from pathlib import Path
	from .extract import extract_csv
	from .transform import transform

	p = Path(__file__).parent.parent / "data" / "raw" / "data.csv"
	df = extract_csv(p)
	t = transform(df)
	load_to_csv(t, Path(__file__).parent.parent / "data" / "processed" / "cleaned.csv")
	print("Carga completada: CSV")
