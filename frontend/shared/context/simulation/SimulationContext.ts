import type { SimulationInfo } from "@/types";
import { createContext } from "react";

export interface SimulationContextValue {
  simulation: SimulationInfo | null;
  simulationActive: boolean;
  loading: boolean;
}

export const SimulationContext = createContext<SimulationContextValue | null>(null);
