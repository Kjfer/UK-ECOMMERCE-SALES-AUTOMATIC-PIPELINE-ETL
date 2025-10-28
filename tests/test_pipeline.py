import sys
import sqlite3
from pathlib import Path

# Asegurar que el paquete top-level esté en sys.path cuando pytest lo ejecute
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.extract import extract_csv
from src.transform import transform
from src.load import load_to_sqlite


def test_pipeline_end_to_end(tmp_path):
    p = Path("data") / "raw" / "data.csv"
    df = extract_csv(p)
    assert len(df) > 0
    t = transform(df)
    assert "TotalPrice" in t.columns

    db = tmp_path / "pipeline_test.db"
    load_to_sqlite(t, db)
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sales")
    cnt = cur.fetchone()[0]
    conn.close()
    assert cnt == len(t)
