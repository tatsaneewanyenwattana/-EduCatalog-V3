import { getAccessTokenCookieName } from "@/lib/auth-cookies";
import {
  decodeJwtPayload,
  isAccessTokenUsable,
  roleFromPayload,
} from "@/lib/jwt-access";
import { UserRole } from "@/types/user";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

/**
 * guard route ตาม role ใน JWT (กฎ scaffold กลุ่ม 1) — อย่าใช้แทน authorize บน API
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const token = request.cookies.get(getAccessTokenCookieName())?.value;
  const payload = token ? decodeJwtPayload(token) : null;
  const sessionOk = Boolean(payload && isAccessTokenUsable(payload));
  const role = sessionOk ? roleFromPayload(payload) : null;

  const isAuthPage = pathname === "/login" || pathname === "/register";
  if (isAuthPage && sessionOk) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  if (pathname.startsWith("/admin")) {
    if (!sessionOk || role !== UserRole.ADMIN) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  if (pathname.startsWith("/my-datasets")) {
    if (!sessionOk || (role !== UserRole.AGENCY && role !== UserRole.ADMIN)) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*", "/my-datasets/:path*", "/login", "/register"],
};
