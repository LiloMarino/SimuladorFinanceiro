import type { ElectionMap, MapParty, MapPlace, VoterGroup } from "@/types";
import { displayMonthShort, parseLocalDate } from "@/shared/lib/utils/display";

/** "2027-03-01" → "1 mar": o dia sem zero à esquerda e o mês curto. */
export function dayMonth(isoDate: string) {
  return `${parseLocalDate(isoDate).getDate()} ${displayMonthShort(isoDate)}`;
}

export type MapLensId = "leads" | "result" | "performance" | "change" | "rejection" | "approval" | "group";
export type MapDivision = "state" | "region";

/** O grupo aberto na lente do eleitorado e o que sustenta as lentes que não dependem de grupo. */
export const DEFAULT_GROUP: VoterGroup = "WELFARE";

export type MapLens = {
  id: MapLensId;
  label: string;
  section: "Eleição" | "Seu partido" | "Governo" | "Eleitorado";
  key: string | null;
};

// As lentes na ordem do menu; a tecla de cada uma troca a lente em qualquer tela do mapa
export const MAP_LENSES: MapLens[] = [
  { id: "leads", label: "Quem lidera", section: "Eleição", key: "1" },
  { id: "result", label: "Resultado", section: "Eleição", key: null },
  { id: "performance", label: "Desempenho", section: "Seu partido", key: "2" },
  { id: "change", label: "Variação", section: "Seu partido", key: "3" },
  { id: "rejection", label: "Rejeição", section: "Seu partido", key: "4" },
  { id: "approval", label: "Aprovação", section: "Governo", key: "5" },
  { id: "group", label: "Onde vive cada grupo", section: "Eleitorado", key: "6" },
];

export const MAP_LENS_BY_KEY = Object.fromEntries(MAP_LENSES.filter((l) => l.key).map((l) => [l.key, l.id])) as Record<
  string,
  MapLensId
>;

export const MAP_SECTIONS = ["Eleição", "Seu partido", "Governo", "Eleitorado"] as const;

/** Os lugares da divisão escolhida, na ordem da API. */
export function placesOf(map: ElectionMap, division: MapDivision) {
  const kind = division === "state" ? "STATE" : "REGION";
  return map.places.filter((place) => place.kind === kind);
}

export function placeByCode(map: ElectionMap, code: string) {
  return map.places.find((place) => place.code === code);
}

/** O lugar de abertura da página: o de maior eleitorado da divisão. */
export function defaultPlace(map: ElectionMap, division: MapDivision) {
  return placesOf(map, division).reduce((best, place) => (place.electorate > best.electorate ? place : best));
}

export function partyOf(map: ElectionMap, id: number): MapParty | undefined {
  return map.parties.find((party) => party.id === id);
}

/** O partido pintado nas lentes do partido: o escolhido, senão o do jogador, senão o líder nacional da pesquisa. */
export function paintedParty(map: ElectionMap, chosen: number | null): MapParty | undefined {
  if (chosen !== null) {
    const found = partyOf(map, chosen);
    if (found) return found;
  }
  if (map.viewer_party_id !== null) return partyOf(map, map.viewer_party_id);
  const leader = map.poll ? nationalLeader(map) : undefined;
  return leader ?? map.parties[0];
}

// A pesquisa nacional é a soma dos lugares, pesada pelo eleitorado; o líder dela abre a página sem partido do jogador
function nationalLeader(map: ElectionMap) {
  const poll = map.poll;
  if (!poll) return undefined;
  const totals = new Map<number, number>();
  for (const place of placesOf(map, "region")) {
    const entry = poll.places.find((item) => item.code === place.code);
    for (const row of entry?.entries ?? []) {
      totals.set(row.party_id, (totals.get(row.party_id) ?? 0) + Number(row.points) * Number(place.electorate_share));
    }
  }
  const best = [...totals.entries()].sort((a, b) => b[1] - a[1])[0];
  return best ? partyOf(map, best[0]) : undefined;
}

export type LensAvailability = { available: true } | { available: false; reason: string };

/** Quando a lente liga: sem os dados dela, o motivo vai escrito no botão apagado. */
export function lensAvailability(map: ElectionMap, lens: MapLensId): LensAvailability {
  switch (lens) {
    case "leads":
    case "performance":
      return map.poll ? { available: true } : { available: false, reason: `abre em ${dayMonth(map.opens_on)}` };
    case "change":
      if (!map.poll) return { available: false, reason: `abre em ${dayMonth(map.opens_on)}` };
      return map.poll.previous_date ? { available: true } : { available: false, reason: "precisa de 2 pesquisas" };
    case "result":
      return map.result ? { available: true } : { available: false, reason: `em ${dayMonth(map.first_round)}` };
    case "rejection":
      return map.rejection.length > 0 ? { available: true } : { available: false, reason: "sem partidos" };
    case "approval":
      return map.approval ? { available: true } : { available: false, reason: "sem dados por lugar" };
    case "group":
      return { available: true };
  }
}

