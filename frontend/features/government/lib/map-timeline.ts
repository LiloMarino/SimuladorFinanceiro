import { displayDayMonth, displayMonthShort } from "@/shared/lib/utils/display";
import type { MapParty, MapPlace, TimelineMilestone, TimelinePoint, TimelineYear } from "@/types";

/** A folga da régua em cada lado, para o ponto e o rótulo caberem. */
export const RULER_MARGIN = 26;

/** Quantas eleições o seletor mostra por inteiro; acima disso ficam as 3 mais recentes e o "Anteriores". */
const YEARS_IN_ROW = 4;
const RECENT_YEARS = 3;

/** No máximo este tanto de marcos por intervalo; o resto vira "+N". */
const MILESTONES_PER_SLOT = 2;

// Os passos entre dois pontos seguidos: o respiro do 1º turno para a primeira semanal é de 1,5 passo
function stepsBetween(before: TimelinePoint["kind"], after: TimelinePoint["kind"]) {
  return before === "FIRST_ROUND" && (after === "RUNOFF_POLL" || after === "RUNOFF") ? 1.5 : 1;
}

/**
 * A posição de cada ponto na régua, em px. A distância segue a ordem dos pontos e não as datas: as pesquisas
 * mensais e as semanais ocupam o mesmo espaço cada uma.
 */
export function rulerLayout(points: Pick<TimelinePoint, "kind">[], width: number) {
  const gaps = points.slice(1).map((point, index) => stepsBetween(points[index]!.kind, point.kind));
  const total = gaps.reduce((sum, gap) => sum + gap, 0);
  const step = total > 0 ? (width - 2 * RULER_MARGIN) / total : 0;
  const xs: number[] = [];
  let x = RULER_MARGIN;
  for (const [index] of points.entries()) {
    if (index > 0) x += gaps[index - 1]! * step;
    xs.push(x);
  }
  return { xs, step };
}

export type MilestoneSlot = {
  after: string;
  before: string;
  /** Os marcos que aparecem na régua. */
  shown: TimelineMilestone[];
  /** Os que não couberam: o "+N" e o resto da dica. */
  hidden: TimelineMilestone[];
  /** A lista inteira do intervalo, na ordem da API. */
  all: TimelineMilestone[];
};

/**
 * Os marcos agrupados por intervalo entre duas pesquisas. Promessas e ações são do partido em foco; as
 * alianças aparecem sempre.
 */
export function milestoneSlots(milestones: TimelineMilestone[], focusParty: number | null): MilestoneSlot[] {
  const slots = new Map<string, MilestoneSlot>();
  for (const milestone of milestones) {
    if (milestone.kind !== "ALLIANCE" && milestone.party_id !== focusParty) continue;
    const key = `${milestone.after}|${milestone.before}`;
    const slot = slots.get(key) ?? { after: milestone.after, before: milestone.before, shown: [], hidden: [], all: [] };
    slot.all.push(milestone);
    (slot.shown.length < MILESTONES_PER_SLOT ? slot.shown : slot.hidden).push(milestone);
    slots.set(key, slot);
  }
  return [...slots.values()].sort((a, b) => a.after.localeCompare(b.after));
}

/** O número que o selo do marco mostra: quantos itens ele junta; sem selo quando é um só. */
export function milestoneCount(milestone: TimelineMilestone) {
  return milestone.items.length > 1 ? milestone.items.length : null;
}

export type VisibleYears = {
  /** Os anos que ficam no seletor, do mais antigo ao mais recente. */
  row: TimelineYear[];
  /** Os que ficam atrás do "Anteriores"; vazio com até 4 eleições. */
  older: TimelineYear[];
};

export function visibleYears(years: TimelineYear[]): VisibleYears {
  if (years.length <= YEARS_IN_ROW) return { row: years, older: [] };
  return { row: years.slice(-RECENT_YEARS), older: years.slice(0, -RECENT_YEARS) };
}

/** O rótulo embaixo de cada ponto: o mês nas mensais, o dia e o mês nas semanais e o nome dos turnos. */
export function pointLabel(point: Pick<TimelinePoint, "kind" | "date">) {
  switch (point.kind) {
    case "POLL":
      return displayMonthShort(point.date);
    case "RUNOFF_POLL":
      return displayDayMonth(point.date);
    case "FIRST_ROUND":
      return "1º turno";
    case "RUNOFF":
      return "2º turno";
  }
}

