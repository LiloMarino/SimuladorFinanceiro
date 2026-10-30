import type { ElectionParty, ElectionPoll, ElectorateRow, VoterGroup, VoterGroupInfo, VoterValue } from "@/types";

export const GROUP_INFO: Record<VoterGroup, { label: string; short: string }> = {
  INVESTORS: { label: "Investidores", short: "Investidores" },
  ENTREPRENEURS: { label: "Empreendedores", short: "Empreendedores" },
  FORMAL_WORKERS: { label: "Trabalhadores com carteira", short: "Carteira" },
  PUBLIC_SERVANTS: { label: "Servidores", short: "Servidores" },
  RETIREES: { label: "Aposentados", short: "Aposentados" },
  WELFARE: { label: "Quem depende de auxílio", short: "Auxílio" },
};

export const READING_LABEL: Record<VoterGroupInfo["readings"][number], string> = {
  INFLATION: "inflação",
  SELIC: "SELIC",
  STOCKS: "Ibovespa",
  CAPITAL_GAINS_TAX: "imposto",
  UNEMPLOYMENT: "desemprego",
  RISK_PREMIUM: "prêmio de risco",
};

/** A pontuação de cada valor, da lista da API para um mapa. */
export function valueScores(scores: { value: VoterValue; score: string }[]) {
  return Object.fromEntries(scores.map((item) => [item.value, Number(item.score)])) as Record<VoterValue, number>;
}

/** A pontuação de cada grupo, da lista da API para um mapa. */
export function groupScores(scores: { group: VoterGroup; score: string }[]) {
  return Object.fromEntries(scores.map((item) => [item.group, Number(item.score)])) as Record<VoterGroup, number>;
}

/** A afinidade com que o partido nasce em cada grupo: a base mais o que cada bandeira soma. */
export function foundingAffinity(group: VoterGroupInfo, flags: VoterValue[], base: number) {
  const perFlag = valueScores(group.flag_affinity);
  return Math.max(0, base + flags.reduce((sum, flag) => sum + perFlag[flag], 0));
}

/** Os grupos que mais gostam do valor (querem 75 ou mais), do que mais quer ao que menos. */
export function pleasedBy(groups: VoterGroupInfo[], value: VoterValue) {
  return groups
    .map((group) => ({ group: group.group, wants: valueScores(group.wants)[value] }))
    .filter((item) => item.wants >= 75)
    .sort((a, b) => b.wants - a.wants)
    .map((item) => item.group);
}

/** Os valores que o grupo mais quer, até dois, do mais querido ao menos. */
export function topWants(group: VoterGroupInfo, count = 2) {
  return [...group.wants]
    .filter((item) => Number(item.score) >= 75)
    .sort((a, b) => Number(b.score) - Number(a.score))
    .slice(0, count)
    .map((item) => item.value);
}

/** "Investidores, empreendedores": a lista de grupos em texto corrido. */
export function groupList(groups: VoterGroup[]) {
  return groups
    .map((group, index) => (index === 0 ? GROUP_INFO[group].short : GROUP_INFO[group].short.toLowerCase()))
    .join(", ");
}

/** A faixa onde o número real está, dado o publicado e a margem. */
export function marginRange(points: number, margin: number): [number, number] {
  return [Math.max(0, points - margin), Math.min(100, points + margin)];
}

/**
 * Empate técnico: as faixas de dois partidos se cobrem, ou seja, a distância entre eles é de até duas
 * margens. Com margem zero, só o empate exato.
 */
export function inTechnicalTie(points: number, others: number[], margin: number) {
  return margin > 0 && others.some((other) => Math.abs(points - other) <= 2 * margin);
}

/** Os pontos de cada partido numa pesquisa, por id. */
export function pollPoints(entries: ElectionPoll["entries"]) {
  return new Map(entries.map((entry) => [entry.party_id, Number(entry.points)]));
}

/** Quão perto o perfil do partido está do que o grupo quer num valor, em palavras. */
export function distanceWord(wants: number, profile: number) {
  const gap = Math.abs(wants - profile);
  if (gap <= 20) return { word: "perto", tone: "up" as const };
  if (gap <= 45) return { word: "meio", tone: "wa" as const };
  return { word: "longe", tone: "dn" as const };
}

/** O partido de cada linha da pesquisa ou do eleitorado, na ordem da página. */
export function partyOrder(parties: ElectionParty[]) {
  return [...parties].sort((a, b) => Number(b.intention_points) - Number(a.intention_points) || a.id - b.id);
}

/** A cor do partido nos gráficos; o do computador, sem cor própria, fica cinza. */
export const partyFill = (party: Pick<ElectionParty, "color">) => party.color ?? "var(--muted-foreground)";

export type GroupSort = "weight" | "balance";

/** As linhas do eleitorado, do maior grupo ao menor ou do melhor saldo ao pior. */
export function sortElectorate(rows: ElectorateRow[], groups: VoterGroupInfo[], sort: GroupSort) {
  const weight = new Map(groups.map((group) => [group.group, Number(group.weight)]));
  const key = (row: ElectorateRow) =>
    sort === "weight" ? (weight.get(row.group) ?? 0) : Number(row.support) - Number(row.rejection);
  return [...rows].sort((a, b) => key(b) - key(a));
}

/** O dia 1º do mês seguinte a `today`: quando sai a próxima pesquisa. */
export function nextPollDate(today: string) {
  const [year = 0, month = 1] = today.split("-").map(Number);
  const next = new Date(year, month, 1);
  return `${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, "0")}-01`;
}

/** Pontos da pesquisa como porcentagem: inteiros quando há margem (o decimal está dentro do erro), uma casa sem ela. */
export function pollPercent(points: number, margin: number) {
  return `${points.toLocaleString("pt-BR", { maximumFractionDigits: margin > 0 ? 0 : 1 })}%`;
}

/** "+24", "−7" ou "0": pontos com sinal, sem casas. */
export function signedPoints(value: number) {
  const rounded = Math.round(value);
  const sign = rounded > 0 ? "+" : rounded < 0 ? "−" : "";
  return `${sign}${Math.abs(rounded).toLocaleString("pt-BR")}`;
}
