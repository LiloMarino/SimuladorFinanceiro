const WHITE = "var(--primary-foreground)";
const INK = "var(--foreground)";

/**
 * Paleta dos jogadores: `key` é o que o servidor guarda e devolve. O texto da sigla
 * é o que passa de 4,5:1 de contraste sobre a cor (branco ou tinta). `hex` é o valor
 * do token `--chart-N` no index.css, porque o partido guarda a cor em hex.
 */
export const PLAYER_COLORS = [
  { key: "chart-1", name: "Azul", hex: "#2350D8", foreground: WHITE },
  { key: "chart-2", name: "Verde-água", hex: "#209993", foreground: INK },
  { key: "chart-3", name: "Lima", hex: "#809614", foreground: INK },
  { key: "chart-4", name: "Roxo", hex: "#4F1599", foreground: WHITE },
  { key: "chart-5", name: "Salmão", hex: "#CC726B", foreground: INK },
  { key: "chart-6", name: "Framboesa", hex: "#C81C60", foreground: WHITE },
  { key: "chart-7", name: "Lavanda", hex: "#9E75FA", foreground: INK },
  { key: "chart-8", name: "Floresta", hex: "#0B5E35", foreground: WHITE },
  { key: "chart-9", name: "Ameixa", hex: "#682455", foreground: WHITE },
  { key: "chart-10", name: "Marrom", hex: "#722604", foreground: WHITE },
] as const;

/** O tamanho da paleta é o teto de jogadores da sala. */
export const MAX_PLAYERS = PLAYER_COLORS.length;

const NEUTRAL = { background: "var(--muted)", foreground: "var(--muted-foreground)" };

/** Fundo e texto da sigla para a chave da paleta; chave desconhecida fica neutra. */
export function playerColorStyle(key: string | undefined) {
  const color = PLAYER_COLORS.find((c) => c.key === key);
  return color ? { background: `var(--${color.key})`, foreground: color.foreground } : NEUTRAL;
}

export function playerColorName(key: string) {
  return PLAYER_COLORS.find((c) => c.key === key)?.name ?? key;
}
