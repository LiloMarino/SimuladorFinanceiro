// Ordem fixa da paleta categórica; com até 8 jogadores, ninguém repete cor
const PALETTE = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
  "var(--chart-7)",
  "var(--chart-8)",
];

/**
 * A cor de cada rótulo de jogador pela posição dele na ordem alfabética: a mesma em
 * todas as abas do relatório, porque todas recebem os mesmos jogadores.
 */
export function playerColors(labels: string[]): (label: string) => string {
  const order = [...new Set(labels)].sort((a, b) => a.localeCompare(b));
  return (label) => PALETTE[order.indexOf(label) % PALETTE.length] ?? PALETTE[0];
}
