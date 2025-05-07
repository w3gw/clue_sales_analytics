import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_csv_data(df: pd.DataFrame) -> bool:
    """Validate the CSV data structure and content."""
    required_columns = ['date', 'product_id', 'product_name', 'region', 'quantity', 'unit_price']
    
    # Check required columns
    if not all(col in df.columns for col in required_columns):
        logger.error(f"Missing required columns. Required: {required_columns}")
        return False
    
    # Validate data types
    try:
        df['date'] = pd.to_datetime(df['date'])
        df['quantity'] = pd.to_numeric(df['quantity'])
        df['unit_price'] = pd.to_numeric(df['unit_price'])
    except Exception as e:
        logger.error(f"Data type validation failed: {str(e)}")
        return False
    
    # Validate non-negative values
    if (df['quantity'] < 0).any() or (df['unit_price'] < 0).any():
        logger.error("Found negative values in quantity or unit_price")
        return False
    
    return True

def calculate_total_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total revenue for each row."""
    df['total_revenue'] = df['quantity'] * df['unit_price']
    return df