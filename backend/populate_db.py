import sys
import os
import random
from datetime import datetime, date, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
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

MEDICINES = [
    ("Paracetamol 650mg", "Acetaminophen", "Analgesic"),
    ("Paracetamol 500mg", "Acetaminophen", "Analgesic"),
    ("Ibuprofen 400mg", "Ibuprofen", "Analgesic"),
    ("Diclofenac 50mg", "Diclofenac Sodium", "Analgesic"),
    ("Aspirin 75mg", "Aspirin", "Anticoagulant"),
    ("Clopidogrel 75mg", "Clopidogrel", "Anticoagulant"),
    ("Warfarin 5mg", "Warfarin Sodium", "Anticoagulant"),
    ("Amoxicillin 500mg", "Amoxicillin", "Antibiotic"),
    ("Amoxicillin 250mg", "Amoxicillin", "Antibiotic"),
    ("Azithromycin 500mg", "Azithromycin", "Antibiotic"),
    ("Azithromycin 250mg", "Azithromycin", "Antibiotic"),
    ("Ciprofloxacin 500mg", "Ciprofloxacin", "Antibiotic"),
    ("Metronidazole 400mg", "Metronidazole", "Antibiotic"),
    ("Cefixime 200mg", "Cefixime", "Antibiotic"),
    ("Doxycycline 100mg", "Doxycycline", "Antibiotic"),
    ("Cetirizine 10mg", "Cetirizine", "Antihistamine"),
    ("Levocetirizine 5mg", "Levocetirizine", "Antihistamine"),
    ("Fexofenadine 120mg", "Fexofenadine", "Antihistamine"),
    ("Montelukast 10mg", "Montelukast", "Antihistamine"),
    ("Omeprazole 20mg", "Omeprazole", "Gastric"),
    ("Pantoprazole 40mg", "Pantoprazole", "Gastric"),
    ("Ranitidine 150mg", "Ranitidine", "Gastric"),
    ("Domperidone 10mg", "Domperidone", "Gastric"),
    ("Ondansetron 4mg", "Ondansetron", "Gastric"),
    ("Metformin 500mg", "Metformin HCl", "Antidiabetic"),
    ("Metformin 1000mg", "Metformin HCl", "Antidiabetic"),
    ("Glimepiride 2mg", "Glimepiride", "Antidiabetic"),
    ("Sitagliptin 100mg", "Sitagliptin", "Antidiabetic"),
    ("Insulin Glargine 100IU", "Insulin Glargine", "Antidiabetic"),
    ("Atorvastatin 10mg", "Atorvastatin", "Cardiovascular"),
    ("Atorvastatin 20mg", "Atorvastatin", "Cardiovascular"),
    ("Rosuvastatin 10mg", "Rosuvastatin", "Cardiovascular"),
    ("Amlodipine 5mg", "Amlodipine Besylate", "Cardiovascular"),
    ("Losartan 50mg", "Losartan Potassium", "Cardiovascular"),
    ("Telmisartan 40mg", "Telmisartan", "Cardiovascular"),
    ("Enalapril 5mg", "Enalapril", "Cardiovascular"),
    ("Metoprolol 50mg", "Metoprolol Tartrate", "Cardiovascular"),
    ("Furosemide 40mg", "Furosemide", "Cardiovascular"),
    ("Hydrochlorothiazide 25mg", "Hydrochlorothiazide", "Cardiovascular"),
    ("Salbutamol Inhaler 100mcg", "Salbutamol", "Respiratory"),
    ("Budesonide Inhaler 200mcg", "Budesonide", "Respiratory"),
    ("Theophylline 300mg", "Theophylline", "Respiratory"),
    ("Prednisolone 5mg", "Prednisolone", "Steroid"),
    ("Dexamethasone 0.5mg", "Dexamethasone", "Steroid"),
    ("Methylprednisolone 4mg", "Methylprednisolone", "Steroid"),
    ("Sertraline 50mg", "Sertraline", "Antidepressant"),
    ("Fluoxetine 20mg", "Fluoxetine", "Antidepressant"),
    ("Escitalopram 10mg", "Escitalopram", "Antidepressant"),
    ("Alprazolam 0.5mg", "Alprazolam", "Anxiolytic"),
    ("Clonazepam 0.5mg", "Clonazepam", "Anxiolytic"),
    ("Levothyroxine 50mcg", "Levothyroxine", "Thyroid"),
    ("Levothyroxine 100mcg", "Levothyroxine", "Thyroid"),
    ("Calcium + Vitamin D3", "Calcium Carbonate", "Supplement"),
    ("Multivitamin Tablet", "Multivitamin", "Supplement"),
    ("Iron + Folic Acid", "Ferrous Sulfate", "Supplement"),
    ("Vitamin B12 1500mcg", "Methylcobalamin", "Supplement"),
    ("Zinc 50mg", "Zinc Sulfate", "Supplement"),
    ("Vitamin C 500mg", "Ascorbic Acid", "Supplement"),
    ("Tramadol 50mg", "Tramadol", "Pain Management"),
    ("Gabapentin 300mg", "Gabapentin", "Pain Management"),
]

