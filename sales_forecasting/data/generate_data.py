import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

regions = ['North', 'South', 'East', 'West', 'Central']
categories = ['Electronics', 'Clothing', 'Furniture', 'Food & Beverage', 'Sports']
products = {
    'Electronics': ['Laptop', 'Mobile Phone', 'Tablet', 'Headphones', 'Smart Watch'],
    'Clothing':    ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Dress'],
    'Furniture':   ['Chair', 'Table', 'Sofa', 'Bookshelf', 'Bed Frame'],
    'Food & Beverage': ['Coffee Beans', 'Protein Bar', 'Juice Pack', 'Snack Box', 'Tea Set'],
    'Sports':      ['Yoga Mat', 'Dumbbells', 'Running Shoes', 'Cycling Helmet', 'Tennis Racket'],
}
base_prices = {
    'Laptop': 75000, 'Mobile Phone': 35000, 'Tablet': 28000, 'Headphones': 8000, 'Smart Watch': 15000,
    'T-Shirt': 800,  'Jeans': 2200,  'Jacket': 4500, 'Shoes': 3500, 'Dress': 3000,
    'Chair': 12000,  'Table': 18000, 'Sofa': 45000, 'Bookshelf': 9000, 'Bed Frame': 22000,
    'Coffee Beans': 1200, 'Protein Bar': 300, 'Juice Pack': 250, 'Snack Box': 450, 'Tea Set': 1800,
    'Yoga Mat': 1500, 'Dumbbells': 3000, 'Running Shoes': 4500, 'Cycling Helmet': 2800, 'Tennis Racket': 6000,
}

rows = []
start_date = datetime(2022, 1, 1)
end_date   = datetime(2024, 12, 31)
order_id   = 10001

for _ in range(5000):
    date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    region   = random.choice(regions)
    category = random.choice(categories)
    product  = random.choice(products[category])

    # seasonal multiplier: Q4 boost, Q1 dip
    month = date.month
    seasonal = 1.0
    if month in [10, 11, 12]: seasonal = 1.35
    elif month in [1, 2]:     seasonal = 0.80
    elif month in [6, 7]:     seasonal = 1.15

    base      = base_prices[product]
    unit_price = round(base * np.random.uniform(0.90, 1.10), 2)
    quantity   = int(np.random.poisson(lam=3 * seasonal)) + 1
    discount   = round(random.choice([0, 0, 0, 5, 10, 15, 20]) / 100, 2)
    revenue    = round(unit_price * quantity * (1 - discount), 2)
    cost       = round(unit_price * quantity * np.random.uniform(0.50, 0.70), 2)
    profit     = round(revenue - cost, 2)

    rows.append({
        'order_id':    order_id,
        'order_date':  date.strftime('%Y-%m-%d'),
        'region':      region,
        'category':    category,
        'product':     product,
        'unit_price':  unit_price,
        'quantity':    quantity,
        'discount':    discount,
        'revenue':     revenue,
        'cost':        cost,
        'profit':      profit,
    })
    order_id += 1

df = pd.DataFrame(rows).sort_values('order_date').reset_index(drop=True)
out = os.path.join(os.path.dirname(__file__), 'sales_data.csv')
df.to_csv(out, index=False)
print(f"Generated {len(df)} rows → {out}")
print(df.head())
