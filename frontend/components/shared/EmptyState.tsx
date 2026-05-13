import type { ReactNode } from "react";

export interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
}

/**
 * ใช้ซ้ำแทนหน้าว่างเมื่อ list ว่าง — ลด cognitive load ว่าโหลดแล้วแต่ไม่มีข้อมูล
 */

export function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div
      className="flex flex-col items-center border border-border bg-page text-center"
      style={{
        gap: "var(--space-3)",
        padding: "var(--pad-card-lg)",
      }}
    >
      <div className="text-primary" aria-hidden>
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-foreground">{title}</h3>
      {description ? (
        <p className="max-w-md text-sm text-foreground-secondary">
          {description}
        </p>
      ) : null}
      {action ? (
        <button
          type="button"
          className="mt-2 border border-primary text-sm font-semibold text-primary hover:bg-primary-light"
          style={{ padding: "var(--pad-btn)" }}
          onClick={action.onClick}
        >
          {action.label}
        </button>
      ) : null}
    </div>
  );
}
