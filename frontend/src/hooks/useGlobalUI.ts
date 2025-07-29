import { useContext } from "react";
import { GlobalUIContext } from "@/components/Global/GlobalUIProvider";
import type { GlobalUIContextType } from "@/utils/types";

export const useGlobalUI = (): GlobalUIContextType => {
  const context = useContext(GlobalUIContext);
  if (!context) {
    throw new Error("useGlobalUI must be used within GlobalUIProvider");
  }
  return context;
};
