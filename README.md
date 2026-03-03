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
