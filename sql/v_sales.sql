CREATE OR REPLACE VIEW v_sales AS
SELECT
    f.*,
    d.date, d.year, d.quarter, d.month,
    p.ProductName, p.CategoryName,
    s.StoreKey, s.CountryName, s.State,
    c.FullName, c.City
FROM fact_sales f
JOIN dim_date     d ON f.OrderDate     = d.date
JOIN dim_product  p ON f.ProductKey  = p.ProductKey
JOIN dim_store    s ON f.StoreKey    = s.StoreKey
JOIN dim_customer c ON f.CustomerKey = c.CustomerKey
JOIN dim_currency cu ON f.CurrencyCode = cu.CurrencyCode;
