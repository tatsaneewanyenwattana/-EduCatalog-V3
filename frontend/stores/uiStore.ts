import { create } from "zustand";

export type ToastType = "success" | "error" | "warning";

export interface UiToast {
  id: string;
  type: ToastType;
  message: string;
}

/**
 * แยกจาก server state (React Query) เพราะเป็น client-only UI (กฎ F2/F3)
 */
interface UiState {
  sidebarOpen: boolean;
  toasts: UiToast[];
  toggleSidebar: () => void;
  addToast: (t: Omit<UiToast, "id">) => void;
  removeToast: (id: string) => void;
}

export const useUiStore = create<UiState>((set, get) => ({
  sidebarOpen: true,
  toasts: [],
  toggleSidebar: () => set({ sidebarOpen: !get().sidebarOpen }),
  addToast: (t) => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    set({ toasts: [...get().toasts, { ...t, id }] });
  },
  removeToast: (id) =>
    set({
      toasts: get().toasts.filter((x) => x.id !== id),
    }),
}));
