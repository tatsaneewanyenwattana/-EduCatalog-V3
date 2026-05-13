"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

/** ประกาศอยู่ครั้งเดียวเพื่อไม่เก็บ consent ครั้งเก่าวนลูปเมื่อ refactor key */
export const EDUCATALOG_COOKIE_STORAGE_KEY = "ec_cookie_consent_v1";

/**
 * เก็บ consent ใน localStorage เพราะเป็น preference ผู้ใช้ฝั่ง client — เก็บ httpOnly เฉพาะ token จาก auth
 */

export function CookieBanner() {
  const [hide, setHide] = useState(true);

  useEffect(() => {
    try {
      const accepted = typeof window !== "undefined" &&
        window.localStorage.getItem(EDUCATALOG_COOKIE_STORAGE_KEY) === "1";
      setHide(Boolean(accepted));
    } catch {
      setHide(false);
    }
  }, []);

  function accept(): void {
    try {
      window.localStorage.setItem(EDUCATALOG_COOKIE_STORAGE_KEY, "1");
    } finally {
      setHide(true);
    }
  }

  if (hide) return null;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-[80] border-t border-border bg-surface p-4 shadow-lg"
      style={{ padding: "var(--pad-card)" }}
      role="dialog"
      aria-labelledby="cookie-title"
      aria-live="polite"
    >
      <div className="mx-auto flex max-w-7xl flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 id="cookie-title" className="font-semibold text-foreground">
            คุกกี้เพื่อปรับปรุงประสบการณ์
          </h2>
          <p className="mt-1 max-w-xl text-sm text-foreground-secondary">
            เราใช้คุกกี้เก็บ consent และสถานะ session ตามนโยบาย PDPA และกฎ D ของ EduCatalog
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          <Link
            href="/cookies"
            className="inline-flex items-center justify-center border border-border bg-page px-[20px] py-2.5 text-sm font-semibold text-foreground"
            style={{ padding: "var(--pad-btn)" }}
          >
            ดูนโยบาย
          </Link>
          <button
            type="button"
            onClick={() => accept()}
            className="inline-flex bg-primary px-[20px] py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary-dark"
            style={{ padding: "var(--pad-btn)" }}
          >
            ยอมรับ
          </button>
        </div>
      </div>
    </div>
  );
}
