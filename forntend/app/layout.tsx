import "./globals.css";
import { ReactNode } from "react";

export const metadata = {
  title: "Expense Management Dashboard",
  description: "Next.js frontend for FastAPI expense manager",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen">{children}</body>
    </html>
  );
}