/** O ponto que o ano abre por padrão: o último que já aconteceu, ou o primeiro quando nada aconteceu. */
export function lastHappened(points: TimelinePoint[]) {
  return [...points].reverse().find((point) => point.happened) ?? points[0];
}

/** O ponto da URL, quando existe na régua; senão o último que já aconteceu. */
export function pointAt(points: TimelinePoint[], date: string | null) {
  return points.find((point) => point.date === date && point.happened) ?? lastHappened(points);
}

/**
 * Os dois partidos que foram ao 2º turno, na ordem da apuração do 1º. Vazio quando a eleição não teve 2º turno
 * ou o 1º ainda não foi apurado.
 */
export function finalists(points: TimelinePoint[]) {
  const hasRunoff = points.some((point) => point.kind === "RUNOFF_POLL" || point.kind === "RUNOFF");
  const national = points.find((point) => point.kind === "FIRST_ROUND")?.result?.national;
  if (!hasRunoff || !national) return [];
  return [...national]
    .sort((a, b) => Number(b.share) - Number(a.share))
    .slice(0, 2)
    .map((entry) => entry.party_id);
}

/** "14 out 2030": o dia completo, como a bandeira da régua mostra. */
export function fullDate(isoDate: string) {
  return `${displayDayMonth(isoDate)} ${isoDate.slice(0, 4)}`;
}

/**
 * O texto da bandeira sobre o ponto escolhido: a data e, nos turnos, o nome do turno e o que ele decidiu.
 * `mandate` vale quando o último turno é o que governa até a próxima eleição.
 */
export function flagText(
  point: TimelinePoint,
  points: TimelinePoint[],
  parties: Pick<MapParty, "id" | "abbr">[],
  mandate: boolean,
) {
  const date = fullDate(point.date);
  if (point.kind === "FIRST_ROUND") {
    const decided = !points.some((item) => item.kind === "RUNOFF_POLL" || item.kind === "RUNOFF");
    const top = [...(point.result?.national ?? [])].sort((a, b) => Number(b.share) - Number(a.share))[0];
    const winner = decided && top ? parties.find((party) => party.id === top.party_id) : undefined;
    return `1º turno · ${date}${winner && top ? ` · ${winner.abbr} venceu com ${Math.round(Number(top.share))}%` : ""}`;
  }
  if (point.kind === "RUNOFF") return `2º turno · ${date}${mandate ? " · vale até a próxima eleição" : ""}`;
  return date;
}

export type MarkerDelta = {
  /** Pontos que o partido andou no país, pesando as regiões pelo eleitorado. */
  national: number;
  /** O mesmo na região do marco; `null` quando o marco não mira região. */
  region: { code: string; delta: number } | null;
};

/**
 * Quanto o partido andou da pesquisa antes do marco para a pesquisa depois dele. `null` quando um dos dois
 * pontos não tem pesquisa do partido.
 */
export function markerDelta(
  before: TimelinePoint | undefined,
  after: TimelinePoint | undefined,
  partyId: number,
  regionCode: string | null,
  regions: Pick<MapPlace, "code" | "electorate_share">[],
): MarkerDelta | null {
  const nowNational = nationalPoints(after, partyId, regions);
  const thenNational = nationalPoints(before, partyId, regions);
  if (nowNational === null || thenNational === null) return null;
  const nowRegion = regionCode ? placePoints(after, partyId, regionCode) : null;
  const thenRegion = regionCode ? placePoints(before, partyId, regionCode) : null;
  return {
    national: Math.round(nowNational - thenNational),
    region:
      regionCode && nowRegion !== null && thenRegion !== null
        ? { code: regionCode, delta: Math.round(nowRegion - thenRegion) }
        : null,
  };
}

function placePoints(point: TimelinePoint | undefined, partyId: number, code: string) {
  const entry = point?.poll?.places.find((item) => item.code === code)?.entries.find((e) => e.party_id === partyId);
  return entry ? Number(entry.points) : null;
}

// A intenção nacional é a soma das regiões pesada pelo eleitorado
function nationalPoints(
  point: TimelinePoint | undefined,
  partyId: number,
  regions: Pick<MapPlace, "code" | "electorate_share">[],
) {
  let total = 0;
  let found = false;
  for (const region of regions) {
    const points = placePoints(point, partyId, region.code);
    if (points === null) continue;
    found = true;
    total += points * Number(region.electorate_share);
  }
  return found ? total : null;
}
