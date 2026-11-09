import { displayDayMonth } from "@/shared/lib/utils/display";
import type { CampaignActionKind, MapParty, MapPlace, TimelineMilestone, TimelinePoint } from "@/types";
import { ACTION_INFO } from "./campaign";
import { markerDelta, type MarkerDelta } from "./map-timeline";
import { GROUP_INFO } from "./voters";

type MilestoneItem = TimelineMilestone["items"][number];

const KIND_WORDS: Record<TimelineMilestone["kind"], { one: string; many: string }> = {
  PROMISE: { one: "promessa", many: "promessas" },
  CAMPAIGN: { one: "ação de campanha", many: "ações de campanha" },
  ALLIANCE: { one: "aliança", many: "alianças" },
};

/** O nome de cada tipo de marco, na régua e na legenda. */
export const MILESTONE_NAMES: Record<TimelineMilestone["kind"], string> = {
  PROMISE: "Promessa",
  CAMPAIGN: "Ações de campanha",
  ALLIANCE: "Aliança",
};

export type MilestoneContext = {
  parties: Pick<MapParty, "id" | "abbr">[];
  points: TimelinePoint[];
  /** As regiões do mapa: o nome da região do marco e o peso dela no país. */
  regions: Pick<MapPlace, "code" | "name" | "electorate_share">[];
};

export type MilestoneTip = {
  title: string;
  span: string;
  lines: string[];
  effect: string | null;
};

// Sigla em maiúsculas (TV) fica como está; o resto desce para minúsculas dentro da frase
function lower(word: string) {
  return word === word.toUpperCase() ? word : word.toLowerCase();
}

function abbrOf(parties: MilestoneContext["parties"], id: number | null) {
  return parties.find((party) => party.id === id)?.abbr ?? "outro partido";
}

function campaignLines(items: MilestoneItem[], parties: MilestoneContext["parties"]) {
  const groups = new Map<string, { item: MilestoneItem; count: number }>();
  for (const item of items) {
    const key = `${item.action}|${item.group}|${item.rival_id}`;
    const found = groups.get(key);
    if (found) found.count += 1;
    else groups.set(key, { item, count: 1 });
  }
  return [...groups.values()].map(({ item, count }) => {
    const info = ACTION_INFO[item.action as CampaignActionKind];
    const noun = `${count} ${lower(count === 1 ? info.noun : info.plural)}`;
    const group = item.group ? lower(GROUP_INFO[item.group].label) : null;
    switch (item.action) {
      case "RALLY":
        return group ? `${noun} para ${group}` : noun;
      case "EVENT":
        return group ? `${noun} com ${group}` : noun;
      case "ATTACK":
        return `${noun} ao ${abbrOf(parties, item.rival_id)}${group ? ` com ${group}` : ""}`;
      default:
        return noun;
    }
  });
}

function allianceLine(item: MilestoneItem, parties: MilestoneContext["parties"]) {
  const partner = abbrOf(parties, item.partner_id);
  return item.title ? `Federação ${item.title} com ${partner}` : `apoiou o ${partner}`;
}

/** As linhas da dica: o que o partido fez no intervalo, uma por promessa, aliança ou grupo de ações iguais. */
export function milestoneLines(milestone: TimelineMilestone, parties: MilestoneContext["parties"]) {
  switch (milestone.kind) {
    case "PROMISE":
      return milestone.items.map((item) => item.title ?? "Promessa");
    case "ALLIANCE":
      return milestone.items.map((item) => allianceLine(item, parties));
    case "CAMPAIGN":
      return campaignLines(milestone.items, parties);
  }
}

function moved(delta: number) {
  if (delta === 0) return "ficou estável";
  return `${delta > 0 ? "subiu" : "caiu"} ${Math.abs(delta)}`;
}

/** Quanto o partido andou na pesquisa seguinte: no país e, nas ações, na região onde o grupo pesa mais. */
export function milestoneEffect(
  abbr: string,
  delta: MarkerDelta | null,
  kind: TimelineMilestone["kind"],
  regionName: string | null,
) {
  if (!delta) return null;
  const parts = [`${moved(delta.national)} no país`];
  if (delta.region && regionName) parts.push(`${moved(delta.region.delta)} no ${regionName}`);
  const where = kind === "CAMPAIGN" && delta.region ? ", onde esse grupo pesa mais" : "";
  return `Na pesquisa seguinte o ${abbr} ${parts.join(" e ")}${where}.`;
}

/** O texto da dica do marco: título, intervalo, lista do que foi feito e a mexida na pesquisa seguinte. */
export function milestoneTip(milestone: TimelineMilestone, context: MilestoneContext): MilestoneTip {
  const abbr = abbrOf(context.parties, milestone.party_id);
  const words = KIND_WORDS[milestone.kind];
  const count = milestone.items.length;
  const before = context.points.find((point) => point.date === milestone.after);
  const after = context.points.find((point) => point.date === milestone.before);
  const region = milestone.region ? context.regions.find((place) => place.code === milestone.region) : undefined;
  const delta = markerDelta(before, after, milestone.party_id, region?.code ?? null, context.regions);
  return {
    title: `${abbr} · ${count} ${count === 1 ? words.one : words.many}`,
    span: `entre ${displayDayMonth(milestone.after)} e ${displayDayMonth(milestone.before)} ${milestone.before.slice(0, 4)}`,
    lines: milestoneLines(milestone, context.parties),
    effect: milestoneEffect(abbr, delta, milestone.kind, region?.name ?? null),
  };
}
