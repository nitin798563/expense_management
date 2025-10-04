"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import toast, { Toaster } from "react-hot-toast";

interface Expense {
  id: number;
  amount: number;
  currency: string;
  category: string;
  description: string;
  status: string;
  created_at: string;
  employee?: string;
}

export default function DashboardHome() {
  const [user, setUser] = useState<any>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [form, setForm] = useState({
    amount: "",
    currency: "INR",
    category: "",
    description: "",
  });
  const [filter, setFilter] = useState("pending");
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;
  const [loading, setLoading] = useState(false);

  const fetchExpenses = async () => {
    try {
      const res = await api.get("/expenses/");
      setExpenses(res.data);
    } catch (err) {
      console.error(err);
      toast.error("Failed to fetch expenses");
    }
  };

  useEffect(() => {
    api
      .get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => (window.location.href = "/"));
  }, []);

  useEffect(() => {
    if (user) fetchExpenses();
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/expenses/", {
        amount: parseFloat(form.amount),
        currency: form.currency,
        category: form.category,
        description: form.description,
      });
      toast.success("Expense submitted successfully ✅");
      setForm({ amount: "", currency: "INR", category: "", description: "" });
      fetchExpenses();
    } catch (err) {
      console.error(err);
      toast.error("Failed to submit expense ❌");
    } finally {
      setLoading(false);
    }
  };

  const handleApproveReject = async (id: number, action: "approve" | "reject") => {
    try {
      await api.post(`/expenses/${id}/${action}`);
      toast.success(
        action === "approve" ? "Expense approved ✅" : "Expense rejected ❌"
      );
      fetchExpenses();
    } catch (err) {
      console.error(err);
      toast.error("Failed to update expense");
    }
  };

  // ✅ Fixed filtering logic
  const filteredExpenses = expenses.filter((exp) => {
    if (user?.role === "employee") {
      // Employee: apne khud ke expense aur filter ke hisaab se
      return filter === "all" ? true : exp.status === filter;
    } else {
      // Manager/Admin: sab dekh sakta hai (pending default)
      if (filter === "all") return true;
      return exp.status === filter;
    }
  });

  const searchedExpenses = filteredExpenses.filter((exp) => {
    const searchTerm = search.toLowerCase();
    return (
      exp.employee?.toLowerCase().includes(searchTerm) ||
      exp.category.toLowerCase().includes(searchTerm) ||
      exp.description.toLowerCase().includes(searchTerm)
    );
  });

  // ✅ Manager/Admin ke liye pending default view
  const displayedExpenses =
    user?.role === "manager" || user?.role === "admin"
      ? searchedExpenses.filter((exp) => exp.status === filter)
      : searchedExpenses;

  const paginatedExpenses = displayedExpenses.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  if (!user)
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-400">
        <p className="text-white text-lg animate-pulse">Loading Dashboard...</p>
      </main>
    );

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-400 p-6">
      <Toaster position="top-right" reverseOrder={false} />
      <div className="max-w-6xl mx-auto bg-white/90 backdrop-blur-lg rounded-2xl shadow-2xl p-8">
        {/* Header */}
        <header className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome, {user.username} 👋
          </h1>
          <p className="text-gray-600 mt-2">
            Role:{" "}
            <span className="capitalize font-medium text-indigo-600">
              {user.role}
            </span>
          </p>
        </header>

        {/* EMPLOYEE VIEW */}
        {user.role === "employee" && (
          <>
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              💰 Submit New Expense
            </h2>

            <form
              onSubmit={handleSubmit}
              className="grid sm:grid-cols-2 gap-6 mb-10 bg-white/80 backdrop-blur-md p-6 rounded-2xl shadow-lg border border-gray-100"
            >
              <InputField
                label="💰 Amount"
                type="number"
                placeholder="Enter Amount (e.g. 500)"
                value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                required
              />
              <InputField
                label="🏷️ Category"
                type="text"
                placeholder="Enter Category (e.g. Travel, Food)"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                required
              />
              <TextAreaField
                label="✏️ Description"
                placeholder="Add Description (optional)"
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
              <button
                type="submit"
                disabled={loading}
                className="sm:col-span-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold px-6 py-3 rounded-lg shadow-md transition-all duration-300 hover:shadow-lg disabled:opacity-50"
              >
                {loading ? "Submitting..." : "🚀 Submit Expense"}
              </button>
            </form>

            {/* My Expenses */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-800">
                🧾 My Submitted Expenses
              </h2>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-gray-700 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 shadow-sm"
              >
                <option value="all">All</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {filteredExpenses.length === 0 ? (
              <p className="text-gray-600">No expenses found.</p>
            ) : (
              <ExpenseTable data={filteredExpenses} role="employee" />
            )}
          </>
        )}

        {/* MANAGER / ADMIN VIEW */}
        {(user.role === "manager" || user.role === "admin") && (
          <>
            <h2 className="text-xl font-semibold mb-4 text-gray-800">
              ✅ Pending Expenses for Review
            </h2>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row justify-between gap-4 mb-4">
              <input
                type="text"
                placeholder="🔍 Search by employee, category, or description..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 bg-white text-gray-700 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 shadow-sm"
              />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-gray-700 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 shadow-sm"
              >
                <option value="pending">Pending</option>
                <option value="all">All</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {displayedExpenses.length === 0 ? (
              <p className="text-gray-600">No matching expenses found.</p>
            ) : (
              <ExpenseTable
                data={paginatedExpenses}
                role={user.role}
                onAction={handleApproveReject}
              />
            )}

            {/* Pagination */}
            <div className="flex justify-between items-center mt-4">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 bg-indigo-500 text-white rounded-md disabled:opacity-50"
              >
                Prev
              </button>
              <span className="text-gray-700">
                Page {currentPage} of{" "}
                {Math.ceil(displayedExpenses.length / itemsPerPage) || 1}
              </span>
              <button
                onClick={() =>
                  setCurrentPage((p) =>
                    p < Math.ceil(displayedExpenses.length / itemsPerPage)
                      ? p + 1
                      : p
                  )
                }
                disabled={
                  currentPage >=
                  Math.ceil(displayedExpenses.length / itemsPerPage)
                }
                className="px-3 py-1 bg-indigo-500 text-white rounded-md disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  );
}

/* --- Helper Components --- */
function InputField({ label, ...props }: any) {
  return (
    <div className="flex flex-col">
      <label className="text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        {...props}
        className="border border-gray-300 px-4 py-2 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 bg-white shadow-sm"
      />
    </div>
  );
}

function TextAreaField({ label, ...props }: any) {
  return (
    <div className="flex flex-col sm:col-span-2">
      <label className="text-sm font-medium text-gray-700 mb-1">{label}</label>
      <textarea
        {...props}
        className="border border-gray-300 px-4 py-2 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 bg-white shadow-sm h-28 resize-none"
      />
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    approved: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
    pending: "bg-yellow-100 text-yellow-700",
  };
  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold ${
        styles[status] || "bg-gray-100 text-gray-700"
      }`}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}

function ExpenseTable({
  data,
  role,
  onAction,
}: {
  data: Expense[];
  role: string;
  onAction?: (id: number, action: "approve" | "reject") => void;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border rounded-lg bg-white shadow-sm">
        <thead className="bg-indigo-50 text-indigo-700">
          <tr>
            {role !== "employee" && (
              <th className="p-3 text-left font-semibold">Employee</th>
            )}
            <th className="p-3 text-left font-semibold">Category</th>
            <th className="p-3 text-left font-semibold">Description</th>
            <th className="p-3 text-left font-semibold">Amount</th>
            <th className="p-3 text-left font-semibold">Status</th>
            {role !== "employee" && (
              <th className="p-3 text-left font-semibold">Actions</th>
            )}
          </tr>
        </thead>
        <tbody>
          {data.map((exp) => (
            <tr key={exp.id} className="border-t hover:bg-indigo-50/30">
              {role !== "employee" && (
                <td className="p-3">{exp.employee || "N/A"}</td>
              )}
              <td className="p-3">{exp.category}</td>
              <td className="p-3 text-gray-600">{exp.description}</td>
              <td className="p-3 font-medium">
                {exp.currency} {exp.amount}
              </td>
              <td className="p-3">
                <StatusBadge status={exp.status} />
              </td>
              {role !== "employee" && exp.status === "pending" && (
                <td className="p-3 flex gap-2">
                  <button
                    onClick={() => onAction && onAction(exp.id, "approve")}
                    className="px-3 py-1 bg-green-500 text-white text-sm rounded-md hover:bg-green-600 transition"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => onAction && onAction(exp.id, "reject")}
                    className="px-3 py-1 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition"
                  >
                    Reject
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}