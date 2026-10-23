import { addYears, subYears } from "date-fns";
import { CALENDAR_END_YEAR, CALENDAR_START_YEAR, isIsoDate, toIso } from "@/shared/lib/utils/date-field";
import { displayIsoDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";

// Indexadores da renda fixa: o período só começa onde os três têm dado
const RATE_SERIES = ["CDI", "SELIC", "IPCA"];

/** A linha do tempo mede em meses desde jan/1993: 0 é 01/01/1993 e AXIS_MONTHS é o fim de dez/2040. */
export const AXIS_MONTHS = (CALENDAR_END_YEAR - CALENDAR_START_YEAR + 1) * 12;
export const AXIS_START_DATE = `${CALENDAR_START_YEAR}-01-01`;
export const AXIS_END_DATE = `${CALENDAR_END_YEAR}-12-31`;

/** Anos redondos marcados sob a linha. */
export const AXIS_TICK_YEARS = [1995, 2005, 2015, 2025, 2035];

export type Period = { start: string; end: string };

/** Primeiro dia com dado de todos os indicadores, e o indicador que o limita. */
export type DataFloor = { date: string; key: string };

export type DataEnds = {
  /** Último dia com dado real em todas as séries */
  realEnd: string | undefined;
  /** Último dia do futuro gerado em todas as séries que o têm */
  generatedEnd: string | undefined;
};

export type PeriodShortcut = {
  id: string;
  label: string;
  group: "past" | "future";
  period: Period;
  /** Motivo de o atalho estar desligado; nulo quando vale */
  blocked: string | null;
};

const SHORTCUT_YEARS = { past: [5, 10, 20], future: [5, 10] } as const;

/** Mês de uma data na linha do tempo: 0 é jan/1993. */
export function monthIndex(isoDate: string): number {
  const [year, month] = isoDate.split("-").map(Number);
  return (year - CALENDAR_START_YEAR) * 12 + (month - 1);
}

function daysInMonth(isoDate: string): number {
  const [year, month] = isoDate.split("-").map(Number);
  return new Date(year, month, 0).getDate();
}

/** Posição de uma data na linha, em meses; o início conta desde o começo do dia e o fim, até o limite dele. */
export function axisPosition(isoDate: string, edge: "start" | "end"): number {
  const day = Number(isoDate.slice(8, 10));
  const fraction = (edge === "start" ? day - 1 : day) / daysInMonth(isoDate);
  return monthIndex(isoDate) + fraction;
}

/** Posição na linha em % da largura, presa aos limites do eixo. */
export function axisPercent(position: number): number {
  return (Math.min(Math.max(position, 0), AXIS_MONTHS) / AXIS_MONTHS) * 100;
}

export const firstDayOfMonth = (index: number) => toIso(new Date(CALENDAR_START_YEAR, index, 1));

export const lastDayOfMonth = (index: number) => toIso(new Date(CALENDAR_START_YEAR, index + 1, 0));

/** O início de um mês cheio; o primeiro dia com dado vale no lugar do dia 1 quando cai depois dele. */
function monthStart(index: number, floor: DataFloor | undefined): string {
  const first = firstDayOfMonth(index);
  return floor && floor.date > first ? floor.date : first;
}

/** O período só existe com as duas datas completas e o fim depois do início. */
export function parsePeriod(startDate: string, endDate: string): Period | null {
  if (!isIsoDate(startDate) || !isIsoDate(endDate) || endDate <= startDate) return null;
  return { start: startDate, end: endDate };
}

/** Meses do período, contando o mês do início e o do fim: 01/04/2020 → 31/10/2026 são 79. */
export function periodMonths(period: Period): number {
  return monthIndex(period.end) - monthIndex(period.start) + 1;
}

/** 79 → "6 anos e 7 meses". */
export function displayDuration(months: number): string {
  const years = Math.floor(months / 12);
  const rest = months % 12;
  const yearsText = years === 1 ? "1 ano" : `${years} anos`;
  const restText = rest === 1 ? "1 mês" : `${rest} meses`;
  if (years === 0) return restText;
  return rest === 0 ? yearsText : `${yearsText} e ${restText}`;
}

/** Primeiro dia em que o indicador atende a partida: o IPCA é mensal e vale desde o dia 1 do mês. */
function seriesFirstDay(series: SeriesCoverage): string | undefined {
  if (!series.start) return undefined;
  if (series.key !== "IPCA" || series.start.endsWith("-01")) return series.start;
  return firstDayOfMonth(monthIndex(series.start) + 1);
}

/** O mais tardio dos primeiros dias dos indicadores; indefinido quando nenhum tem dado. */
export function dataFloor(coverage: SeriesCoverage[]): DataFloor | undefined {
  let floor: DataFloor | undefined;
  for (const series of coverage) {
    if (series.kind !== "INDICATOR" || !RATE_SERIES.includes(series.key)) continue;
    const date = seriesFirstDay(series);
    if (date && (!floor || date > floor.date)) floor = { date, key: series.key };
  }
  if (floor && floor.date < AXIS_START_DATE) return { ...floor, date: AXIS_START_DATE };
  return floor;
}

/** Até onde vai o dado real e o futuro gerado: o fim mais cedo entre as séries que os têm. */
export function dataEnds(coverage: SeriesCoverage[]): DataEnds {
  const earliest = (dates: (string | null)[]) => dates.filter((d): d is string => !!d).sort()[0];
  return {
    realEnd: earliest(coverage.map((s) => s.real_end)),
    generatedEnd: earliest(coverage.map((s) => s.generated_end)),
  };
}

export type TimelineZone = { kind: "no-data" | "real" | "future" | "repeat"; from: number; to: number };

/** As faixas da linha, em % da largura: sem dado, dado real, futuro gerado e o trecho que repete o último valor. */
export function timelineZones(floor: DataFloor | undefined, ends: DataEnds): TimelineZone[] {
  const floorPercent = floor ? axisPercent(axisPosition(floor.date, "start")) : 0;
  const realPercent = ends.realEnd
    ? Math.max(axisPercent(axisPosition(ends.realEnd, "end")), floorPercent)
    : floorPercent;
  const futurePercent = ends.generatedEnd
    ? Math.max(axisPercent(axisPosition(ends.generatedEnd, "end")), realPercent)
    : realPercent;
  const zones: TimelineZone[] = [
    { kind: "no-data", from: 0, to: floorPercent },
    { kind: "real", from: floorPercent, to: realPercent },
    { kind: "future", from: realPercent, to: futurePercent },
    { kind: "repeat", from: futurePercent, to: 100 },
  ];
  return zones.filter((zone) => zone.to > zone.from);
}

/** Posições das alças na linha, em meses; nulo quando o período não está completo. */
export function periodRange(period: Period | null): [number, number] | null {
  if (!period) return null;
  return [axisPosition(period.start, "start"), axisPosition(period.end, "end")];
}

/** Mês onde a alça de início para: antes do primeiro dia com dado ela não vai. */
function floorMonth(floor: DataFloor | undefined): number {
  return floor ? monthIndex(floor.date) : 0;
}

/** A alça de início parada em `boundary` (meses): vai para o dia 1 do mês, sem passar do primeiro dia com dado. */
export function startAtBoundary(boundary: number, floor: DataFloor | undefined): string {
  const month = Math.min(Math.max(Math.round(boundary), floorMonth(floor)), AXIS_MONTHS - 1);
  return monthStart(month, floor);
}

/** A alça de fim parada em `boundary` (meses): vai para o último dia do mês, sem passar do fim da linha. */
export function endAtBoundary(boundary: number): string {
  const month = Math.min(Math.max(Math.round(boundary), 1), AXIS_MONTHS) - 1;
  return lastDayOfMonth(month);
}

/** A barra andou `months`: as duas pontas mudam o mesmo tanto, a duração em meses fica, e param nas bordas. */
export function shiftPeriod(origin: Period, months: number, floor: DataFloor | undefined): Period {
  const startMonth = monthIndex(origin.start);
  const endMonth = monthIndex(origin.end);
  const lowest = Math.min(0, floorMonth(floor) - startMonth);
  const highest = AXIS_MONTHS - 1 - endMonth;
  const shift = Math.min(Math.max(months, lowest), highest);
  if (shift === 0) return origin;
  return { start: monthStart(startMonth + shift, floor), end: lastDayOfMonth(endMonth + shift) };
}

/** Onde o período encosta: no primeiro dia com dado, no fim da linha ou em lugar nenhum. */
export function periodStop(period: Period, floor: DataFloor | undefined): "floor" | "end" | null {
  if (period.end >= AXIS_END_DATE) return "end";
  if (floor && period.start <= floor.date) return "floor";
  return null;
}

/** O aviso da parada: o que impediu a alça de seguir. */
export function stopMessage(stop: "floor" | "end", floor: DataFloor | undefined): string {
  return stop === "floor" && floor
    ? `Sem dado antes de ${displayIsoDate(floor.date)}`
    : `Fim da linha: ${displayIsoDate(AXIS_END_DATE)}`;
}

/** Os atalhos de "Até hoje" e "Pra frente"; o que começaria antes do primeiro dia com dado vem desligado, com o motivo. */
export function buildShortcuts(today: string, floor: DataFloor | undefined): PeriodShortcut[] {
  const todayDate = parseLocalDate(today);

  const past = SHORTCUT_YEARS.past.map((years): PeriodShortcut => {
    const start = toIso(subYears(todayDate, years));
    return {
      id: `past-${years}`,
      label: `${years} anos`,
      group: "past",
      period: { start, end: today },
      blocked:
        floor && start < floor.date
          ? `${floor.key} só tem dado desde ${displayIsoDate(floor.date)}`
          : start < AXIS_START_DATE
            ? `A linha começa em ${displayIsoDate(AXIS_START_DATE)}`
            : null,
    };
  });
  const all: PeriodShortcut = {
    id: "past-all",
    label: "Tudo",
    group: "past",
    period: { start: floor?.date ?? AXIS_START_DATE, end: today },
    blocked: null,
  };
  const future = SHORTCUT_YEARS.future.map((years): PeriodShortcut => {
    const end = toIso(addYears(todayDate, years));
    return {
      id: `future-${years}`,
      label: `${years} anos`,
      group: "future",
      period: { start: today, end },
      blocked: end > AXIS_END_DATE ? `Passa do fim da linha (${displayIsoDate(AXIS_END_DATE)})` : null,
    };
  });
  return [...past, all, ...future];
}

/** O atalho que o período atual reproduz, se algum. */
export function activeShortcut(period: Period | null, shortcuts: PeriodShortcut[]): PeriodShortcut | undefined {
  if (!period) return undefined;
  return shortcuts.find((s) => s.period.start === period.start && s.period.end === period.end);
}

export type BubbleLayout = "split" | "split-flipped" | "merged-start" | "merged-end";

/**
 * As datas sobre as alças: cada uma para fora da sua alça; o fim vira para dentro quando não cabe à direita;
 * uma só quando o início encosta na borda esquerda ou as duas ficariam uma sobre a outra.
 */
export function bubbleLayout(startPercent: number, endPercent: number): BubbleLayout {
  if (startPercent < 18) return "merged-start";
  if (endPercent <= 82) return "split";
  return endPercent - startPercent < 21 ? "merged-end" : "split-flipped";
}
