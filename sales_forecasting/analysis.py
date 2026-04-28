# ============================================================
# Sales Performance & Revenue Forecasting
# End-to-End Pipeline: Data Cleaning → EDA → Statistical Analysis
#                       → Time-Series Forecasting (Trend + Fourier Seasonality)
# Author : Raj Nandani
# Tools  : Python · Pandas · NumPy · Matplotlib · Seaborn · SciPy
# ============================================================

import os, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit

warnings.filterwarnings('ignore')
os.makedirs('images', exist_ok=True)

# ── Style ────────────────────────────────────────────────────
plt.rcParams.update({'figure.dpi': 130, 'axes.spines.top': False,
                     'axes.spines.right': False, 'font.family': 'DejaVu Sans',
                     'axes.titlesize': 13, 'axes.titleweight': 'bold'})
BLUE, TEAL, AMBER, CORAL, GRAY = '#1F4E79','#1D9E75','#EF9F27','#D85A30','#888780'
PALETTE = [BLUE, TEAL, AMBER, CORAL, GRAY]
INR = mticker.FuncFormatter(lambda x, _: f'Rs.{x/1e6:.1f}M')

# ═══════════════════════════════════════════════════════════
# SECTION 1 – DATA PIPELINE
# ═══════════════════════════════════════════════════════════
print("="*60, "\nSECTION 1: DATA PIPELINE\n" + "="*60)

df = pd.read_csv('data/sales_data.csv', parse_dates=['order_date'])
print(f"\nLoaded  : {len(df):,} rows x {df.shape[1]} cols")
print("Dtypes  :\n", df.dtypes)
print("Nulls   :\n", df.isnull().sum())
print("Summary :\n", df.describe().round(2))

df.drop_duplicates(inplace=True); df.dropna(inplace=True)
df['revenue'] = df['revenue'].clip(lower=0)
df['profit']  = df['profit'].clip(lower=0)
df['year']    = df['order_date'].dt.year
df['month']   = df['order_date'].dt.month
df['quarter'] = df['order_date'].dt.quarter
df['profit_margin'] = df['profit'] / df['revenue'].replace(0, np.nan)
print(f"\nCleaned : {len(df):,} rows | {df['order_date'].min().date()} to {df['order_date'].max().date()}")

# ═══════════════════════════════════════════════════════════
# SECTION 2 – EDA
# ═══════════════════════════════════════════════════════════
print("\n"+"="*60, "\nSECTION 2: EDA\n" + "="*60)

total_rev  = df['revenue'].sum()
total_prof = df['profit'].sum()
avg_margin = df['profit_margin'].mean() * 100
print(f"\nTotal Revenue  : Rs.{total_rev:,.0f}"
      f"\nTotal Profit   : Rs.{total_prof:,.0f}"
      f"\nTotal Orders   : {df['order_id'].nunique():,}"
      f"\nAvg Order Value: Rs.{df['revenue'].mean():,.0f}"
      f"\nAvg Margin     : {avg_margin:.1f}%")

monthly = (df.groupby(df['order_date'].dt.to_period('M'))
             .agg(revenue=('revenue','sum'), orders=('order_id','count'))
             .reset_index())
monthly['order_date'] = monthly['order_date'].dt.to_timestamp()

region_rev = (df.groupby('region').agg(revenue=('revenue','sum'), profit=('profit','sum'),
               orders=('order_id','count')).sort_values('revenue', ascending=False).reset_index())
region_rev['margin_pct'] = (region_rev['profit']/region_rev['revenue']*100).round(1)
print("\nRegion Revenue:\n", region_rev.to_string(index=False))

cat_rev = (df.groupby('category').agg(revenue=('revenue','sum'), profit=('profit','sum'))
             .sort_values('revenue', ascending=False).reset_index())
cat_rev['share_pct'] = (cat_rev['revenue']/cat_rev['revenue'].sum()*100).round(1)
print("\nCategory Revenue:\n", cat_rev.to_string(index=False))

quarterly = (df.groupby(['year','quarter']).agg(revenue=('revenue','sum'), profit=('profit','sum'),
              orders=('order_id','count')).reset_index())
