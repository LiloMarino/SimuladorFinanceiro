import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNavigate } from "react-router-dom";
import { LobbyPlayersList } from "../components/lobby-player-list";
import { LobbySimulationForm } from "../components/lobby-simulation-form";
import type { SimulationSettings } from "@/types";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { LoadingPage } from "@/pages/loading";
import { ErrorPage } from "@/pages/error";

export function LobbyPage() {
  const navigate = useNavigate();
  const { data: settings, loading, error } = useQueryApi<SimulationSettings>("/api/simulation/settings");

  useRealtime("simulation_started", (simulation) => {
    if (simulation.active) {
      navigate("/", { replace: true });
    }
  });

  if (loading) {
    return <LoadingPage variant="fullscreen" />;
  } else if (!settings) {
    return (
      <ErrorPage
        code={String(error?.status) || "500"}
        title="Erro ao entrar no Lobby"
        message={String(error?.message)}
        actionHref="/login"
        actionLabel="Voltar ao Login"
      />
    );
  }

  return (
    <section className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow p-6 max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 w-full min-h-[50vh]">
        <LobbyPlayersList maxPlayers={8} />

        <LobbySimulationForm simulationData={settings?.simulation} isHost={settings?.is_host} />
      </div>
    </section>
  );
}
