"""
SQLAlchemy ORM Models for Star Schema Data Model.
Contains FactSales, DimCustomer, DimProduct, DimRegion, and DimDate models.
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DimCustomer(Base):
    __tablename__ = "dim_customer"
    
    customer_key = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, nullable=False, index=True)

class DimProduct(Base):
    __tablename__ = "dim_product"
    
    product_key = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    cost = Column(Float, nullable=False)

class DimRegion(Base):
    __tablename__ = "dim_region"
    
    region_key = Column(Integer, primary_key=True, autoincrement=True)
    region_name = Column(String(50), unique=True, nullable=False, index=True)

class DimDate(Base):
    __tablename__ = "dim_date"
    
    date_key = Column(Integer, primary_key=True)  # Format YYYYMMDD e.g. 20240515
    full_date = Column(Date, unique=True, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    month_name = Column(String(20), nullable=False)
    week_of_year = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    day_name = Column(String(20), nullable=False)

class FactSales(Base):
    __tablename__ = "fact_sales"
    
    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), nullable=False, index=True)
    
    date_key = Column(Integer, ForeignKey("dim_date.date_key"), nullable=False, index=True)
    customer_key = Column(Integer, ForeignKey("dim_customer.customer_key"), nullable=False, index=True)
    product_key = Column(Integer, ForeignKey("dim_product.product_key"), nullable=False, index=True)
    region_key = Column(Integer, ForeignKey("dim_region.region_key"), nullable=False, index=True)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    sales = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    profit_margin = Column(Float, nullable=False)

    # Relationships
    date_dim = relationship("DimDate")
    customer_dim = relationship("DimCustomer")
    product_dim = relationship("DimProduct")
    region_dim = relationship("DimRegion")
