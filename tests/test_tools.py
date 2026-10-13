from src.tools import is_safe_sql

def test_allows_select():
    assert is_safe_sql("SELECT product_name FROM v_sales LIMIT 5")

def test_blocks_dangerous():
    assert not is_safe_sql("DROP TABLE fact_sales")
    assert not is_safe_sql("SELECT 1; DELETE FROM fact_sales")