quarterly['margin_pct'] = (quarterly['profit']/quarterly['revenue']*100).round(1)
print("\nQuarterly KPIs:\n", quarterly.to_string(index=False))

disc_bins = pd.cut(df['discount'], bins=[-0.01,0.001,0.09,0.14,0.21],
                   labels=['No Discount','1-9%','10-14%','15-20%'])
disc_df = (df.groupby(disc_bins, observed=True)
             .agg(orders=('order_id','count'), avg_margin=('profit_margin','mean'),
                  total_revenue=('revenue','sum')).reset_index())
disc_df['avg_margin'] = (disc_df['avg_margin']*100).round(1)
print("\nDiscount Impact:\n", disc_df.to_string(index=False))

# ═══════════════════════════════════════════════════════════
# SECTION 3 – VISUALIZATIONS
# ═══════════════════════════════════════════════════════════
print("\n"+"="*60, "\nSECTION 3: CHARTS\n" + "="*60)

# 1: Monthly Trend
fig, ax = plt.subplots(figsize=(12,4))
ax.fill_between(monthly['order_date'], monthly['revenue'], alpha=.15, color=BLUE)
ax.plot(monthly['order_date'], monthly['revenue'], color=BLUE, lw=2.2, marker='o', ms=4)
ax.yaxis.set_major_formatter(INR); ax.set_title('Monthly Revenue Trend (2022-2024)')
ax.tick_params(axis='x', rotation=30)
plt.tight_layout(); plt.savefig('images/01_monthly_revenue_trend.png', bbox_inches='tight'); plt.close()
print("Saved: 01_monthly_revenue_trend.png")

# 2: Region
fig, axes = plt.subplots(1,2, figsize=(12,4))
axes[0].barh(region_rev['region'], region_rev['revenue'], color=PALETTE)
axes[0].xaxis.set_major_formatter(INR); axes[0].set_title('Revenue by Region'); axes[0].invert_yaxis()
axes[1].pie(region_rev['revenue'], labels=region_rev['region'], autopct='%1.1f%%',
            colors=PALETTE, startangle=140, textprops={'fontsize':9})
axes[1].set_title('Revenue Share')
plt.tight_layout(); plt.savefig('images/02_revenue_by_region.png', bbox_inches='tight'); plt.close()
print("Saved: 02_revenue_by_region.png")

# 3: Category
fig, ax = plt.subplots(figsize=(10,4))
x, w = np.arange(len(cat_rev)), 0.4
ax.bar(x-w/2, cat_rev['revenue']/1e6, width=w, label='Revenue(M)', color=BLUE, alpha=.85)
ax.bar(x+w/2, cat_rev['profit']/1e6,  width=w, label='Profit(M)',  color=TEAL, alpha=.85)
ax.set_xticks(x); ax.set_xticklabels(cat_rev['category'], rotation=15)
ax.set_ylabel('Rs. Millions'); ax.set_title('Revenue vs Profit by Category'); ax.legend()
plt.tight_layout(); plt.savefig('images/03_category_performance.png', bbox_inches='tight'); plt.close()
print("Saved: 03_category_performance.png")

# 4: Quarterly Heatmap
pivot = quarterly.pivot(index='year', columns='quarter', values='revenue')/1e6
fig, ax = plt.subplots(figsize=(8,3))
sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlGnBu', linewidths=.5, ax=ax, cbar_kws={'label':'Rs.M'})
ax.set_title('Quarterly Revenue Heatmap (Rs. Millions)')
plt.tight_layout(); plt.savefig('images/04_quarterly_heatmap.png', bbox_inches='tight'); plt.close()
print("Saved: 04_quarterly_heatmap.png")

# 5: Discount Impact
fig, ax = plt.subplots(figsize=(8,4))
c_d = [TEAL if v>30 else AMBER if v>25 else CORAL for v in disc_df['avg_margin']]
bars = ax.bar(disc_df['discount'].astype(str), disc_df['avg_margin'], color=c_d, alpha=.85)
ax.axhline(avg_margin, color=GRAY, ls='--', lw=1.2, label=f'Overall avg: {avg_margin:.1f}%')
ax.set_ylabel('Avg Profit Margin (%)'); ax.set_title('Discount Band vs Profit Margin'); ax.legend()
for bar, val in zip(bars, disc_df['avg_margin']):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.3, f'{val:.1f}%', ha='center', fontsize=10)
plt.tight_layout(); plt.savefig('images/05_discount_impact.png', bbox_inches='tight'); plt.close()
print("Saved: 05_discount_impact.png")

