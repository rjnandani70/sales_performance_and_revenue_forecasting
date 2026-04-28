# Sales Performance & Revenue Forecasting Dashboard

> End-to-end data analytics project: SQL extraction → Python EDA & forecasting → Power BI dashboard

---

## Project Overview

This project builds a complete sales analytics pipeline for a retail business with 3 years of transaction data (2022–2024). It covers data cleaning, exploratory data analysis (EDA), statistical analysis, time-series revenue forecasting, and an interactive Power BI dashboard.

**Tools:** SQL (PostgreSQL) · Python (Pandas, NumPy, Matplotlib, Prophet) · Power BI

---

## Key Results

| Metric | Value |
|--------|-------|
| Total Revenue (3 years) | ₹23.67 Crore |
| Overall Profit Margin | 35.4% |
| Total Orders Analysed | 5,000+ |
| Forecast Accuracy | 85%+ (MAPE < 15%) |
| Top Category | Electronics (53% of revenue) |
| Forecast Period | 6 months ahead (Jan–Jun 2025) |

---

## Repository Structure

```
sales_forecasting/
├── data/
│   ├── generate_data.py        # Dataset generator (realistic synthetic data)
│   └── sales_data.csv          # 5,000 rows × 11 columns, 2022–2024
│
├── sql/
│   └── analysis_queries.sql    # 10 SQL queries: KPIs, regional, YoY, segmentation
│
├── python/
│   ├── sales_analysis.py       # Full EDA + forecasting pipeline
│   └── outputs/
│       ├── 01_monthly_revenue_trend.png
│       ├── 02_revenue_by_region.png
│       ├── 03_category_performance.png
│       ├── 04_quarterly_kpi.png
│       ├── 05_discount_impact.png
│       ├── 06_revenue_forecast.png
│       ├── monthly_summary.csv
│       ├── region_summary.csv
│       ├── category_summary.csv
│       ├── revenue_forecast.csv
│       └── sales_clean.csv
│
└── powerbi_guide/
    └── POWERBI_SETUP.md        # Step-by-step Power BI dashboard guide
```

---

## Data Pipeline

```
Raw CSV  →  SQL Extraction  →  Python EDA  →  Forecasting  →  Power BI Dashboard
           (10 queries)       (5 charts)     (Prophet/        (3 pages, slicers,
                                              Trend model)     KPI cards)
```

---

## SQL Analysis (10 Queries)

The `sql/analysis_queries.sql` file covers:

1. **Table creation & data load** — PostgreSQL schema
2. **Monthly revenue trend** — time-series baseline for forecasting
3. **Regional performance** — revenue, profit, margin, avg order value
4. **Category analysis** — revenue contribution per product category
5. **Top 10 products** — by revenue with margin breakdown
6. **Quarterly KPI with QoQ growth** — window function (LAG)
7. **Discount impact analysis** — discount band vs margin
8. **Year-over-year comparison** — CASE WHEN pivot by year
9. **High-value order segmentation** — NTILE decile analysis
10. **Monthly export** — formatted for Prophet forecasting input

---

## EDA Insights

**Monthly Revenue Trend**
![Monthly Revenue](python/outputs/01_monthly_revenue_trend.png)

**Regional Performance**
![Region Revenue](python/outputs/02_revenue_by_region.png)

**Category Performance**
![Category](python/outputs/03_category_performance.png)

**Quarterly KPI**
![Quarterly KPI](python/outputs/04_quarterly_kpi.png)

**Discount Impact on Margin**
![Discount](python/outputs/05_discount_impact.png)

**Revenue Forecast — 6 Months**
![Forecast](python/outputs/06_revenue_forecast.png)

---

## Revenue Forecasting

The forecasting model uses **Facebook Prophet** (with polynomial trend + seasonal decomposition as fallback). It captures:

- **Trend**: Long-term growth/decline using changepoint detection
- **Seasonality**: Monthly seasonal patterns (Q4 peak, Q1 dip)
- **Confidence intervals**: ±12% band for planning risk assessment

**Forecasted Revenue (Jan–Jun 2025):**

| Month | Forecast | Lower Bound | Upper Bound |
|-------|----------|-------------|-------------|
| Jan 2025 | ₹49.9L | ₹43.9L | ₹55.9L |
| Feb 2025 | ₹48.2L | ₹42.4L | ₹53.9L |
| Mar 2025 | ₹59.8L | ₹52.6L | ₹66.9L |
| Apr 2025 | ₹61.0L | ₹53.7L | ₹68.3L |
| May 2025 | ₹53.7L | ₹47.3L | ₹60.2L |
| Jun 2025 | ₹46.4L | ₹40.8L | ₹51.9L |

---

## Power BI Dashboard

The dashboard has **3 pages**:

**Page 1 — Executive Summary**
- KPI cards: Total Revenue, Profit, Margin %, Total Orders
- Monthly revenue & profit trend line
- Revenue by region (filled map)
- Category performance (bar chart)

**Page 2 — Regional & Product Analysis**
- Regional KPI matrix table
- Product category treemap
- Slicers: Year, Region, Category

**Page 3 — Revenue Forecast**
- Actual vs forecast combined line chart
- Forecast table with confidence bands
- 6-month forward-looking KPI cards

See `powerbi_guide/POWERBI_SETUP.md` for full setup instructions.

---

## How to Run

```bash
# 1. Clone the repository
git clone https://github.com/rjnandani70/sales_performance_forecasting
cd sales_performance_forecasting

# 2. Install dependencies
pip install pandas numpy matplotlib prophet

# 3. Generate dataset
python data/generate_data.py

# 4. Run full analysis + forecasting
python python/sales_analysis.py

# 5. Open Power BI Desktop
# Import CSVs from python/outputs/
# Follow powerbi_guide/POWERBI_SETUP.md
```

---

## Skills Demonstrated

- **SQL**: Complex queries with window functions (LAG, NTILE), CTEs, CASE WHEN pivots, aggregations
- **Python**: Data pipeline, EDA, statistical analysis, time-series forecasting, Matplotlib visualisation
- **Power BI**: Multi-page dashboard, DAX measures, slicers, KPI cards, forecast visualisation
- **Data Engineering**: End-to-end pipeline from raw CSV → cleaned data → insights → dashboard
- **Statistical Analysis**: Seasonal decomposition, trend analysis, confidence interval estimation

---

## Author

**Raj Nandani** — Data Analyst | BFSI Domain | SQL · Python · Power BI

- LinkedIn: [linkedin.com/in/raj-nandani-824220293](https://www.linkedin.com/in/raj-nandani-824220293/)
- GitHub: [github.com/rjnandani70](https://github.com/rjnandani70)
- Email: rjnandani70@gmail.com
