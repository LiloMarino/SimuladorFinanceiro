import { useEffect, useState } from "react";
import type { PropsWithChildren } from "react";
import { SimulationContext } from "./SimulationContext";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { SimulationInfo } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";

const DEFAULT_SIMULATION: SimulationInfo = {
  active: false,
};

export function SimulationProvider({ children }: PropsWithChildren) {
  const [simulation, setSimulation] = useState<SimulationInfo>(DEFAULT_SIMULATION);
  const { data, loading } = useQueryApi<SimulationInfo>("/api/simulation/status");

  // 🔹 Sincroniza backend → frontend
  useEffect(() => {
    if (data && data.active && data.simulation) {
      const { start_date, end_date } = data.simulation;
      setSimulation({
        active: data.active,
        simulation: {
          start_date: start_date,
          end_date: end_date,
        },
      });
    }
  }, [data]);

  useRealtime(
    "simulation_created",
    (payload) => {
      setSimulation(payload.active ? payload : DEFAULT_SIMULATION);
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