/** A lente do primeiro uso: a de eleição quando há pesquisa, senão a de eleitorado, que sempre liga. */
export function fallbackLens(map: ElectionMap, wanted: MapLensId): MapLensId {
  if (lensAvailability(map, wanted).available) return wanted;
  const next = MAP_LENSES.find((lens) => lensAvailability(map, lens.id).available);
  return next?.id ?? "group";
}

export type Standing = { partyId: number; points: number };

/** A pesquisa (ou o resultado) do lugar, do primeiro ao último. Com o resultado entre os turnos, só os finalistas. */
export function standings(map: ElectionMap, code: string, source: "poll" | "result"): Standing[] {
  const entries =
    source === "poll"
      ? (map.poll?.places.find((place) => place.code === code)?.entries ?? [])
      : (map.result?.places.find((place) => place.code === code)?.entries ?? []);
  return entries
    .map((entry) => ({ partyId: entry.party_id, points: Number(entry.points) }))
    .sort((a, b) => b.points - a.points || a.partyId - b.partyId);
}

export type PlaceClass =
  | { kind: "leads"; leader: number; lead: number }
  | { kind: "tie"; leaders: [number, number]; lead: number; of: 2 | 3 };

/**
 * Quem lidera o lugar. Empate técnico: o 1º e o 2º estão a no máximo a margem do lugar; com 3 partidos
 * na margem do 1º, o empate é entre 3. Com margem 0 só o empate exato é empate.
 */
export function classifyPlace(ranked: Standing[], margin: number): PlaceClass | null {
  const [first, second, third] = ranked;
  if (!first) return null;
  if (!second) return { kind: "leads", leader: first.partyId, lead: first.points };
  const lead = first.points - second.points;
  const tied = margin > 0 ? lead <= margin : lead === 0;
  if (!tied) return { kind: "leads", leader: first.partyId, lead };
  const triple =
    third !== undefined && (margin > 0 ? first.points - third.points <= margin : first.points === third.points);
  return { kind: "tie", leaders: [first.partyId, second.partyId], lead, of: triple ? 3 : 2 };
}

/** O número de pontos do partido no lugar (pesquisa ou resultado). */
export function pointsOf(ranked: Standing[], partyId: number) {
  return ranked.find((row) => row.partyId === partyId)?.points ?? 0;
}

/** Variação do partido desde a pesquisa anterior, em pontos; sem pesquisa anterior, null. */
export function changeOf(map: ElectionMap, code: string, partyId: number) {
  const place = map.poll?.places.find((item) => item.code === code);
  if (!place || place.previous_entries.length === 0) return null;
  const now = place.entries.find((entry) => entry.party_id === partyId);
  const before = place.previous_entries.find((entry) => entry.party_id === partyId);
  if (!now || !before) return null;
  return Number(now.points) - Number(before.points);
}

function rejectionOf(map: ElectionMap, code: string, partyId: number) {
  const value = map.rejection.find((row) => row.party_id === partyId)?.places.find((p) => p.code === code)?.value;
  return value === undefined ? null : Number(value);
}

function approvalOf(map: ElectionMap, code: string) {
  const value = map.approval?.places.find((p) => p.code === code)?.value;
  return value === undefined ? null : Number(value);
}

/** A fatia do eleitorado do lugar que é do grupo, em pontos percentuais (0 a 100). */
export function groupShare(place: MapPlace, group: VoterGroup) {
  const score = place.groups.find((item) => item.group === group)?.score;
  return score === undefined ? 0 : Number(score) * 100;
}

export function nationalGroupShare(map: ElectionMap, group: VoterGroup) {
  const score = map.national_groups.find((item) => item.group === group)?.score;
  return score === undefined ? 0 : Number(score) * 100;
}

/** O número de cada lugar da divisão na lente de escala (todas, menos Quem lidera e Resultado). */
export function lensValues(
  map: ElectionMap,
  division: MapDivision,
  lens: Exclude<MapLensId, "leads" | "result">,
  partyId: number | null,
  group: VoterGroup,
): Record<string, number | null> {
  const values: Record<string, number | null> = {};
  for (const place of placesOf(map, division)) {
    values[place.code] = valueOf(map, place, lens, partyId, group);
  }
  return values;
}

