function formatCurrency(amount: number): string {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(amount);
}

const statusStyles: Record<string, string> = {
    Active: "bg-emerald-50 text-emerald-600 border-emerald-200",
    "Low Stock": "bg-amber-50 text-amber-600 border-amber-200",
    Expired: "bg-red-50 text-red-600 border-red-200",
    "Out of Stock": "bg-gray-100 text-gray-500 border-gray-200",
};

export { formatCurrency, statusStyles };