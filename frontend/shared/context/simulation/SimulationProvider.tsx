import { useEffect, type PropsWithChildren } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { SimulationContext } from "./SimulationContext";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNavigate } from "react-router-dom";
import { queryKeys } from "@/shared/lib/queryKeys";
import { useSimulationStatus } from "@/shared/hooks/queries/useSimulationStatus";
import { CreditNotifications } from "@/shared/notifications/credit-notifications";
import { StrategyNotifications } from "@/shared/notifications/strategy-notifications";
import { LifeNotifications } from "@/shared/notifications/life-notifications";
import { PlayerActivityReporter } from "./PlayerActivityReporter";
import { useRealtimeContext } from "@/shared/hooks/useRealtimeContext";
import { revalidateSimulation } from "@/shared/lib/simulation-cache";

export function SimulationProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { connected } = useRealtimeContext();

  useEffect(() => {
    if (connected) void revalidateSimulation(queryClient);
  }, [connected, queryClient]);

  useRealtime("speed_update", ({ speed }) => {
    if (speed <= 0) void revalidateSimulation(queryClient);
  });

  const { data: simulation, isLoading: loading, isError: failed, refetch } = useSimulationStatus();

  useRealtime(
    "simulation_started",
    (payload) => {
      if (payload?.active) {
        queryClient.setQueryData(queryKeys.simulationStatus(), payload);
        void revalidateSimulation(queryClient);
        // A partida começou com as regras do lobby, e o servidor já as zerou para a próxima
        void queryClient.invalidateQueries({ queryKey: queryKeys.simulationSettings() });
        // Os bots deixam a sala ao iniciar, sem evento de saída
        void queryClient.invalidateQueries({ queryKey: queryKeys.simulationPlayers() });
      }
    },
    true,
  );

  useRealtime(
    "simulation_ended",
    (payload) => {
      if (payload.reason === "error") {
        toast.error("A partida parou por um erro no servidor", {
          description: "O que foi jogado até o último pregão está salvo.",
        });
      }
      // A rota muda antes do status: com a partida inativa, o guard tira de /statistics
      // quem ainda estiver lá. O backend já liberou a simulação, então o refetch a vê inativa.
      // O relatório em cache parou num pregão do meio: o fechamento busca o da partida inteira.
      void queryClient.invalidateQueries({ queryKey: queryKeys.statistics() });
      void navigate(`/match-result/${payload.simulation_id}`);
      void queryClient.invalidateQueries({ queryKey: queryKeys.simulationStatus() });
    },
    true,
  );

  // O backtest não é partida, mas o guard decide a rota do host pelo status: ele muda com o início e o fim
  useRealtime("backtest_started", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.simulationStatus() });
  });
  useRealtime("backtest_ended", () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.simulationStatus() });
    void queryClient.invalidateQueries({ queryKey: queryKeys.simulationList() });
  });

  return (
    <SimulationContext.Provider
      value={{
        simulation: simulation ?? null,
        simulationActive: simulation?.active ?? false,
        loading,
        failed,
        retry: () => void refetch(),
      }}
    >
      {/* Avisos e renovação da vida financeira do viver de renda */}
      <LifeNotifications />
      {/* Avisos de parcela, nota e quitação do crédito */}
      <CreditNotifications />
      <StrategyNotifications />
      {/* Atividade desta aba na sala */}
      <PlayerActivityReporter />
      {children}
    </SimulationContext.Provider>
  );
}
