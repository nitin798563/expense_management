"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function DashboardHome() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    api
      .get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => (window.location.href = "/"));
  }, []);

  if (!user)
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-400">
        <p className="text-white text-lg animate-pulse">Loading Dashboard...</p>
      </main>
    );

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-400 p-6">
      <div className="max-w-6xl mx-auto bg-white/90 backdrop-blur-lg rounded-2xl shadow-2xl p-8">
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

        <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {user.role === "admin" && (
            <DashboardCard
              title="Manage Users"
              desc="View and edit all users"
              icon="👥"
            />
          )}
          {(user.role === "admin" || user.role === "manager") && (
            <DashboardCard
              title="Approve Expenses"
              desc="Review and approve submitted expenses"
              icon="✅"
            />
          )}
          <DashboardCard
            title="Submit Expense"
            desc="Create a new expense entry"
            icon="💰"
          />
          <DashboardCard
            title="Rules"
            desc="Manage category and policy rules"
            icon="⚙️"
          />
        </section>
      </div>
    </main>
  );
}

function DashboardCard({
  title,
  desc,
  icon,
}: {
  title: string;
  desc: string;
  icon: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-5 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="font-semibold text-gray-800 text-lg">{title}</h3>
      <p className="text-sm text-gray-500 mt-1">{desc}</p>
    </div>
  );
}