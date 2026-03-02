"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { api, MedicineCreate, Medicine } from "@/lib/api";

interface AddMedicineModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
    editMedicine?: Medicine | null;
}

const initialForm: MedicineCreate = {
    name: "",
    generic_name: "",
    category: "",
    batch_no: "",
    expiry_date: "",
    quantity: 0,
    cost_price: 0,
    mrp: 0,
    supplier: "",
};

export default function AddMedicineModal({ isOpen, onClose, onSuccess, editMedicine }: AddMedicineModalProps) {
    const [form, setForm] = useState<MedicineCreate>(
        editMedicine
            ? {
                name: editMedicine.name,
                generic_name: editMedicine.generic_name,
                category: editMedicine.category,
                batch_no: editMedicine.batch_no,
                expiry_date: editMedicine.expiry_date,
                quantity: editMedicine.quantity,
                cost_price: editMedicine.cost_price,
                mrp: editMedicine.mrp,
                supplier: editMedicine.supplier,
            }
            : initialForm
    );
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setForm((prev) => ({
            ...prev,
            [name]: type === "number" ? Number(value) : value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            if (editMedicine) {
                await api.inventory.updateMedicine(editMedicine.id, form);
            } else {
                await api.inventory.addMedicine(form);
            }
            onSuccess();
            onClose();
            setForm(initialForm);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : "Failed to save medicine");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[100]" onClick={onClose}>
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 animate-in" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between p-6 border-b border-border">
                    <h2 className="text-lg font-semibold text-text">
                        {editMedicine ? "Update Medicine" : "Add New Medicine"}
                    </h2>
                    <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-text-muted transition-colors">
                        <X size={18} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {error && (
                        <div className="bg-danger-light text-danger text-sm px-4 py-3 rounded-lg">{error}</div>
                    )}

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">Medicine Name</label>
                            <input name="name" value={form.name} onChange={handleChange} required className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder="Paracetamol 650mg" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">Generic Name</label>
                            <input name="generic_name" value={form.generic_name} onChange={handleChange} required className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder="Acetaminophen" />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">Category</label>
                            <input name="category" value={form.category} onChange={handleChange} required className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder="Analgesic" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">Batch Number</label>
                            <input name="batch_no" value={form.batch_no} onChange={handleChange} required className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder="PCM-2024-0892" />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">Expiry Date</label>
                            <input name="expiry_date" type="date" value={form.expiry_date} onChange={handleChange} required className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">Quantity</label>
                            <input name="quantity" type="number" value={form.quantity} onChange={handleChange} required min="0" className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">Cost Price (₹)</label>
                            <input name="cost_price" type="number" step="0.01" value={form.cost_price} onChange={handleChange} required min="0" className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-text-secondary mb-1">MRP (₹)</label>
                            <input name="mrp" type="number" step="0.01" value={form.mrp} onChange={handleChange} required min="0" className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1">Supplier</label>
                        <input name="supplier" value={form.supplier} onChange={handleChange} required className="w-full px-3 py-2 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" placeholder="MedSupply Co." />
                    </div>

                    <div className="flex gap-3 pt-2">
                        <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 rounded-lg border border-border text-sm font-medium text-text-secondary hover:bg-gray-50 transition-colors">
                            Cancel
                        </button>
                        <button type="submit" disabled={loading} className="flex-1 px-4 py-2.5 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50">
                            {loading ? "Saving..." : editMedicine ? "Update Medicine" : "Add Medicine"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