function valueOf(
  map: ElectionMap,
  place: MapPlace,
  lens: Exclude<MapLensId, "leads" | "result">,
  partyId: number | null,
  group: VoterGroup,
) {
  switch (lens) {
    case "performance":
      return partyId === null ? null : pointsOf(standings(map, place.code, "poll"), partyId);
    case "change":
      return partyId === null ? null : changeOf(map, place.code, partyId);
    case "rejection":
      return partyId === null ? null : rejectionOf(map, place.code, partyId);
    case "approval":
      return approvalOf(map, place.code);
    case "group":
      return groupShare(place, group);
  }
}

export type Extremes = { min: { code: string; value: number }; max: { code: string; value: number } };

/** O lugar de menor e o de maior valor; vazio quando nenhum lugar tem dado. */
export function extremes(values: Record<string, number | null>): Extremes | null {
  let min: Extremes["min"] | null = null;
  let max: Extremes["max"] | null = null;
  for (const [code, value] of Object.entries(values)) {
    if (value === null) continue;
    if (!min || value < min.value) min = { code, value };
    if (!max || value > max.value) max = { code, value };
  }
  return min && max ? { min, max } : null;
}

export type ScaleCenter = number | null;

/** O centro da escala: a média do país na aprovação, zero na variação, nenhum nas demais. */
export function scaleCenter(map: ElectionMap, lens: MapLensId): ScaleCenter {
  if (lens === "approval") return map.approval ? Number(map.approval.national) : null;
  if (lens === "change") return 0;
  return null;
}

/**
 * Onde o valor cai na escala, de 0 a 1. Com centro, 0,5 é o centro e cada metade se estica até o extremo do
 * seu lado, então o centro nunca muda de cor com os dados.
 */
export function scalePosition(value: number, min: number, max: number, center: ScaleCenter) {
  if (center === null) return max === min ? 0.5 : (value - min) / (max - min);
  if (value >= center) return max <= center ? 0.5 : 0.5 + 0.5 * ((value - center) / (max - center));
  return min >= center ? 0.5 : 0.5 - 0.5 * ((center - value) / (center - min));
}

/**
 * A cor do lugar como `color-mix` sobre tokens: `from` em 0 e `to` em 1. Com centro, o miolo é o token
 * `middle`, e cada metade mistura dele para o seu extremo.
 */
export function mixColor(position: number, ends: { from: string; to: string; middle?: string }) {
  const t = Math.min(1, Math.max(0, position));
  if (!ends.middle) return `color-mix(in oklab, ${ends.to} ${pct(t)}, ${ends.from})`;
  if (t >= 0.5) return `color-mix(in oklab, ${ends.to} ${pct((t - 0.5) * 2)}, ${ends.middle})`;
  return `color-mix(in oklab, ${ends.from} ${pct((0.5 - t) * 2)}, ${ends.middle})`;
}

function pct(fraction: number) {
  return `${Math.round(fraction * 100)}%`;
}

/** Quantos estados cada partido venceu no resultado; empate técnico não existe no resultado. */
export function statesWon(map: ElectionMap) {
  const wins = new Map<number, number>();
  for (const place of placesOf(map, "state")) {
    const winner = standings(map, place.code, "result")[0];
    if (winner) wins.set(winner.partyId, (wins.get(winner.partyId) ?? 0) + 1);
  }
  return wins;
}

/** Os votos do partido em milhões: pontos ÷ 100 × eleitorado do país. */
export function votesInMillions(points: number, electorate: number) {
  return (points / 100) * (electorate / 1_000_000);
}

/** Pontos percentuais já na escala 0–100 (52 → "52%"): sem casa decimal na pesquisa com margem e com uma casa ("52,4%") sem ela. */
export function formatPercent(value: number, digits = 0) {
  return `${value.toLocaleString("pt-BR", { maximumFractionDigits: digits, minimumFractionDigits: digits })}%`;
}

/** "Pesquisa de 26 ago 2027": a data com o ano. */
export function pollDateLabel(isoDate: string) {
  return `${dayMonth(isoDate)} ${isoDate.slice(0, 4)}`;
}

export type SentenceInput = {
  map: ElectionMap;
  division: MapDivision;
  lens: MapLensId;
  /** A sigla do partido pintado. */
  abbr: string;
  values: Record<string, number | null>;
};

