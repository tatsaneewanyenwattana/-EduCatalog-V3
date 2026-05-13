import { AppError } from "@/types/api";
import { useUiStore } from "@/stores/uiStore";

/** ให้ query/mutation ปิด toast รวมได้เมื่อจัด error เอง (อ่านใน meta ของแต่ละ query ถ้าต้องข้าม) */
export const QUERY_CLIENT_META = {
  SKIP_GLOBAL_ERROR_TOAST: "skipGlobalErrorToast",
} as const;

function messageFromUnknown(err: unknown): string {
  if (err instanceof AppError) {
    return typeof err.body.detail === "string" && err.body.detail.length > 0
      ? err.body.detail
      : err.message;
  }
  if (err instanceof Error) return err.message;
  return "เกิดข้อผิดพลาด กรุณาลองใหม่";
}

/**
 * รวมจุดแสดง toast error (กฎ F5) — query/mutation ที่ไม่อยากซ้ำซ้อนใช้ meta ข้างบน
 */
export const defaultOptions = {
  onError: (err: unknown) => {
    const msg = messageFromUnknown(err);
    useUiStore.getState().addToast({ type: "error", message: msg });
  },
};

export function isAppError(err: unknown): err is AppError {
  return err instanceof AppError;
}
