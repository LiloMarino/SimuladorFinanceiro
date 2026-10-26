import { addMonths, differenceInCalendarDays, differenceInCalendarMonths } from "date-fns";
import { parseLocalDate } from "@/shared/lib/utils/display";
import type { ElectionPhase } from "@/types";

/** Os diálogos da página da eleição que um atalho de fora (o aviso da campanha) abre ao chegar. */
export type ElectionShortcut = "found" | "join" | "contribution";

/** Quantas vezes a raiz do gasto mensal divide em pontos de intenção (a cada 100 eleitores). */
const VOTE_DIVISOR = 64;

export const PROMISE_BANDS = [
  { value: 1, title: "Impostos bem baixos", description: "Corte geral de imposto." },
  { value: 2, title: "Impostos baixos", description: "Isenção para um setor." },
  { value: 3, title: "Meio-termo", description: "Mexe pouco nos dois." },
  { value: 4, title: "Gasto alto", description: "Taxa um setor; o gasto público fica entre 4 e 5." },
  { value: 5, title: "Gasto bem alto", description: "Imposto geral novo." },
] as const;

export const PROMISE_ENDS = { low: "Impostos baixos", high: "Gasto alto" } as const;

export function promiseBand(promise: number) {
  return PROMISE_BANDS[Math.min(Math.max(promise, 1), 5) - 1] ?? PROMISE_BANDS[0];
}

/** Posição da faixa na régua, em % da largura: cada uma das 5 faixas ocupa um quinto e o marcador fica no meio dela. */
export function rulerPosition(promise: number) {
  return ((promise - 0.5) / 5) * 100;
}

/** Pontos de intenção que uma verba mensal rende por mês: raiz do gasto dividida por 64. */
export function monthlyYield(monthlySpend: number) {
  return Math.sqrt(Math.max(monthlySpend, 0)) / VOTE_DIVISOR;
}

/** A curva "quanto a verba rende": cada gasto mensal de 0 até o teto e os pontos que ele compra. */
export function yieldCurve(maxSpend: number, steps = 20) {
  return Array.from({ length: steps + 1 }, (_, index) => {
    const spend = (maxSpend * index) / steps;
    return { spend, points: monthlyYield(spend) };
  });
}

/** O gasto mensal que a curva mostra: o dobro da verba atual, com piso para o gráfico não nascer vazio. */
export function curveCeiling(budget: number) {
  return Math.max(budget * 2, 10_000);
}

/** "6 meses e 23 dias": o tempo de `from` até `to`, em meses cheios e dias. */
export function countdownLabel(from: string, to: string) {
  const start = parseLocalDate(from);
  const end = parseLocalDate(to);
  if (end <= start) return "hoje";
  let months = differenceInCalendarMonths(end, start);
  if (addMonths(start, months) > end) months -= 1;
  const days = differenceInCalendarDays(end, addMonths(start, months));
  const parts = [];
  if (months > 0) parts.push(`${months} ${months === 1 ? "mês" : "meses"}`);
  if (days > 0) parts.push(`${days} ${days === 1 ? "dia" : "dias"}`);
  return parts.join(" e ");
}

/** Quantos dias 1º ainda cobram a verba até o 1º turno: o primeiro dia de cada mês depois de hoje. */
export function remainingCollections(today: string, firstRound: string) {
  const start = parseLocalDate(today);
  const end = parseLocalDate(firstRound);
  let count = 0;
  for (let day = new Date(start.getFullYear(), start.getMonth() + 1, 1); day <= end; day = addMonths(day, 1)) {
    count += 1;
  }
  return count;
}

/** O selo da fase no topo da página. */
export function phaseLabel(phase: ElectionPhase) {
  switch (phase) {
    case "BEFORE_CAMPAIGN":
      return "Candidaturas ainda fechadas";
    case "CAMPAIGN":
      return "Campanha aberta";
    case "BETWEEN_ROUNDS":
      return "Entre os turnos";
    case "AWAITING_TERM":
      return "Aguardando a posse";
    case "TERM":
      return "Mandato em curso";
  }
}
