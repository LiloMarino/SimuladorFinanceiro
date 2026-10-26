import { teamName } from "@/shared/lib/teams";
import type { RoomPlayer, TeamNaming } from "@/types";

export type TeamsCheck = {
  /** Quem ainda não escolheu equipe */
  missing: RoomPlayer[];
  /** Quantos jogadores há em cada equipe formada, da menor para a maior */
  sizes: number[];
  /** Todos na mesma equipe: a partida precisa de pelo menos duas */
  single: boolean;
  /** Equipes formadas com tamanhos diferentes: vale, a média resolve */
  uneven: boolean;
  /** Pode iniciar: todo mundo numa equipe e pelo menos duas equipes */
  ready: boolean;
  /** Nome da equipe única, quando todos estão nela */
  singleName: string | null;
};

/** Situação das equipes na sala; quem jogou a partida salva (`saved`) conta com a equipe guardada. */
export function checkTeams(players: RoomPlayer[], saved: RoomPlayer[], naming: TeamNaming): TeamsCheck {
  const missing = players.filter((p) => !p.team);
  const members = new Map<number, number>();
  for (const player of [...players, ...saved.filter((s) => !players.some((p) => p.nickname === s.nickname))]) {
    if (player.team) members.set(player.team, (members.get(player.team) ?? 0) + 1);
  }
  const sizes = [...members.values()].sort((a, b) => a - b);
  const single = missing.length === 0 && members.size === 1;
  const [onlyTeam] = members.keys();
  return {
    missing,
    sizes,
    single,
    uneven: missing.length === 0 && sizes.length >= 2 && sizes[0] !== sizes[sizes.length - 1],
    ready: missing.length === 0 && members.size >= 2,
    singleName: single && onlyTeam !== undefined ? teamName(onlyTeam, naming) : null,
  };
}
