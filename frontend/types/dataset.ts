/** สถานะ workflow dataset — mirror backend enum เมื่อ ERD พร้อม */
export enum DatasetStatus {
  DRAFT = "draft",
  PENDING_APPROVAL = "pending_approval",
  PUBLISHED = "published",
  REJECTED = "rejected",
  ARCHIVED = "archived",
}

export interface Agency {
  id: string;
  name: string;
  slug?: string | null;
}

export interface Category {
  id: string;
  name: string;
  slug?: string | null;
  parentId?: string | null;
}

export interface Dataset {
  id: string;
  slug: string;
  title: string;
  summary: string | null;
  categoryId: string | null;
  agencyId: string | null;
  status: DatasetStatus;
  updatedAt?: string | null;
  publishedAt?: string | null;
}
