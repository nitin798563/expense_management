"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

interface Rule {
  id: number;
  category: string;
  limit: number;
}

export default function RulesPage() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [category, setCategory] = useState("");
  const [limit, setLimit] = useState("");

  const fetchRules = async () => {
    const res = await api.get("/rules/");
    setRules(res.data);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/rules/", { category, limit: parseFloat(limit) });
    setCategory("");
    setLimit("");
    fetchRules();
  };

  useEffect(() => {
    fetchRules();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Expense Rules</h1>

      <form onSubmit={handleAdd} className="bg-white shadow p-4 rounded-md mb-6 space-y-3">
        <div className="grid gap-2 sm:grid-cols-2">
          <Input placeholder="Category" value={category} onChange={(e) => setCategory(e.target.value)} />
          <Input placeholder="Limit (₹)" type="number" value={limit} onChange={(e) => setLimit(e.target.value)} />
        </div>
        <Button type="submit" className="w-full sm:w-auto">Add Rule</Button>
      </form>

      <div className="bg-white shadow rounded-md p-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2">Category</th>
              <th>Limit (₹)</th>
            </tr>
          </thead>
          <tbody>
            {rules.map((rule) => (
              <tr key={rule.id} className="border-b hover:bg-gray-50">
                <td className="py-2">{rule.category}</td>
                <td>{rule.limit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
