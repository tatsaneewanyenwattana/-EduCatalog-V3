"use client";

import Link from "next/link";
import { useState } from "react";
import { BookOpenText, Layers, Menu, X } from "lucide-react";

/**
 * แยกจาก layout เป็น component เพื่อทดสอบ nav แต่โดดเดียวได้ และควบคุม mobile drawer เป็น client subtree
 */

function docsHref(): string {
  return (
    process.env.NEXT_PUBLIC_BACKEND_DOCS_URL ?? "http://localhost:8000/docs"
  );
}

export function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <header className="fixed left-0 right-0 top-0 z-[60] border-b border-border bg-surface">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2 text-primary">
          <BookOpenText className="h-9 w-9" aria-hidden />
          <span className="flex flex-col text-left font-semibold leading-tight text-foreground">
            <span className="text-sm text-foreground-secondary">EduCatalog</span>
            <span className="text-base">ระบบ Data Catalog การศึกษาไทย</span>
          </span>
        </Link>

        <nav className="hidden flex-1 items-center justify-center gap-8 md:flex">
          <Link
            className="text-sm font-medium text-foreground-secondary transition hover:text-foreground"
            href="/search"
          >
            ค้นหา
          </Link>
          <Link
            className="text-sm font-medium text-foreground-secondary transition hover:text-foreground"
            href="/categories"
          >
            หมวดหมู่
          </Link>
          <a
            href={docsHref()}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-foreground-secondary transition hover:text-foreground"
          >
            API Docs
          </a>
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <Link
            href="/login"
            className="inline-flex items-center px-[14px] py-2 text-sm font-semibold text-primary underline-offset-4 hover:underline"
            style={{ padding: "var(--pad-btn-sm)" }}
          >
            เข้าสู่ระบบ
          </Link>
          <Link
            href="/register"
            className="inline-flex bg-primary px-[20px] py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary-dark"
            style={{ padding: "var(--pad-btn)" }}
          >
            สมัครสมาชิก
          </Link>
        </div>

        <button
          type="button"
          aria-label={open ? "ปิดเมนู" : "เปิดเมนู"}
          className="inline-flex items-center justify-center border border-border bg-surface p-2 md:hidden"
          style={{ padding: "var(--space-2)" }}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-border bg-surface md:hidden">
          <div className="flex flex-col gap-1 px-4 py-3">
            <Link
              className="py-3 text-base font-medium text-foreground-secondary"
              href="/search"
              onClick={() => setOpen(false)}
            >
              ค้นหา
            </Link>
            <Link
              className="flex items-center gap-2 py-3 text-base font-medium text-foreground-secondary"
              href="/categories"
              onClick={() => setOpen(false)}
            >
              <Layers className="h-4 w-4" aria-hidden /> หมวดหมู่
            </Link>
            <a
              href={docsHref()}
              target="_blank"
              rel="noopener noreferrer"
              className="py-3 text-base font-medium text-foreground-secondary"
              onClick={() => setOpen(false)}
            >
              API Docs
            </a>
            <div className="mt-2 flex flex-col gap-2 border-t border-border pt-3">
              <Link
                href="/login"
                className="inline-flex justify-center border border-primary py-2.5 text-sm font-semibold text-primary"
                style={{ padding: "var(--pad-btn)" }}
                onClick={() => setOpen(false)}
              >
                เข้าสู่ระบบ
              </Link>
              <Link
                href="/register"
                className="inline-flex justify-center bg-primary py-2.5 text-sm font-semibold text-primary-foreground"
                style={{ padding: "var(--pad-btn)" }}
                onClick={() => setOpen(false)}
              >
                สมัครสมาชิก
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
