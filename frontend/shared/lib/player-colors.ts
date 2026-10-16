const WHITE = "var(--primary-foreground)";
const INK = "var(--foreground)";

/**
 * Paleta dos jogadores: `key` é o que o servidor guarda e devolve. O texto da sigla
 * é o que passa de 4,5:1 de contraste sobre a cor (branco ou tinta).
 */
export const PLAYER_COLORS = [
  { key: "chart-1", name: "Azul", foreground: WHITE },
  { key: "chart-2", name: "Verde-água", foreground: INK },
  { key: "chart-3", name: "Âmbar", foreground: INK },
  { key: "chart-4", name: "Roxo", foreground: WHITE },
  { key: "chart-5", name: "Laranja", foreground: INK },
  { key: "chart-6", name: "Rosa", foreground: WHITE },
  { key: "chart-7", name: "Ciano", foreground: INK },
  { key: "chart-8", name: "Lima", foreground: INK },
  { key: "chart-9", name: "Cinza", foreground: WHITE },
  { key: "chart-10", name: "Marrom", foreground: WHITE },
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
