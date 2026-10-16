CREATE OR REPLACE VIEW v_sales AS
SELECT
    f.OrderKey                              AS order_number,
    f.LineNumber                            AS line_number,
    CAST(f.OrderDate AS DATE)               AS full_date,
    d.Year                                  AS year,
    d.Quarter                               AS quarter,
    d.MonthNumber                           AS month_number,
    d.Month                                 AS month,
    d.YearMonth                             AS year_month,
    d.DayofWeek                             AS day_of_week,

    f.ProductKey                            AS product_key,
    p.ProductBase                           AS product_name,
    p.Brand                                 AS brand,
    p.Color                                 AS color,
    p.CategoryName                          AS category_name,
    p.SubCategoryName                       AS subcategory_name,

    f.CustomerKey                           AS customer_key,
    c.FullName                              AS customer_name,
    c.Gender                                AS gender,
    c.Age                                   AS age,
    CASE WHEN c.Age <= 20 THEN 'BELOW 20'
         WHEN c.Age <= 30 THEN '21 - 30'
         WHEN c.Age <= 40 THEN '31 - 40'
         WHEN c.Age <= 50 THEN '41 - 50'
         WHEN c.Age <= 60 THEN '51 - 60'
         WHEN c.Age <= 70 THEN '61 - 70'
         WHEN c.Age <= 80 THEN '71 - 80'
         ELSE 'ABOVE 80' END                AS age_group,
    c.Occupation                            AS occupation,
    c.Country                               AS customer_country,
    c.Continent                             AS continent,

    f.StoreKey                              AS store_key,
    s.CountryName                           AS country_name,
    s.CountryName                           AS region,
    CASE WHEN s.CountryName = 'Online' THEN 'Online Store'
         ELSE s.State || ', ' || s.CountryName || ' #' || CAST(s.StoreKey AS VARCHAR)
    END                                     AS store_name,

    f.CurrencyCode                          AS currency_code,
    f.Quantity                              AS quantity,
    f.SalesAmountUSD                        AS sales_amount,
    f.CostAmount                            AS total_cost,
    f.SalesAmountUSD - f.CostAmount         AS profit,
    f.SalesAmount                           AS sales_amount_local
FROM fact_sales f
LEFT JOIN dim_date     d ON CAST(d.Date AS DATE) = CAST(f.OrderDate AS DATE)
LEFT JOIN dim_product  p ON p.ProductKey  = f.ProductKey
LEFT JOIN dim_customer c ON c.CustomerKey = f.CustomerKey
LEFT JOIN dim_store    s ON s.StoreKey    = f.StoreKey;
