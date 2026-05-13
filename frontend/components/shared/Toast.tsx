"use client";

import { useUiStore, type UiToast } from "@/stores/uiStore";
import { useEffect } from "react";

/**
 * ซ้อน toast ทางมุมขวาล่างเพื่อไม่บัง Navbar — auto dismiss ให้สอดคล้อง UX มาตรฐาน (กฎ F5)
 */

function ToastPiece({ toast }: { toast: UiToast }) {
  const remove = useUiStore((s) => s.removeToast);

  useEffect(() => {
    const t = setTimeout(() => remove(toast.id), 3000);
    return () => clearTimeout(t);
  }, [remove, toast.id]);

  const accent =
    toast.type === "success"
      ? "border-success bg-primary-light text-foreground"
      : toast.type === "warning"
        ? "border-warning bg-page text-foreground"
        : "border-error bg-page text-foreground";

  return (
    <div
      className={`pointer-events-auto border shadow-md ${accent}`}
      style={{ padding: "var(--pad-card)", minWidth: "260px" }}
      role="status"
    >
      <p className="text-sm font-medium">{toast.message}</p>
    </div>
  );
}

export function ToastHost() {
  const toasts = useUiStore((s) => s.toasts);
  return (
    <div className="pointer-events-none fixed bottom-0 right-0 z-[100] flex flex-col items-end gap-2 p-4">
      {toasts.map((t) => (
        <ToastPiece key={t.id} toast={t} />
      ))}
    </div>
  );
}
