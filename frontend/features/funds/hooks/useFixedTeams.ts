import { useSimulation } from "@/shared/hooks/useSimulation";

/** Na aquisição hostil em equipes os co-gestores são os do lobby até o fim da partida. */
export function useFixedTeams(): boolean {
  const { simulation } = useSimulation();
  const current = simulation?.active ? simulation.simulation : null;
  return current?.game_type === "FUND_TAKEOVER" && current.player_grouping === "TEAMS";
}
