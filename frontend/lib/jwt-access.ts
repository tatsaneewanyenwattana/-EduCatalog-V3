import { UserRole } from "@/types/user";

/**
 * claims จาก access JWT — เฉพาะ field ที่ใช้ใน middleware (ไม่ verify ซ้ำ ต้องให้ backend เป็นตัว definitive)
 */
export interface JwtAccessPayload {
  exp?: number;
  role?: string;
  sub?: string;
}

export function decodeJwtPayload(payload: string): JwtAccessPayload | null {
  try {
    if (typeof atob !== "function") return null;
    const parts = payload.split(".");
    if (parts.length < 2) return null;
    const b64 = parts[1]?.replace(/-/g, "+").replace(/_/g, "/") ?? "";
    const padLen = (4 - (b64.length % 4)) % 4;
    const padded = b64 + "=".repeat(padLen);
    const json = atob(padded);
    return JSON.parse(json) as JwtAccessPayload;
  } catch {
    return null;
  }
}
export function roleFromPayload(
  payload: JwtAccessPayload | null,
): UserRole | null {
  if (!payload?.role) return null;
  const hit = (Object.values(UserRole) as string[]).includes(payload.role);
  return hit ? (payload.role as UserRole) : null;
}

/** ตรวจแค่ exp เพื่อ UX redirect — การอนุญาตจริงอยู่ที่ API */
export function isAccessTokenUsable(payload: JwtAccessPayload | null): boolean {
  if (!payload) return false;
  if (typeof payload.exp !== "number") return true;
  return payload.exp * 1000 > Date.now();
}
