import { useCallback, useState } from "react";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { useNavigate } from "react-router-dom";
import type { SimulationInfo } from "@/types";
import { LobbyPlayersList } from "../components/lobby-player-list";
import { LobbySimulationForm } from "../components/lobby-simulation-form";

export function LobbyPage() {
  const navigate = useNavigate();

  useRealtime("simulation_created", (simulation) => {
    navigate(`/simulation/${simulation.id}`);
  });

  const { mutate: createSimulation, loading } = useMutationApi<
    SimulationInfo,
    { start_date: string; end_date: string }
  >("/api/simulations");

  const handleStart = useCallback(
    (startDate: string, endDate: string) => {
      createSimulation({
        start_date: startDate,
        end_date: endDate,
      });
    },
    [createSimulation]
  );

  return (
    <section className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow p-6 max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        <LobbyPlayersList maxPlayers={8} />

        <LobbySimulationForm onStart={handleStart} loading={loading} />
      </div>
    </section>
  );
}
