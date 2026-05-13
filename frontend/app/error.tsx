"use client";

import { AlertTriangle } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/** "use client" เพื่อใช้ reset() จาก error boundary ของ App Router และไม่บังคับทั้งเลย์เอาต์เป็น RCC */
export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production") {
      console.error("route error boundary", error?.digest ?? error?.message);
    }
  }, [error]);

  return (
    <div
      className="flex flex-col items-center justify-center border border-error bg-page text-center"
      style={{
        gap: "var(--space-4)",
        padding: "var(--pad-card-lg)",
        minHeight: "50vh",
      }}
    >
      <AlertTriangle className="h-16 w-16 text-warning" aria-hidden />
      <h1 className="text-2xl font-bold text-foreground">
        เกิดข้อผิดพลาดในระบบ
      </h1>
      <p className="max-w-lg text-sm text-foreground-secondary">
        เกิดความผิดพลาดที่ไม่คาดหมาย ลองใหม่อีกครั้ง หากยังเป็นอยู่ติดต่อผู้ดูแลระบบ
      </p>
      <div
        className="mt-4 flex flex-wrap justify-center"
        style={{ gap: "var(--space-3)" }}
      >
        <button
          type="button"
          className="inline-flex border border-primary bg-primary text-sm font-semibold text-primary-foreground hover:bg-primary-dark"
          style={{ padding: "var(--pad-btn)" }}
          onClick={() => reset()}
        >
          ลองใหม่
        </button>
        <Link
          href="/"
          className="inline-flex border border-border bg-surface text-sm font-semibold text-foreground hover:border-primary hover:text-primary"
          style={{ padding: "var(--pad-btn)" }}
        >
          กลับหน้าหลัก
        </Link>
      </div>
    </div>
  );
}