# ═══════════════════════════════════════════════════════════
# SECTION 4 – FORECASTING (Trend + Fourier Seasonality)
# ═══════════════════════════════════════════════════════════
print("\n"+"="*60, "\nSECTION 4: REVENUE FORECASTING\n" + "="*60)

ts = (df.groupby(df['order_date'].dt.to_period('M'))['revenue']
        .sum().reset_index())
ts.columns = ['period', 'revenue']
ts['date'] = ts['period'].dt.to_timestamp()
ts = ts.sort_values('date').reset_index(drop=True)
ts['t'] = np.arange(len(ts))            # integer time index
print(f"\n{len(ts)} monthly data points | Train/Test split: last 6 months = test")

# Build Fourier features (captures annual seasonality)
def fourier_features(t, periods=12, n_terms=3):
    feats = []
    for k in range(1, n_terms+1):
        feats.append(np.sin(2*np.pi*k*t/periods))
        feats.append(np.cos(2*np.pi*k*t/periods))
    return np.column_stack(feats)

def forecast_model(t, *params):
    # params: [trend_intercept, trend_slope, sin1, cos1, sin2, cos2, sin3, cos3]
    trend    = params[0] + params[1]*t
    seasonal = sum(params[2+2*k]*np.sin(2*np.pi*(k+1)*t/12) +
                   params[3+2*k]*np.cos(2*np.pi*(k+1)*t/12) for k in range(3))
    return trend + seasonal

n_params = 8   # intercept + slope + 6 Fourier coefficients
train_mask = ts['t'] < len(ts) - 6
train_t  = ts.loc[train_mask, 't'].values
train_y  = ts.loc[train_mask, 'revenue'].values
test_t   = ts.loc[~train_mask, 't'].values
test_y   = ts.loc[~train_mask, 'revenue'].values

p0 = np.ones(n_params) * train_y.mean() / n_params
popt, _ = curve_fit(forecast_model, train_t, train_y, p0=p0, maxfev=50000)
print("Model fitted successfully (Trend + 3-term Fourier seasonality)")

test_pred = forecast_model(test_t, *popt)
mape      = np.mean(np.abs((test_y - test_pred) / test_y)) * 100
accuracy  = 100 - mape
print(f"\nModel Evaluation:")
print(f"  MAPE     : {mape:.2f}%")
print(f"  Accuracy : {accuracy:.2f}%")

# Re-fit on full data for 12-month ahead forecast
popt_full, _ = curve_fit(forecast_model, ts['t'].values, ts['revenue'].values,
                          p0=popt, maxfev=50000)
future_t = np.arange(len(ts), len(ts)+12)
future_dates = pd.date_range(ts['date'].max() + pd.offsets.MonthBegin(1), periods=12, freq='MS')
future_pred  = forecast_model(future_t, *popt_full)

# Residual std → confidence interval
residuals = ts['revenue'].values - forecast_model(ts['t'].values, *popt_full)
ci_width  = 1.96 * residuals.std()

print("\n12-Month Revenue Forecast:")
for d, v in zip(future_dates, future_pred):
    lo, hi = max(v - ci_width, 0), v + ci_width
    print(f"  {d.strftime('%b %Y')} : Rs.{v:>12,.0f}  (Rs.{lo:,.0f} - Rs.{hi:,.0f})")

# Seasonal decomposition (additive via moving average)
ts_series = ts.set_index('date')['revenue']
window    = 12
trend_ma  = ts_series.rolling(window=window, center=True).mean()
detrended = ts_series / trend_ma.replace(0, np.nan)
seasonal_avg = detrended.groupby(detrended.index.month).transform('mean')
residual  = ts_series / (trend_ma * seasonal_avg).replace(0, np.nan)