FORCED_STATUS = {
    0: (MedicineStatus.ACTIVE, 500, 180),
    1: (MedicineStatus.LOW_STOCK, 35, 200),
    2: (MedicineStatus.EXPIRED, 300, -90),
    3: (MedicineStatus.OUT_OF_STOCK, 0, 120),
    4: (MedicineStatus.ACTIVE, 250, 365),
    5: (MedicineStatus.LOW_STOCK, 12, 300),
    6: (MedicineStatus.EXPIRED, 100, -30),
    7: (MedicineStatus.OUT_OF_STOCK, 0, 60),
    8: (MedicineStatus.ACTIVE, 600, 500),
    9: (MedicineStatus.LOW_STOCK, 8, 150),
    10: (MedicineStatus.EXPIRED, 200, -150),
    11: (MedicineStatus.OUT_OF_STOCK, 0, 400),
}

SUPPLIERS = [
    "MedSupply Co.",
    "HealthCare Ltd.",
    "PharmaCorp",
    "GreenMed",
    "Apollo Pharmacy Supply",
    "Cipla Distributors",
    "Sun Pharma Direct",
    "Dr. Reddy's Supply",
    "Zydus Healthcare",
    "Lupin Pharma",
]

PATIENT_NAMES = [
    "Rajesh Kumar", "Sarah Smith", "Michael Johnson", "Priya Sharma",
    "Amit Patel", "Sneha Reddy", "Vikram Singh", "Anjali Desai",
    "Rohit Gupta", "Meera Nair", "Arjun Mehta", "Kavitha Rao",
    "Suresh Iyer", "Pooja Joshi", "Deepak Mishra", "Anita Kulkarni",
    "Ramesh Verma", "Sunita Pillai", "Karthik Menon", "Divya Chopra",
    "Manoj Tiwari", "Lakshmi Bhat", "Sanjay Pandey", "Rekha Agarwal",
    "Vivek Saxena", "Geeta Thakur", "Nitin Jain", "Swati Kapoor",
    "Ravi Shankar", "Uma Maheshwari", "Ibrahim Khan", "Fatima Begum",
    "Joseph Thomas", "Mary D'Souza", "Harpreet Kaur", "Gurpreet Singh",
    "Ananya Banerjee", "Sourav Das", "Nandini Murthy", "Prakash Hegde",
]


def clear_tables(db):
    db.query(SaleItem).delete()
    db.commit()
    db.query(Sale).delete()
    db.commit()
    db.query(PurchaseOrder).delete()
    db.commit()
    db.query(Medicine).delete()
    db.commit()
    print("Cleared all existing data")


def seed_medicines(db):
    meds = []
    today = date.today()
    batch_counter = 5000

    for idx, (name, generic, category) in enumerate(MEDICINES):
        batch_counter += 1
        prefix = name[:3].upper()
        batch_no = f"{prefix}-2026-{batch_counter}"

        if idx in FORCED_STATUS:
            status, quantity, days_offset = FORCED_STATUS[idx]
            expiry_date = today + timedelta(days=days_offset)
        else:
            rand = random.random()
            if rand < 0.08:
                quantity = 0
                expiry_date = today + timedelta(days=random.randint(30, 365))
                status = MedicineStatus.OUT_OF_STOCK
            elif rand < 0.18:
                quantity = random.randint(200, 500)
                expiry_date = today - timedelta(days=random.randint(1, 180))
                status = MedicineStatus.EXPIRED
            elif rand < 0.35:
                quantity = random.randint(5, 45)
                expiry_date = today + timedelta(days=random.randint(60, 500))
                status = MedicineStatus.LOW_STOCK
            else:
                quantity = random.randint(100, 800)
                expiry_date = today + timedelta(days=random.randint(90, 730))
                status = MedicineStatus.ACTIVE

        cost = round(random.uniform(8, 200), 2)
        mrp = round(cost * random.uniform(1.3, 2.0), 2)
        supplier = random.choice(SUPPLIERS)

        med = Medicine(
            name=name,
            generic_name=generic,
            category=category,
            batch_no=batch_no,
            expiry_date=expiry_date,
            quantity=quantity,
            cost_price=cost,
            mrp=mrp,
            supplier=supplier,
            status=status,
        )
        db.add(med)
        meds.append(med)

    db.commit()
    for med in meds:
        db.refresh(med)

    active = sum(1 for m in meds if m.status == MedicineStatus.ACTIVE)
    low = sum(1 for m in meds if m.status == MedicineStatus.LOW_STOCK)
    expired = sum(1 for m in meds if m.status == MedicineStatus.EXPIRED)
    oos = sum(1 for m in meds if m.status == MedicineStatus.OUT_OF_STOCK)
    print(f"Seeded {len(meds)} medicines: {active} Active, {low} Low Stock, {expired} Expired, {oos} Out of Stock")
    return meds


