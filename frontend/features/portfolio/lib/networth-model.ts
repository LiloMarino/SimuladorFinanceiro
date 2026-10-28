import { niceScale } from "@/shared/lib/chart-scale";
import { goalAt } from "@/shared/lib/goal";
import { displayNumber, displayShortMonthYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { PortfolioHistoryPoint, SeriesPoint } from "@/types";

export type Period = "6M" | "1Y" | "ALL";

export const PERIODS: { value: Period; label: string; months: number | null }[] = [
  { value: "6M", label: "6M", months: 6 },
  { value: "1Y", label: "1A", months: 12 },
  { value: "ALL", label: "Tudo", months: null },
];

export type NetworthPoint = {
  date: string;
  networth: number;
  provided: number;
  debt: number;
  equity: number;
  fixed: number;
  cash: number;
  /** Meta vigente no dia; ausente fora da corrida */
  goal: number | undefined;
};

/** Os campos da API chegam em string decimal; o gráfico lê tudo como número. */
export function toNetworthPoints(history: PortfolioHistoryPoint[], goalSteps: SeriesPoint[] | undefined) {
  return history.map((p): NetworthPoint => ({
    date: p.snapshot_date,
    networth: Number(p.total_networth),
    provided: Number(p.total_provided),
    debt: Number(p.total_debt),
    equity: Number(p.total_equity),
    fixed: Number(p.total_fixed),
    cash: Number(p.total_cash),
    goal: goalAt(goalSteps ?? [], p.snapshot_date),
  }));
}

/** Data de `isoDate` recuada em `months` meses, com o dia limitado ao tamanho do mês de chegada. */
function monthsBefore(isoDate: string, months: number) {
  const date = parseLocalDate(isoDate);
  const target = new Date(date.getFullYear(), date.getMonth() - months, 1);
  const lastDay = new Date(target.getFullYear(), target.getMonth() + 1, 0).getDate();
  target.setDate(Math.min(date.getDate(), lastDay));
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${target.getFullYear()}-${pad(target.getMonth() + 1)}-${pad(target.getDate())}`;
}

/** O período cabe no histórico: a partida já é tão longa quanto ele. */
export function isPeriodAvailable(points: NetworthPoint[], period: Period) {
  const months = PERIODS.find((p) => p.value === period)?.months ?? null;
  const first = points[0];
  const last = points.at(-1);
  if (months === null) return true;
  if (!first || !last) return false;
  return first.date <= monthsBefore(last.date, months);
}

/** Os pontos que caem na janela do período, até o último dia. */
export function pointsInPeriod(points: NetworthPoint[], period: Period) {
  const months = PERIODS.find((p) => p.value === period)?.months ?? null;
  const last = points.at(-1);
  if (months === null || !last) return points;
  const cutoff = monthsBefore(last.date, months);
  return points.filter((p) => p.date >= cutoff);
}

/** Um trecho contínuo em que o patrimônio ficou do mesmo lado do aportado. */
export type Run = { x: number; provided: number; networth: number }[];

/**
 * Separa a série em trechos de ganho (patrimônio acima do aportado) e de perda (abaixo).
 * Quando as duas linhas se cruzam entre dois pontos, o trecho termina no ponto exato do cruzamento.
 */
export function splitGainLoss(points: Run): { gains: Run[]; losses: Run[] } {
  const runs: { kind: "gain" | "loss"; run: Run }[] = [];

  for (const [i, point] of points.entries()) {
    const kind = point.networth >= point.provided ? "gain" : "loss";
    const previous = points[i - 1];
    let open = runs.at(-1);

    if (previous && open && open.kind !== kind) {
      const before = previous.networth - previous.provided;
      const after = point.networth - point.provided;
      // Mudar de lado é cruzar a linha entre os dois pontos ou encostar nela em um deles
      const t = before / (before - after);
      const boundary =
        before * after < 0
          ? {
              x: previous.x + (point.x - previous.x) * t,
              provided: previous.provided + (point.provided - previous.provided) * t,
              networth: previous.networth + (point.networth - previous.networth) * t,
            }
          : after === 0
            ? point
            : previous;
      if (boundary !== previous) open.run.push(boundary);
      open = { kind, run: [boundary] };
      runs.push(open);
    }
    if (!open) {
      open = { kind, run: [] };
      runs.push(open);
    }
    if (open.run.at(-1) !== point) open.run.push(point);
  }

  const only = (kind: "gain" | "loss") => runs.filter((r) => r.kind === kind && r.run.length > 1).map((r) => r.run);
  return { gains: only("gain"), losses: only("loss") };
}

/** Escala do eixo Y: parte do menor valor (dívida ou patrimônio negativo) e cobre o maior, meta incluída. */
export function valueScale(values: number[]) {
  const low = Math.min(0, ...values);
  const high = Math.max(0, ...values);
  if (low === 0 && high === 0) return { ticks: [0, 1], floor: 0, ceiling: 1 };
  return niceScale(low, high);
}

export type AxisTick = { index: number; label: string; anchor: "start" | "middle" | "end" };

const MIN_TICK_GAP = 64;
const MONTH_STEPS = [1, 2, 3, 6, 12, 24, 60, 120];

const monthIndex = (isoDate: string) => {
  const d = parseLocalDate(isoDate);
  return d.getFullYear() * 12 + d.getMonth();
};

/**
 * Marcas do eixo X por posição: dd/MM em janela curta, senão o início de alguns meses
 * (o espaçamento em meses cresce até as marcas caberem em `width`).
 */
export function axisTicks(dates: string[], width: number): AxisTick[] {
  const first = dates[0];
  const last = dates.at(-1);
  if (!first || !last) return [];
  const perIndex = dates.length > 1 ? width / (dates.length - 1) : width;
  const anchorOf = (index: number): AxisTick["anchor"] =>
    index === 0 ? "start" : index === dates.length - 1 ? "end" : "middle";

  const spanDays = (parseLocalDate(last).getTime() - parseLocalDate(first).getTime()) / 86_400_000;
  if (spanDays <= 45) {
    const every = Math.max(1, Math.ceil(MIN_TICK_GAP / perIndex));
    return dates.flatMap((date, index) => {
      if (index % every !== 0) return [];
      const d = parseLocalDate(date);
      const label = `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}`;
      return [{ index, label, anchor: anchorOf(index) }];
    });
  }

  // O primeiro dia de cada mês presente na janela
  const monthStarts = dates.flatMap((date, index) => {
    const previous = dates[index - 1];
    return previous === undefined || monthIndex(previous) !== monthIndex(date) ? [{ index, date }] : [];
  });
  const picked = (step: number) => monthStarts.filter((m) => monthIndex(m.date) % step === 0);
  const fits = (ticks: { index: number }[]) =>
    ticks.every((tick, i) => i === 0 || (tick.index - (ticks[i - 1]?.index ?? 0)) * perIndex >= MIN_TICK_GAP);

  const step = MONTH_STEPS.find((s) => fits(picked(s))) ?? 120;
  const ticks = picked(step);
  // O começo da janela leva rótulo quando sobra espaço até a primeira marca
  const next = ticks[0];
  if (next?.index !== 0 && (!next || next.index * perIndex >= MIN_TICK_GAP)) ticks.unshift({ index: 0, date: first });
  return ticks.map(({ index, date }) => ({ index, label: displayShortMonthYear(date), anchor: anchorOf(index) }));
}

/** "50 mil", "1,5 mi", "−50 mil": o eixo Y e as variações dos painéis. */
export function displayThousands(value: number) {
  if (value === 0) return "0";
  const sign = value < 0 ? "−" : "";
  const abs = Math.abs(value);
  return abs >= 1_000_000
    ? `${sign}${displayNumber(abs / 1_000_000, 1)} mi`
    : `${sign}${displayNumber(abs / 1_000, abs % 1_000 === 0 ? 0 : 1)} mil`;
}

/** "+19,0 mil", "−1,0 mil": variação de um painel de classe. */
export function displaySignedThousands(value: number) {
  const abs = Math.abs(value);
  const text = abs >= 1_000_000 ? `${displayNumber(abs / 1_000_000, 1)} mi` : `${displayNumber(abs / 1_000, 1)} mil`;
  if (Math.round(abs / 100) === 0) return text;
  return `${value < 0 ? "−" : "+"}${text}`;
}
