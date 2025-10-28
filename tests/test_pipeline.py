import sys
import sqlite3
from pathlib import Path

# Asegurar que el paquete top-level esté en sys.path cuando pytest lo ejecute
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.extract import extract_csv
from src.transform import transform
from src.load import load_to_csv


def test_pipeline_end_to_end(tmp_path):
    p = Path("data") / "raw" / "data.csv"
    df = extract_csv(p)
    assert len(df) > 0
    t = transform(df)
    assert "TotalPrice" in t.columns

    out_csv = tmp_path / "pipeline_test.csv"
    load_to_csv(t, out_csv)
    # comprobar que el CSV existe y tiene las mismas filas
    import pandas as pd
    df_out = pd.read_csv(out_csv)
    assert len(df_out) == len(t)
