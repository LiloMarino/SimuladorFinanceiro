import type { PropsWithChildren } from "react";
import { SimulationContext } from "./SimulationContext";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { SimulationInfo } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";

export function SimulationProvider({ children }: PropsWithChildren) {
  const { data: simulation, setData: setSimulation, loading } = useQueryApi<SimulationInfo>("/api/simulation/status");

  useRealtime(
    "simulation_started",
    (payload) => {
      if (payload?.active) {
        setSimulation(payload);
      }
    },
    true
  );

  return (
    <SimulationContext.Provider
      value={{
        simulation,
        loading,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
}
