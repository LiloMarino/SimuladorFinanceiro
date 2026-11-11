import { playerInitials } from "./player-initials";

export const WHITE = "var(--primary-foreground)";
export const INK = "var(--foreground)";

/**
 * Paleta dos jogadores: `key` é o que o servidor guarda e devolve. `background` é o
 * token `--player-N` do index.css e `hex` é o mesmo valor, porque o partido guarda a cor
 * em hex. O texto da sigla é o que passa de 4,5:1 de contraste sobre a cor (branco ou tinta).
 */
export const PLAYER_COLORS = [
  { key: "chart-1", name: "Azul", background: "var(--player-1)", hex: "#2350D8", foreground: WHITE },
  { key: "chart-2", name: "Verde-água", background: "var(--player-2)", hex: "#209993", foreground: INK },
  { key: "chart-3", name: "Lima", background: "var(--player-3)", hex: "#7E9314", foreground: INK },
  { key: "chart-4", name: "Roxo", background: "var(--player-4)", hex: "#4F1599", foreground: WHITE },
  { key: "chart-5", name: "Salmão", background: "var(--player-5)", hex: "#CB7069", foreground: INK },
  { key: "chart-6", name: "Framboesa", background: "var(--player-6)", hex: "#C81C60", foreground: WHITE },
  { key: "chart-7", name: "Lavanda", background: "var(--player-7)", hex: "#9A6FFA", foreground: INK },
  { key: "chart-8", name: "Floresta", background: "var(--player-8)", hex: "#0B5E35", foreground: WHITE },
  { key: "chart-9", name: "Ameixa", background: "var(--player-9)", hex: "#682455", foreground: WHITE },
  { key: "chart-10", name: "Marrom", background: "var(--player-10)", hex: "#722604", foreground: WHITE },
  { key: "chart-11", name: "Rosa", background: "var(--player-11)", hex: "#E0489B", foreground: INK },
  { key: "chart-12", name: "Azul-céu", background: "var(--player-12)", hex: "#1E88E5", foreground: INK },
] as const;

/** A paleta no formato do seletor de cor: o valor escolhido é a `key` que o servidor guarda. */
export const PLAYER_SWATCHES = PLAYER_COLORS.map((color) => ({
  value: color.key,
  name: color.name,
  background: color.background,
  foreground: color.foreground,
}));

/** Quem já tem cada cor, no formato do seletor: a cor, a sigla do dono e o nome dele. */
export function playerOwners(players: { nickname: string; color: string }[]) {
  return players.map((p) => ({ color: p.color, label: playerInitials(p.nickname), owner: p.nickname }));
}

/** O tamanho da paleta é o teto de jogadores da sala. */
export const MAX_PLAYERS = PLAYER_COLORS.length;

const NEUTRAL = { background: "var(--muted)", foreground: "var(--muted-foreground)" };

/** Fundo e texto da sigla para a chave da paleta; chave desconhecida fica neutra. */
export function playerColorStyle(key: string | undefined) {
  const color = PLAYER_COLORS.find((c) => c.key === key);
  return color ? { background: color.background, foreground: color.foreground } : NEUTRAL;
}

export function playerColorName(key: string) {
  return PLAYER_COLORS.find((c) => c.key === key)?.name ?? key;
}
