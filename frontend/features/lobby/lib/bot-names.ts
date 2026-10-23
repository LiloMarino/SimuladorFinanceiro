import type { StrategyInfo } from "@/types";

const sameName = (a: string, b: string) => a.trim().toLowerCase() === b.trim().toLowerCase();

/** O nome já está na sala (sem distinguir maiúsculas). */
export function nameTaken(name: string, taken: string[]) {
  return taken.some((t) => sameName(t, name));
}

/**
 * Sorteia o nome do bot entre os da estratégia que a sala ainda não tem. Quando a lista
 * acaba, vira "<estratégia> #2", "#3"…, o menor número livre.
 */
export function drawBotName(strategy: StrategyInfo, taken: string[], random: () => number = Math.random) {
  const free = strategy.bot_names.filter((name) => !nameTaken(name, taken));
  if (free.length > 0) return free[Math.floor(random() * free.length)];

  let number = 2;
  while (nameTaken(`${strategy.name} #${number}`, taken)) number++;
  return `${strategy.name} #${number}`;
}

/** O nome veio do sorteio da estratégia (da lista ou "<estratégia> #N"), e não foi digitado. */
export function isDrawnName(name: string, strategy: StrategyInfo) {
  return (
    strategy.bot_names.some((n) => sameName(n, name)) ||
    (name.startsWith(`${strategy.name} #`) && /^\d+$/.test(name.slice(strategy.name.length + 2)))
  );
}
