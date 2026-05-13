import { useAuthStore } from "@/stores/authStore";
import { AppError, type ApiErrorBody } from "@/types/api";
import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

/**
 * เวอร์ชัน API จาก env — ห้าม hardcode host (กฎ A5)
 */
function buildApiRoot(): string {
  const base =
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ??
    "http://localhost:8000";
  const ver = process.env.NEXT_PUBLIC_API_VERSION ?? "v1";
  return `${base}/api/${ver}`;
}

/**
 * path refresh รอ contract จริงจาก backend — override ผ่าน env เมื่อ path เปลี่ยน
 */
function refreshPath(): string {
  const p = process.env.NEXT_PUBLIC_AUTH_REFRESH_PATH ?? "/auth/refresh";
  return p.startsWith("/") ? p : `/${p}`;
}

function normalizeAxiosError(err: AxiosError<ApiErrorBody>): AppError {
  const status = err.response?.status ?? 500;
  const raw = err.response?.data;
  const body: ApiErrorBody =
    raw && typeof raw === "object" && typeof raw.error === "string"
      ? raw
      : {
          error: "NETWORK_ERROR",
          code: status,
          detail:
            typeof raw === "object" && raw !== null && "detail" in raw
              ? String((raw as ApiErrorBody).detail)
              : err.message,
        };
  const message =
    typeof body.detail === "string" && body.detail.length > 0
      ? body.detail
      : err.message;
  return new AppError(message, body.code ?? status, body);
}

function extractTokens(payload: unknown): {
  access: string;
  refresh?: string | null;
} | null {
  if (!payload || typeof payload !== "object") return null;
  const root = payload as Record<string, unknown>;
  const inner = (typeof root.data === "object" && root.data !== null
    ? root.data
    : root) as Record<string, unknown>;

  const accessRaw =
    inner.access_token ?? inner.accessToken ?? inner.access;
  if (typeof accessRaw !== "string") return null;

  const refreshRaw = inner.refresh_token ?? inner.refreshToken ?? inner.refresh;

  return {
    access: accessRaw,
    refresh: typeof refreshRaw === "string" ? refreshRaw : null,
  };
}

/** axios ดิบสำหรับ refresh — ห้ามผูก interceptor แบบวนลูป */
const rawClient: AxiosInstance = axios.create({
  baseURL: buildApiRoot(),
  timeout: Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS ?? 15_000),
});

let refreshQueue: Promise<void> | null = null;

async function refreshTokensOnce(): Promise<void> {
  const rt = useAuthStore.getState().refreshToken;
  if (!rt) throw new Error("MISSING_REFRESH_TOKEN");

  const { data } = await rawClient.post(refreshPath(), {
    refresh_token: rt,
  });

  const parsed = extractTokens(data);
  if (!parsed) throw new Error("INVALID_REFRESH_RESPONSE");

  useAuthStore.getState().setTokens(parsed.access, parsed.refresh ?? rt);
}

export const api: AxiosInstance = axios.create({
  baseURL: buildApiRoot(),
  timeout: Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS ?? 15_000),
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError<ApiErrorBody>) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };
    const status = error.response?.status;

    if (
      original &&
      !original._retry &&
      status === 401 &&
      useAuthStore.getState().refreshToken
    ) {
      original._retry = true;

      try {
        if (!refreshQueue) {
          refreshQueue = refreshTokensOnce().finally(() => {
            refreshQueue = null;
          });
        }
        await refreshQueue;
        const nextToken = useAuthStore.getState().accessToken;
        if (nextToken && original.headers) {
          original.headers.Authorization = `Bearer ${nextToken}`;
        }
        return api(original);
      } catch {
        useAuthStore.getState().logout();
      }
    }

    return Promise.reject(
      axios.isAxiosError(error) ? normalizeAxiosError(error) : error,
    );
  },
);
