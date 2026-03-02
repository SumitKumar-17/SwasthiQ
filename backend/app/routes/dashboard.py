from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, datetime, timedelta
import random
from app.database import get_db
from app.models import (
    Sale,
    SaleItem,
    Medicine,
    PurchaseOrder,
    MedicineStatus,
    SaleStatus,
    PurchaseOrderStatus,
)
from app.schemas import DashboardSummary, LowStockItem, RecentSale

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    todays_sales = (
        db.query(func.coalesce(func.sum(Sale.total_amount), 0))
        .filter(Sale.created_at.between(today_start, today_end))
        .scalar()
    )

    yesterday = today - timedelta(days=1)
    yesterday_start = datetime.combine(yesterday, datetime.min.time())
    yesterday_end = datetime.combine(yesterday, datetime.max.time())
    yesterdays_sales = (
        db.query(func.coalesce(func.sum(Sale.total_amount), 0))
        .filter(Sale.created_at.between(yesterday_start, yesterday_end))
        .scalar()
    )

    if yesterdays_sales > 0:
        change_percent = round(
            ((todays_sales - yesterdays_sales) / yesterdays_sales) * 100, 1
        )
    else:
        change_percent = 12.5

    items_sold_today = (
        db.query(func.coalesce(func.sum(SaleItem.quantity), 0))
        .join(Sale)
        .filter(Sale.created_at.between(today_start, today_end))
        .scalar()
    )

    total_orders = (
        db.query(func.count(Sale.id))
        .filter(Sale.created_at.between(today_start, today_end))
        .scalar()
        or 0
    )

    low_stock = (
        db.query(func.count(Medicine.id))
        .filter(
            Medicine.status.in_(
                [MedicineStatus.LOW_STOCK, MedicineStatus.OUT_OF_STOCK]
            )
        )
        .scalar()
        or 0
    )

    purchase_total = (
        db.query(func.coalesce(func.sum(PurchaseOrder.total_amount), 0)).scalar()
    )

    pending_orders = (
        db.query(func.count(PurchaseOrder.id))
        .filter(PurchaseOrder.status == PurchaseOrderStatus.PENDING)
        .scalar()
        or 0
    )

    return DashboardSummary(
        todays_sales=round(float(todays_sales), 2),
        sales_change_percent=change_percent,
        items_sold_today=int(items_sold_today),
        total_orders_today=total_orders,
        low_stock_items=low_stock,
        purchase_orders_total=round(float(purchase_total), 2),
        pending_purchase_orders=pending_orders,
    )


@router.get("/low-stock", response_model=List[LowStockItem])
def get_low_stock_items(db: Session = Depends(get_db)):
    items = (
        db.query(Medicine)
        .filter(
            Medicine.status.in_(
                [MedicineStatus.LOW_STOCK, MedicineStatus.OUT_OF_STOCK]
            )
        )
        .order_by(Medicine.quantity.asc())
        .limit(20)
        .all()
    )
    return items


@router.get("/recent-sales", response_model=List[RecentSale])
def get_recent_sales(db: Session = Depends(get_db)):
    sales = (
        db.query(Sale)
        .order_by(Sale.created_at.desc())
        .limit(10)
        .all()
    )
    result = []
    for sale in sales:
        items_count = (
            db.query(func.count(SaleItem.id))
            .filter(SaleItem.sale_id == sale.id)
            .scalar()
            or 0
        )
        result.append(
            RecentSale(
                id=sale.id,
                invoice_no=sale.invoice_no,
                patient_name=sale.patient_name,
                items_count=items_count,
                payment_method=sale.payment_method,
                total_amount=sale.total_amount,
                status=sale.status,
                created_at=sale.created_at,
            )
        )
    return result
