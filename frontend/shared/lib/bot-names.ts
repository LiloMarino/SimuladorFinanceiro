import type { StrategyInfo } from "@/types";
import { NAME_MAX_LENGTH } from "./name-limit";

const sameName = (a: string, b: string) => a.trim().toLowerCase() === b.trim().toLowerCase();

/** O nome já está na sala (sem distinguir maiúsculas). */
export function nameTaken(name: string, taken: string[]) {
  return taken.some((t) => sameName(t, name));
}

/** "<estratégia> #N", com o nome da estratégia cortado para o conjunto caber no limite de nome. */
function numberedName(strategy: StrategyInfo, number: number) {
  const suffix = ` #${number}`;
  return `${strategy.name.slice(0, NAME_MAX_LENGTH - suffix.length).trimEnd()}${suffix}`;
}

/**
 * Sorteia o nome do bot entre os da estratégia que a sala ainda não tem. Quando a lista
 * acaba, vira "<estratégia> #2", "#3"…, o menor número livre.
 */
export function drawBotName(strategy: StrategyInfo, taken: string[], random: () => number = Math.random) {
  const free = strategy.bot_names.filter((name) => !nameTaken(name, taken));
  const drawn = free[Math.floor(random() * free.length)];
  if (drawn !== undefined) return drawn;

  let number = 2;
  while (nameTaken(numberedName(strategy, number), taken)) number++;
  return numberedName(strategy, number);
}

/** O nome veio do sorteio da estratégia (da lista ou "<estratégia> #N"), e não foi digitado. */
export function isDrawnName(name: string, strategy: StrategyInfo) {
  return (
    strategy.bot_names.some((n) => sameName(n, name)) ||
    numberedName(strategy, Number(/ #(\d+)$/.exec(name)?.[1])) === name
  );
}
