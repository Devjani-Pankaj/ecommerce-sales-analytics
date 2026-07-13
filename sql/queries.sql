-- Sample analyst queries against data/warehouse.db (SQLite dialect).
-- Run via: sqlite3 data/warehouse.db < sql/queries.sql
-- or load individually in the `database.run_query()` helper.

-- 1. Monthly revenue trend
SELECT
    strftime('%Y-%m', order_date) AS month,
    ROUND(SUM(total_amount), 2)   AS revenue,
    COUNT(DISTINCT order_id)      AS orders
FROM orders
GROUP BY month
ORDER BY month;

-- 2. Top 10 products by revenue
SELECT
    p.product_name,
    p.category,
    ROUND(SUM(o.total_amount), 2) AS revenue,
    SUM(o.quantity)               AS units_sold
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;

-- 3. Revenue and average order value by region
SELECT
    c.region,
    ROUND(SUM(o.total_amount), 2)          AS revenue,
    COUNT(DISTINCT o.order_id)             AS orders,
    ROUND(AVG(o.total_amount), 2)          AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue DESC;

-- 4. Customer lifetime value (top 10 customers by total spend)
SELECT
    c.customer_id,
    c.name,
    c.region,
    COUNT(DISTINCT o.order_id)    AS num_orders,
    ROUND(SUM(o.total_amount), 2) AS lifetime_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id
ORDER BY lifetime_value DESC
LIMIT 10;

-- 5. RFM inputs computed in SQL (recency in days from most recent order date,
--    frequency = distinct orders, monetary = total spend), scored into
--    quartiles with NTILE. Combine with src/analysis.py's rfm_analysis() for
--    the pandas equivalent used by the dashboard.
WITH snapshot AS (
    SELECT DATE(MAX(order_date), '+1 day') AS snapshot_date FROM orders
),
customer_rfm AS (
    SELECT
        o.customer_id,
        CAST(julianday((SELECT snapshot_date FROM snapshot)) - julianday(MAX(o.order_date)) AS INTEGER) AS recency,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(o.total_amount), 2) AS monetary
    FROM orders o
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    recency,
    frequency,
    monetary,
    NTILE(4) OVER (ORDER BY recency DESC) AS r_score,
    NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
FROM customer_rfm
ORDER BY monetary DESC;
