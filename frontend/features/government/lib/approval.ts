import { addDays, addMonths, format, startOfMonth, subMonths } from "date-fns";
import { displayList, displayMonthShort, parseLocalDate } from "@/shared/lib/utils/display";
import type { GovernmentApproval, GovernmentPanel, VoterGroup } from "@/types";
import { GROUP_INFO } from "./voters";

const MINUS = "−";

export type GroupApproval = GovernmentApproval["groups"][number];
export type GroupVerdict = GroupApproval["verdict"];
export type ApprovalFactor = GroupApproval["factors"][number];

/** Quanto da distância até o alvo a satisfação anda a cada fechamento de mês. */
const MONTH_STEP = 1 / 3;

/** Quantos fechamentos à frente o gráfico projeta. */
export const PROJECTED_MONTHS = 4;

/** A linha do gráfico e da lista que representa o total do eleitorado. */
export const ALL_GROUPS = "ALL";
export type Selection = VoterGroup | typeof ALL_GROUPS;

export const VERDICT_BADGE: Record<GroupVerdict, { label: string; variant: "success" | "secondary" | "destructive" }> =
  {
    APPROVES: { label: "Aprova", variant: "success" },
    NEUTRAL: { label: "Neutro", variant: "secondary" },
    REPROVES: { label: "Reprova", variant: "destructive" },
  };

/** Cor da barra e do número de cada veredito; classes literais para o Tailwind enxergar. */
export const VERDICT_FILL: Record<GroupVerdict, string> = {
  APPROVES: "bg-success",
  NEUTRAL: "bg-muted-foreground/60",
  REPROVES: "bg-destructive",
};

type Thresholds = Pick<GovernmentApproval, "approves_above" | "reproves_below">;

/** O veredito de uma satisfação: acima da faixa neutra aprova, abaixo reprova. */
export function verdictOf(satisfaction: number, thresholds: Thresholds): GroupVerdict {
  if (satisfaction > thresholds.approves_above) return "APPROVES";
  if (satisfaction < thresholds.reproves_below) return "REPROVES";
  return "NEUTRAL";
}

/** Pontos de um fator com uma casa e o menos tipográfico: "4.0" → "+4", "-6.5" → "−6,5". */
export function signedFactor(points: string) {
  const value = Number(points);
  if (value === 0) return "0";
  const text = Math.abs(value).toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  return `${value > 0 ? "+" : MINUS}${text}`;
}

/** O ponto neutro (BASE) não leva sinal: é de onde a soma parte. */
export function factorPoints(factor: ApprovalFactor) {
  return factor.kind === "BASE" ? String(Number(factor.points)) : signedFactor(factor.points);
}

export type Trend = "rising" | "falling" | "steady";

/** Para onde a satisfação anda se nada mudar. */
export function trendOf(satisfaction: number, target: number): Trend {
  if (target > satisfaction) return "rising";
  if (target < satisfaction) return "falling";
  return "steady";
}

export const TREND_LABEL: Record<Trend, string> = { rising: "subindo", falling: "caindo", steady: "estável" };

/** O tom da tendência: subir é bom, cair pede atenção. */
export const TREND_VARIANT: Record<Trend, "success" | "warning" | "secondary"> = {
  rising: "success",
  falling: "warning",
  steady: "secondary",
};

/** Seta até o alvo: "▼ 33" se cai, "▲ 55" se sobe, "= 63" se fica. */
export function targetArrow(satisfaction: number, target: number) {
  const trend = trendOf(satisfaction, target);
  if (trend === "steady") return `= ${target}`;
  return `${trend === "rising" ? "▲" : "▼"} ${target}`;
}

/** Variação desde o fechamento anterior: "▼ 2" ou "▲ 3"; vazio se nada mudou. */
export function deltaLabel(value: number, previous: number | null) {
  if (previous === null || previous === value) return "";
  return `${value > previous ? "▲" : "▼"} ${Math.abs(value - previous)}`;
}

/** A satisfação nos próximos fechamentos, andando um terço do caminho até o alvo a cada mês. */
export function projection(satisfaction: number, target: number, months = PROJECTED_MONTHS) {
  const path: number[] = [];
  let current = satisfaction;
  for (let month = 0; month < months; month += 1) {
    current += (target - current) * MONTH_STEP;
    path.push(current);
  }
  return path;
}

/** "Hoje 37, depois 36, 35 e 34": a trajetória em frase. */
export function projectionSentence(satisfaction: number, target: number) {
  const next = projection(satisfaction, target, 3).map(Math.round);
  return `hoje ${satisfaction}, depois ${displayList(next.map(String))}`;
}

/** Os dias de fechamento à frente: o próximo é `closes_on` e os seguintes caem nos meses seguintes. */
function upcomingClosings(approval: Pick<GovernmentApproval, "closes_on">, count: number) {
  const first = startOfMonth(parseLocalDate(approval.closes_on));
  return Array.from({ length: count }, (_, index) => format(addMonths(first, index), "yyyy-MM-dd"));
}

