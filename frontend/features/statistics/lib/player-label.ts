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

/**
 * Nome da série: "Nick", ou "Nick · A" quando há várias simulações na tela.
 * Entre simulações, quem está vendo aparece como "Você · A", sem o nickname.
 */
export function playerLabel(player: PlayerRef, simulationIds: number[], currentPlayerName?: string) {
  if (simulationIds.length <= 1) return player.player_nickname;
  const letter = simulationLetter(simulationIds, player.simulation_id);
  return player.player_nickname === currentPlayerName ? `Você · ${letter}` : `${player.player_nickname} · ${letter}`;
}

/** Nome em legenda e rótulo de linha: quem está vendo ganha "(você)" quando o nome ainda não diz isso. */
export function youLabel(label: string, isYou: boolean) {
  return isYou && !label.startsWith("Você") ? `${label} (você)` : label;
}

/** Chave única do jogador entre simulações, para `key` e mapas. */
export function playerKey(player: PlayerRef) {
  return `${player.simulation_id}|${player.player_nickname}`;
}
