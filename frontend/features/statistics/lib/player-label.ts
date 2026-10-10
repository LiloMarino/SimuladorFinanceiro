import type { PlayerRef } from "@/types";

/** Nome da série: "Nick", ou "Nick#Simulação" quando há várias simulações na tela. */
export function playerLabel(player: PlayerRef, showSimulation: boolean) {
  return showSimulation ? `${player.player_nickname}#${player.simulation_name}` : player.player_nickname;
}
