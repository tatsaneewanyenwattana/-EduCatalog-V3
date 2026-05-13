import { FileQuestion } from "lucide-react";
import Link from "next/link";

/** ประกอบจาก root layout แล้ว (Navbar/Footer เดิม) — เฉพาะเนื้อหา center */
export default function NotFoundPage() {
  return (
    <div
      className="flex flex-col items-center justify-center border border-border bg-page text-center"
      style={{
        gap: "var(--space-4)",
        padding: "var(--pad-card-lg)",
        minHeight: "50vh",
      }}
    >
      <FileQuestion
        className="h-16 w-16 text-primary"
        strokeWidth={1.5}
        aria-hidden
      />
      <h1 className="text-2xl font-bold text-foreground">
        ไม่พบหน้าที่คุณต้องการ
      </h1>
      <p className="max-w-md text-sm text-foreground-secondary">
        เส้นทางที่ขอไม่มีในระบบ หรือถูกย้าย — ใช้ค้นหาหรือกลับหน้าแรกแทน
      </p>
      <div
        className="mt-6 flex flex-wrap justify-center"
        style={{ gap: "var(--space-3)" }}
      >
        <Link
          href="/"
          className="inline-flex border border-primary bg-primary text-sm font-semibold text-primary-foreground hover:bg-primary-dark"
          style={{ padding: "var(--pad-btn)" }}
        >
          กลับหน้าหลัก
        </Link>
        <Link
          href="/search"
          className="inline-flex border border-border bg-surface text-sm font-semibold text-foreground hover:border-primary hover:text-primary"
          style={{ padding: "var(--pad-btn)" }}
        >
          ค้นหา
        </Link>
      </div>
    </div>
  );
}
