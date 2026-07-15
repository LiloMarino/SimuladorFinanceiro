import type { PropsWithChildren } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { SimulationContext } from "./SimulationContext";
import type { SimulationInfo } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";

export function SimulationProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: simulation, isLoading: loading } = useApiQuery({
    queryKey: queryKeys.simulationStatus(),
    queryFn: ({ signal }) => apiFetch<SimulationInfo>("/api/simulation/status", { signal }),
    staleTime: 1 * 60 * 1000, // 1min (simulação muda mais rápido)
    gcTime: 5 * 60 * 1000, // 5min cache
  });

  useRealtime(
    "simulation_started",
    (payload) => {
      if (payload?.active) {
        queryClient.setQueryData(queryKeys.simulationStatus(), payload);
      }
    },
    true,
  );

  useRealtime(
    "simulation_ended",
    (payload) => {
      queryClient.setQueryData(queryKeys.simulationStatus(), { active: false });

      const reason =
        payload.reason === "stopped_by_host"
          ? "A simulação foi encerrada pelo host."
          : "A simulação foi concluída com sucesso!";

      toast.info(reason);

      // Redireciona para o lobby
      navigate("/lobby");
    },
    true,
  );

  return (
    <SimulationContext.Provider
      value={{
        simulation: simulation ?? null,
        simulationActive: simulation?.active ?? false,
        loading,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
}
