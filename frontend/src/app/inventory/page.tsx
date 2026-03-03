"use client";

import { useState, useEffect, useCallback } from "react";
import {
    Package,
    CheckCircle,
    AlertTriangle,
    DollarSign,
    Filter,
    Download,
    Search,
    Plus,
    Pencil,
    Trash2,
} from "lucide-react";
import { api, Medicine, InventoryOverview } from "@/lib/api";
import AddMedicineModal from "@/components/AddMedicineModal";
import { formatCurrency, statusStyles } from "../../../common";
import MedicineColumns from "@/components/MedicineColumns";

export default function InventoryPage() {
    const [overview, setOverview] = useState<InventoryOverview | null>(null);
    const [medicines, setMedicines] = useState<Medicine[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("");
    const [categoryFilter, setCategoryFilter] = useState("");
    const [categories, setCategories] = useState<string[]>([]);
    const [showAddModal, setShowAddModal] = useState(false);
    const [editMedicine, setEditMedicine] = useState<Medicine | null>(null);
    const [showFilters, setShowFilters] = useState(false);

    const loadData = useCallback(async () => {
        try {
            setLoading(true);
            const [overviewData, medsData, catsData] = await Promise.all([
                api.inventory.getOverview(),
                api.inventory.getMedicines({
                    search: searchTerm || undefined,
                    status: statusFilter || undefined,
                    category: categoryFilter || undefined,
                }),
                api.inventory.getCategories(),
            ]);
            setOverview(overviewData);
            setMedicines(medsData);
            setCategories(catsData);
        } catch (err) {
            console.error("Failed to load inventory:", err);
        } finally {
            setLoading(false);
        }
    }, [searchTerm, statusFilter, categoryFilter]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handleDelete = async (id: number) => {
        if (!confirm("Are you sure you want to delete this medicine?")) return;
        try {
            await api.inventory.deleteMedicine(id);
            loadData();
        } catch (err) {
            console.error("Failed to delete:", err);
        }
    };

    const overviewCards = [
        {
            label: "Total Items",
            value: overview?.total_items || 0,
            icon: Package,
            iconColor: "text-blue-500",
        },
        {
            label: "Active Stock",
            value: overview?.active_stock || 0,
            icon: CheckCircle,
            iconColor: "text-emerald-500",
        },
        {
            label: "Low Stock",
            value: overview?.low_stock || 0,
            icon: AlertTriangle,
            iconColor: "text-amber-500",
        },
        {
            label: "Total Value",
            value: formatCurrency(overview?.total_value || 0),
            icon: DollarSign,
            iconColor: "text-emerald-500",
        },
    ];

    if (loading && !overview) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

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
                        onClick={() => { setEditMedicine(null); setShowAddModal(true); }}
                        className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors shadow-sm shadow-primary/20"
                    >
                        <Plus size={16} />
                        Add Medicine
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {overviewCards.map((card, idx) => (
                    <div key={idx} className="bg-white rounded-xl border border-border p-5 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between mb-2">
                            <p className="text-sm text-text-muted">{card.label}</p>
                            <card.icon size={18} className={card.iconColor} />
                        </div>
                        <p className="text-2xl font-bold text-text">{card.value}</p>
                    </div>
                ))}
            </div>

            <div className="bg-white rounded-xl border border-border overflow-hidden">
                <div className="bg-blue-50/60 p-5">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-base font-semibold text-text">Inventory Overview</h3>
                    </div>

                    <div className="grid grid-cols-4 gap-4">
                        {overviewCards.map((card, idx) => (
                            <div key={idx} className="bg-white/80 rounded-lg p-4 border border-blue-100">
                                <div className="flex items-center justify-between mb-1">
                                    <p className="text-sm text-text-muted">{card.label}</p>
                                    <card.icon size={16} className={card.iconColor} />
                                </div>
                                <p className="text-xl font-bold text-text">{card.value}</p>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="p-5 border-t border-border">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-base font-semibold text-text">Complete Inventory</h3>
                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                                <input
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    placeholder="Search medicines..."
                                    className="pl-9 pr-4 py-2 rounded-lg border border-border text-sm w-64 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                                />
                            </div>
                            <button
                                onClick={() => setShowFilters(!showFilters)}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${showFilters || statusFilter || categoryFilter
                                        ? "border-primary text-primary bg-primary/5"
                                        : "border-border text-text-secondary hover:bg-gray-50"
                                    }`}
                            >
                                <Filter size={16} />
                                Filter
                            </button>
                            <button className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-sm font-medium text-text-secondary hover:bg-gray-50 transition-colors">
                                <Download size={16} />
                                Export
                            </button>
                        </div>
                    </div>

                    {showFilters && (
                        <div className="flex gap-3 mb-4 p-3 bg-gray-50 rounded-lg">
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                className="px-3 py-2 rounded-lg border border-border text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/20"
                            >
                                <option value="">All Status</option>
                                <option value="Active">Active</option>
                                <option value="Low Stock">Low Stock</option>
                                <option value="Expired">Expired</option>
                                <option value="Out of Stock">Out of Stock</option>
                            </select>
                            <select
                                value={categoryFilter}
                                onChange={(e) => setCategoryFilter(e.target.value)}
                                className="px-3 py-2 rounded-lg border border-border text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary/20"
                            >
                                <option value="">All Categories</option>
                                {categories.map((cat) => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                            {(statusFilter || categoryFilter) && (
                                <button
                                    onClick={() => { setStatusFilter(""); setCategoryFilter(""); }}
                                    className="px-3 py-2 text-sm text-danger hover:underline"
                                >
                                    Clear filters
                                </button>
                            )}
                        </div>
                    )}

                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <MedicineColumns/>
                            <tbody>
                                {medicines.map((med) => (
                                    <tr key={med.id} className="border-b border-border/50 hover:bg-gray-50/50 transition-colors">
                                        <td className="px-4 py-3.5 font-medium text-text">{med.name}</td>
                                        <td className="px-4 py-3.5 text-text-secondary">{med.generic_name}</td>
                                        <td className="px-4 py-3.5 text-text-secondary">{med.category}</td>
                                        <td className="px-4 py-3.5 text-text-secondary font-mono text-xs">{med.batch_no}</td>
                                        <td className="px-4 py-3.5 text-text-secondary">{med.expiry_date}</td>
                                        <td className={`px-4 py-3.5 font-medium ${med.quantity === 0 ? "text-red-500" : med.quantity <= 50 ? "text-amber-500" : "text-text"
                                            }`}>
                                            {med.quantity}
                                        </td>
                                        <td className="px-4 py-3.5 text-text-secondary">{formatCurrency(med.cost_price)}</td>
                                        <td className="px-4 py-3.5 text-text-secondary">{formatCurrency(med.mrp)}</td>
                                        <td className="px-4 py-3.5 text-text-secondary">{med.supplier}</td>
                                        <td className="px-4 py-3.5">
                                            <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium border ${statusStyles[med.status] || "bg-gray-50 text-gray-500"}`}>
                                                {med.status}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3.5">
                                            <div className="flex items-center gap-1">
                                                <button
                                                    onClick={() => { setEditMedicine(med); setShowAddModal(true); }}
                                                    className="w-8 h-8 rounded-lg flex items-center justify-center text-text-muted hover:bg-blue-50 hover:text-blue-600 transition-colors"
                                                    title="Edit"
                                                >
                                                    <Pencil size={14} />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(med.id)}
                                                    className="w-8 h-8 rounded-lg flex items-center justify-center text-text-muted hover:bg-red-50 hover:text-red-600 transition-colors"
                                                    title="Delete"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                {medicines.length === 0 && (
                                    <tr>
                                        <td colSpan={11} className="px-4 py-12 text-center text-text-muted">
                                            No medicines found
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <AddMedicineModal
                isOpen={showAddModal}
                onClose={() => { setShowAddModal(false); setEditMedicine(null); }}
                onSuccess={loadData}
                editMedicine={editMedicine}
            />
        </div>
    );
}
