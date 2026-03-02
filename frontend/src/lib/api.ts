const API_BASE = "https://swasthi-q-lq4k.vercel.app/api"
    // process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(error.detail || `HTTP ${res.status}`);
    }
    if (res.status === 204) return null as T;
    return res.json();
}

export interface DashboardSummary {
    todays_sales: number;
    sales_change_percent: number;
    items_sold_today: number;
    total_orders_today: number;
    low_stock_items: number;
    purchase_orders_total: number;
    pending_purchase_orders: number;
}

export interface RecentSale {
    id: number;
    invoice_no: string;
    patient_name: string;
    items_count: number;
    payment_method: string;
    total_amount: number;
    status: string;
    created_at: string;
}

export interface Medicine {
    id: number;
    name: string;
    generic_name: string;
    category: string;
    batch_no: string;
    expiry_date: string;
    quantity: number;
    cost_price: number;
    mrp: number;
    supplier: string;
    status: string;
    created_at: string;
    updated_at: string;
}

export interface InventoryOverview {
    total_items: number;
    active_stock: number;
    low_stock: number;
    total_value: number;
}

export interface MedicineCreate {
    name: string;
    generic_name: string;
    category: string;
    batch_no: string;
    expiry_date: string;
    quantity: number;
    cost_price: number;
    mrp: number;
    supplier: string;
}

export interface SaleCreate {
    patient_name: string;
    payment_method: string;
    items: { medicine_id: number; quantity: number }[];
}

export const api = {
    dashboard: {
        getSummary: () => fetchApi<DashboardSummary>("/dashboard/summary"),
        getRecentSales: () => fetchApi<RecentSale[]>("/dashboard/recent-sales"),
        getLowStock: () => fetchApi<Medicine[]>("/dashboard/low-stock"),
    },
    inventory: {
        getOverview: () => fetchApi<InventoryOverview>("/inventory/overview"),
        getMedicines: (params?: { search?: string; category?: string; status?: string }) => {
            const query = new URLSearchParams();
            if (params?.search) query.set("search", params.search);
            if (params?.category) query.set("category", params.category);
            if (params?.status) query.set("status", params.status);
            const qs = query.toString();
            return fetchApi<Medicine[]>(`/inventory/medicines${qs ? `?${qs}` : ""}`);
        },
        addMedicine: (data: MedicineCreate) =>
            fetchApi<Medicine>("/inventory/medicines", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        updateMedicine: (id: number, data: Partial<MedicineCreate>) =>
            fetchApi<Medicine>(`/inventory/medicines/${id}`, {
                method: "PUT",
                body: JSON.stringify(data),
            }),
        deleteMedicine: (id: number) =>
            fetchApi<void>(`/inventory/medicines/${id}`, { method: "DELETE" }),
        getCategories: () => fetchApi<string[]>("/inventory/categories"),
    },
    sales: {
        create: (data: SaleCreate) =>
            fetchApi<RecentSale>("/sales/", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        list: () => fetchApi<RecentSale[]>("/sales/"),
    },
};
