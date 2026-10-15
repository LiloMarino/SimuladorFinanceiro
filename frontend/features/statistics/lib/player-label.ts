import type { PlayerRef } from "@/types";

// Cor de cada simulação na ordem da escolha: a mesma da letra no seletor
const SIMULATION_PALETTE = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"];

/** A letra da simulação pela ordem em que foi escolhida: a primeira é A. */
export function simulationLetter(simulationIds: number[], simulationId: number) {
  return String.fromCharCode(65 + simulationIds.indexOf(simulationId));
}

export function simulationColor(simulationIds: number[], simulationId: number) {
  return SIMULATION_PALETTE[simulationIds.indexOf(simulationId) % SIMULATION_PALETTE.length];
}

/** Nome da série: "Nick", ou "Nick · A" quando há várias simulações na tela. */
export function playerLabel(player: PlayerRef, simulationIds: number[]) {
  return simulationIds.length > 1
    ? `${player.player_nickname} · ${simulationLetter(simulationIds, player.simulation_id)}`
    : player.player_nickname;
}

/** Chave única do jogador entre simulações, para `key` e mapas. */
export function playerKey(player: PlayerRef) {
  return `${player.simulation_id}|${player.player_nickname}`;
}
