import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(num_records=1000):
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate dates for the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Generate product data
    products = [
        {'id': f'PROD{i:03d}', 'name': f'Product {i}'} 
        for i in range(1, 21)  # 20 different products
    ]
    
    # Generate regions
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    # Generate random data
    data = []
    for _ in range(num_records):
        product = random.choice(products)
        data.append({
            'date': random.choice(dates),
            'product_id': product['id'],
            'product_name': product['name'],
            'region': random.choice(regions),
            'quantity': random.randint(1, 100),
            'unit_price': round(random.uniform(10.0, 1000.0), 2)
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort by date
    df = df.sort_values('date')
    
    # Save to CSV
    output_file = 'data/sample_sales_data.csv'
    df.to_csv(output_file, index=False)
    print(f"Generated {num_records} records and saved to {output_file}")
    
    # Print sample of the data
    print("\nSample of generated data:")
    print(df.head())
    
    # Print data summary
    print("\nData Summary:")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Number of unique products: {df['product_id'].nunique()}")
    print(f"Number of regions: {df['region'].nunique()}")
    print(f"Total quantity sold: {df['quantity'].sum()}")
    print(f"Average unit price: ${df['unit_price'].mean():.2f}")

if __name__ == "__main__":
    generate_sample_data(1000)  # Generate 1000 records 