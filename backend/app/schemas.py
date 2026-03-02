from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.models import MedicineStatus, PaymentMethod, SaleStatus


class MedicineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    generic_name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    batch_no: str = Field(..., min_length=1, max_length=50)
    expiry_date: date
    quantity: int = Field(..., ge=0)
    cost_price: float = Field(..., gt=0)
    mrp: float = Field(..., gt=0)
    supplier: str = Field(..., min_length=1, max_length=255)


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    category: Optional[str] = None
    batch_no: Optional[str] = None
    expiry_date: Optional[date] = None
    quantity: Optional[int] = None
    cost_price: Optional[float] = None
    mrp: Optional[float] = None
    supplier: Optional[str] = None
    status: Optional[MedicineStatus] = None


class MedicineResponse(MedicineBase):
    id: int
    status: MedicineStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SaleItemCreate(BaseModel):
    medicine_id: int
    quantity: int = Field(..., gt=0)


class SaleItemResponse(BaseModel):
    id: int
    medicine_id: int
    medicine_name: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    patient_name: str = Field(..., min_length=1, max_length=255)
    payment_method: PaymentMethod = PaymentMethod.CASH
    items: List[SaleItemCreate]


class SaleResponse(BaseModel):
    id: int
    invoice_no: str
    patient_name: str
    payment_method: PaymentMethod
    total_amount: float
    status: SaleStatus
    items_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    todays_sales: float
    sales_change_percent: float
    items_sold_today: int
    total_orders_today: int
    low_stock_items: int
    purchase_orders_total: float
    pending_purchase_orders: int


class LowStockItem(BaseModel):
    id: int
    name: str
    quantity: int
    status: MedicineStatus

    class Config:
        from_attributes = True


class RecentSale(BaseModel):
    id: int
    invoice_no: str
    patient_name: str
    items_count: int
    payment_method: PaymentMethod
    total_amount: float
    status: SaleStatus
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryOverview(BaseModel):
    total_items: int
    active_stock: int
    low_stock: int
    total_value: float


class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[dict] = None
