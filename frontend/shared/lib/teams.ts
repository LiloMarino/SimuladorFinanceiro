import type { TeamNaming } from "@/types";

/**
 * Equipes do modo em equipes: o servidor guarda e devolve o índice (1 a 10) e o front
 * traduz para o nome e a cor (`--team-N`). O tamanho da lista é o teto de equipes.
 */
export const TEAMS = [
  { number: 1, name: "Índigo" },
  { number: 2, name: "Carmim" },
  { number: 3, name: "Floresta" },
  { number: 4, name: "Ouro" },
  { number: 5, name: "Petróleo" },
  { number: 6, name: "Ameixa" },
  { number: 7, name: "Grafite" },
  { number: 8, name: "Oliva" },
  { number: 9, name: "Ferrugem" },
  { number: 10, name: "Marinho" },
] as const;

export const MAX_TEAMS = TEAMS.length;

/** Nome curto: a cor ("Índigo") ou o número ("Equipe 1"), conforme a regra da partida. */
export function teamShortName(team: number, naming: TeamNaming) {
  return naming === "NUMBER" ? `Equipe ${team}` : (TEAMS[team - 1]?.name ?? `Equipe ${team}`);
}

/** Nome completo: "Equipe Índigo" ou "Equipe 1". */
export function teamName(team: number, naming: TeamNaming) {
  return naming === "NUMBER" ? `Equipe ${team}` : `Equipe ${TEAMS[team - 1]?.name ?? team}`;
}

/** Cor da equipe como valor CSS. */
export function teamColor(team: number) {
  return `var(--team-${team})`;
}
