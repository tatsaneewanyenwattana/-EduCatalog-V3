/** บทบาทสำหรับ RBAC + middleware — ต้องตรงกับ claim ใน JWT */
export enum UserRole {
  VISITOR = "visitor",
  AGENCY = "agency",
  ADMIN = "admin",
}

/** โมเดล User จาก API /me เมื่อ auth พร้อม */
export enum UserStatus {
  ACTIVE = "active",
  PENDING = "pending",
  SUSPENDED = "suspended",
}

export interface User {
  id: string;
  email: string;
  fullName: string | null;
  role: UserRole;
  agencyId?: string | null;
  status: UserStatus;
  createdAt: string | null;
  updatedAt: string | null;
}
