-- ============================================================
-- Sales Performance & Revenue Forecasting
-- SQL Scripts for Data Extraction & Analysis
-- Author: Raj Nandani
-- ============================================================

-- 1. CREATE TABLE
CREATE TABLE IF NOT EXISTS sales (
    order_id     VARCHAR(20) PRIMARY KEY,
    order_date   DATE NOT NULL,
    region       VARCHAR(20),
    category     VARCHAR(50),
    product      VARCHAR(50),
    unit_price   NUMERIC(12,2),
    quantity     INT,
    discount     NUMERIC(4,2),
    revenue      NUMERIC(12,2),
    cost         NUMERIC(12,2),
    profit       NUMERIC(12,2)
);
-- Load CSV (PostgreSQL):
-- COPY sales FROM '/path/to/sales_data.csv' DELIMITER ',' CSV HEADER;


-- 2. MONTHLY REVENUE TREND (used for forecasting baseline)
SELECT
    DATE_TRUNC('month', order_date)   AS month,
    SUM(revenue)                      AS total_revenue,
    SUM(profit)                       AS total_profit,
    SUM(quantity)                     AS total_units,
    ROUND(AVG(discount)*100, 1)       AS avg_discount_pct,
    COUNT(DISTINCT order_id)          AS total_orders
FROM sales
GROUP BY 1
ORDER BY 1;


-- 3. REGIONAL PERFORMANCE
SELECT
    region,
    SUM(revenue)                                        AS total_revenue,
    SUM(profit)                                         AS total_profit,
    ROUND(SUM(profit)/NULLIF(SUM(revenue),0)*100, 2)   AS profit_margin_pct,
    COUNT(DISTINCT order_id)                            AS total_orders,
    ROUND(AVG(revenue), 2)                              AS avg_order_value
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;


-- 4. PRODUCT CATEGORY ANALYSIS
SELECT
    category,
    SUM(revenue)                                        AS total_revenue,
    SUM(profit)                                         AS total_profit,
    ROUND(SUM(profit)/NULLIF(SUM(revenue),0)*100, 2)   AS profit_margin_pct,
    SUM(quantity)                                       AS units_sold
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;


-- 5. TOP 10 PRODUCTS BY REVENUE
SELECT
    product, category,
    SUM(revenue)             AS total_revenue,
    SUM(quantity)            AS units_sold,
    ROUND(AVG(unit_price),2) AS avg_price,
    ROUND(SUM(profit)/NULLIF(SUM(revenue),0)*100,2) AS margin_pct
FROM sales
GROUP BY product, category
ORDER BY total_revenue DESC
LIMIT 10;


-- 6. QUARTERLY KPI WITH QoQ GROWTH
SELECT
    EXTRACT(YEAR FROM order_date)    AS year,
    EXTRACT(QUARTER FROM order_date) AS quarter,
    SUM(revenue)                     AS total_revenue,
    SUM(profit)                      AS total_profit,
    ROUND(SUM(profit)/NULLIF(SUM(revenue),0)*100,2) AS profit_margin_pct,
    COUNT(DISTINCT order_id)         AS orders,
    ROUND(
        (SUM(revenue) - LAG(SUM(revenue)) OVER (
            ORDER BY EXTRACT(YEAR FROM order_date), EXTRACT(QUARTER FROM order_date)
        )) / NULLIF(LAG(SUM(revenue)) OVER (
            ORDER BY EXTRACT(YEAR FROM order_date), EXTRACT(QUARTER FROM order_date)
        ),0)*100, 2
    ) AS qoq_growth_pct
FROM sales
GROUP BY 1,2
ORDER BY 1,2;


-- 7. DISCOUNT IMPACT ON PROFIT MARGIN
SELECT
    CASE
        WHEN discount = 0     THEN 'No Discount'
        WHEN discount <= 0.05 THEN '1-5%'
        WHEN discount <= 0.10 THEN '6-10%'
        WHEN discount <= 0.15 THEN '11-15%'
        ELSE '16-20%'
    END                        AS discount_band,
    COUNT(*)                   AS order_count,
    ROUND(AVG(revenue),2)      AS avg_revenue,
    ROUND(AVG(profit),2)       AS avg_profit,
    ROUND(AVG(profit)/NULLIF(AVG(revenue),0)*100,2) AS avg_margin_pct
FROM sales
GROUP BY 1
ORDER BY MIN(discount);


-- 8. YEAR-OVER-YEAR MONTHLY COMPARISON
SELECT
    EXTRACT(MONTH FROM order_date)  AS month_num,
    TO_CHAR(order_date,'Month')     AS month_name,
    SUM(CASE WHEN EXTRACT(YEAR FROM order_date)=2022 THEN revenue ELSE 0 END) AS rev_2022,
    SUM(CASE WHEN EXTRACT(YEAR FROM order_date)=2023 THEN revenue ELSE 0 END) AS rev_2023,
    SUM(CASE WHEN EXTRACT(YEAR FROM order_date)=2024 THEN revenue ELSE 0 END) AS rev_2024
FROM sales
GROUP BY 1,2
ORDER BY 1;


-- 9. HIGH-VALUE ORDER SEGMENTATION (Top 10%)
WITH deciles AS (
    SELECT order_id, region, category, revenue, profit,
           NTILE(10) OVER (ORDER BY revenue DESC) AS revenue_decile
    FROM sales
)
SELECT
    revenue_decile,
    COUNT(*)               AS order_count,
    ROUND(AVG(revenue),2)  AS avg_revenue,
    ROUND(SUM(revenue),2)  AS total_revenue,
    ROUND(AVG(profit),2)   AS avg_profit
FROM deciles
GROUP BY revenue_decile
ORDER BY revenue_decile;


-- 10. MONTHLY EXPORT FOR PYTHON PROPHET FORECASTING
SELECT
    DATE_TRUNC('month', order_date)::DATE AS ds,
    ROUND(SUM(revenue),2)                 AS y
FROM sales
GROUP BY 1
ORDER BY 1;
