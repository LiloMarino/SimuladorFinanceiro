import { displayNumber, parseLocalDate } from "@/shared/lib/utils/display";
import type { IndicatorPoint, StockCandle } from "@/types";
import type { AnnotationColors } from "../../lib/chart-annotations";
import { SCALE_DAYS, type Series, type TimeScale } from "./chart-config";

export const dayOf = (candle: StockCandle) => candle.price_date.slice(0, 10);

/** O primeiro dia do período escolhido, contado a partir do último candle do histórico. */
export function fromDay(history: StockCandle[], scale: TimeScale) {
  const last = history[history.length - 1];
  const days = SCALE_DAYS[scale];
  if (!last || days === null) return null;
  const from = new Date(last.price_date);
  from.setDate(from.getDate() - days);
  return from.toISOString().slice(0, 10);
}

/** As cores do tema que as anotações do gráfico usam. */
export function readAnnotationColors(): AnnotationColors {
  const styles = getComputedStyle(document.documentElement);
  const color = (token: string) => styles.getPropertyValue(token).trim();
  return {
    up: color("--candle-up"),
    down: color("--candle-down"),
    neutral: color("--faint-foreground"),
    band: color("--chart-1-canvas"),
  };
}

export function valueOn(points: IndicatorPoint[] | null | undefined, day: string | null) {
  if (!points?.length) return null;
  if (day === null) return points.at(-1)?.value ?? null;
  return points.find((point) => point.date === day)?.value ?? null;
}

/** O quadro fica à direita da mira e passa para a esquerda perto da borda. */
export function popLeft({ x, width }: { x: number; width: number }, popWidth: number) {
  return x + 16 + popWidth > width ? x - 16 - popWidth : x + 16;
}

/** O valor do dia, ou quando o indicador aparece se o histórico ainda é curto. */
export function formatOrMissing(
  value: number | null,
  needed: number,
  sessions: number,
  format: (value: number) => string,
) {
  if (value !== null) return format(value);
  if (sessions < needed) return `aparece com ${needed} pregões · faltam ${needed - sessions}`;
  return "—";
}

export function bandsValue(series: Series, day: string | null, period: number, sessions: number) {
  const lower = valueOn(series.bollinger?.lower, day);
  const upper = valueOn(series.bollinger?.upper, day);
  if (lower === null || upper === null) return formatOrMissing(null, period, sessions, String);
  return `${displayNumber(lower)} a ${displayNumber(upper)}`;
}

export const displayOrDash = (value: number | null, format: (value: number) => string) =>
  value === null ? "—" : format(value);

/** "2023-02-15" → "qua 15 fev 23", o dia que a mira aponta. */
export function displayCrosshairDay(isoDate: string) {
  const parts = new Intl.DateTimeFormat("pt-BR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    year: "2-digit",
  }).formatToParts(parseLocalDate(isoDate));
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value.replace(".", "") ?? "";
  return `${part("weekday")} ${part("day")} ${part("month")} ${part("year")}`;
}
