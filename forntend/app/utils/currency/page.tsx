"use client";

import { useState } from "react";
import api from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

export default function CurrencyPage() {
  const [amount, setAmount] = useState("");
  const [from, setFrom] = useState("USD");
  const [to, setTo] = useState("INR");
  const [result, setResult] = useState<string | null>(null);

  const handleConvert = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.get(`/utils/convert?amount=${amount}&from=${from}&to=${to}`);
      setResult(`${amount} ${from} = ${res.data.converted_amount} ${to}`);
    } catch {
      setResult("Conversion failed.");
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Currency Converter</h1>
      <form onSubmit={handleConvert} className="bg-white shadow p-4 rounded-md space-y-4">
        <div className="grid gap-3 sm:grid-cols-3">
          <Input placeholder="Amount" value={amount} onChange={(e) => setAmount(e.target.value)} />
          <Input placeholder="From (e.g., USD)" value={from} onChange={(e) => setFrom(e.target.value)} />
          <Input placeholder="To (e.g., INR)" value={to} onChange={(e) => setTo(e.target.value)} />
        </div>
        <Button type="submit" className="w-full sm:w-auto">Convert</Button>
      </form>

      {result && (
        <div className="mt-6 bg-white shadow rounded-md p-4">
          <p className="text-lg font-medium text-indigo-600">{result}</p>
        </div>
      )}
    </div>
  );
}