import Link from "next/link";
import { BookOpenText } from "lucide-react";

/**
 * แยกส่วนท้ายเป็นคอลัมน์เพื่ออ่านนโยบายและลิงก์หลักชัดเมื่อผู้ใช้หา PDPA/metadata
 */

export function Footer() {
  return (
    <footer className="mt-auto bg-footer-bg text-footer-fg">
      <div className="mx-auto grid max-w-7xl gap-8 md:grid-cols-3" style={{ padding: "var(--pad-card-lg) var(--space-4)" }}>
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2 text-accent">
            <BookOpenText className="h-8 w-8" aria-hidden />
            <span className="font-semibold">EduCatalog</span>
          </div>
          <p className="max-w-xs text-sm text-footer-muted leading-relaxed">
            แคตตาล็อกชุดข้อมูลและเมตาดาต้าภาคการศึกษาของไทยในรูปแบบค้นหาและเข้าถึงเป็นมาตรฐาน
          </p>
        </div>
        <div>
          <h3 className="mb-4 text-lg font-semibold text-footer-fg">ลิงก์</h3>
          <ul className="flex flex-col gap-2 text-sm text-footer-muted">
            <li>
              <Link className="hover:text-footer-fg" href="/search">
                ค้นหา
              </Link>
            </li>
            <li>
              <Link className="hover:text-footer-fg" href="/categories">
                หมวดหมู่
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <h3 className="mb-4 text-lg font-semibold text-footer-fg">
            นโยบาย
          </h3>
          <ul className="flex flex-col gap-2 text-sm text-footer-muted">
            <li>
              <Link className="hover:text-footer-fg" href="/privacy">
                นโยบายความเป็นส่วนตัว (PDPA)
              </Link>
            </li>
            <li>
              <Link className="hover:text-footer-fg" href="/cookies">
                การใช้คุกกี้
              </Link>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-t px-4 py-4" style={{ borderColor: "var(--color-footer-muted)" }}>
        <p className="mx-auto max-w-7xl text-xs text-footer-muted">
          © 2569 EduCatalog · ระบบ Data Catalog การศึกษาไทย
        </p>
      </div>
    </footer>
  );
}
