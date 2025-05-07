import pytest
from datetime import datetime, timedelta
from sqlalchemy import text
from utils.database import init_db, get_db_session, Sales
import time
import pandas as pd
import numpy as np

@pytest.fixture(scope="session")
def db():
    """Initialize test database and return session."""
    engine = init_db()
    session = get_db_session()
    yield session
    session.close()

@pytest.fixture(scope="session")
def sample_data(db):
    """Generate and insert sample data for testing."""
    # Generate 100,000 sample records
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    products = [f'PROD{i:03d}' for i in range(1, 101)]
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    records = []
    for _ in range(100000):
        record = {
            'date': np.random.choice(dates),
            'product_id': np.random.choice(products),
            'product_name': f'Product {np.random.choice(products)}',
            'region': np.random.choice(regions),
            'quantity': np.random.randint(1, 100),
            'unit_price': round(np.random.uniform(10, 1000), 2)
        }
        record['total_revenue'] = record['quantity'] * record['unit_price']
        records.append(record)
    
    # Insert in batches
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        sales_objects = [
            Sales(**record)
            for record in batch
        ]
        db.bulk_save_objects(sales_objects)
        db.commit()

def test_monthly_summary_performance(db):
    """Test performance of monthly summary endpoint."""
    # Test with different date ranges
    test_cases = [
        ('Full year', None, None),
        ('Last 3 months', datetime.now() - timedelta(days=90), datetime.now()),
        ('Last month', datetime.now() - timedelta(days=30), datetime.now())
    ]
    
    for name, start_date, end_date in test_cases:
        start_time = time.time()
        
        query = """
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(total_revenue) as total_revenue,
            SUM(quantity) as total_quantity,
            AVG(unit_price) as avg_unit_price
        FROM sales
        WHERE 1=1
        """
        params = {}
        
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        query += " GROUP BY strftime('%Y-%m', date) ORDER BY month"
        
        result = db.execute(text(query), params)
        execution_time = time.time() - start_time
        
        print(f"\n{name} query execution time: {execution_time:.3f} seconds")
        assert execution_time < 1.0, f"{name} query took too long: {execution_time:.3f} seconds"

def test_top_products_performance(db):
    """Test performance of top products endpoint."""
    # Test with different limits and filters
    test_cases = [
        ('Top 5 all time', 5, None, None, None),
        ('Top 10 last month', 10, datetime.now() - timedelta(days=30), datetime.now(), None),
        ('Top 20 by region', 20, None, None, 'North')
    ]
    
    for name, limit, start_date, end_date, region in test_cases:
        start_time = time.time()
        
        query = """
        SELECT 
            product_id,
            product_name,
            SUM(total_revenue) as total_revenue,
            SUM(quantity) as total_quantity
        FROM sales
        WHERE 1=1
        """
        params = {}
        
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        if region:
            query += " AND region = :region"
            params['region'] = region
        
        query += """
        GROUP BY product_id, product_name
        ORDER BY total_revenue DESC
        LIMIT :limit
        """
        params['limit'] = limit
        
        result = db.execute(text(query), params)
        execution_time = time.time() - start_time
        
        print(f"\n{name} query execution time: {execution_time:.3f} seconds")
        assert execution_time < 1.0, f"{name} query took too long: {execution_time:.3f} seconds"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 