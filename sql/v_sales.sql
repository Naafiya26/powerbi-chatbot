CREATE OR REPLACE VIEW v_sales AS
SELECT
    f.OrderDate,f.ProductKey,f.StoreKey,f.CustomerKey,f.CurrencyCode,f.Quantity,f.SalesAmount,
    d.Date AS OrderDate, d.Year AS OrderYear, d.Quarter AS OrderQuarter, d.Month AS OrderMonth,
    p.ProductName, p.CategoryName,
    s.StoreKey, s.CountryName, s.State,
    c.FullName AS CustomerName, c.City,c.Occupation,c.Gender,c.Age,
    cu.CurrencyCode AS CurrencyCodeDim
FROM fact_sales f
JOIN dim_date     d ON f.OrderDate     = d.Date
JOIN dim_product  p ON f.ProductKey  = p.ProductKey
JOIN dim_store    s ON f.StoreKey    = s.StoreKey
JOIN dim_customer c ON f.CustomerKey = c.CustomerKey
JOIN dim_currency cu ON f.CurrencyCode = cu.CurrencyCode;
