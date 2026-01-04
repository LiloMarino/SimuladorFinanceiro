import { useRealtime } from "@/shared/hooks/useRealtime";
import { useNavigate } from "react-router-dom";
import { LobbyPlayersList } from "../components/lobby-player-list";
import { LobbySimulationForm } from "../components/lobby-simulation-form";

export function LobbyPage() {
  const navigate = useNavigate();

  useRealtime("simulation_created", (simulation) => {
    if (simulation.active) {
      navigate("/", { replace: true });
    }
  });

  return (
    <section className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow p-6 max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 w-full min-h-[50vh]">
        <LobbyPlayersList maxPlayers={8} />

        <LobbySimulationForm />
      </div>
    </section>
  );
}