/** A frase que acompanha o mapa: o extremo da lente e o que ele quer dizer. */
export function lensSentence({ map, division, lens, abbr, values }: SentenceInput): string {
  const names = Object.fromEntries(map.places.map((place) => [place.code, place.name]));
  const range = extremes(values);
  switch (lens) {
    case "leads":
      return leadsSentence(map, division);
    case "result":
      return "";
    case "performance":
      return range
        ? `Mais forte: ${names[range.max.code]}, ${formatPercent(range.max.value)}. Mais fraco: ${names[range.min.code]}, ${formatPercent(range.min.value)}.`
        : "";
    case "change":
      return changeSentence(map, division, values);
    case "rejection":
      return range
        ? `${formatPercent(range.max.value)} em ${names[range.max.code]} não votam no ${abbr} de jeito nenhum: é onde a campanha rende menos. O menor é ${names[range.min.code]}, ${formatPercent(range.min.value)}.`
        : "";
    case "approval":
      return map.approval
        ? `O centro da escala é a média do país (${formatPercent(Number(map.approval.national))}): azul aprova mais que o país, vermelho menos.`
        : "";
    case "group":
      return range
        ? `Maior fatia: ${names[range.max.code]}, ${formatPercent(range.max.value)} do eleitorado. Menor: ${names[range.min.code]}, ${formatPercent(range.min.value)}.`
        : "";
  }
}

function leadsSentence(map: ElectionMap, division: MapDivision) {
  const all = placesOf(map, division);
  const unit = division === "state" ? "estados" : "regiões";
  if (all.every((place) => place.margin === 0)) return "Sem margem de erro na partida: nenhum lugar fica listrado.";
  const tied = all.filter((place) => classifyPlace(standings(map, place.code, "poll"), place.margin)?.kind === "tie");
  if (tied.length === 0)
    return `Nenhum ${division === "state" ? "estado" : "região"} listrado: o líder de cada um está além da margem.`;
  const margins = tied.map((place) => place.margin);
  const low = Math.min(...margins);
  const high = Math.max(...margins);
  const range = low === high ? `±${low}` : `±${low} a ±${high}`;
  return `${tied.length} dos ${all.length} ${unit} listrados: a margem deles é de ${range}.`;
}

// A variação resumida por região: a região cresceu se todos os lugares dela subiram, e caiu se todos desceram
function changeSentence(map: ElectionMap, division: MapDivision, values: Record<string, number | null>) {
  const byRegion = new Map<string, number[]>();
  for (const place of placesOf(map, division)) {
    const value = values[place.code];
    if (value === null || value === undefined) continue;
    const region = place.region ?? place.code;
    byRegion.set(region, [...(byRegion.get(region) ?? []), Math.round(value)]);
  }
  const regionNames = Object.fromEntries(placesOf(map, "region").map((place) => [place.code, place.name]));
  const describe = (sign: 1 | -1) => {
    const parts: string[] = [];
    for (const [region, rounded] of byRegion) {
      if (!rounded.every((value) => value * sign > 0)) continue;
      const low = Math.min(...rounded.map((value) => Math.abs(value)));
      const high = Math.max(...rounded.map((value) => Math.abs(value)));
      const arrow = sign > 0 ? "▲" : "▼";
      parts.push(`${regionNames[region]} (${low === high ? `${arrow}${low}` : `${arrow}${low} a ${arrow}${high}`})`);
    }
    return parts;
  };
  const grew = describe(1);
  const fell = describe(-1);
  const since = map.poll?.previous_date ? ` desde ${dayMonth(map.poll.previous_date)}` : "";
  const pieces = [
    grew.length ? `Cresceu em ${joinList(grew)}` : "",
    fell.length ? `${grew.length ? "caiu" : "Caiu"} em ${joinList(fell)}` : "",
  ].filter(Boolean);
  return pieces.length ? `${pieces.join(" e ")}${since}.` : `Sem mudança clara de região${since}.`;
}

function joinList(items: string[]) {
  return items.length < 2 ? (items[0] ?? "") : `${items.slice(0, -1).join(", ")} e ${items[items.length - 1]}`;
}

/** A frase do dialog: onde o partido foi melhor e pior, e quanto teve no país. */
export function resultSentence(map: ElectionMap, partyId: number) {
  const names = Object.fromEntries(map.places.map((place) => [place.code, place.name]));
  const state = bestAndWorstOf(map, "state", partyId);
  const region = bestAndWorstOf(map, "region", partyId);
  if (!state || !region) return null;
  return {
    best: `${names[state.best.code]} (${formatPercent(state.best.value)}) e ${names[region.best.code]} (${formatPercent(region.best.value)})`,
    worst: `${names[state.worst.code]} (${formatPercent(state.worst.value)}) e ${names[region.worst.code]} (${formatPercent(region.worst.value)})`,
  };
}

function bestAndWorstOf(map: ElectionMap, division: MapDivision, partyId: number) {
  const values: Record<string, number | null> = {};
  for (const place of placesOf(map, division)) {
    const ranked = standings(map, place.code, "result");
    const total = ranked.reduce((sum, row) => sum + row.points, 0);
    values[place.code] = total > 0 ? (pointsOf(ranked, partyId) / total) * 100 : null;
  }
  const range = extremes(values);
  return range ? { best: range.max, worst: range.min } : null;
}
