import { playerColorStyle } from "@/shared/lib/player-colors";
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

/**
 * Cor de cada rótulo em gráficos e legendas: a do jogador na partida, a mesma do lobby.
 * Comparando simulações a cor é da partida (a mesma da letra A, B…), porque o que se
 * distingue ali é a partida e não o jogador.
 */
export function labelColors(players: PlayerRef[], simulationIds: number[], currentPlayerName?: string) {
  const comparing = simulationIds.length > 1;
  const colors = new Map(
    players.map((p) => [
      playerLabel(p, simulationIds, currentPlayerName),
      comparing ? simulationColor(simulationIds, p.simulation_id) : playerColorStyle(p.color).background,
    ]),
  );
  return (label: string) => colors.get(label) ?? "var(--foreground)";
}

/** Nome em legenda e rótulo de linha: quem está vendo ganha "(você)" quando o nome ainda não diz isso. */
export function youLabel(label: string, isYou: boolean) {
  return isYou && !label.startsWith("Você") ? `${label} (você)` : label;
}

/** Chave única do jogador entre simulações, para `key` e mapas. */
export function playerKey(player: PlayerRef) {
  return `${player.simulation_id}|${player.player_nickname}`;
}
