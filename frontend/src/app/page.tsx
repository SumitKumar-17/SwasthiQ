"use client";

import { useState, useEffect, useCallback } from "react";
import {
  DollarSign,
  ShoppingCart,
  AlertTriangle,
  ArrowDownToLine,
  TrendingUp,
  Download,
  Plus,
  Search,
} from "lucide-react";
import { api, DashboardSummary, RecentSale, Medicine } from "@/lib/api";
import AddMedicineModal from "@/components/AddMedicineModal";

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentSales, setRecentSales] = useState<RecentSale[]>([]);
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"sales" | "purchase" | "inventory">("sales");
  const [showAddModal, setShowAddModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [patientId, setPatientId] = useState("");
  const [saleItems, setSaleItems] = useState<{ medicine_id: number; quantity: number; name: string; mrp: number }[]>([]);
  const [saleLoading, setSaleLoading] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [summaryData, salesData, medsData] = await Promise.all([
        api.dashboard.getSummary(),
        api.dashboard.getRecentSales(),
        api.inventory.getMedicines(),
      ]);
      setSummary(summaryData);
      setRecentSales(salesData);
      setMedicines(medsData);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAddToSale = (medicine: Medicine) => {
    const exists = saleItems.find((i) => i.medicine_id === medicine.id);
    if (exists) return;
    setSaleItems((prev) => [...prev, { medicine_id: medicine.id, quantity: 1, name: medicine.name, mrp: medicine.mrp }]);
    setSearchTerm("");
  };

  const handleCreateSale = async () => {
    if (!patientId || saleItems.length === 0) return;
    setSaleLoading(true);
    try {
      await api.sales.create({
        patient_name: patientId,
        payment_method: "Cash",
        items: saleItems.map(({ medicine_id, quantity }) => ({ medicine_id, quantity })),
      });
      setSaleItems([]);
      setPatientId("");
      loadData();
    } catch (err) {
      console.error("Failed to create sale:", err);
    } finally {
      setSaleLoading(false);
    }
  };

  const filteredMedicines = searchTerm
    ? medicines.filter(
      (m) =>
        m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.generic_name.toLowerCase().includes(searchTerm.toLowerCase())
    )
    : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const summaryCards = [
    {
      icon: DollarSign,
      iconBg: "bg-emerald-500",
      label: "Today's Sales",
      value: formatCurrency(summary?.todays_sales || 0),
      badge: `${(summary?.sales_change_percent ?? 0) > 0 ? "+" : ""}${summary?.sales_change_percent ?? 0}%`,
      badgeBg: "bg-emerald-50 text-emerald-600",
      badgeIcon: TrendingUp,
    },
    {
      icon: ShoppingCart,
      iconBg: "bg-blue-500",
      label: "Items Sold Today",
      value: summary?.items_sold_today?.toString() || "0",
      badge: `${summary?.total_orders_today || 0} Orders`,
      badgeBg: "bg-blue-50 text-blue-600",
    },
    {
      icon: AlertTriangle,
      iconBg: "bg-orange-500",
      label: "Low Stock Items",
      value: summary?.low_stock_items?.toString() || "0",
      badge: "Action Needed",
      badgeBg: "bg-orange-50 text-orange-600",
    },
    {
      icon: ArrowDownToLine,
      iconBg: "bg-purple-500",
      label: "Purchase Orders",
      value: formatCurrency(summary?.purchase_orders_total || 0),
      badge: `${summary?.pending_purchase_orders || 0} Pending`,
      badgeBg: "bg-purple-50 text-purple-600",
    },
  ];

  return (
    <div className="max-w-[1400px] mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-text">Pharmacy CRM</h1>
          <p className="text-text-secondary text-sm mt-1">Manage inventory, sales, and purchase orders</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2.5 rounded-lg border border-border text-sm font-medium text-text-secondary hover:bg-gray-50 transition-colors">
            <Download size={16} />
            Export
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors shadow-sm shadow-primary/20"
          >
            <Plus size={16} />
            Add Medicine
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {summaryCards.map((card, idx) => (
          <div key={idx} className="bg-white rounded-xl border border-border p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className={`w-10 h-10 ${card.iconBg} rounded-xl flex items-center justify-center`}>
                <card.icon size={20} className="text-white" />
              </div>
              <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${card.badgeBg}`}>
                {card.badgeIcon && <card.badgeIcon size={12} />}
                {card.badge}
              </div>
            </div>
            <p className="text-2xl font-bold text-text">{card.value}</p>
            <p className="text-sm text-text-muted mt-1">{card.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-border overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex gap-1">
            {(["sales", "purchase", "inventory"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === tab
                    ? "bg-gray-100 text-text"
                    : "text-text-muted hover:text-text-secondary"
                  }`}
              >
                {tab === "sales" && <ShoppingCart size={16} />}
                {tab === "purchase" && <ArrowDownToLine size={16} />}
                {tab === "inventory" && <AlertTriangle size={16} />}
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg border border-primary text-primary text-sm font-medium hover:bg-primary/5 transition-colors">
              <Plus size={16} />
              New Sale
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-sm font-medium text-text-secondary hover:bg-gray-50 transition-colors">
              <Plus size={16} />
              New Purchase
            </button>
          </div>
        </div>

        {activeTab === "sales" && (
          <div>
            <div className="bg-blue-50/60 p-5 border-b border-blue-100">
              <h3 className="text-base font-semibold text-text mb-1">Make a Sale</h3>
              <p className="text-sm text-text-secondary mb-4">Select medicines from inventory</p>
              <div className="flex gap-3 items-center">
                <input
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  placeholder="Patient Id"
                  className="px-4 py-2.5 rounded-lg border border-border bg-white text-sm w-56 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                />
                <div className="relative flex-1 max-w-md">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                  <input
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search medicines..."
                    className="w-full pl-9 pr-4 py-2.5 rounded-lg border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  />
                  {searchTerm && filteredMedicines.length > 0 && (
                    <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-border rounded-lg shadow-lg z-10 max-h-48 overflow-auto">
                      {filteredMedicines.map((med) => (
                        <button
                          key={med.id}
                          onClick={() => handleAddToSale(med)}
                          className="w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 flex justify-between items-center border-b border-border/50 last:border-0"
                        >
                          <span className="font-medium">{med.name}</span>
                          <span className="text-text-muted">{formatCurrency(med.mrp)}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <button className="px-6 py-2.5 rounded-lg bg-teal-500 text-white text-sm font-medium hover:bg-teal-600 transition-colors">
                  Enter
                </button>
                <div className="ml-auto">
                  <button
                    onClick={handleCreateSale}
                    disabled={saleLoading || saleItems.length === 0}
                    className="px-8 py-2.5 rounded-lg bg-red-500 text-white text-sm font-medium hover:bg-red-600 transition-colors disabled:opacity-50"
                  >
                    {saleLoading ? "Processing..." : "Bill"}
                  </button>
                </div>
              </div>

              {saleItems.length > 0 && (
                <div className="mt-4 bg-white rounded-lg border border-border overflow-hidden">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-50 border-b border-border">
                        <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Medicine</th>
                        <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Quantity</th>
                        <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Price</th>
                        <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {saleItems.map((item) => (
                        <tr key={item.medicine_id} className="border-b border-border/50">
                          <td className="px-4 py-2.5">{item.name}</td>
                          <td className="px-4 py-2.5">
                            <input
                              type="number"
                              min="1"
                              value={item.quantity}
                              onChange={(e) =>
                                setSaleItems((prev) =>
                                  prev.map((i) =>
                                    i.medicine_id === item.medicine_id
                                      ? { ...i, quantity: Number(e.target.value) || 1 }
                                      : i
                                  )
                                )
                              }
                              className="w-16 px-2 py-1 border border-border rounded text-center text-sm"
                            />
                          </td>
                          <td className="px-4 py-2.5">{formatCurrency(item.mrp)}</td>
                          <td className="px-4 py-2.5 font-medium">{formatCurrency(item.mrp * item.quantity)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="mt-3">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-blue-200/60">
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Medicine Name</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Generic Name</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Batch No</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Expiry Date</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Quantity</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">MRP / Price</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Supplier</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Status</th>
                      <th className="text-left px-4 py-2.5 font-semibold text-text-secondary text-xs uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody />
                </table>
              </div>
            </div>

            <div className="p-5">
              <h3 className="text-base font-semibold text-text mb-4">Recent Sales</h3>
              <div className="space-y-3">
                {recentSales.map((sale) => (
                  <div key={sale.id} className="flex items-center gap-4 p-4 rounded-xl border border-border hover:shadow-sm transition-shadow">
                    <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center">
                      <ShoppingCart size={18} className="text-emerald-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-text">{sale.invoice_no}</p>
                      <p className="text-xs text-text-muted mt-0.5">
                        {sale.patient_name} &bull; {sale.items_count} items &bull; {sale.payment_method}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-text">{formatCurrency(sale.total_amount)}</p>
                      <p className="text-xs text-text-muted mt-0.5">{formatDate(sale.created_at)}</p>
                    </div>
                    <span className="px-3 py-1 text-xs font-medium bg-emerald-50 text-emerald-600 rounded-full">
                      {sale.status}
                    </span>
                  </div>
                ))}
                {recentSales.length === 0 && (
                  <p className="text-center text-text-muted py-8 text-sm">No recent sales</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "purchase" && (
          <div className="p-8 text-center text-text-muted">
            <ArrowDownToLine size={40} className="mx-auto mb-3 opacity-30" />
            <p className="text-sm">Purchase orders management coming soon</p>
          </div>
        )}

        {activeTab === "inventory" && (
          <div className="p-8 text-center text-text-muted">
            <AlertTriangle size={40} className="mx-auto mb-3 opacity-30" />
            <p className="text-sm">View full inventory on the <a href="/inventory" className="text-primary hover:underline">Inventory page</a></p>
          </div>
        )}
      </div>

      <AddMedicineModal isOpen={showAddModal} onClose={() => setShowAddModal(false)} onSuccess={loadData} />
    </div>
  );
}
