import { partyColor, partyForeground } from "@/shared/lib/party-colors";
import type { ElectionMap, MapParty, VoterGroup } from "@/types";
import type { MapFill } from "../components/brazil-map";
import {
  classifyPlace,
  extremes,
  formatPercent,
  lensSentence,
  lensValues,
  mixColor,
  momentSource,
  partyOf,
  placesOf,
  pollDateLabel,
  previousDate,
  scaleCenter,
  scalePosition,
  standings,
  dayMonth,
  type MapDivision,
  type MapLensId,
} from "./map-lenses";
import { GROUP_INFO, GROUP_MAP_COLOR } from "./voters";

type ScaleEnds = { from: string; to: string; middle?: string };

type MapLegend =
  | { kind: "parties"; parties: MapParty[]; tie: boolean }
  | { kind: "scale"; gradient: string; min: string; max: string };

export type LensView = {
  title: string;
  explanation: string;
  fills: Record<string, MapFill>;
  legend: MapLegend;
  sentence: string;
  /** O número de cada lugar nas lentes de escala, já formatado; vazio em Quem lidera. */
  valueText: Record<string, string>;
};

const WHITE_TEXT = "var(--primary-foreground)";
const DARK_TEXT = "var(--foreground)";

/** As pontas da escala de cor de uma lente de número. */
export function scaleEnds(lens: MapLensId, party: MapParty | undefined, group: VoterGroup): ScaleEnds {
  switch (lens) {
    case "performance": {
      const color = party ? partyColor(party) : "var(--muted-foreground)";
      return {
        from: `color-mix(in oklab, ${color} 12%, var(--card))`,
        to: `color-mix(in oklab, ${color} 60%, var(--foreground))`,
      };
    }
    case "change":
      return { from: "var(--map-change-low)", middle: "var(--subtle)", to: "var(--map-change-high)" };
    case "rejection":
      return { from: "var(--map-rejection-light)", to: "var(--map-rejection-dark)" };
    case "approval":
      return { from: "var(--map-approval-low)", middle: "var(--map-approval-center)", to: "var(--map-approval-high)" };
    default:
      return { from: GROUP_MAP_COLOR[group].light, to: GROUP_MAP_COLOR[group].dark };
  }
}

const GRADIENT_STEPS = [0, 0.2, 0.4, 0.6, 0.8, 1];

/** O degradê da escala em seis passos, para a legenda e para o ícone da lente. */
export function scaleGradient(ends: ScaleEnds) {
  return `linear-gradient(90deg, ${GRADIENT_STEPS.map((step) => mixColor(step, ends)).join(", ")})`;
}

function lensTitle(lens: MapLensId, abbr: string, group: VoterGroup, since: string | null) {
  switch (lens) {
    case "leads":
      return "Quem lidera";
    case "performance":
      return `Desempenho do ${abbr}`;
    case "change":
      return `Variação do ${abbr}${since ? ` desde ${since}` : ""}`;
    case "rejection":
      return `Rejeição do ${abbr}`;
    case "approval":
      return "Aprovação do presidente";
    case "group":
      return GROUP_INFO[group].label;
  }
}

function leadsExplanation(map: ElectionMap, unit: string) {
  if (map.poll) {
    const finalists = map.poll.runoff ? ", só os dois finalistas" : "";
    return `Pesquisa de ${pollDateLabel(map.poll.date)}${finalists}. Listrado: a diferença cabe na margem do ${unit}.`;
  }
  const winner = nationalWinner(map);
  return `Cor cheia: resultado não tem margem.${winner ? ` ${winner.abbr} venceu com ${formatPercent(winner.share)} no país.` : ""}`;
}

// O partido com mais votos válidos no país no turno apurado
function nationalWinner(map: ElectionMap) {
  const top = map.result?.national.reduce((best, row) => (Number(row.share) > Number(best.share) ? row : best));
  const party = top ? partyOf(map, top.party_id) : undefined;
  return top && party ? { abbr: party.abbr, share: Number(top.share) } : null;
}

function lensExplanation(map: ElectionMap, lens: MapLensId, unit: string) {
  switch (lens) {
    case "leads":
      return leadsExplanation(map, unit);
    case "performance":
      return `A intenção de voto do partido em cada ${unit}: quanto mais escuro, mais voto.`;
    case "change":
      return `Quanto a intenção de voto do partido subiu ou caiu em cada ${unit} desde a pesquisa anterior, em pontos. Verde subiu, vermelho caiu.`;
    case "rejection":
      return `De cada 100 eleitores do ${unit}, quantos não votam no partido de jeito nenhum: quanto mais escuro, mais rejeição.`;
    case "approval":
      return `A aprovação do governo em cada ${unit}, calculada pela mistura de grupos de eleitores dele. Esta lente só existe para o dia de hoje.`;
    case "group":
      return `Que fatia do eleitorado do ${unit} é do grupo: quanto mais escuro, mais gente do grupo.`;
  }
}

