from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import Medicine, MedicineStatus
from app.schemas import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse,
    InventoryOverview,
)

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("/overview", response_model=InventoryOverview)
def get_inventory_overview(db: Session = Depends(get_db)):
    total_items = db.query(func.count(Medicine.id)).scalar() or 0
    active_stock = (
        db.query(func.count(Medicine.id))
        .filter(Medicine.status == MedicineStatus.ACTIVE)
        .scalar()
        or 0
    )
    low_stock = (
        db.query(func.count(Medicine.id))
        .filter(Medicine.status == MedicineStatus.LOW_STOCK)
        .scalar()
        or 0
    )
    total_value = (
        db.query(func.sum(Medicine.mrp * Medicine.quantity)).scalar() or 0
    )
    return InventoryOverview(
        total_items=total_items,
        active_stock=active_stock,
        low_stock=low_stock,
        total_value=round(total_value, 2),
    )


@router.get("/medicines", response_model=List[MedicineResponse])
def list_medicines(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[MedicineStatus] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Medicine)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Medicine.name.ilike(search_term))
            | (Medicine.generic_name.ilike(search_term))
            | (Medicine.batch_no.ilike(search_term))
        )
    if category:
        query = query.filter(Medicine.category == category)
    if status:
        query = query.filter(Medicine.status == status)
    offset = (page - 1) * limit
    medicines = query.order_by(Medicine.id.desc()).offset(offset).limit(limit).all()
    return medicines


@router.get("/medicines/{medicine_id}", response_model=MedicineResponse)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine


@router.post("/medicines", response_model=MedicineResponse, status_code=201)
def add_medicine(medicine_data: MedicineCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Medicine)
        .filter(Medicine.batch_no == medicine_data.batch_no)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Medicine with this batch number already exists"
        )
    medicine = Medicine(**medicine_data.model_dump())
    if medicine.quantity == 0:
        medicine.status = MedicineStatus.OUT_OF_STOCK
    elif medicine.quantity <= 50:
        medicine.status = MedicineStatus.LOW_STOCK
    elif medicine.expiry_date <= date.today():
        medicine.status = MedicineStatus.EXPIRED
    else:
        medicine.status = MedicineStatus.ACTIVE
    db.add(medicine)
    db.commit()
    db.refresh(medicine)
    return medicine


@router.put("/medicines/{medicine_id}", response_model=MedicineResponse)
def update_medicine(
    medicine_id: int,
    medicine_data: MedicineUpdate,
    db: Session = Depends(get_db),
):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    update_dict = medicine_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(medicine, key, value)
    if "status" not in update_dict:
        if medicine.quantity == 0:
            medicine.status = MedicineStatus.OUT_OF_STOCK
        elif medicine.quantity <= 50:
            medicine.status = MedicineStatus.LOW_STOCK
        elif medicine.expiry_date <= date.today():
            medicine.status = MedicineStatus.EXPIRED
        else:
            medicine.status = MedicineStatus.ACTIVE
    medicine.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(medicine)
    return medicine


@router.patch("/medicines/{medicine_id}/status", response_model=MedicineResponse)
def update_medicine_status(
    medicine_id: int,
    status: MedicineStatus,
    db: Session = Depends(get_db),
):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    medicine.status = status
    medicine.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(medicine)
    return medicine


@router.delete("/medicines/{medicine_id}", status_code=204)
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(medicine)
    db.commit()
    return None


@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Medicine.category).distinct().all()
    return [c[0] for c in categories]
