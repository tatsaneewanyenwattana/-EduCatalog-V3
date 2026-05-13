/**
 * Wrapper ความสำเร็จ — ให้ตรงกับ API_CONTRACT (กฎ C2)
 */
export interface ApiResponse<T> {
  data: T;
}

/**
 * Wrapper หน้า list พร้อม meta pagination (กฎ C2 + C6)
 */
export interface ApiListResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  total: number;
  limit: number;
}

/** ให้จับจาก body { error, code?, detail } ตาม errors.py เมื่อผูกจริง */
export interface ApiErrorBody {
  error: string;
  code?: number;
  detail?: string;
}

/** Normalize จาก axios/backend ให้ UX โชว์ได้สม่ำเสมอ (ทั้ง toast + inline) */
export class AppError extends Error {
  readonly code: number;

  readonly body: ApiErrorBody;

  constructor(message: string, code: number, body: ApiErrorBody) {
    super(message);
    this.code = code;
    this.body = body;
    this.name = "AppError";
  }
}