def seed_sales(db, medicines):
    now = datetime.now(timezone.utc)
    active_meds = [m for m in medicines if m.status == MedicineStatus.ACTIVE and m.quantity > 10]
    if not active_meds:
        print("No active medicines to create sales")
        return

    payment_cycle = list(PaymentMethod)
    sale_status_options = [
        SaleStatus.COMPLETED,
        SaleStatus.COMPLETED,
        SaleStatus.COMPLETED,
        SaleStatus.COMPLETED,
        SaleStatus.COMPLETED,
        SaleStatus.PENDING,
        SaleStatus.CANCELLED,
    ]

    sales_created = 0

    for day_offset in range(30):
        sale_date_base = now - timedelta(days=day_offset)
        num_sales = random.randint(4, 12) if day_offset == 0 else random.randint(3, 8)

        for sale_idx in range(num_sales):
            sales_created += 1
            invoice_no = f"INV-2026-{20000 + sales_created}"
            patient = random.choice(PATIENT_NAMES)
            payment = payment_cycle[(sales_created - 1) % len(payment_cycle)]
            status = sale_status_options[(sales_created - 1) % len(sale_status_options)]

            sale_time = sale_date_base.replace(
                hour=random.randint(8, 20),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )

            sale = Sale(
                invoice_no=invoice_no,
                patient_name=patient,
                payment_method=payment,
                total_amount=0,
                status=status,
                created_at=sale_time,
            )
            db.add(sale)
            db.flush()

            num_items = random.randint(1, 5)
            chosen_meds = random.sample(active_meds, min(num_items, len(active_meds)))
            total = 0

            for med in chosen_meds:
                qty = random.randint(1, 5)
                item_total = round(med.mrp * qty, 2)
                sale_item = SaleItem(
                    sale_id=sale.id,
                    medicine_id=med.id,
                    quantity=qty,
                    unit_price=med.mrp,
                    total_price=item_total,
                )
                db.add(sale_item)
                total += item_total

            sale.total_amount = round(total, 2)

        db.commit()

    print(f"Seeded {sales_created} sales across 30 days (Cash/Card/UPI + Completed/Pending/Cancelled)")


def seed_purchase_orders(db):
    now = datetime.now(timezone.utc)
    orders = []
    po_statuses = list(PurchaseOrderStatus)
    po_num = 200

    for i in range(20):
        po_num += 1
        status = po_statuses[i % len(po_statuses)]
        po = PurchaseOrder(
            order_no=f"PO-2026-{po_num}",
            supplier=SUPPLIERS[i % len(SUPPLIERS)],
            total_amount=round(random.uniform(5000, 50000), 2),
            status=status,
            created_at=now - timedelta(days=random.randint(0, 30)),
        )
        db.add(po)
        orders.append(po)

    db.commit()
    pending = sum(1 for o in orders if o.status == PurchaseOrderStatus.PENDING)
    completed = sum(1 for o in orders if o.status == PurchaseOrderStatus.COMPLETED)
    cancelled = sum(1 for o in orders if o.status == PurchaseOrderStatus.CANCELLED)
    print(f"Seeded {len(orders)} purchase orders: {pending} Pending, {completed} Completed, {cancelled} Cancelled")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Clearing existing data...")
        clear_tables(db)

        print("\nSeeding medicines...")
        medicines = seed_medicines(db)

        print("\nSeeding sales...")
        seed_sales(db, medicines)

        print("\nSeeding purchase orders...")
        seed_purchase_orders(db)

        med_count = db.query(Medicine).count()
        sale_count = db.query(Sale).count()
        item_count = db.query(SaleItem).count()
        po_count = db.query(PurchaseOrder).count()

        print("\n" + "=" * 50)
        print("DATABASE SEEDED SUCCESSFULLY")
        print("=" * 50)
        print(f"  Medicines:       {med_count}")
        print(f"  Sales:           {sale_count}")
        print(f"  Sale Items:      {item_count}")
        print(f"  Purchase Orders: {po_count}")
        print("=" * 50)

        print("\nMedicine status breakdown:")
        for s in MedicineStatus:
            c = db.query(Medicine).filter(Medicine.status == s).count()
            print(f"  {s.value}: {c}")

        print("\nCategory breakdown:")
        cats = db.query(Medicine.category).distinct().all()
        for (cat,) in sorted(cats):
            c = db.query(Medicine).filter(Medicine.category == cat).count()
            print(f"  {cat}: {c}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
