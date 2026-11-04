import { PLAYER_COLORS } from "./player-colors";

const WHITE = "var(--primary-foreground)";

/** As cores que a fundadora escolhe para o partido: as mesmas dos jogadores. */
export const PARTY_COLORS = PLAYER_COLORS.map((color) => color.hex);

/** Os partidos do computador não escolhem cor: cada um tem a sua, fixa e fora da paleta dos jogadores. */
const COMPUTER_COLORS: Record<string, string> = {
  UPR: "#6B6B6B",
  ACI: "#0F7C9C",
  MNV: "#7E6B17",
};

/** A cor do partido em toda tela: a escolhida pela fundadora ou, no partido do computador, a da paleta fixa. */
export function partyColor(party: { abbr: string; color: string | null }): string {
  return party.color ?? COMPUTER_COLORS[party.abbr] ?? "#7D879B";
}

/** O texto da sigla sobre a cor do partido: o mesmo da cor de jogador de igual hex; fora da paleta, branco. */
export function partyForeground(color: string): string {
  return PLAYER_COLORS.find((c) => c.hex === color.toUpperCase())?.foreground ?? WHITE;
}

/** A cor que o partido novo traz marcada: a do jogador que funda, se nenhum partido a usa; senão a 1ª livre. */
export function defaultPartyColor(founderColor: string | undefined, takenColors: string[]): string {
  const taken = new Set(takenColors.map((color) => color.toUpperCase()));
  const own = PLAYER_COLORS.find((c) => c.key === founderColor)?.hex;
  if (own && !taken.has(own)) return own;
  return PARTY_COLORS.find((color) => !taken.has(color)) ?? PLAYER_COLORS[0].hex;
}
