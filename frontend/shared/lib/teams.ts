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

/**
 * Nome curto: o da gestora quando a equipe leva o nome dela (aquisição hostil em equipes);
 * senão a cor ("Índigo") ou o número ("Equipe 1"), conforme a regra da partida.
 */
export function teamShortName(team: number, naming: TeamNaming, name?: string | null) {
  if (name) return name;
  return naming === "NUMBER" ? `Equipe ${team}` : (TEAMS[team - 1]?.name ?? `Equipe ${team}`);
}

/** Nome completo: o da gestora quando a equipe leva o nome dela; senão "Equipe Índigo" ou "Equipe 1". */
export function teamName(team: number, naming: TeamNaming, name?: string | null) {
  if (name) return name;
  return naming === "NUMBER" ? `Equipe ${team}` : `Equipe ${TEAMS[team - 1]?.name ?? team}`;
}

/**
 * Nome da gestora de cada equipe, a partir das equipes que a mesma resposta já traz.
 * O jogador só carrega o índice da equipe; o nome vem daqui. Equipe sem gestora devolve `null`.
 */
export function teamNameLookup(teams: readonly { team: number; name: string | null }[]) {
  const names = new Map(teams.map((t) => [t.team, t.name]));
  return (team: number | null | undefined) => (team ? (names.get(team) ?? null) : null);
}

/** Cor da equipe como valor CSS. */
export function teamColor(team: number) {
  return `var(--team-${team})`;
}
