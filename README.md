# SwasthiQ - Pharmacy CRM

A full-stack Pharmacy CRM system for managing inventory, sales, and purchase orders.

Backend (https://swasthi-q-flame.vercel.app)

Frontend (https://swasthiq-six.vercel.app)

Dashboard page: (https://swasthiq-six.vercel.app)

Inventory Page: (https://swasthiq-six.vercel.app/inventory)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Database | PostgreSQL (NeonDB) |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Icons | Lucide React |

## Project Structure

```
SwasthiQ/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── dashboard.py
│   │   │   ├── inventory.py
│   │   │   └── sales.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── seed.py
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── inventory/page.tsx
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── AddMedicineModal.tsx
│   │   │   └── Sidebar.tsx
│   │   └── lib/
│   │       └── api.ts
│   └── package.json
└── README.md
```

## Setup & Running

> In the Backend .env you need a DATABASE_URL and the frontend env need a NEXT_PUBLIC_API_URL where the backend is hosted

### Backend

```bash
cd backend
uv venv venv
source venv/bin/activate
uv pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at http://localhost:3000, API at http://localhost:8000.

## API Contracts

### Dashboard APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/summary` | Today's sales summary, items sold, low stock count, purchase orders |
| GET | `/api/dashboard/recent-sales` | Last 10 sales with invoice, patient, amount, status |
| GET | `/api/dashboard/low-stock` | Medicines with low stock or out of stock status |

### Inventory APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory/overview` | Total items, active stock, low stock count, total inventory value |
| GET | `/api/inventory/medicines` | List medicines with search, category, and status filters |
| GET | `/api/inventory/medicines/:id` | Get single medicine details |
| POST | `/api/inventory/medicines` | Add new medicine |
| PUT | `/api/inventory/medicines/:id` | Update medicine details |
| PATCH | `/api/inventory/medicines/:id/status` | Update medicine status (Active/Low Stock/Expired/Out of Stock) |
| DELETE | `/api/inventory/medicines/:id` | Delete a medicine |
| GET | `/api/inventory/categories` | List all unique categories |

### Sales APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sales/` | Create a new sale (auto-generates invoice, deducts stock) |
| GET | `/api/sales/` | List all sales |
| GET | `/api/sales/:id/items` | Get items for a specific sale |

### Response Format

All endpoints return structured JSON. Error responses follow:

```json
{
  "detail": "Error message"
}
```

## Technical Explanation

### REST API Architecture

The backend follows a layered REST architecture:

```
Request → FastAPI Router → Route Handler → SQLAlchemy ORM → PostgreSQL (NeonDB)
```

**Route Organization**: APIs are grouped by domain into three routers, each with a distinct URL prefix:
- `/api/dashboard/*` — Read-only aggregation queries (summary stats, recent sales, low stock)
- `/api/inventory/*` — Full CRUD for medicines with filtering, search, and status management
- `/api/sales/*` — Sale creation with transactional stock deduction, listing, and item details

Each router is defined in its own module (`routes/dashboard.py`, `routes/inventory.py`, `routes/sales.py`) and registered on the FastAPI app via `app.include_router()`. This keeps route handlers focused and testable.

**Request/Response Models**: Every endpoint uses Pydantic schemas (`schemas.py`) for:
- **Input validation**: `MedicineCreate`, `MedicineUpdate`, `SaleCreate` enforce required fields, type constraints (`min_length`, `ge`, `gt`), and optional partial updates via `Optional` fields.
- **Output serialization**: `MedicineResponse`, `SaleResponse`, `DashboardSummary` ensure consistent JSON structure. The `from_attributes = True` config allows direct ORM-to-schema conversion.

### Data Consistency on Updates

The Python functions enforce data consistency through several mechanisms:

#### 1. Automatic Status Derivation
When a medicine is created (`add_medicine`) or updated (`update_medicine`), the status is **automatically computed** from the current data rather than relying on manual input:

```python
if medicine.quantity == 0:
    medicine.status = "Out of Stock"
elif medicine.quantity <= 50:
    medicine.status = "Low Stock"
elif medicine.expiry_date <= date.today():
    medicine.status = "Expired"
else:
    medicine.status = "Active"
```

This guarantees the status always reflects the true inventory state. If a user explicitly sets a status via `PATCH /medicines/:id/status`, that override is respected.

#### 2. Transactional Sale Creation
The `create_sale` function performs **multiple related operations atomically**:
1. Creates the `Sale` record
2. For each item: validates medicine exists, checks stock sufficiency, creates `SaleItem`, deducts quantity
3. Updates medicine status if stock drops to low/zero
4. Sets the total amount

If any step fails (e.g. medicine not found, insufficient stock), `db.rollback()` is called and an HTTP 400/404 error is returned. The entire sale is either fully committed or fully rolled back — no partial sales.

#### 3. Unique Constraint Enforcement
- `batch_no` on medicines has a `UNIQUE` database constraint. The `add_medicine` function checks for duplicates before insert and returns a clear error message.
- `invoice_no` on sales is auto-generated using the pattern `INV-{year}-{sequential_number}`, querying the last invoice to ensure uniqueness.

#### 4. Cascading Relationships
SQLAlchemy relationships with `cascade="all, delete-orphan"` on `Sale.items` ensure that deleting a sale automatically removes its associated `SaleItem` records, preventing orphaned data.

### Database Schema

```
medicines (id, name, generic_name, category, batch_no, expiry_date, quantity, cost_price, mrp, supplier, status, created_at, updated_at)
sales (id, invoice_no, patient_name, payment_method, total_amount, status, created_at)
sale_items (id, sale_id → sales.id, medicine_id → medicines.id, quantity, unit_price, total_price)
purchase_orders (id, order_no, supplier, total_amount, status, created_at)
```
