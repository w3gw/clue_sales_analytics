from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

class Sales(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    product_id = Column(String(50), nullable=False)
    product_name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_revenue = Column(Float, nullable=False)
    
    # Create indexes for frequently queried columns
    __table_args__ = (
        Index('idx_date', 'date'),
        Index('idx_product_id', 'product_id'),
        Index('idx_region', 'region'),
        Index('idx_date_product', 'date', 'product_id'),
    )

def get_db_engine():
    """Create and return a database engine."""
    db_path = os.getenv('DATABASE_URL', 'sqlite:///sales.db')
    return create_engine(db_path)

def init_db():
    """Initialize the database and create tables."""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    return engine

def get_db_session():
    """Create and return a database session."""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session() 