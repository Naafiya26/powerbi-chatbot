CREATE OR REPLACE VIEW v_stores AS
SELECT
    StoreKey                      AS store_key,
    CountryName                   AS country_name,
    State                         AS state,
    SquareMeters                  AS store_area,
    CAST(OpenDate AS DATE)        AS open_date,
    CAST(CloseDate AS DATE)       AS close_date,
    YEAR(CAST(OpenDate AS DATE))  AS open_year,
    COALESCE(Status, 'Open')      AS status
FROM dim_store;