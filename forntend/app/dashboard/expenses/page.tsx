"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

interface Expense {
  id: number;
  title: string;
  amount: number;
  category: string;
  status: string;
}

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");

  const fetchExpenses = async () => {
    const res = await api.get("/expenses/");
    setExpenses(res.data);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/expenses/", {
      title,
      amount: parseFloat(amount),
      category,
    });
    setTitle("");
    setAmount("");
    setCategory("");
    fetchExpenses();
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Expenses</h1>

      <form onSubmit={handleAdd} className="bg-white shadow p-4 rounded-md mb-6 space-y-3">
        <div className="grid gap-2 sm:grid-cols-3">
          <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <Input placeholder="Amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} />
          <Input placeholder="Category" value={category} onChange={(e) => setCategory(e.target.value)} />
        </div>
        <Button type="submit" className="w-full sm:w-auto">Add Expense</Button>
      </form>

      <div className="bg-white shadow rounded-md p-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2">Title</th>
              <th>Amount</th>
              <th>Category</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {expenses.map((exp) => (
              <tr key={exp.id} className="border-b hover:bg-gray-50">
                <td className="py-2">{exp.title}</td>
                <td>${exp.amount.toFixed(2)}</td>
                <td>{exp.category}</td>
                <td>
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      exp.status === "approved"
                        ? "bg-green-100 text-green-700"
                        : exp.status === "rejected"
                        ? "bg-red-100 text-red-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {exp.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}