import { useEffect, useState } from "react";
import type { PropsWithChildren } from "react";
import { SimulationContext } from "./SimulationContext";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { SimulationInfo } from "@/types";

const DEFAULT_SIMULATION: SimulationInfo = {
  active: false,
};

export function SimulationProvider({ children }: PropsWithChildren) {
  const [simulation, setSimulation] = useState<SimulationInfo>(DEFAULT_SIMULATION);
  const { data } = useQueryApi<SimulationInfo>("/api/simulation/status");

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

  return (
    <SimulationContext.Provider
      value={{
        simulation,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
}
