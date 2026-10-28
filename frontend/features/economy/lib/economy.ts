import { subMonths } from "date-fns";
import {
  displayMoney,
  displayPercent,
  displayPercentagePoints,
  displayShortMonthYear,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";

type EconomyPoint = EconomyPanel["points"][number];
type CopomChange = EconomyPanel["copom_changes"][number];

export type EconomyRange = "all" | "year";

export type EconomyRow = {
  time: number;
  selic: number;
  ipca: number;
  realRate: number;
  target: number;
  /** A faixa da meta: de meta − tolerância até meta + tolerância */
  band: [number, number];
  /** Mudança da SELIC decidida nesse dia, quando houve */
  copom: CopomChange | undefined;
};

/** Os pontos do painel em linhas do gráfico, com a mudança do Copom do dia ligada à linha dele. */
export function economyRows(panel: EconomyPanel, range: EconomyRange = "all"): EconomyRow[] {
  const changeByDate = new Map(panel.copom_changes.map((change) => [change.date, change]));
  const last = panel.points.at(-1);
  const since = range === "year" && last ? subMonths(parseLocalDate(last.date), 12).getTime() : -Infinity;

  return panel.points
    .map((point: EconomyPoint) => ({
      time: parseLocalDate(point.date).getTime(),
      selic: Number(point.selic),
      ipca: Number(point.ipca),
      realRate: Number(point.real_rate),
      target: Number(point.target),
      band: [Number(point.target) - Number(point.tolerance), Number(point.target) + Number(point.tolerance)] as [
        number,
        number,
      ],
      copom: changeByDate.get(point.date),
    }))
    .filter((row) => row.time >= since);
}

/** "Copom subiu a SELIC em 0,50 p.p., para 14,75%" */
export function copomLabel(change: CopomChange): string {
  const rose = Number(change.change) > 0;
  const size = displayPercentagePoints(Math.abs(Number(change.change))).replace("+", "");
  return `Copom ${rose ? "subiu" : "baixou"} a SELIC em ${size}, para ${displayPercent(change.selic, 2)}`;
}

/** A última mudança da SELIC ("▼ 0,50 p.p. em mar/25"), ou o aviso de que ela ainda não mudou. */
export function lastCopomNote(changes: CopomChange[]): string {
  const last = changes.at(-1);
  if (!last) return "Sem mudança do Copom ainda";
  const arrow = Number(last.change) > 0 ? "▲" : "▼";
  const size = displayPercentagePoints(Math.abs(Number(last.change))).replace("+", "");
  return `${arrow} ${size} em ${displayShortMonthYear(last.date)}`;
}

/** A inflação de 12 meses contra a meta do ano. */
export function targetNote(point: EconomyPoint): string {
  return `meta de ${displayPercent(point.target, 2)}`;
}

/** O que R$ 100 parados na SELIC viram em um ano. */
export function selicExample(point: EconomyPoint): string {
  return `O juro básico: R$ 100 parados nela viram ${displayMoney(100 * (1 + Number(point.selic)))} em um ano.`;
}

/** O que custava R$ 100 há um ano. */
export function ipcaExample(point: EconomyPoint): string {
  return `A inflação: o que custava R$ 100 há um ano custa ${displayMoney(100 * (1 + Number(point.ipca)))}.`;
}

/** Juro real negativo é dinheiro perdendo da inflação. */
export function realRateTone(point: EconomyPoint): "destructive" | "default" {
  return Number(point.real_rate) < 0 ? "destructive" : "default";
}
