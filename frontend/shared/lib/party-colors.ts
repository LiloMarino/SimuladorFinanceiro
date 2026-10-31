/** As cores que a fundadora escolhe para o partido. */
export const PARTY_COLORS = [
  "#15803D",
  "#BE185D",
  "#2350D8",
  "#9A3412",
  "#7C3AED",
  "#0E7490",
  "#B45309",
  "#4D7C0F",
] as const;

/** Os partidos do computador não escolhem cor: cada um tem a sua, fixa. */
const COMPUTER_COLORS: Record<string, string> = {
  UPR: "#7D879B",
  ACI: "#0369A1",
  MNV: "#A16207",
};

/** A cor do partido em toda tela: a escolhida pela fundadora ou, no partido do computador, a da paleta fixa. */
export function partyColor(party: { abbr: string; color: string | null }): string {
  return party.color ?? COMPUTER_COLORS[party.abbr] ?? "#7D879B";
}