// "Quem lidera" vira "Quem venceu" no ponto de resultado, e a data entra no título fora do hoje
function leadsTitle(map: ElectionMap, past: boolean, unit: string) {
  if (map.poll) return `Quem lidera · ${past ? pollDateLabel(map.poll.date) : `por ${unit}`}`;
  return `Quem venceu · ${map.result ? `${map.result.round}º turno de ${map.result.date.slice(0, 4)}` : `por ${unit}`}`;
}

function textOn(position: number, centered: boolean) {
  const strength = centered ? Math.abs(position - 0.5) * 2 : position;
  return strength > 0.6 ? WHITE_TEXT : DARK_TEXT;
}

/** Cores, legenda, título e frase de uma lente numa divisão. O partido pintado vale nas lentes de partido. */
export function lensView(
  map: ElectionMap,
  division: MapDivision,
  lens: MapLensId,
  party: MapParty | undefined,
  group: VoterGroup,
  /** O momento mostrado não é o de hoje: a data entra no título. */
  past = false,
): LensView {
  const unit = division === "state" ? "estado" : "região";
  const previous = previousDate(map);
  const sinceLabel = previous ? dayMonth(previous) : null;
  const explanation = lensExplanation(map, lens, unit);

  if (lens === "leads") {
    return leaderView(map, division, { title: leadsTitle(map, past, unit), explanation });
  }
  const title = `${lensTitle(lens, party?.abbr ?? "", group, sinceLabel)} · por ${unit}`;

  const values = lensValues(map, division, lens, party?.id ?? null, group);
  const ends = scaleEnds(lens, party, group);
  const range = extremes(values);
  const center = scaleCenter(map, lens);
  const fills: Record<string, MapFill> = {};
  for (const [code, value] of Object.entries(values)) {
    if (value === null || !range) {
      fills[code] = { kind: "empty" };
      continue;
    }
    const position = scalePosition(value, range.min.value, range.max.value, center);
    fills[code] = { kind: "solid", color: mixColor(position, ends), text: textOn(position, center !== null) };
  }
  const signed = lens === "change";
  const format = (value: number) => (signed ? signedPercent(value) : formatPercent(value));
  const valueText = Object.fromEntries(
    Object.entries(values).map(([code, value]) => [code, value === null ? "sem dado" : format(value)]),
  );
  return {
    title,
    explanation,
    fills,
    valueText,
    legend: {
      kind: "scale",
      gradient: scaleGradient(ends),
      min: range ? format(range.min.value) : "",
      max: range ? format(range.max.value) : "",
    },
    sentence: lensSentence({ map, division, lens, abbr: party?.abbr ?? "", values }),
  };
}

function signedPercent(value: number) {
  const rounded = Math.round(value);
  return `${rounded > 0 ? "+" : rounded < 0 ? "−" : ""}${Math.abs(rounded)} p.p.`;
}

function leaderView(map: ElectionMap, division: MapDivision, head: { title: string; explanation: string }): LensView {
  const source = momentSource(map) ?? "poll";
  const fills: Record<string, MapFill> = {};
  const seen = new Set<number>();
  let tie = false;
  for (const place of placesOf(map, division)) {
    const ranked = standings(map, place.code, source);
    const result = classifyPlace(ranked, source === "poll" ? place.margin : 0);
    if (!result) {
      fills[place.code] = { kind: "empty" };
      continue;
    }
    if (result.kind === "leads") {
      const leader = partyOf(map, result.leader);
      if (!leader) {
        fills[place.code] = { kind: "empty" };
        continue;
      }
      seen.add(leader.id);
      const color = partyColor(leader);
      fills[place.code] = { kind: "solid", color, text: partyForeground(color) };
      continue;
    }
    const [first, second] = result.leaders.map((id) => partyOf(map, id));
    if (!first || !second) {
      fills[place.code] = { kind: "empty" };
      continue;
    }
    tie = true;
    seen.add(first.id);
    seen.add(second.id);
    fills[place.code] = { kind: "stripes", colors: [partyColor(first), partyColor(second)], text: DARK_TEXT };
  }
  const shown = map.parties.filter((candidate) => seen.has(candidate.id));
  return {
    ...head,
    fills,
    valueText: {},
    legend: { kind: "parties", parties: shown, tie },
    sentence: lensSentence({ map, division, lens: "leads", abbr: "", values: {} }),
  };
}
