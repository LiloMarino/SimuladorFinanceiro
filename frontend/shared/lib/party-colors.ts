import { INK, PLAYER_COLORS, WHITE } from "./player-colors";

/**
 * As 20 cores que a fundadora escolhe para o partido, no formato do seletor de cor: o valor
 * escolhido é o hex, que o servidor guarda. As primeiras são as dos jogadores, na mesma ordem;
 * as 8 últimas (vermelho, laranja, caramelo, verde, vinho, magenta, âmbar e musgo) são só de
 * partido: vermelho e âmbar ficam fora da paleta dos jogadores porque, nos gráficos de carteira,
 * significam perda e alerta. O âmbar é o amarelo da paleta: o mais claro que ainda se distingue
 * do laranja e do caramelo, com 2,5 para 1 de contraste contra o fundo (as demais passam de 3).
 * A paleta tem sempre mais cores que a sala tem vagas, então toda fundadora acha uma cor livre.
 * Preto, branco e cinzas ficam de fora: o sistema os reserva (destaque do mapa, selos, UPR e
 * partido sem cor).
 */
export const PARTY_PALETTE = [
  ...PLAYER_COLORS.map((color) => ({
    value: color.hex,
    name: color.name,
    background: color.hex,
    foreground: color.foreground,
  })),
  { value: "#D92D20", name: "Vermelho", background: "#D92D20", foreground: WHITE },
  { value: "#E8590C", name: "Laranja", background: "#E8590C", foreground: INK },
  { value: "#A85F00", name: "Caramelo", background: "#A85F00", foreground: WHITE },
  { value: "#1A9A44", name: "Verde", background: "#1A9A44", foreground: INK },
  { value: "#800020", name: "Vinho", background: "#800020", foreground: WHITE },
  { value: "#B5179E", name: "Magenta", background: "#B5179E", foreground: WHITE },
  { value: "#CC8A00", name: "Âmbar", background: "#CC8A00", foreground: INK },
  { value: "#517722", name: "Musgo", background: "#517722", foreground: WHITE },
];

/** Os partidos do computador não escolhem cor: cada um tem a sua, fixa e fora da paleta de escolha. */
export const COMPUTER_COLORS: Record<string, string> = {
  UPR: "#6B6B6B",
  ACI: "#0F7C9C",
  MNV: "#7E6B17",
};

/** O cinza do partido sem cor. */
export const NO_COLOR = "#7D879B";

/** A cor do partido em toda tela: a escolhida pela fundadora ou, no partido do computador, a da paleta fixa. */
export function partyColor(party: { abbr: string; color: string | null }): string {
  return party.color ?? COMPUTER_COLORS[party.abbr] ?? NO_COLOR;
}

/** O texto da sigla sobre a cor do partido: o da cor da paleta de igual hex; fora da paleta, branco. */
export function partyForeground(color: string): string {
  return PARTY_PALETTE.find((c) => c.value === color.toUpperCase())?.foreground ?? WHITE;
}

/** A cor que o partido novo traz marcada: a do jogador que funda, se nenhum partido a usa; senão a 1ª livre. */
export function defaultPartyColor(founderColor: string | undefined, takenColors: string[]): string {
  const taken = new Set(takenColors.map((color) => color.toUpperCase()));
  const own = PLAYER_COLORS.find((c) => c.key === founderColor)?.hex;
  if (own && !taken.has(own)) return own;
  return PARTY_PALETTE.find((c) => !taken.has(c.value))?.value ?? PLAYER_COLORS[0].hex;
}
