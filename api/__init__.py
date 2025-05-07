
from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from sqlalchemy import text
from data import MonthlySummary, TopProduct, UploadResponse
from utils.database import get_db_session, Sales
from utils.data_ingestion import validate_csv_data, calculate_total_revenue
from datetime import date
from typing import List, Optional
import time
import pandas as pd
import io

router = APIRouter()



@router.post("/upload-csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and process a CSV file containing sales data.
    The CSV should have the following columns:
    - date
    - product_id
    - product_name
    - region
    - quantity
    - unit_price
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV content
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate data
        if not validate_csv_data(df):
            return UploadResponse(
                success=False,
                message="Data validation failed",
                errors=["Invalid data format or content"]
            )
        
        # Calculate total revenue
        df = calculate_total_revenue(df)
        
        # Get database session
        session = get_db_session()
        
        # Process in batches
        batch_size = 1000
        total_records = len(df)
        processed_records = 0
        errors = []
        
        try:
            for i in range(0, total_records, batch_size):
                batch_df = df.iloc[i:i + batch_size]
                
                # Convert DataFrame rows to Sales objects
                sales_objects = []
                for _, row in batch_df.iterrows():
                    try:
                        sales_objects.append(Sales(
                            date=pd.to_datetime(row['date']).date(),
                            product_id=row['product_id'],
                            product_name=row['product_name'],
                            region=row['region'],
                            quantity=int(row['quantity']),
                            unit_price=float(row['unit_price']),
                            total_revenue=float(row['total_revenue'])
                        ))
                    except Exception as e:
                        errors.append(f"Error processing row {processed_records + len(sales_objects) + 1}: {str(e)}")
                
                # Insert batch
                if sales_objects:
                    session.bulk_save_objects(sales_objects)
                    session.commit()
                    processed_records += len(sales_objects)
            
            return UploadResponse(
                success=True,
                message=f"Successfully processed {processed_records} records",
                records_processed=processed_records,
                errors=errors if errors else None
            )
            
        finally:
            session.close()
            
    except Exception as e:
        return UploadResponse(
            success=False,
            message=f"Error processing file: {str(e)}",
            errors=[str(e)]
        )

@router.get("/monthly-summary", response_model=List[MonthlySummary])
async def get_monthly_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Filter by region"),
    product_id: Optional[str] = Query(None, description="Filter by product ID")
):
    """
    Get monthly sales summaries with optimized query execution.
    Uses indexes on date, region, and product_id for efficient filtering.
    """
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
    if region:
        query += " AND region = :region"
        params['region'] = region
    if product_id:
        query += " AND product_id = :product_id"
        params['product_id'] = product_id
    
    query += " GROUP BY strftime('%Y-%m', date) ORDER BY month"
    
    session = get_db_session()
    try:
        result = session.execute(text(query), params)
        execution_time = time.time() - start_time
        
        return [
            MonthlySummary(
                month=row[0],
                total_revenue=float(row[1]),
                total_quantity=int(row[2]),
                avg_unit_price=float(row[3])
            )
            for row in result
        ]
    finally:
        session.close()

@router.get("/top-products", response_model=List[TopProduct])
async def get_top_products(
    limit: int = Query(5, ge=1, le=100, description="Number of top products to return"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    region: Optional[str] = Query(None, description="Filter by region")
):
    """
    Get top products by revenue with optimized query execution.
    Uses indexes on date, region, and product_id for efficient filtering.
    """
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
    
    session = get_db_session()
    try:
        result = session.execute(text(query), params)
        execution_time = time.time() - start_time
        
        return [
            TopProduct(
                product_id=row[0],
                product_name=row[1],
                total_revenue=float(row[2]),
                total_quantity=int(row[3])
            )
            for row in result
        ]
    finally:
        session.close()
