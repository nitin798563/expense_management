import { ReactNode } from "react";

export default function Card({ children }: { children: ReactNode }) {
  return (
    <div className="bg-white shadow rounded-lg p-6 max-w-md w-full">{children}</div>
  );
}