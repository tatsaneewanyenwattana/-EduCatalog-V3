import type { User } from "@/types/user";
import { create } from "zustand";

/**
 * เก็บ session เฉพาะฝั่ง client (กฎ F2) — ไม่เก็บใน React state ตามกฎ F3
 */
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setTokens: (access: string | null, refresh: string | null) => void;
  logout: () => void;
  updateUser: (partial: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  setUser: (user) => set({ user }),
  setTokens: (access, refresh) =>
    set({
      accessToken: access,
      refreshToken: refresh,
      isAuthenticated: access !== null,
    }),
  logout: () =>
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    }),
  updateUser: (partial) => {
    const current = get().user;
    if (!current) return;
    set({
      user: { ...current, ...partial },
    });
  },
}));
