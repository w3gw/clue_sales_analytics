from typing import List, Optional
from pydantic import BaseModel

class UploadResponse(BaseModel):
    success: bool
    message: str
    records_processed: Optional[int] = None
    errors: Optional[List[str]] = None

class MonthlySummary(BaseModel):
    month: str
    total_revenue: float
    total_quantity: int
    avg_unit_price: float

class TopProduct(BaseModel):
    product_id: str
    product_name: str
    total_revenue: float
    total_quantity: int