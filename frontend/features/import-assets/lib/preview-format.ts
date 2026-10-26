import {
  displayDate,
  displayMonthSlashYear,
  displayNumber,
  displaySignedPercent,
  displayPercent,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { FuturePreview } from "@/types";
import { withMinus } from "./future-readings";

/** Pontos do Ibovespa em milhares: 142300 → "142 mil". */
const displayThousands = (value: number) =>
  value >= 1000 ? `${Math.round(value / 1000)} mil` : displayNumber(value, 0);

const displayRate = (value: number, digits: number) =>
  new Intl.NumberFormat("pt-BR", { maximumFractionDigits: digits }).format(value);

export type PreviewNumber = { value: string; detail: string; tone: "up" | "down" | "neutral" };

export function ibovEndNumber(change: FuturePreview["ibov_change"]): PreviewNumber {
  return {
    value: withMinus(displaySignedPercent(change.change, 0)),
    detail: `em ${displayDate(parseLocalDate(change.on))}: de ${displayThousands(change.start)} para ${displayThousands(change.end)} pontos`,
    tone: change.change < 0 ? "down" : "up",
  };
}

export function maxDrawdownNumber(drawdown: FuturePreview["max_drawdown"]): PreviewNumber {
  if (!drawdown) return { value: "—", detail: "o Ibovespa não cai no período", tone: "neutral" };
  return {
    value: withMinus(displayPercent(drawdown.value, 0)),
    detail: `do pico de ${displayMonthSlashYear(drawdown.peak)} ao fundo de ${displayMonthSlashYear(drawdown.trough)}`,
    tone: "down",
  };
}

export function selicPeakNumber(peak: FuturePreview["selic_peak"]): PreviewNumber {
  if (!peak) return { value: "—", detail: "sem dado de SELIC", tone: "neutral" };
  return {
    value: `${displayNumber(peak.value, 1)}%`,
    detail: `ao ano, em ${displayMonthSlashYear(peak.on)} · hoje ${displayRate(peak.today, 2)}%`,
    tone: "neutral",
  };
}

export function ipcaPeakNumber(peak: FuturePreview["ipca_peak"]): PreviewNumber {
  if (!peak) return { value: "—", detail: "sem dado de IPCA", tone: "neutral" };
  return {
    value: `${displayNumber(peak.value, 1)}%`,
    detail: `IPCA de 12 meses, em ${peak.on.slice(0, 4)} · hoje ${displayRate(peak.today, 2)}%`,
    tone: "neutral",
  };
}
