import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "gold.duckdb"

con = duckdb.connect(str(DB))
for f in sorted(RAW.iterdir()):
    if f.suffix.lower() in {".csv", ".parquet"}:
        reader = "read_csv_auto" if f.suffix.lower() == ".csv" else "read_parquet"
        con.execute(f"CREATE OR REPLACE TABLE {f.stem} AS SELECT * FROM {reader}('{f.as_posix()}')")
        print("Loaded", f.stem, con.execute(f"SELECT COUNT(*) FROM {f.stem}").fetchone()[0], "rows")

con.execute((ROOT / "sql" / "v_sales.sql").read_text())
print("View v_sales created:", con.execute("SELECT COUNT(*) FROM v_sales").fetchone()[0], "rows")


con.execute((ROOT / "sql" / "v_stores.sql").read_text())
print("v_stores:", con.execute("SELECT COUNT(*) FROM v_stores").fetchone()[0], "rows")
con.close()