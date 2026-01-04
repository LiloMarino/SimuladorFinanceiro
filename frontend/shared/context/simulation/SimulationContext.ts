import type { SimulationInfo } from "@/types";
import { createContext } from "react";

export interface SimulationContextValue {
  simulation: SimulationInfo;
}

export const SimulationContext = createContext<SimulationContextValue | null>(null);
