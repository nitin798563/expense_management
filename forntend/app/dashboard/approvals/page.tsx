"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Button from "@/components/ui/Button";

interface Expense {
  id: number;
  title: string;
  amount: number;
  category: string;
  status: string;
  user: string;
}

export default function ApprovalsPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);

  const fetchPending = async () => {
    const res = await api.get("/expenses/pending");
    setExpenses(res.data);
  };

  const handleApprove = async (id: number) => {
    await api.post(`/expenses/${id}/approve`);
    fetchPending();
  };

  const handleReject = async (id: number) => {
    await api.post(`/expenses/${id}/reject`);
    fetchPending();
  };

  useEffect(() => {
    fetchPending();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Pending Approvals</h1>
      <div className="bg-white shadow rounded-md p-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2">Title</th>
              <th>Amount</th>
              <th>Category</th>
              <th>Submitted By</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {expenses.map((exp) => (
              <tr key={exp.id} className="border-b hover:bg-gray-50">
                <td className="py-2">{exp.title}</td>
                <td>${exp.amount.toFixed(2)}</td>
                <td>{exp.category}</td>
                <td>{exp.user}</td>
                <td className="space-x-2">
                  <Button onClick={() => handleApprove(exp.id)} className="bg-green-600 hover:bg-green-700">
                    Approve
                  </Button>
                  <Button onClick={() => handleReject(exp.id)} className="bg-red-600 hover:bg-red-700">
                    Reject
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}