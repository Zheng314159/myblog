// src/store/useLoadingStore.ts
import { create } from "zustand";

export const useLoadingStore = create<{
  loading: boolean;
  tip: string;
  setLoading: (loading: boolean, tip?: string) => void;
}>((set) => ({
  loading: false,
  tip: "加载中...",
  setLoading: (loading, tip = "加载中...") => set({ loading, tip }),
}));
