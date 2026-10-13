import re
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from .db import get_con
from .config import MAX_ROWS, FORECAST_METRICS

BLOCKED = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|detach|copy|pragma|install|load|export)\b", re.I)

def is_safe_sql(query: str) -> bool:
    q = query.strip().rstrip(";")
    return bool(re.match(r"^(select|with)\b", q, re.I)) and ";" not in q and not BLOCKED.search(q)

def run_sql(query: str):
    if not is_safe_sql(query):
        return "Blocked: only a single SELECT query is allowed."
    try:
        df = get_con().execute(query).df()
    except Exception as e:
        return f"SQL error: {e}. Fix the query and try again."
    return {"row_count": len(df), "rows": df.head(MAX_ROWS).to_dict("records")}

def forecast(metric: str = "SalesAmount", months: int = 3,
             ProductName: str = "", StoreKey: int = "", CountryName: str = ""):
    """Forecast monthly totals of a metric for the next N months.
    Optionally filter by product_name, store_name or region (leave empty for all)."""
    if metric not in FORECAST_METRICS:
        return f"metric must be one of {sorted(FORECAST_METRICS)}"
    months = max(1, min(int(months), 12))

    where, params = [], []
    for col, val in (("ProductName", ProductName), ("storekey", StoreKey), ("countryname", CountryName)):
        if val:
            where.append(f"{col} = ?")
            params.append(val)
    w = ("WHERE " + " AND ".join(where)) if where else ""

    df = get_con().execute(
        f"SELECT date_trunc('month', full_date) AS m, SUM({metric}) AS v "
        f"FROM v_sales {w} GROUP BY 1 ORDER BY 1", params).df()

    if len(df) < 6:
        return "Not enough monthly history (need at least 6 months) to forecast."

    s = df.set_index("m")["v"].astype(float).asfreq("MS", fill_value=0)
    seasonal = len(s) >= 24
    fit = ExponentialSmoothing(
        s, trend="add",
        seasonal="add" if seasonal else None,
        seasonal_periods=12 if seasonal else None).fit()
    out = fit.forecast(months)
    return {
        "method": "Holt-Winters exponential smoothing",
        "months_of_history": len(s),
        "last_actual_month": str(s.index[-1].date()),
        "last_actual_value": round(float(s.iloc[-1]), 2),
        "forecast": {str(k.date()): round(float(v), 2) for k, v in out.items()},
    }