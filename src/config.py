import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "gold.duckdb"
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")
MAX_ROWS = 100
FORECAST_METRICS = {"SalesAmount", "Quantity", "CostAmount", "SalesAmountUSD"}   