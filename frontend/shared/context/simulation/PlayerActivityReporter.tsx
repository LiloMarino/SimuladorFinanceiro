import { useEffect, useSyncExternalStore } from "react";
import { useLocation } from "react-router-dom";
import { useRealtimeContext } from "@/shared/hooks/useRealtimeContext";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { activityForPath } from "@/shared/lib/player-activity";
import type { PlayerActivity, SimulationEvents } from "@/types";

function subscribeVisibility(onChange: () => void) {
  document.addEventListener("visibilitychange", onChange);
  return () => document.removeEventListener("visibilitychange", onChange);
}

/**
 * Avisa a sala o que esta aba está fazendo: a tela em que está, ou "away" com a aba escondida.
 * Com a partida em andamento a tela fica de fora (entregaria a jogada) e o aviso é nulo, "Online".
 * O aviso é desta aba: o servidor escolhe qual das abas do jogador aparece no selo.
 */
export function PlayerActivityReporter() {
  const { subscriber, connected } = useRealtimeContext<SimulationEvents>();
  const { simulationActive, loading } = useSimulation();
  const { pathname } = useLocation();
  const hidden = useSyncExternalStore(subscribeVisibility, () => document.hidden);

  const activity: PlayerActivity | null = hidden ? "away" : simulationActive ? null : activityForPath(pathname);

  // Sem o status da partida carregado ainda não se sabe se a tela pode ser dita
  const ready = connected && !loading;
  useEffect(() => {
    if (ready) subscriber.send("presence", { activity });
  }, [subscriber, ready, activity]);

  return null;
}
