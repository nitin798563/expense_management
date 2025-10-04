"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function Topbar() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    api.get("/auth/me").then((res) => setUser(res.data)).catch(() => {});
  }, []);

  return (
    <header className="flex items-center justify-between bg-white shadow px-6 py-3">
      <h2 className="text-lg font-semibold">Dashboard</h2>
      {user && (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>{user.username}</span>
          <span className="text-gray-400">|</span>
          <span className="capitalize">{user.role}</span>
        </div>
      )}
    </header>
  );
}