"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Switch from "@/components/ui/Switch";

export default function ProfilePage() {
  const [user, setUser] = useState<any>(null);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    api.get("/auth/me").then((res) => setUser(res.data)).catch(() => {});
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  if (!user) return <p>Loading...</p>;

  return (
    <div className="max-w-md bg-white shadow rounded-md p-6">
      <h1 className="text-2xl font-semibold mb-4">Profile</h1>
      <p><strong>Username:</strong> {user.username}</p>
      <p><strong>Role:</strong> {user.role}</p>
      <div className="mt-4 flex items-center justify-between">
        <span>Dark Mode</span>
        <Switch checked={dark} onChange={() => setDark(!dark)} />
      </div>
    </div>
  );
}