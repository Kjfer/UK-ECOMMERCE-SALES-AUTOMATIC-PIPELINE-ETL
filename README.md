# sales-etl-pipeline

Pipeline ETL minimal para los datos de ejemplo en `data/raw/data.csv`.

Qué hace:
- Extrae el CSV bruto
- Transforma: parsea fechas, normaliza números, marca devoluciones y calcula TotalPrice
- Carga a CSV limpio y/o SQLite

Requisitos
- Python 3.8+
- Dependencias (ver `requirements.txt`): pandas, numpy, python-dateutil

Ejemplo de uso (PowerShell):

```powershell
python -m src.run_etl --input data/raw/data.csv --out-csv data/processed/cleaned.csv --sqlite data/processed/sales.db
```

Siguientes pasos recomendados:
- Ajustar reglas de transformación según requisitos de negocio
- Añadir registro (logging) y manejo de errores más granular
- Añadir tests adicionales y CI