/** Os meses (curtos) dos fechamentos que formam a contagem do impeachment. */
export function streakMonths(approval: Pick<GovernmentApproval, "history" | "low_streak">) {
  if (approval.low_streak === 0) return [];
  return approval.history.slice(-approval.low_streak).map((point) => displayMonthShort(point.date));
}

/** Quantos fechamentos abaixo do piso ainda faltam para o impeachment. */
export function closingsLeft(approval: Pick<GovernmentApproval, "low_streak" | "impeachment_months">) {
  return Math.max(0, approval.impeachment_months - approval.low_streak);
}

/** "set, out e nov": os meses dos próximos fechamentos que faltam. */
export function remainingMonths(approval: Pick<GovernmentApproval, "closes_on" | "low_streak" | "impeachment_months">) {
  return displayList(upcomingClosings(approval, closingsLeft(approval)).map(displayMonthShort));
}

/** O dia em que o governo seguinte toma posse: o dia depois do fim do mandato. */
function nextTermStart(termEnd: string | null) {
  return termEnd ? format(addDays(parseLocalDate(termEnd), 1), "yyyy-MM-dd") : null;
}

/** Quantos grupos aprovaram, ficaram neutros e reprovaram em cada ponto do histórico. */
export function verdictCounts(approval: GovernmentApproval, date: string) {
  const counts: Record<GroupVerdict, number> = { APPROVES: 0, NEUTRAL: 0, REPROVES: 0 };
  for (const group of approval.groups) {
    const point = group.history.find((item) => item.date === date);
    if (point) counts[verdictOf(point.value, approval)] += 1;
  }
  return counts;
}

/** "4 grupos aprovaram, 1 neutro, 1 reprovou": o fechamento do mês em uma frase. */
export function verdictCountsSentence(counts: Record<GroupVerdict, number>) {
  const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;
  return [
    plural(counts.APPROVES, "grupo aprovou", "grupos aprovaram"),
    plural(counts.NEUTRAL, "neutro", "neutros"),
    plural(counts.REPROVES, "reprovou", "reprovaram"),
  ].join(", ");
}

/** Os grupos em texto corrido, no início da frase: "Carteira, auxílio e servidores". */
export function groupsSentence(groups: VoterGroup[]) {
  const names = displayList(groups.map((group) => GROUP_INFO[group].short.toLowerCase()));
  return names.charAt(0).toUpperCase() + names.slice(1);
}

/** O nome do grupo, ou "Geral" para o total do eleitorado. */
export function selectionLabel(selection: Selection) {
  return selection === ALL_GROUPS ? "Geral" : GROUP_INFO[selection].label;
}

/** A aprovação geral e a satisfação de cada grupo, na mesma forma, para a lista e o gráfico. */
export function selectedSeries(approval: GovernmentApproval, selection: Selection) {
  if (selection === ALL_GROUPS) {
    return {
      value: approval.value,
      previous: approval.previous,
      target: approval.target,
      history: approval.history,
    };
  }
  const group = approval.groups.find((item) => item.group === selection) ?? approval.groups[0];
  return {
    value: group?.satisfaction ?? approval.value,
    previous: group?.previous ?? null,
    target: group?.target ?? approval.target,
    history: group?.history ?? approval.history,
  };
}

/** Os grupos aprovados do aviso do mês, para os filiados do partido do governo. */
export function closingSentence(
  partyAbbr: string,
  closing: { approved: VoterGroup[]; reproved: VoterGroup[]; neutral: VoterGroup[] },
) {
  const parts: string[] = [];
  if (closing.approved.length > 0) {
    parts.push(`${groupsSentence(closing.approved)} aprovaram: o apoio do ${partyAbbr} subiu neles.`);
  }
  if (closing.reproved.length > 0) {
    parts.push(`${groupsSentence(closing.reproved)} reprovaram: a rejeição do ${partyAbbr} subiu.`);
  }
  if (closing.neutral.length > 0) {
    parts.push(`${groupsSentence(closing.neutral)} ficaram neutros.`);
  }
  return parts.join(" ");
}

/** O governo sem presidente congela os grupos; o card diz até quando. */
export function neutralGovernmentSentence(panel: Pick<GovernmentPanel, "term_end">) {
  const start = nextTermStart(panel.term_end);
  return start
    ? `Sem presidente, ninguém é aprovado nem reprovado: os grupos ficam onde estavam e nenhum partido ganha apoio ou rejeição até a posse de ${displayMonthShort(start)} ${parseLocalDate(start).getFullYear()}.`
    : "Sem presidente, ninguém é aprovado nem reprovado: os grupos ficam onde estavam e nenhum partido ganha apoio ou rejeição.";
}

/** "jun a nov 2021": os `count` meses até o mês de `last`; o ano aparece em cada ponta só se mudar. */
export function monthsSpan(last: string, count: number) {
  const end = parseLocalDate(last);
  const start = subMonths(startOfMonth(end), count - 1);
  const label = (day: Date) => displayMonthShort(format(day, "yyyy-MM-dd"));
  return start.getFullYear() === end.getFullYear()
    ? `${label(start)} a ${label(end)} ${end.getFullYear()}`
    : `${label(start)} ${start.getFullYear()} a ${label(end)} ${end.getFullYear()}`;
}
