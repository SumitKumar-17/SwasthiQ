from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import dashboard, inventory, sales
from app.seed import seed_database

# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SwasthiQ Pharmacy CRM API",
    description="REST API for pharmacy inventory, sales, and purchase order management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(inventory.router)
app.include_router(sales.router)


# @app.on_event("startup")
# def on_startup():
#     seed_database()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "SwasthiQ Pharmacy CRM API"}
