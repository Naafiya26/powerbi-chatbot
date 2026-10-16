from .db import get_con

SALES_VIEW = "v_sales"
STORE_VIEW = "v_stores"
COL = {
    "sales": "sales_amount",        
    "cost": "total_cost",           
    "order": "order_number",        
    "qty": "quantity",
    "customer": "customer_key",
    "product": "product_key",
    "store_key": "store_key",
    "store_status": "status",
    "store_area": "store_area",
}
FILTER_COLS = {
    "year": "year",
    "country": "country_name",              
    "customer_country": "customer_country", 
    "continent": "continent",
    "category": "category_name",
    "subcategory": "subcategory_name",
}
STORE_FILTER_COLS = {"country": "country_name"}
OPEN = ("Open",)
CLOSED = ("Closed", "Restructured")

def _in(values):
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)

SALES, COST, ORDER, QTY = COL["sales"], COL["cost"], COL["order"], COL["qty"]
CUST, PROD = COL["customer"], COL["product"]
SK, ST, AREA = COL["store_key"], COL["store_status"], COL["store_area"]

def _k(label, expr, fmt, view, desc, aliases=()):
    return dict(label=label, expr=expr, fmt=fmt, view=view, desc=desc, aliases=aliases)

KPIS = {
    "total_revenue": _k("Total Revenue", f"SUM({SALES})", "money", SALES_VIEW,
                        "sum of sales amount", ("revenue", "total sales", "sales")),
    "total_cost": _k("Total Cost", f"SUM({COST})", "money", SALES_VIEW,
                     "sum of total cost", ("cost",)),
    "gross_profit": _k("Gross Profit", f"SUM({SALES}) - SUM({COST})", "money", SALES_VIEW,
                       "Total Revenue minus Total Cost", ("profit",)),
    "total_orders": _k("Total Orders", f"COUNT(DISTINCT {ORDER})", "count", SALES_VIEW,
                       "distinct count of order numbers (NOT row count)", ("orders", "order count")),
    "yoy_growth": _k("YoY Growth%", None, "pct", SALES_VIEW,
                     "(Revenue of selected year - Revenue of previous year) / Revenue of previous year; needs a year",
                     ("yoy", "year over year growth", "growth")),
    "quantity_sold": _k("Quantity Sold", f"SUM({QTY})", "count", SALES_VIEW,
                        "sum of quantity", ("quantity", "units sold", "total quantity")),
    "total_products": _k("Total Products", f"COUNT(DISTINCT {PROD})", "count", SALES_VIEW,
                         "distinct count of products", ("products", "product count")),
    "average_price": _k("Average Price", f"SUM({SALES}) / NULLIF(SUM({QTY}), 0)", "money", SALES_VIEW,
                        "Total Revenue / Quantity Sold", ("avg price",)),
    "customer_count": _k("Customer Count", f"COUNT(DISTINCT {CUST})", "count", SALES_VIEW,
                         "distinct count of customers", ("customers", "total customers")),
    "sales_per_customer": _k("Sales per Customer", f"SUM({SALES}) / NULLIF(COUNT(DISTINCT {CUST}), 0)",
                             "money", SALES_VIEW, "Total Revenue / Customer Count"),
    "average_order_value": _k("Average Order Value", f"SUM({SALES}) / NULLIF(COUNT(DISTINCT {ORDER}), 0)",
                              "money", SALES_VIEW, "Total Revenue / Total Orders", ("aov",)),
    "total_stores": _k("Total Stores", f"COUNT(DISTINCT {SK})", "count", STORE_VIEW,
                       "all stores in the store table", ("stores", "store count")),
    "open_stores": _k("Open Stores", f"COUNT(DISTINCT CASE WHEN {ST} IN ({_in(OPEN)}) THEN {SK} END)",
                      "count", STORE_VIEW, "stores with status Open"),
    "closed_stores": _k("Closed Stores", f"COUNT(DISTINCT CASE WHEN {ST} IN ({_in(CLOSED)}) THEN {SK} END)",
                        "count", STORE_VIEW, "stores with status Closed OR Restructured (as on the dashboard)"),
    "total_store_area": _k("Total Store Area", f"SUM({AREA})", "count", STORE_VIEW,
                           "sum of store area", ("store area",)),
}

PAGES = {
    "sales_overview": ["total_revenue", "total_cost", "gross_profit", "total_orders", "yoy_growth"],
    "product_performance": ["quantity_sold", "total_products", "total_orders", "average_price"],
    "customer_insights": ["customer_count", "sales_per_customer", "average_order_value", "total_orders"],
    "store_insights": ["total_stores", "open_stores", "closed_stores", "total_store_area"],
}

def _norm(s):
    return "".join(ch for ch in str(s).lower() if ch.isalnum())

ALIASES = {}
for _key, _v in KPIS.items():
    for _name in (_key, _v["label"], *_v["aliases"]):
        ALIASES[_norm(_name)] = _key
