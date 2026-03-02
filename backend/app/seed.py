from datetime import datetime, date, timedelta
import random
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import (
    Medicine,
    Sale,
    SaleItem,
    PurchaseOrder,
    MedicineStatus,
    PaymentMethod,
    SaleStatus,
    PurchaseOrderStatus,
)


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    existing = db.query(Medicine).first()
    if existing:
        print("Database already seeded")
        db.close()
        return

    medicines_data = [
        {
            "name": "Paracetamol 650mg",
            "generic_name": "Acetaminophen",
            "category": "Analgesic",
            "batch_no": "PCM-2024-0892",
            "expiry_date": date(2026, 8, 20),
            "quantity": 500,
            "cost_price": 15.00,
            "mrp": 25.00,
            "supplier": "MedSupply Co.",
            "status": MedicineStatus.ACTIVE,
        },
        {
            "name": "Omeprazole 20mg Capsule",
            "generic_name": "Omeprazole",
            "category": "Gastric",
            "batch_no": "OMP-2024-5873",
            "expiry_date": date(2025, 11, 10),
            "quantity": 45,
            "cost_price": 65.00,
            "mrp": 95.75,
            "supplier": "HealthCare Ltd.",
            "status": MedicineStatus.LOW_STOCK,
        },
        {
            "name": "Aspirin 75mg",
            "generic_name": "Aspirin",
            "category": "Anticoagulant",
            "batch_no": "ASP-2023-3401",
            "expiry_date": date(2024, 9, 30),
            "quantity": 300,
            "cost_price": 28.00,
            "mrp": 45.00,
            "supplier": "GreenMed",
            "status": MedicineStatus.EXPIRED,
        },
        {
            "name": "Atorvastatin 10mg",
            "generic_name": "Atorvastatin Besylate",
            "category": "Cardiovascular",
            "batch_no": "AME-2024-0945",
            "expiry_date": date(2025, 10, 15),
            "quantity": 0,
            "cost_price": 145.00,
            "mrp": 195.00,
            "supplier": "PharmaCorp",
            "status": MedicineStatus.OUT_OF_STOCK,
        },
        {
            "name": "Amoxicillin 500mg",
            "generic_name": "Amoxicillin",
            "category": "Antibiotic",
            "batch_no": "AMX-2024-7721",
            "expiry_date": date(2026, 3, 15),
            "quantity": 200,
            "cost_price": 35.00,
            "mrp": 55.00,
            "supplier": "MedSupply Co.",
            "status": MedicineStatus.ACTIVE,
        },
        {
            "name": "Metformin 500mg",
            "generic_name": "Metformin HCl",
            "category": "Antidiabetic",
            "batch_no": "MET-2024-1123",
            "expiry_date": date(2026, 6, 20),
            "quantity": 350,
            "cost_price": 22.00,
            "mrp": 38.00,
            "supplier": "HealthCare Ltd.",
            "status": MedicineStatus.ACTIVE,
        },
        {
            "name": "Cetirizine 10mg",
            "generic_name": "Cetirizine",
            "category": "Antihistamine",
            "batch_no": "CET-2024-3345",
            "expiry_date": date(2026, 1, 10),
            "quantity": 30,
            "cost_price": 12.00,
            "mrp": 20.00,
            "supplier": "GreenMed",
            "status": MedicineStatus.LOW_STOCK,
        },
        {
            "name": "Azithromycin 250mg",
            "generic_name": "Azithromycin",
            "category": "Antibiotic",
            "batch_no": "AZI-2024-8890",
            "expiry_date": date(2026, 5, 25),
            "quantity": 150,
            "cost_price": 85.00,
            "mrp": 120.00,
            "supplier": "PharmaCorp",
            "status": MedicineStatus.ACTIVE,
        },
        {
            "name": "Losartan 50mg",
            "generic_name": "Losartan Potassium",
            "category": "Cardiovascular",
            "batch_no": "LOS-2024-2234",
            "expiry_date": date(2026, 7, 30),
            "quantity": 180,
            "cost_price": 55.00,
            "mrp": 78.00,
            "supplier": "MedSupply Co.",
            "status": MedicineStatus.ACTIVE,
        },
        {
            "name": "Pantoprazole 40mg",
            "generic_name": "Pantoprazole",
            "category": "Gastric",
            "batch_no": "PAN-2024-6678",
            "expiry_date": date(2026, 4, 18),
            "quantity": 25,
            "cost_price": 45.00,
            "mrp": 68.00,
            "supplier": "HealthCare Ltd.",
            "status": MedicineStatus.LOW_STOCK,
        },
    ]

    medicines = []
    for med_data in medicines_data:
        medicine = Medicine(**med_data)
        db.add(medicine)
        medicines.append(medicine)

    db.flush()

    sales_data = [
        {
            "invoice_no": "INV-2024-1234",
            "patient_name": "Rajesh Kumar",
            "payment_method": PaymentMethod.CARD,
            "items": [(0, 2), (4, 1)],
        },
        {
            "invoice_no": "INV-2024-1235",
            "patient_name": "Sarah Smith",
            "payment_method": PaymentMethod.CASH,
            "items": [(5, 1), (6, 1)],
        },
        {
            "invoice_no": "INV-2024-1236",
            "patient_name": "Michael Johnson",
            "payment_method": PaymentMethod.UPI,
            "items": [(0, 3), (7, 1), (8, 1)],
        },
        {
            "invoice_no": "INV-2024-1237",
            "patient_name": "Priya Sharma",
            "payment_method": PaymentMethod.CARD,
            "items": [(1, 2), (9, 1)],
        },
        {
            "invoice_no": "INV-2024-1238",
            "patient_name": "Amit Patel",
            "payment_method": PaymentMethod.UPI,
            "items": [(4, 3), (5, 2)],
        },
    ]

    now = datetime.utcnow()
    for i, sale_data in enumerate(sales_data):
        sale = Sale(
            invoice_no=sale_data["invoice_no"],
            patient_name=sale_data["patient_name"],
            payment_method=sale_data["payment_method"],
            total_amount=0,
            status=SaleStatus.COMPLETED,
            created_at=now - timedelta(hours=i * 2),
        )
        db.add(sale)
        db.flush()

        total = 0
        for med_idx, qty in sale_data["items"]:
            medicine = medicines[med_idx]
            item_total = medicine.mrp * qty
            sale_item = SaleItem(
                sale_id=sale.id,
                medicine_id=medicine.id,
                quantity=qty,
                unit_price=medicine.mrp,
                total_price=item_total,
            )
            db.add(sale_item)
            total += item_total
        sale.total_amount = round(total, 2)

    purchase_orders = [
        PurchaseOrder(
            order_no="PO-2024-001",
            supplier="MedSupply Co.",
            total_amount=25000.00,
            status=PurchaseOrderStatus.PENDING,
            created_at=now - timedelta(days=1),
        ),
        PurchaseOrder(
            order_no="PO-2024-002",
            supplier="HealthCare Ltd.",
            total_amount=18500.00,
            status=PurchaseOrderStatus.PENDING,
            created_at=now - timedelta(days=2),
        ),
        PurchaseOrder(
            order_no="PO-2024-003",
            supplier="PharmaCorp",
            total_amount=15250.00,
            status=PurchaseOrderStatus.COMPLETED,
            created_at=now - timedelta(days=3),
        ),
        PurchaseOrder(
            order_no="PO-2024-004",
            supplier="GreenMed",
            total_amount=22000.00,
            status=PurchaseOrderStatus.PENDING,
            created_at=now - timedelta(days=4),
        ),
        PurchaseOrder(
            order_no="PO-2024-005",
            supplier="MedSupply Co.",
            total_amount=15500.00,
            status=PurchaseOrderStatus.PENDING,
            created_at=now - timedelta(days=5),
        ),
    ]

    for po in purchase_orders:
        db.add(po)

    db.commit()
    db.close()
    print("Database seeded successfully")


if __name__ == "__main__":
    seed_database()
