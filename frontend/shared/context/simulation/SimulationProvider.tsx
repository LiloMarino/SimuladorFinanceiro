import type { PropsWithChildren } from "react";
import { SimulationContext } from "./SimulationContext";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { SimulationInfo } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export function SimulationProvider({ children }: PropsWithChildren) {
  const { data: simulation, setData: setSimulation, loading } = useQueryApi<SimulationInfo>("/api/simulation/status");
  const navigate = useNavigate();

  useRealtime(
    "simulation_started",
    (payload) => {
      if (payload?.active) {
        setSimulation(payload);
      }
    },
    true,
  );

  useRealtime(
    "simulation_ended",
    (payload) => {
      setSimulation({ active: false });

      const reason =
        payload.reason === "stopped_by_host"
          ? "A simulação foi encerrada pelo host."
          : "A simulação foi concluída com sucesso!";

      toast.info(reason);

      // Redireciona para o lobby
      // TODO: melhorar isso com invalidateQuery quando tivermos #54
      navigate("/lobby");
    },
    true,
  );

  return (
    <SimulationContext.Provider
      value={{
        simulation,
        simulationActive: simulation?.active ?? false,
        loading,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
}
