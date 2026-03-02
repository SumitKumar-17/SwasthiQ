"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Search,
    LayoutGrid,
    Menu,
    TrendingUp,
    CalendarDays,
    Users,
    Pill,
    Link as LinkIcon,
    Plus,
    Sparkles,
    Settings,
} from "lucide-react";

const navItems = [
    { icon: Search, href: "#", label: "Search" },
    { icon: LayoutGrid, href: "/", label: "Dashboard" },
    { icon: Menu, href: "#", label: "Menu" },
    { icon: TrendingUp, href: "#", label: "Analytics" },
    { icon: CalendarDays, href: "#", label: "Calendar" },
    { icon: Users, href: "#", label: "Customers" },
    { icon: Pill, href: "/inventory", label: "Inventory" },
    { icon: LinkIcon, href: "#", label: "Links" },
];

const bottomItems = [
    { icon: Plus, href: "#", label: "Add" },
    { icon: Sparkles, href: "#", label: "AI" },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 h-screen w-[72px] bg-white border-r border-border flex flex-col items-center py-6 z-50">
            <nav className="flex flex-col items-center gap-2 flex-1">
                {navItems.map((item) => {
                    const isActive =
                        (item.href === "/" && pathname === "/") ||
                        (item.href !== "/" && item.href !== "#" && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.label}
                            href={item.href}
                            className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 group relative ${isActive
                                    ? "bg-primary text-white shadow-md shadow-primary/30"
                                    : "text-text-muted hover:bg-gray-100 hover:text-text-secondary"
                                }`}
                            title={item.label}
                        >
                            <item.icon size={20} strokeWidth={isActive ? 2.5 : 2} />
                        </Link>
                    );
                })}
            </nav>

            <div className="flex flex-col items-center gap-2 mt-auto">
                {bottomItems.map((item) => (
                    <Link
                        key={item.label}
                        href={item.href}
                        className="w-10 h-10 rounded-xl flex items-center justify-center text-text-muted hover:bg-gray-100 hover:text-text-secondary transition-all duration-200"
                        title={item.label}
                    >
                        <item.icon size={20} />
                    </Link>
                ))}
                <div className="w-8 h-[1px] bg-border my-1" />
                <Link
                    href="#"
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-text-muted hover:bg-gray-100 hover:text-text-secondary transition-all duration-200"
                    title="Settings"
                >
                    <Settings size={20} />
                </Link>
            </div>
        </aside>
    );
}
