"use client";

import { useState } from "react";
import api from "@/lib/api";
import Button from "@/components/ui/Button";

export default function OCRPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<string>("");

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post("/utils/ocr", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data.text);
    } catch {
      setResult("Error processing the image.");
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Receipt OCR</h1>
      <form onSubmit={handleUpload} className="bg-white shadow p-4 rounded-md space-y-4">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="w-full"
        />
        <Button type="submit" className="w-full sm:w-auto">
          Upload & Extract
        </Button>
      </form>

      {result && (
        <div className="mt-6 bg-white shadow rounded-md p-4">
          <h2 className="font-semibold mb-2">Extracted Text:</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{result}</p>
        </div>
      )}
    </div>
  );
}