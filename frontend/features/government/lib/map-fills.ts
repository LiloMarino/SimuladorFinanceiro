import { partyColor, partyForeground } from "@/shared/lib/party-colors";
import { displayMonthShort } from "@/shared/lib/utils/display";
import type { ElectionMap, MapParty, VoterGroup } from "@/types";
import type { MapFill } from "../components/brazil-map";
import {
  classifyPlace,
  extremes,
  formatPercent,
  lensSentence,
  lensValues,
  mixColor,
  partyOf,
  placesOf,
  scaleCenter,
  scalePosition,
  standings,
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
  /** O número de cada lugar nas lentes de escala, já formatado; vazio em Quem lidera e Resultado. */
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
    case "result":
      return "Quem venceu";
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

function lensExplanation(lens: MapLensId, unit: string) {
  switch (lens) {
    case "leads":
      return `A cor é o partido à frente no ${unit}. Listrado: a diferença entre o 1º e o 2º cabe na margem do ${unit}, e a pesquisa não diz quem lidera.`;
    case "result":
      return `A cor é o partido com mais votos válidos no ${unit}. No resultado não há margem: a cor é cheia.`;
    case "performance":
      return `A intenção de voto do partido em cada ${unit}: quanto mais escuro, mais voto.`;
    case "change":
      return `Quanto a intenção de voto do partido subiu ou caiu em cada ${unit} desde a pesquisa anterior, em pontos. Verde subiu, vermelho caiu.`;
    case "rejection":
      return `De cada 100 eleitores do ${unit}, quantos não votam no partido de jeito nenhum: quanto mais escuro, mais rejeição.`;
    case "approval":
      return `A aprovação do governo em cada ${unit}, calculada pela mistura de grupos de eleitores dele.`;
    case "group":
      return `Que fatia do eleitorado do ${unit} é do grupo: quanto mais escuro, mais gente do grupo.`;
  }
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
): LensView {
  const unit = division === "state" ? "estado" : "região";
  const sinceLabel = map.poll?.previous_date ? displayMonthShort(map.poll.previous_date) : null;
  const title = `${lensTitle(lens, party?.abbr ?? "", group, sinceLabel)} · por ${unit}`;
  const explanation = lensExplanation(lens, unit);

  if (lens === "leads" || lens === "result") {
    return leaderView(map, division, lens, { title, explanation });
  }

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

function leaderView(
  map: ElectionMap,
  division: MapDivision,
  lens: "leads" | "result",
  head: { title: string; explanation: string },
): LensView {
  const source = lens === "leads" ? "poll" : "result";
  const fills: Record<string, MapFill> = {};
  const seen = new Set<number>();
  let tie = false;
  for (const place of placesOf(map, division)) {
    const ranked = standings(map, place.code, source);
    const result = classifyPlace(ranked, lens === "leads" ? place.margin : 0);
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
    sentence: lensSentence({ map, division, lens, abbr: "", values: {} }),
  };
}
