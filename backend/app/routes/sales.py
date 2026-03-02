from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Sale, SaleItem, Medicine, MedicineStatus, SaleStatus
from app.schemas import SaleCreate, SaleResponse, SaleItemResponse

router = APIRouter(prefix="/api/sales", tags=["Sales"])


def generate_invoice_no(db: Session) -> str:
    current_year = datetime.now().year
    last_sale = (
        db.query(Sale)
        .filter(Sale.invoice_no.like(f"INV-{current_year}-%"))
        .order_by(Sale.id.desc())
        .first()
    )
    if last_sale:
        last_num = int(last_sale.invoice_no.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1001
    return f"INV-{current_year}-{new_num}"


@router.post("/", response_model=SaleResponse, status_code=201)
def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db)):
    invoice_no = generate_invoice_no(db)
    sale = Sale(
        invoice_no=invoice_no,
        patient_name=sale_data.patient_name,
        payment_method=sale_data.payment_method,
        total_amount=0,
        status=SaleStatus.COMPLETED,
    )
    db.add(sale)
    db.flush()

    total_amount = 0
    for item_data in sale_data.items:
        medicine = (
            db.query(Medicine)
            .filter(Medicine.id == item_data.medicine_id)
            .first()
        )
        if not medicine:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Medicine with id {item_data.medicine_id} not found",
            )
        if medicine.quantity < item_data.quantity:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {medicine.name}. Available: {medicine.quantity}",
            )

        item_total = medicine.mrp * item_data.quantity
        sale_item = SaleItem(
            sale_id=sale.id,
            medicine_id=medicine.id,
            quantity=item_data.quantity,
            unit_price=medicine.mrp,
            total_price=item_total,
        )
        db.add(sale_item)
        total_amount += item_total

        medicine.quantity -= item_data.quantity
        if medicine.quantity == 0:
            medicine.status = MedicineStatus.OUT_OF_STOCK
        elif medicine.quantity <= 50:
            medicine.status = MedicineStatus.LOW_STOCK

    sale.total_amount = round(total_amount, 2)
    db.commit()
    db.refresh(sale)

    items_count = (
        db.query(func.count(SaleItem.id))
        .filter(SaleItem.sale_id == sale.id)
        .scalar()
        or 0
    )

    return SaleResponse(
        id=sale.id,
        invoice_no=sale.invoice_no,
        patient_name=sale.patient_name,
        payment_method=sale.payment_method,
        total_amount=sale.total_amount,
        status=sale.status,
        items_count=items_count,
        created_at=sale.created_at,
    )


@router.get("/", response_model=List[SaleResponse])
def list_sales(db: Session = Depends(get_db)):
    sales = db.query(Sale).order_by(Sale.created_at.desc()).limit(50).all()
    result = []
    for sale in sales:
        items_count = (
            db.query(func.count(SaleItem.id))
            .filter(SaleItem.sale_id == sale.id)
            .scalar()
            or 0
        )
        result.append(
            SaleResponse(
                id=sale.id,
                invoice_no=sale.invoice_no,
                patient_name=sale.patient_name,
                payment_method=sale.payment_method,
                total_amount=sale.total_amount,
                status=sale.status,
                items_count=items_count,
                created_at=sale.created_at,
            )
        )
    return result


@router.get("/{sale_id}/items", response_model=List[SaleItemResponse])
def get_sale_items(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    items = db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
    result = []
    for item in items:
        medicine = (
            db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        )
        result.append(
            SaleItemResponse(
                id=item.id,
                medicine_id=item.medicine_id,
                medicine_name=medicine.name if medicine else "Unknown",
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
        )
    return result
