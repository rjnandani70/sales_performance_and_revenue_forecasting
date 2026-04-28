# Power BI Dashboard Setup Guide
## Sales Performance & Revenue Forecasting

---

## Step 1 — Import Data

Open Power BI Desktop → **Get Data → Text/CSV**

Import these 5 files from `python/outputs/`:

| File | Used For |
|------|----------|
| `sales_clean.csv` | Main fact table |
| `monthly_summary.csv` | Revenue trend line chart |
| `region_summary.csv` | Regional KPI table & map |
| `category_summary.csv` | Category bar chart |
| `revenue_forecast.csv` | Forecast chart |

---

## Step 2 — Data Model

In **Model view**, create relationships:
- `sales_clean[order_date]` → `monthly_summary[order_date]` (Many-to-One)

---

## Step 3 — DAX Measures

Create these measures in the `sales_clean` table:

```dax
Total Revenue =
    SUM(sales_clean[revenue])

Total Profit =
    SUM(sales_clean[profit])

Profit Margin % =
    DIVIDE(SUM(sales_clean[profit]), SUM(sales_clean[revenue]), 0) * 100

Total Orders =
    COUNTROWS(sales_clean)

Avg Order Value =
    AVERAGE(sales_clean[revenue])

MoM Revenue Growth % =
    VAR CurrentMonth = [Total Revenue]
    VAR PrevMonth =
        CALCULATE([Total Revenue],
            DATEADD(sales_clean[order_date], -1, MONTH))
    RETURN
        DIVIDE(CurrentMonth - PrevMonth, PrevMonth, 0) * 100

YTD Revenue =
    TOTALYTD([Total Revenue], sales_clean[order_date])
```

---

## Step 4 — Dashboard Layout (3 Pages)

### Page 1: Executive Summary
```
┌──────────────────────────────────────────────────────────┐
│  KPI Cards (Row 1)                                       │
│  [Total Revenue]  [Total Profit]  [Margin%]  [Orders]   │
├──────────────────────────────────────────────────────────┤
│  Monthly Revenue Trend (Line Chart)     │ Region Map     │
│  X: month_str  Y: total_revenue         │ (Filled Map)   │
├──────────────────────────────────────────────────────────┤
│  Category Revenue (Bar Chart)           │ Top Products   │
│  X: category  Y: total_revenue          │ (Table visual) │
└──────────────────────────────────────────────────────────┘
```

**Slicers to add:**
- Year (2022, 2023, 2024)
- Region (North, South, East, West, Central)
- Category (Electronics, Clothing, Furniture, etc.)

---

### Page 2: Regional & Product Deep Dive
```
┌──────────────────────────────────────────────────────────┐
│  Regional KPIs (Matrix Table)                            │
│  Rows: region                                            │
│  Cols: total_revenue, total_profit, profit_margin_pct,  │
│        total_orders, avg_order_value                     │
├──────────────────────────────────────────────────────────┤
│  Revenue by Region (Clustered Bar)  │ Margin by Region  │
│                                     │ (Donut Chart)     │
├──────────────────────────────────────────────────────────┤
│  Product Revenue Treemap                                 │
│  Group: category  Values: revenue                        │
└──────────────────────────────────────────────────────────┘
```

---

### Page 3: Revenue Forecast
```
┌──────────────────────────────────────────────────────────┐
│  Forecast KPI Cards                                      │
│  [Next Month Forecast]  [6-Month Total]  [Avg Growth]   │
├──────────────────────────────────────────────────────────┤
│  Combined Actual + Forecast Line Chart                   │
│  - Line 1: monthly_summary[total_revenue] (Actual)      │
│  - Line 2: revenue_forecast[forecast_revenue] (Forecast) │
│  - Error bars: lower_bound / upper_bound                 │
├──────────────────────────────────────────────────────────┤
│  Forecast Table                                          │
│  Cols: month, forecast_revenue, lower_bound, upper_bound │
└──────────────────────────────────────────────────────────┘
```

---

## Step 5 — Formatting Tips

- **Theme**: Use "Executive" or "Accessible Default" built-in theme
- **KPI Card color**: Dark blue `#1F4E79` for positive metrics
- **Bar chart color**: Use "Diverging" color scale for margin %
- **Forecast line**: Make it dashed/orange to distinguish from actuals
- **Title font**: Segoe UI, 14pt Bold for page titles
- **Add data labels** on bar charts for easy reading

---

## Step 6 — Publish

1. **File → Publish → My Workspace** (requires Power BI account)
2. Take screenshots of each page
3. Save screenshots to `powerbi_guide/screenshots/` folder
4. Add screenshot links to README.md

---

## Quick Color Reference

| Element | Hex |
|---------|-----|
| Primary Blue | `#1F4E79` |
| Secondary Blue | `#2E75B6` |
| Highlight Orange | `#F4A261` |
| Profit Green | `#2A9D8F` |
| Loss Red | `#E76F51` |
