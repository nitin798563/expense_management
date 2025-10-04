"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, FileText, CheckCircle, Settings, Camera, DollarSign, LogOut } from "lucide-react";
import { clearToken } from "@/lib/auth";

export default function Sidebar() {
  const pathname = usePathname();
  const nav = [
    { name: "Dashboard", href: "/dashboard", icon: Home },
    { name: "Expenses", href: "/dashboard/expenses", icon: FileText },
    { name: "Approvals", href: "/dashboard/approvals", icon: CheckCircle },
    { name: "Rules", href: "/dashboard/rules", icon: Settings },
    { name: "OCR", href: "/utils/ocr", icon: Camera },
    { name: "Currency", href: "/utils/currency", icon: DollarSign },
  ];

  const handleLogout = () => {
    clearToken();
    window.location.href = "/";
  };

  return (
    <aside className="w-64 bg-white shadow-lg flex flex-col p-4">
      <h1 className="text-xl font-bold mb-6 text-indigo-600">Expense Manager</h1>
      <nav className="flex-1 space-y-2">
        {nav.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 rounded-md p-2 text-sm font-medium ${
                active ? "bg-indigo-100 text-indigo-600" : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <Icon size={18} />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <button
        onClick={handleLogout}
        className="flex items-center gap-2 mt-4 text-red-500 hover:text-red-700"
      >
        <LogOut size={18} /> Logout
      </button>
    </aside>
  );
}