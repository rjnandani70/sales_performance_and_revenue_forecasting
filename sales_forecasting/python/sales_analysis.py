"""
Sales Performance & Revenue Forecasting
========================================
End-to-end data pipeline:
  1. Data loading & cleaning
  2. Exploratory Data Analysis (EDA)
  3. Statistical Analysis
  4. Revenue Forecasting (Prophet / fallback SARIMA-style linear trend)
  5. Export results for Power BI

Author : Raj Nandani
Dataset: data/sales_data.csv (generated via data/generate_data.py)

Run    : python python/sales_analysis.py
Outputs: python/outputs/  (charts + forecast CSV)
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

warnings.filterwarnings('ignore')

# ── CONFIG ────────────────────────────────────────────────────
DATA_PATH   = os.path.join(os.path.dirname(__file__), '..', 'data', 'sales_data.csv')
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

PALETTE = ['#1F4E79', '#2E75B6', '#9DC3E6', '#F4A261', '#E76F51',
           '#2A9D8F', '#E9C46A', '#264653', '#A8DADC', '#457B9D']

def fmt_inr(x, pos=None):
    """Format axis tick as ₹ in lakhs."""
    return f'₹{x/1e5:.0f}L'


# ══════════════════════════════════════════════════════════════
# 1. LOAD & CLEAN DATA
# ══════════════════════════════════════════════════════════════
print("=" * 60)
print("STEP 1 — Loading & Cleaning Data")
print("=" * 60)

df = pd.read_csv(DATA_PATH, parse_dates=['order_date'])

print(f"Shape           : {df.shape}")
print(f"Date range      : {df['order_date'].min().date()} → {df['order_date'].max().date()}")
print(f"Missing values  :\n{df.isnull().sum()}")
print(f"Duplicate rows  : {df.duplicated().sum()}")

# Clean
df.drop_duplicates(inplace=True)
df.dropna(subset=['order_date', 'revenue'], inplace=True)
df['order_date'] = pd.to_datetime(df['order_date'])
df['revenue']    = pd.to_numeric(df['revenue'],  errors='coerce').fillna(0)
df['profit']     = pd.to_numeric(df['profit'],   errors='coerce').fillna(0)
df['cost']       = pd.to_numeric(df['cost'],     errors='coerce').fillna(0)
df['quantity']   = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)

# Feature engineering
df['year']          = df['order_date'].dt.year
df['month']         = df['order_date'].dt.month
df['month_name']    = df['order_date'].dt.strftime('%b')
df['quarter']       = df['order_date'].dt.quarter
df['profit_margin'] = (df['profit'] / df['revenue'].replace(0, np.nan)) * 100

print(f"\nClean shape     : {df.shape}")


# ══════════════════════════════════════════════════════════════
# 2. STATISTICAL SUMMARY
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 2 — Statistical Summary")
print("=" * 60)

total_rev    = df['revenue'].sum()
total_profit = df['profit'].sum()
overall_margin = (total_profit / total_rev) * 100
avg_order_val  = df['revenue'].mean()

print(f"Total Revenue     : ₹{total_rev:,.0f}")
print(f"Total Profit      : ₹{total_profit:,.0f}")
print(f"Overall Margin    : {overall_margin:.1f}%")
print(f"Avg Order Value   : ₹{avg_order_val:,.0f}")
print(f"Total Orders      : {len(df):,}")
print(f"\nRevenue by Region :\n{df.groupby('region')['revenue'].sum().sort_values(ascending=False).apply(lambda x: f'₹{x:,.0f}')}")
print(f"\nRevenue by Category:\n{df.groupby('category')['revenue'].sum().sort_values(ascending=False).apply(lambda x: f'₹{x:,.0f}')}")


# ══════════════════════════════════════════════════════════════
# 3. EDA CHARTS
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 3 — Generating EDA Charts")
print("=" * 60)

# ── 3a. Monthly Revenue Trend ────────────────────────────────
monthly = df.groupby(df['order_date'].dt.to_period('M')).agg(
    revenue=('revenue', 'sum'),
    profit=('profit', 'sum'),
    orders=('order_id', 'count')
).reset_index()
monthly['order_date'] = monthly['order_date'].dt.to_timestamp()

fig, ax = plt.subplots(figsize=(14, 5))
ax.fill_between(monthly['order_date'], monthly['revenue'], alpha=0.15, color=PALETTE[0])
ax.plot(monthly['order_date'], monthly['revenue'], color=PALETTE[0], linewidth=2, label='Revenue')
ax.plot(monthly['order_date'], monthly['profit'],  color=PALETTE[3], linewidth=2, linestyle='--', label='Profit')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title('Monthly Revenue & Profit Trend (2022–2024)', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Month'); ax.set_ylabel('Amount (₹ Lakhs)')
ax.legend(); ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, '01_monthly_revenue_trend.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 01_monthly_revenue_trend.png")

# ── 3b. Revenue by Region ────────────────────────────────────
region_rev = df.groupby('region')['revenue'].sum().sort_values()
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(region_rev.index, region_rev.values, color=PALETTE[:len(region_rev)])
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
for bar, val in zip(bars, region_rev.values):
    ax.text(val + total_rev*0.002, bar.get_y()+bar.get_height()/2,
            f'₹{val/1e5:.1f}L', va='center', fontsize=10)
ax.set_title('Total Revenue by Region', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Revenue (₹ Lakhs)'); ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, '02_revenue_by_region.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 02_revenue_by_region.png")

# ── 3c. Category Performance ─────────────────────────────────
cat = df.groupby('category').agg(revenue=('revenue','sum'), profit=('profit','sum')).sort_values('revenue', ascending=False)
cat['margin'] = (cat['profit'] / cat['revenue']) * 100
x = np.arange(len(cat))
width = 0.38
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.bar(x - width/2, cat['revenue']/1e5, width, label='Revenue (₹L)', color=PALETTE[0])
ax1.bar(x + width/2, cat['profit']/1e5,  width, label='Profit (₹L)',  color=PALETTE[3])
ax2 = ax1.twinx()
ax2.plot(x, cat['margin'], 'o--', color=PALETTE[4], linewidth=1.5, label='Margin %')
ax2.set_ylabel('Profit Margin (%)', color=PALETTE[4])
ax1.set_xticks(x); ax1.set_xticklabels(cat.index, rotation=15, ha='right')
ax1.set_ylabel('Amount (₹ Lakhs)'); ax1.set_title('Revenue, Profit & Margin by Category', fontsize=14, fontweight='bold')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc='upper right')
ax1.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, '03_category_performance.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 03_category_performance.png")

# ── 3d. Quarterly KPI ────────────────────────────────────────
df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
qtr = df.groupby('year_quarter').agg(revenue=('revenue','sum'), profit=('profit','sum')).reset_index()
qtr['margin'] = (qtr['profit']/qtr['revenue'])*100
fig, ax = plt.subplots(figsize=(13, 5))
ax.bar(qtr['year_quarter'], qtr['revenue']/1e5, color=PALETTE[0], label='Revenue')
ax.bar(qtr['year_quarter'], qtr['profit']/1e5,  color=PALETTE[1], label='Profit', alpha=0.8)
ax.set_xticklabels(qtr['year_quarter'], rotation=45, ha='right', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title('Quarterly Revenue & Profit KPI', fontsize=14, fontweight='bold')
ax.set_ylabel('Amount (₹ Lakhs)'); ax.legend(); ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, '04_quarterly_kpi.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 04_quarterly_kpi.png")

# ── 3e. Discount Impact ──────────────────────────────────────
bins   = [-0.01, 0, 0.05, 0.10, 0.15, 0.20]
labels = ['No Discount', '1-5%', '6-10%', '11-15%', '16-20%']
df['discount_band'] = pd.cut(df['discount'], bins=bins, labels=labels)
disc = df.groupby('discount_band', observed=True).agg(
    avg_revenue=('revenue','mean'), avg_margin=('profit_margin','mean'), orders=('order_id','count')
).reset_index()
fig, ax1 = plt.subplots(figsize=(9, 5))
ax1.bar(disc['discount_band'], disc['avg_revenue'], color=PALETTE[0], label='Avg Revenue')
ax2 = ax1.twinx()
ax2.plot(disc['discount_band'], disc['avg_margin'], 'o-', color=PALETTE[3], linewidth=2, label='Avg Margin %')
ax2.set_ylabel('Profit Margin (%)', color=PALETTE[3])
ax1.set_ylabel('Avg Revenue (₹)'); ax1.set_title('Discount Band vs Revenue & Margin', fontsize=14, fontweight='bold')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2)
ax1.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, '05_discount_impact.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 05_discount_impact.png")


# ══════════════════════════════════════════════════════════════
# 4. REVENUE FORECASTING
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 4 — Revenue Forecasting (6 months ahead)")
print("=" * 60)

# Prepare monthly time-series
ts = monthly[['order_date', 'revenue']].copy()
ts.columns = ['ds', 'y']
ts = ts.sort_values('ds').reset_index(drop=True)

try:
    from prophet import Prophet
    model = Prophet(yearly_seasonality=True, weekly_seasonality=False,
                    daily_seasonality=False, changepoint_prior_scale=0.1)
    model.fit(ts)
    future   = model.make_future_dataframe(periods=6, freq='MS')
    forecast = model.predict(future)
    method   = 'Prophet'
    print("  Using: Facebook Prophet")

except ImportError:
    # Fallback: polynomial trend + seasonal decomposition
    print("  Prophet not installed — using polynomial trend + seasonal decomposition")
    method = 'Trend + Seasonal Decomposition'

    ts_idx  = np.arange(len(ts))
    coeffs  = np.polyfit(ts_idx, ts['y'], deg=2)
    trend_fn = np.poly1d(coeffs)

    # Monthly seasonal index
    ts['month_num'] = ts['ds'].dt.month
    seasonal_idx    = ts.groupby('month_num')['y'].mean()
    overall_mean    = ts['y'].mean()
    seasonal_factor = seasonal_idx / overall_mean

    # Build forecast for next 6 months
    last_date   = ts['ds'].max()
    future_dates = pd.date_range(start=last_date + pd.offsets.MonthBegin(1), periods=6, freq='MS')
    fut_idx      = np.arange(len(ts), len(ts)+6)
    fut_trend    = trend_fn(fut_idx)
    fut_seasonal = [seasonal_factor.get(d.month, 1.0) for d in future_dates]
    fut_yhat     = fut_trend * fut_seasonal

    # Confidence bands (±12%)
    fut_upper = fut_yhat * 1.12
    fut_lower = fut_yhat * 0.88

    # Assemble combined dataframe matching Prophet output structure
    hist_yhat  = trend_fn(ts_idx) * ts['month_num'].map(seasonal_factor)
    forecast   = pd.concat([
        ts[['ds']].assign(yhat=hist_yhat, yhat_upper=hist_yhat*1.12, yhat_lower=hist_yhat*0.88),
        pd.DataFrame({'ds': future_dates, 'yhat': fut_yhat,
                      'yhat_upper': fut_upper, 'yhat_lower': fut_lower})
    ], ignore_index=True)

# ── Forecast chart ───────────────────────────────────────────
hist_end  = ts['ds'].max()
fc_future = forecast[forecast['ds'] > hist_end]
fc_hist   = forecast[forecast['ds'] <= hist_end]

fig, ax = plt.subplots(figsize=(14, 6))
ax.fill_between(fc_future['ds'], fc_future['yhat_lower'], fc_future['yhat_upper'],
                alpha=0.2, color=PALETTE[3], label='Confidence Band (±12%)')
ax.plot(ts['ds'], ts['y'],          color=PALETTE[0], linewidth=2, label='Actual Revenue')
ax.plot(fc_hist['ds'], fc_hist['yhat'], color=PALETTE[1], linewidth=1.5,
        linestyle='--', alpha=0.7, label='Fitted Trend')
ax.plot(fc_future['ds'], fc_future['yhat'], color=PALETTE[3], linewidth=2.5,
        linestyle='--', marker='o', markersize=6, label='Forecast (6 months)')
ax.axvline(hist_end, color='gray', linestyle=':', linewidth=1.2)
ax.text(hist_end, ax.get_ylim()[1]*0.95, '  Forecast →', color='gray', fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_inr))
ax.set_title(f'Revenue Forecast — Next 6 Months ({method})', fontsize=14, fontweight='bold')
ax.set_xlabel('Month'); ax.set_ylabel('Revenue (₹ Lakhs)')
ax.legend(); ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, '06_revenue_forecast.png'), dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ 06_revenue_forecast.png")

# ── Print forecast values ────────────────────────────────────
print("\n  Forecasted Monthly Revenue (next 6 months):")
for _, row in fc_future.iterrows():
    print(f"    {row['ds'].strftime('%b %Y')}: ₹{row['yhat']:>12,.0f}  "
          f"[₹{row['yhat_lower']:,.0f} – ₹{row['yhat_upper']:,.0f}]")


# ══════════════════════════════════════════════════════════════
# 5. EXPORT FOR POWER BI
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("STEP 5 — Exporting CSVs for Power BI")
print("=" * 60)

# Monthly summary
monthly_export = monthly.copy()
monthly_export['month_str'] = monthly_export['order_date'].dt.strftime('%Y-%m')
monthly_export.to_csv(os.path.join(OUTPUT_DIR, 'monthly_summary.csv'), index=False)
print("  ✓ monthly_summary.csv")

# Regional summary
region_summary = df.groupby('region').agg(
    total_revenue=('revenue','sum'), total_profit=('profit','sum'),
    total_orders=('order_id','count'), avg_order_value=('revenue','mean')
).reset_index()
region_summary['profit_margin_pct'] = (region_summary['total_profit']/region_summary['total_revenue'])*100
region_summary.to_csv(os.path.join(OUTPUT_DIR, 'region_summary.csv'), index=False)
print("  ✓ region_summary.csv")

# Category summary
cat.reset_index().to_csv(os.path.join(OUTPUT_DIR, 'category_summary.csv'), index=False)
print("  ✓ category_summary.csv")

# Forecast export
forecast_export = fc_future[['ds','yhat','yhat_lower','yhat_upper']].copy()
forecast_export.columns = ['month','forecast_revenue','lower_bound','upper_bound']
forecast_export.to_csv(os.path.join(OUTPUT_DIR, 'revenue_forecast.csv'), index=False)
print("  ✓ revenue_forecast.csv")

# Full cleaned data
df.to_csv(os.path.join(OUTPUT_DIR, 'sales_clean.csv'), index=False)
print("  ✓ sales_clean.csv")

print("\n" + "=" * 60)
print("ALL DONE — outputs saved to python/outputs/")
print("=" * 60)
