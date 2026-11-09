import type { TimelinePoint } from "@/types";
import { pointLabel } from "./map-timeline";

export type TrendRow = {
  date: string;
  kind: TimelinePoint["kind"];
  /** Por partido: pontos da pesquisa ou, na apuração, a fatia dos votos válidos. Quem saiu da disputa não aparece. */
  values: Record<number, number>;
  /** Só nas pesquisas; a apuração não tem indecisos. */
  undecided: number | null;
};

/** A intenção de cada partido no lugar, ponto a ponto, só dos pontos que já aconteceram. */
export function placeTrend(points: TimelinePoint[], code: string): TrendRow[] {
  const rows: TrendRow[] = [];
  for (const point of points) {
    if (!point.happened) continue;
    const poll = point.poll?.places.find((place) => place.code === code);
    if (poll) {
      rows.push({
        date: point.date,
        kind: point.kind,
        values: Object.fromEntries(poll.entries.map((entry) => [entry.party_id, Number(entry.points)])),
        undecided: Number(poll.undecided),
      });
      continue;
    }
    const result = point.result?.places.find((place) => place.code === code);
    if (!result) continue;
    const total = result.entries.reduce((sum, entry) => sum + Number(entry.points), 0);
    rows.push({
      date: point.date,
      kind: point.kind,
      values: Object.fromEntries(
        result.entries.map((entry) => [entry.party_id, total > 0 ? (Number(entry.points) / total) * 100 : 0]),
      ),
      undecided: null,
    });
  }
  return rows;
}

/** Os partidos com linha no gráfico, na ordem em que aparecem. */
export function trendParties(rows: TrendRow[]) {
  return [...new Set(rows.flatMap((row) => Object.keys(row.values).map(Number)))];
}

/** O rótulo do eixo: o mês da primeira pesquisa e os dois turnos; as demais ficam sem rótulo. */
export function trendTick(rows: TrendRow[], index: number) {
  const row = rows[index];
  if (!row) return "";
  if (row.kind === "FIRST_ROUND") return "1º t.";
  if (row.kind === "RUNOFF") return "2º t.";
  return index === 0 ? pointLabel(row) : "";
}

/** O índice onde começa o trecho do 2º turno (pesquisas semanais e apuração final), se houve. */
export function runoffStart(rows: TrendRow[]) {
  const index = rows.findIndex((row) => row.kind === "RUNOFF_POLL" || row.kind === "RUNOFF");
  return index === -1 ? null : index;
}

function percent(value: number) {
  return `${Math.round(value)}%`;
}

/** A frase que resume o gráfico para o partido: o ponto de partida, a última mensal e o 2º turno. */
export function trendSummary(rows: TrendRow[], partyId: number, abbr: string, placeName: string) {
  const mine = rows.filter((row) => row.values[partyId] !== undefined);
  const monthly = mine.filter((row) => row.kind === "POLL");
  const first = monthly[0];
  if (!first) return null;
  const last = monthly.at(-1)!;
  const parts = [`${placeName}: o ${abbr} foi de ${percent(first.values[partyId]!)} em ${pointLabel(first)}`];
  if (last !== first) parts[0] += ` a ${percent(last.values[partyId]!)} em ${pointLabel(last)}`;
  const firstRound = mine.find((row) => row.kind === "FIRST_ROUND");
  if (firstRound) parts.push(`teve ${percent(firstRound.values[partyId]!)} no 1º turno`);
  const runoff = mine.filter((row) => row.kind === "RUNOFF_POLL" || row.kind === "RUNOFF").at(-1);
  if (runoff) {
    parts.push(`no 2º turno ${runoff.kind === "RUNOFF" ? "teve" : "tem"} ${percent(runoff.values[partyId]!)}`);
  }
  const tail = parts.length > 1 ? ` e ${parts.pop()}` : "";
  return `${parts.join(", ")}${tail}.`;
}
