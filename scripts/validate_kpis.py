import sys
from src.metrics import get_kpi

EXPECTED = {
    "Total Revenue": "219.84M", "Total Cost": "96.48M", "Gross Profit": "123.35M",
    "Total Orders": "93K", "YoY Growth%": "0.0%",
    "Quantity Sold": "704K", "Total Products": "3K", "Average Price": "312.44",
    "Customer Count": "52K", "Sales per Customer": "4.21K", "Average Order Value": "2.35K",
    "Total Stores": "74", "Open Stores": "59", "Closed Stores": "15", "Total Store Area": "109K",
}

failed = 0
print(f"{'KPI':22} {'Dashboard':>10} {'Chatbot':>10}  Result")
for name, want in EXPECTED.items():
    r = get_kpi(name)
    got = r.get("display", r.get("error", "ERROR"))
    ok = got == want
    failed += not ok
    print(f"{name:22} {want:>10} {got:>10}  {'PASS' if ok else 'FAIL  exact=' + str(r.get('exact'))}")
print(f"\n{len(EXPECTED) - failed}/{len(EXPECTED)} KPIs match the dashboard")
sys.exit(1 if failed else 0)