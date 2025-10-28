
# UK ECOMMERCE SALES — ETL automático

Este repositorio contiene un pipeline ETL sencillo pero completo para procesar los datos de ventas de ejemplo (CSV). El objetivo es proporcionar una base reproducible para extraer, transformar y almacenar (en CSV procesado) registros de ventas y facilitar su ejecución diaria mediante GitHub Actions.

Contenido principal
- `src/extract.py` — lectura robusta de CSV (manejo de codificaciones, todo como string).
- `src/transform.py` — limpieza y normalización: parseo de fechas, conversión numérica, detección de devoluciones y cálculo de `TotalPrice`.
- `src/load.py` — escritura de resultados a CSV (crea directorios si hacen falta).
- `src/pipeline.py` — orquestador: recorre `data/raw/*.csv` y genera `data/processed/*_YYYY-MM-DD.csv`.
- `notebooks/` — análisis exploratorio (Jupyter notebook).
- `tests/` — tests de integración/funcionales (pytest).

Descripción del CSV de origen

El fichero de entrada principal esperado está en `data/raw/data.csv`. Es un CSV con las transacciones de ventas en bruto. Breve resumen de su estructura y convenciones:

- Ubicación por defecto: `data/raw/data.csv` (el pipeline procesa todos los CSVs que encuentre en `data/raw`).
- Codificación: típicamente UTF-8; el extractor intenta caer a `latin-1` o `cp1252` si hay problemas con caracteres especiales (símbolos de moneda, acentos).
- Cabeceras/columnas esperadas (mínimo para el pipeline):
	- `InvoiceNo` (string): número/factura; las devoluciones suelen marcarse con una `C` al inicio.
	- `StockCode` (string): código del artículo.
	- `Description` (string): descripción del producto.
	- `Quantity` (numérico): unidades vendidas (puede venir como string en el CSV original).
	- `InvoiceDate` (fecha/hora): fecha de la transacción (el pipeline usa `dayfirst=True` al parsear).
	- `UnitPrice` (numérico): precio unitario.
	- `CustomerID` (numérico/ID): identificador del cliente; filas sin `CustomerID` se descartan por defecto en la transformación.
	- `Country` (string): país del cliente/transacción.

- Formatos y notas:
	- Las columnas numéricas pueden venir como texto; durante la transformación se convierten con `pd.to_numeric(..., errors='coerce')`.
	- Fechas: el parser usado asume formato día primero (UK), p. ej. `31/12/2010 09:45`.
	- Filas sin `CustomerID` se eliminan en `transform.py` (decisión de negocio configurable).
	- `InvoiceNo` que comienzan por `C` se consideran devoluciones y se marcan en la columna `is_return`.

Ejemplo de cabecera (fila 1 del CSV):

```
InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country
```

Si tus datos difieren en nombres de columna o formato, ajusta `src/transform.py` para mapear/normalizar las columnas antes de ejecutar el pipeline.

Requisitos
- Python 3.8+ (recomendado 3.11)
- `requirements.txt` lista dependencias usadas por el proyecto. Las principales librerías son:
	- pandas: manipulación y análisis de datos (DataFrame).
	- numpy: operaciones numéricas (soporte a pandas internamente).
	- python-dateutil: parsing flexible de fechas (utilizado por pandas).
	- python-dotenv: carga de variables de entorno desde un .env (opcional en este proyecto).
	- matplotlib / seaborn: visualizaciones usadas en `notebooks/`.
	- pytest: framework de tests.
	- ipykernel: kernel para ejecutar notebooks desde el virtualenv (necesario para VSCode/Jupyter).

Instalación y ejecución desde cero (Windows / PowerShell)

1) Clona el repositorio:

```powershell
git clone https://github.com/Kjfer/UK-ECOMMERCE-SALES-AUTOMATIC-PIPELINE-ETL.git
cd "UK-ECOMMERCE-SALES-AUTOMATIC-PIPELINE-ETL"
```

2) Crear y activar un virtualenv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Instalar dependencias:

```powershell
pip install -U pip
pip install -r requirements.txt
```

4) Ejecutar el pipeline (procesa todos los CSV en `data/raw` y escribe en `data/processed`):

```powershell
python -m src.pipeline --raw-dir data\raw --out-dir data\processed
```

Opciones relevantes del orquestador `src.pipeline.run`:
- `--raw-dir` (default `data/raw`): directorio con CSVs de entrada.
- `--out-dir` (default `data/processed`): directorio de salida para CSVs procesados.
- `--date` (opcional): fecha a usar en el nombre del archivo (format YYYY-MM-DD). Si no se pasa, se usa la fecha actual.

Ejecutar tests

```powershell
# con el virtualenv activado
python -m pytest -q
```

Abrir el notebook de análisis (opcional)

Si quieres usar el notebook en VSCode, asegúrate de que `ipykernel` esté instalado en el virtualenv (ya figura en `requirements.txt`). Si VSCode muestra un aviso como "La ejecución de celdas requiere ipykernel", instala con:

```powershell
python -m pip install ipykernel -U --force-reinstall
python -m ipykernel install --user --name uk-etl-venv --display-name "uk-etl-venv (Python)"
```

Explicación del flujo ETL

- Extracción (`src/extract.py`): lee un CSV con `pandas.read_csv(..., dtype=str, keep_default_na=False)`. Este enfoque evita conversiones prematuras y permite manejar mejor codificaciones (UTF-8, latin-1, cp1252).
- Transformación (`src/transform.py`): reglas principales:
	- normaliza y hace strip a `Description`;
	- parsea `InvoiceDate` con `dayfirst=True` (formato UK/EU);
	- convierte `Quantity`, `UnitPrice`, `CustomerID` a numéricos (`errors='coerce'` → NaN);
	- marca `is_return` si `InvoiceNo` empieza por `C`;
	- elimina filas sin `CustomerID` (decisión de negocio que puedes ajustar);
	- rellena NaNs numéricos y calcula `TotalPrice = Quantity * UnitPrice`.
- Carga (`src/load.py`): actualmente solo exporta a CSV (`load_to_csv`) y crea directorios si no existen.
- Orquestación (`src/pipeline.py`): procesa todos los CSV del `raw_dir`, aplica extract→transform→load y escribe archivos con sufijo de fecha para mantener histórico.

GitHub Actions (ejecución diaria)

Este repositorio incluye un workflow: `.github/workflows/daily_etl.yml` que está configurado para ejecutarse diariamente (cron) y permite ejecución manual vía `workflow_dispatch`.

- El workflow instala dependencias, ejecuta `python -m src.pipeline --raw-dir data/raw --out-dir data/processed`, sube los CSV procesados como artifact y opcionalmente puede commitear las salidas a la rama `processed-data`.
- Para garantizar la ejecución diaria, asegúrate de:
	- que el workflow esté en la rama por defecto (`main`);
	- que GitHub Actions esté habilitado en el repositorio;
	- revisar la pestaña Actions → Daily ETL para ver ejecuciones y logs.