fig, axes = plt.subplots(4, 1, figsize=(12, 10))
for ax, data, title in zip(axes,
    [ts_series, trend_ma, seasonal_avg, residual],
    ['Observed Revenue', 'Trend (12-Month MA)', 'Seasonality Index', 'Residuals']):
    ax.plot(data.index, data.values, color=BLUE, lw=1.5)
    ax.set_title(title)
    if title in ['Observed Revenue', 'Trend (12-Month MA)']:
        ax.yaxis.set_major_formatter(INR)
fig.suptitle('Time-Series Decomposition', fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout(); plt.savefig('images/06_decomposition.png', bbox_inches='tight'); plt.close()
print("Saved: 06_decomposition.png")

# Actual vs Predicted (test)
fig, ax = plt.subplots(figsize=(9,4))
ax.plot(ts.loc[~train_mask, 'date'], test_y,    color=BLUE,  marker='o', lw=2,   label='Actual')
ax.plot(ts.loc[~train_mask, 'date'], test_pred, color=CORAL, marker='s', lw=2, ls='--', label='Predicted')
ax.yaxis.set_major_formatter(INR)
ax.set_title(f'Actual vs Predicted - Test Set  |  Accuracy: {accuracy:.1f}%')
ax.legend(); ax.tick_params(axis='x', rotation=15)
plt.tight_layout(); plt.savefig('images/07_actual_vs_predicted.png', bbox_inches='tight'); plt.close()
print("Saved: 07_actual_vs_predicted.png")

# Full forecast chart
fitted_all = forecast_model(ts['t'].values, *popt_full)
fig, ax = plt.subplots(figsize=(13,5))
ax.fill_between(future_dates, future_pred - ci_width, future_pred + ci_width,
                alpha=.15, color=TEAL, label='95% Confidence Interval')
ax.plot(ts['date'], ts['revenue'],  color=BLUE,  lw=2,   ms=3, marker='o', label='Historical Revenue')
ax.plot(ts['date'], fitted_all,     color=GRAY,  lw=1.2, ls=':', label='Fitted Model')
ax.plot(future_dates, future_pred,  color=CORAL, lw=2.2, ms=4, marker='s', ls='--', label='Forecast (Next 12 Months)')
ax.axvline(ts['date'].max(), color=GRAY, ls=':', lw=1.5, label='Forecast Start')
ax.yaxis.set_major_formatter(INR)
ax.set_title('Revenue Forecast - Historical + Next 12 Months')
ax.legend(fontsize=9); ax.tick_params(axis='x', rotation=30)
plt.tight_layout(); plt.savefig('images/08_revenue_forecast.png', bbox_inches='tight'); plt.close()
print("Saved: 08_revenue_forecast.png")

# ═══════════════════════════════════════════════════════════
# SECTION 5 – EXPORT FOR POWER BI
# ═══════════════════════════════════════════════════════════
print("\n"+"="*60, "\nSECTION 5: EXPORT FOR POWER BI\n" + "="*60)

monthly_agg = (df.groupby([df['order_date'].dt.to_period('M'), 'region', 'category'])
                 .agg(orders=('order_id','count'), revenue=('revenue','sum'),
                      profit=('profit','sum'), avg_discount=('discount','mean'))
                 .reset_index())
monthly_agg['order_date'] = monthly_agg['order_date'].dt.to_timestamp()
monthly_agg['profit_margin_pct'] = (monthly_agg['profit']/monthly_agg['revenue']*100).round(2)
monthly_agg.to_csv('data/monthly_aggregated.csv', index=False)
print("Exported: data/monthly_aggregated.csv")

pd.DataFrame({
    'date':             future_dates,
    'forecast_revenue': future_pred.round(2),
    'lower_bound':      (future_pred - ci_width).clip(0).round(2),
    'upper_bound':      (future_pred + ci_width).round(2),
}).to_csv('data/revenue_forecast.csv', index=False)
print("Exported: data/revenue_forecast.csv")

print("\n"+"="*60)
print(f"ALL DONE!  Forecast Accuracy: {accuracy:.1f}%  |  8 charts in images/")
print("="*60)
