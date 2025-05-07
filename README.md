# Optimized Data Aggregation API

A Python application that provides optimized analytical reports through API endpoints, built with FastAPI and SQLite.

## Features

- CSV data ingestion with validation and error handling
- Optimized analytical endpoints for sales data
- Performance-optimized database queries with proper indexing
- Comprehensive performance testing suite

## Project Structure

```
.
├── main.py              # FastAPI application with endpoints
├── data/
│   ├── __init__.py     # Data models and schemas
│   ├── generate_sample_data.py # Sample data generation script
│   └── sample_sales_data.csv # Sample sales data
├── utils/
│   ├── database.py     # Database models and connection management
│   └── data_ingestion.py # CSV data loading and validation
├── tests/
│   └── test_performance.py # Performance testing suite
└── requirements.txt    # Project dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

## Usage

### Data Ingestion

You can ingest data in two ways:

1. Using the API endpoint:
```bash
curl -X POST -F "file=@data/sample_sales_data.csv" http://localhost:8000/api/upload-csv
```

2. Using Python code:
```python
from utils.data_ingestion import load_csv_to_db

# Load CSV file
success = load_csv_to_db('/data/sample_sales_data.csv')

# But I would prefer Option 1 for simplicity.
```

The CSV file should have the following columns:
- date (YYYY-MM-DD format)
- product_id (e.g., PROD001)
- product_name
- region
- quantity
- unit_price

### API Endpoints

Start the API server:
```bash
uvicorn main:app --reload
```

Available endpoints:

1. Upload CSV
```
POST /api/upload-csv
Content-Type: multipart/form-data
Body: file (CSV file)
Response: UploadResponse with success status and processing details
```

2. Monthly Summary
```
GET /api/monthly-summary
Query Parameters:
- start_date (optional): YYYY-MM-DD
- end_date (optional): YYYY-MM-DD
- region (optional): Filter by region
- product_id (optional): Filter by product ID
```

3. Top Products
```
GET /api/top-products
Query Parameters:
- limit (optional, default=5): Number of top products to return
- start_date (optional): YYYY-MM-DD
- end_date (optional): YYYY-MM-DD
- region (optional): Filter by region
```

### Sample Data

Generate sample data for testing:
```bash
python data/generate_sample_data.py
```

This will create a sample CSV file with:
- 1,000 records
- 20 different products
- 5 regions (North, South, East, West, Central)
- One year of sales data
- Realistic quantities and prices

## Performance Optimizations

1. Database Schema
   - Optimized table structure with appropriate data types
   - Indexes on frequently queried columns (date, product_id, region)
   - Composite index on date and product_id for common query patterns

2. Query Optimization
   - Efficient SQL queries using proper indexing
   - Batch processing for data ingestion
   - Parameterized queries to prevent SQL injection
   - Proper use of SQL functions for date handling

3. API Performance
   - Async endpoints for better concurrency
   - Efficient data validation and error handling
   - Response models for consistent output
   - Batch processing for large file uploads

## Testing

Run performance tests:
```bash
pytest tests/test_performance.py -v
```

The test suite includes:
- Monthly summary query performance tests
- Top products query performance tests
- Sample data generation for testing
- Performance benchmarks for all endpoints

## Performance Metrics

The application is designed to handle:
- Data ingestion of 100,000+ records efficiently
- Query response times under 1 second for common operations
- Concurrent API requests with proper resource management
- Batch processing of CSV files with progress tracking

## Error Handling

The API provides detailed error responses for:
- Invalid file formats
- Missing or malformed data
- Database errors
- Validation failures

Each error response includes:
- Success status
- Error message
- Detailed error information when applicable
- Number of records processed (for partial successes)
