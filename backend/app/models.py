from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.database import Base


class MedicineStatus(str, enum.Enum):
    ACTIVE = "Active"
    LOW_STOCK = "Low Stock"
    EXPIRED = "Expired"
    OUT_OF_STOCK = "Out of Stock"


class PaymentMethod(str, enum.Enum):
    CASH = "Cash"
    CARD = "Card"
    UPI = "UPI"


class SaleStatus(str, enum.Enum):
    COMPLETED = "Completed"
    PENDING = "Pending"
    CANCELLED = "Cancelled"


class PurchaseOrderStatus(str, enum.Enum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    generic_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    batch_no = Column(String(50), unique=True, nullable=False)
    expiry_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    cost_price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    supplier = Column(String(255), nullable=False)
    status = Column(SQLEnum(MedicineStatus), default=MedicineStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sale_items = relationship("SaleItem", back_populates="medicine")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), unique=True, nullable=False)
    patient_name = Column(String(255), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CASH)
    total_amount = Column(Float, nullable=False, default=0)
    status = Column(SQLEnum(SaleStatus), default=SaleStatus.COMPLETED)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    medicine = relationship("Medicine", back_populates="sale_items")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    supplier = Column(String(255), nullable=False)
    total_amount = Column(Float, nullable=False, default=0)
    status = Column(SQLEnum(PurchaseOrderStatus), default=PurchaseOrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
