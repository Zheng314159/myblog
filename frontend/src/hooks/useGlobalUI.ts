import { useContext } from "react";
import { GlobalUIContext } from "@/components/Global/GlobalUIProvider.tsx";
import type { GlobalUIContextType } from "@/utils/types.ts";

export const useGlobalUI = (): GlobalUIContextType => {
  const context = useContext(GlobalUIContext);
  if (!context) {
    throw new Error("useGlobalUI must be used within GlobalUIProvider");
  }
  return context;
};
