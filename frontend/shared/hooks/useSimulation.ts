import { useContext } from "react";
import { SimulationContext } from "@/shared/context/simulation";

export function useSimulation() {
  const ctx = useContext(SimulationContext);
  if (!ctx) {
    throw new Error("useSimulation must be used within SimulationProvider");
  }
  return ctx;
}