PAGE_ALIASES = {_norm(p): p for p in PAGES}


def fmt(value, kind):
    if value is None:
        return "N/A"
    if kind == "pct":
        return f"{value * 100:.1f}%"
    a = abs(value)
    if a >= 1e9: return f"{value / 1e9:.2f}B"
    if a >= 1e6: return f"{value / 1e6:.2f}M"
    if a >= 1e3: return f"{value / 1e3:.2f}K" if kind == "money" else f"{value / 1e3:.0f}K"
    return f"{value:,.2f}" if kind == "money" else f"{value:,.0f}"

def _exact(value, kind):
    if value is None: return "N/A"
    if kind == "pct": return f"{value * 100:.2f}%"
    return f"{value:,.2f}" if kind == "money" else f"{value:,.0f}"

def _resolve(col, view, value):
    vals = [r[0] for r in get_con().execute(
        f"SELECT DISTINCT {col} FROM {view} WHERE {col} IS NOT NULL").fetchall()]
    for v in vals:
        if str(v).lower() == str(value).lower():
            return v
    raise ValueError(f"'{value}' is not a valid value for {col}. Valid values include: "
                     f"{sorted(map(str, vals))[:25]}")

def _where(view, filters):
    cols = FILTER_COLS if view == SALES_VIEW else STORE_FILTER_COLS
    where, params, applied, ignored = [], [], {}, []
    for name, val in filters.items():
        if val in (None, "", 0):
            continue
        if name not in cols:
            ignored.append(name)
            continue
        real = _resolve(cols[name], view, val)
        where.append(f"{cols[name]} = ?")
        params.append(real)
        applied[name] = real
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    return clause, params, applied, ignored

def _scope(applied):
    parts = [f"Year {applied['year']}" if "year" in applied else "All years"]
    others = [f"{k.replace('_', ' ').title()}: {applied[k]}"
              for k in ("country", "customer_country", "continent", "category", "subcategory") if k in applied]
    parts.append(", ".join(others) if others else "no other filters")
    return " | ".join(parts)
    

def _pack(spec, value, applied, ignored, note=""):
    value = None if value is None else float(value)
    display, exact, scope = fmt(value, spec["fmt"]), _exact(value, spec["fmt"]), _scope(applied)
    answer = f"{spec['label']}: {display} (exact: {exact}) | {scope}"
    if ignored:
        answer += f" | filters not applicable to this KPI: {', '.join(ignored)}"
    if note:
        answer += f" | NOTE: {note}"
    return {"kpi": spec["label"], "display": display, "exact": exact, "scope": scope, "answer": answer}

def _sum_sales(filters):
    clause, params, applied, _ = _where(SALES_VIEW, filters)
    v = get_con().execute(f"SELECT SUM({SALES}) FROM {SALES_VIEW} {clause}", params).fetchone()[0]
    return (None if v is None else float(v)), applied

def _yoy(spec, filters):
    if not filters.get("year"):
        return _pack(spec, 0.0, {}, [],
                     "No year selected; the dashboard shows 0.0% in this case. Ask for a specific year to see real growth.")
    cur, applied = _sum_sales(filters)
    try:
        prev, _ = _sum_sales({**filters, "year": int(filters["year"]) - 1})
    except ValueError:
        return _pack(spec, None, applied, [], "No data for the previous year, so growth cannot be calculated.")
    if not prev:
        return _pack(spec, None, applied, [], "No data for the previous year, so growth cannot be calculated.")
    return _pack(spec, (cur - prev) / prev, applied, [])

def get_kpi(kpi: str, year: int = 0, country: str = "", continent: str = "",
            category: str = "", subcategory: str = "", customer_country: str = "") -> dict:
    key = ALIASES.get(_norm(kpi))
    if key is None:
        return {"error": f"Unknown KPI '{kpi}'. Available: {[v['label'] for v in KPIS.values()]}"}
    spec = KPIS[key]
    filters = dict(year=year, country=country, continent=continent, category=category,
               subcategory=subcategory, customer_country=customer_country)
    try:
        if key == "yoy_growth":
            return _yoy(spec, filters)
        clause, params, applied, ignored = _where(spec["view"], filters)
        value = get_con().execute(f"SELECT {spec['expr']} FROM {spec['view']} {clause}", params).fetchone()[0]
    except Exception as e:
        return {"error": str(e)}
    return _pack(spec, value, applied, ignored)

def get_page_kpis(page: str, year: int = 0, country: str = "", continent: str = "",
                  category: str = "", subcategory: str = "", customer_country: str = "") -> dict:
    p = PAGE_ALIASES.get(_norm(page))
    if p is None:
        return {"error": f"Unknown page. Choose one of {list(PAGES)}"}
    out = []
    for k in PAGES[p]:
        r = get_kpi(k, year, country, continent, category, subcategory)
        out.append(r.get("answer", r.get("error")))
    return {"page": p, "answers": out}