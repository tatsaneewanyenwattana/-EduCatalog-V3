/** ชื่อคุ้กกี้ access JWT — เซ็กชื่อเมื่อมี reverse proxy/session หลายตัว (กฎ A5) */
export function getAccessTokenCookieName(): string {
  return process.env.NEXT_PUBLIC_AUTH_ACCESS_COOKIE ?? "ec_access_token";
}
