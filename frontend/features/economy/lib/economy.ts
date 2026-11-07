import { subMonths } from "date-fns";
import {
  displayMoney,
  displayPercent,
  displayPercentagePoints,
  displayShortMonthYear,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import { isSpending, SPENDING_LABEL } from "@/shared/lib/spending-kinds";
import type { MetricInfo } from "@/shared/lib/metric-info";
import type { EconomyEffect, EconomyLinkEffect, EconomyPanel } from "@/types";
import {
  FISCAL_IMPULSE,
  FISCAL_RISK,
  GDP_GAP,
  GOVERNMENT_SELIC,
  PHILLIPS,
  REAL_RATE_GAP,
  signedPoints,
} from "./economy-metrics";

type EconomyPoint = EconomyPanel["points"][number];
type CopomChange = EconomyPanel["copom_changes"][number];

export type EconomyRange = "all" | "year";

export type EconomyRow = {
  time: number;
  selic: number;
  ipca: number;
  realRate: number;
  target: number;
  /** A faixa da meta: de meta − tolerância até meta + tolerância */
  band: [number, number];
  growth: number;
  unemployment: number;
  /** Só nas partidas com a expansão Governo */
  debt: number | null;
  /** O Ibovespa, em pontos; nulo quando a série não cobre o dia */
  ibovespa: number | null;
  /** A SELIC, o IPCA e o Ibovespa da história, sem as medidas de gasto; nulos sem a expansão Governo */
  storedSelic: number | null;
  storedIpca: number | null;
  storedIbovespa: number | null;
  /** Mudança da SELIC decidida nesse dia, quando houve */
  copom: CopomChange | undefined;
};

const nullable = (value: string | null) => (value === null ? null : Number(value));

/** Os pontos do painel em linhas do gráfico, com a mudança do Copom do dia ligada à linha dele. */
export function economyRows(panel: EconomyPanel, range: EconomyRange = "all"): EconomyRow[] {
  const changeByDate = new Map(panel.copom_changes.map((change) => [change.date, change]));
  const last = panel.points.at(-1);
  const since = range === "year" && last ? subMonths(parseLocalDate(last.date), 12).getTime() : -Infinity;

  return panel.points
    .map((point: EconomyPoint) => ({
      time: parseLocalDate(point.date).getTime(),
      selic: Number(point.selic),
      ipca: Number(point.ipca),
      realRate: Number(point.real_rate),
      target: Number(point.target),
      band: [Number(point.target) - Number(point.tolerance), Number(point.target) + Number(point.tolerance)] as [
        number,
        number,
      ],
      growth: Number(point.growth),
      unemployment: Number(point.unemployment),
      debt: point.debt === null ? null : Number(point.debt),
      ibovespa: nullable(point.ibovespa),
      storedSelic: nullable(point.stored_selic),
      storedIpca: nullable(point.stored_ipca),
      storedIbovespa: nullable(point.stored_ibovespa),
      copom: changeByDate.get(point.date),
    }))
    .filter((row) => row.time >= since);
}

/** "Copom subiu a SELIC em 0,50 p.p., para 14,75%" */
export function copomLabel(change: CopomChange): string {
  const rose = Number(change.change) > 0;
  const size = displayPercentagePoints(Math.abs(Number(change.change))).replace("+", "");
  return `Copom ${rose ? "subiu" : "baixou"} a SELIC em ${size}, para ${displayPercent(change.selic, 2)}`;
}

/** A última mudança da SELIC ("▼ 0,50 p.p. em mar/25"), ou o aviso de que ela ainda não mudou. */
export function lastCopomNote(changes: CopomChange[]): string {
  const last = changes.at(-1);
  if (!last) return "Sem mudança do Copom ainda";
  const arrow = Number(last.change) > 0 ? "▲" : "▼";
  const size = displayPercentagePoints(Math.abs(Number(last.change))).replace("+", "");
  return `${arrow} ${size} em ${displayShortMonthYear(last.date)}`;
}

/** A inflação de 12 meses contra a meta do ano. */
export function targetNote(point: EconomyPoint): string {
  return `meta de ${displayPercent(point.target, 2)}`;
}

/** O que R$ 100 parados na SELIC viram em um ano. */
export function selicExample(point: EconomyPoint): string {
  return `O juro básico: R$ 100 parados nela viram ${displayMoney(100 * (1 + Number(point.selic)))} em um ano.`;
}

/** O que custava R$ 100 há um ano. */
export function ipcaExample(point: EconomyPoint): string {
  return `A inflação: o que custava R$ 100 há um ano custa ${displayMoney(100 * (1 + Number(point.ipca)))}.`;
}

/** Juro real negativo é dinheiro perdendo da inflação. */
export function realRateTone(point: EconomyPoint): "destructive" | "default" {
  return Number(point.real_rate) < 0 ? "destructive" : "default";
}

type MonthlySeries = "growth" | "unemployment";

/** Quanto o número andou no último fechamento de mês: o valor só muda nos fechamentos, então vale a última diferença entre pontos vizinhos. */
export function lastMonthChange(points: EconomyPoint[], key: MonthlySeries): number | null {
  for (let i = points.length - 1; i > 0; i -= 1) {
    const now = points[i]?.[key];
    const before = points[i - 1]?.[key];
    if (now !== undefined && before !== undefined && now !== before) return Number(now) - Number(before);
  }
  return null;
}

const POINTS_FORMAT = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** A diferença entre o primário da partida e o que estabiliza a dívida, em palavras (frações do PIB ao ano). */
export function stabilizingNote(primary: number, stabilizing: number): string {
  const gap = Math.round((stabilizing - primary) * 1000) / 10;
  if (gap === 0) return "O primário segura a dívida onde está.";
  const text = `${POINTS_FORMAT.format(Math.abs(gap))} ${Math.abs(gap) < 2 ? "ponto" : "pontos"} do PIB de primário`;
  return gap > 0 ? `Faltam ${text} para a dívida parar de subir.` : `Sobram ${text}: a dívida cai.`;
}

/** "▲ 0,3 no mês" / "▼ 0,3 no mês" / "estável no mês"; sem fechamento ainda, o aviso de que o mês não fechou. */
export function monthChangeNote(change: number | null): string {
  if (change === null) return "ainda sem fechamento";
  const points = Math.abs(Math.round(change * 1000) / 10);
  if (points === 0) return "estável no mês";
  return `${change > 0 ? "▲" : "▼"} ${POINTS_FORMAT.format(points)} no mês`;
}

/** Desemprego em "de cada 100". */
export function unemploymentExample(point: EconomyPoint): string {
  const per100 = (Number(point.unemployment) * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  return `De cada 100 pessoas que procuram emprego, ${per100} não acham.`;
}

type GrowthParts = EconomyPanel["growth_parts"];

export type GrowthLine = {
  label: string;
  detail: string;
  value: string;
  tone: "up" | "down" | "neutral";
  metric: MetricInfo | null;
};

/** Os textos de uma parcela do crescimento: o que ela é quando empurra, quando freia e quando não mexe. */
type GrowthPartText = { label: string; up: string; down: string; neutral: string; metric?: MetricInfo };

const GROWTH_PARTS: Record<"real_rate" | "stocks" | "works" | "impulse", GrowthPartText> = {
  real_rate: {
    label: "Juro real",
    up: "Abaixo do da história: crédito mais barato empurra",
    down: "Acima do da história: crédito mais caro freia",
    neutral: "Igual ao da história",
  },
  stocks: {
    label: "Bolsa",
    up: "Acima da história: empresas investem mais",
    down: "Abaixo da história: empresas investem menos",
    neutral: "Igual à da história",
  },
  works: {
    label: "Obras",
    up: "O gasto com obras aquece a economia",
    down: "O corte de obras esfria a economia",
    neutral: "Sem obras a mais nem a menos",
  },
  impulse: {
    label: "Impulso fiscal",
    up: "O governo passou a gastar mais ou cobrar menos em 12 meses",
    down: "O governo apertou as contas em 12 meses",
    neutral: "As contas do governo no mesmo patamar de 12 meses atrás",
    metric: FISCAL_IMPULSE,
  },
};

/** O que a partida somou ao crescimento da história, parcela por parcela, com o motivo de cada uma. */
export function growthLines(parts: GrowthParts): GrowthLine[] {
  return (["real_rate", "stocks", "works", "impulse"] as const).map((key) => {
    const text = GROWTH_PARTS[key];
    const part = Number(parts[key]);
    const tone = Math.abs(part) < 0.0005 ? "neutral" : part > 0 ? "up" : "down";
    return { label: text.label, detail: text[tone], value: signedPoints(part), tone, metric: text.metric ?? null };
  });
}

const DAYS_PER_MONTH = 30.4375;
const DAY_MS = 86_400_000;

/** O quanto cada efeito soma à inflação em `time`, em pontos de IPCA: a curva da medida no mês que já correu desde que ela valeu. */
export function effectShares(
  effects: readonly EconomyEffect[],
  time: number,
): { kind: EconomyEffect["kind"]; label: string; points: number }[] {
  return effects
    .map((effect) => {
      const month = Math.floor((time - parseLocalDate(effect.effective).getTime()) / DAY_MS / DAYS_PER_MONTH);
      const points = month < 0 ? 0 : Number(effect.curve[month] ?? 0);
      return { kind: effect.kind, label: effectLabel(effect), points };
    })
    .filter((share) => Math.abs(share.points) >= 0.005)
    .sort((a, b) => Math.abs(b.points) - Math.abs(a.points));
}

/** O nome curto do efeito: o tipo da medida, sem o "de A para B". */
const effectLabel = (effect: Pick<EconomyEffect, "kind">) =>
  isSpending(effect.kind) ? SPENDING_LABEL[effect.kind] : effect.kind;

/** A soma de um campo dos efeitos ativos, de medidas ou de ligações (pontos de IPCA ou de SELIC). */
export const sumEffects = (
  effects: readonly Pick<EconomyEffect, "inflation" | "selic">[],
  key: "inflation" | "selic",
) => effects.reduce((sum, effect) => sum + Number(effect[key]), 0);

/** A métrica de cada ligação: o rótulo, a dica e o formato do desvio contra a história. */
export const LINK_METRIC: Record<EconomyLinkEffect["link"], MetricInfo> = {
  PHILLIPS,
  FISCAL_RISK,
  GDP: GDP_GAP,
  REAL_RATE: REAL_RATE_GAP,
  SELIC: GOVERNMENT_SELIC,
};

/** As ligações que mexem em algo hoje: as outras somam menos que a última casa mostrada. */
export const activeLinks = (links: readonly EconomyLinkEffect[]) =>
  links.filter((link) => Math.abs(Number(link.inflation)) >= 0.005 || Math.abs(Number(link.stocks)) >= 0.0005);

/** A SELIC é do governo quando a ligação dela aparece: só existe com a taxa decidida no Copom. */
export const selicByGovernment = (links: readonly EconomyLinkEffect[]) => links.some((link) => link.link === "SELIC");

export type InflationPart = { key: string; label: string; points: number };

/** O IPCA de hoje aberto por tipo de medida e por ligação: o que cada um soma ou tira, do maior ao menor. */
export function inflationBreakdown(
  effects: readonly EconomyEffect[],
  links: readonly EconomyLinkEffect[] = [],
): InflationPart[] {
  const byKind = new Map<EconomyEffect["kind"], number>();
  for (const effect of effects) byKind.set(effect.kind, (byKind.get(effect.kind) ?? 0) + Number(effect.inflation));
  const measures = [...byKind].map(([kind, points]) => ({ key: kind, label: effectLabel({ kind }), points }));
  const fromLinks = links.map((link) => ({
    key: link.link,
    label: LINK_METRIC[link.link].label,
    points: Number(link.inflation),
  }));
  return [...measures, ...fromLinks]
    .filter((part) => Math.abs(part.points) >= 0.005)
    .sort((a, b) => b.points - a.points);
}

/** O quanto o governo mexe numa série hoje, em pontos: a partida menos a história; nulo sem a expansão Governo. */
export function governmentShift(value: string, stored: string | null): number | null {
  if (stored === null) return null;
  return (Number(value) - Number(stored)) * 100;
}

/** O quanto a bolsa anda por causa do governo: o Ibovespa da partida contra o da história (−0.039 = 3,9% abaixo). */
export function stocksEffect(point: EconomyPoint): number | null {
  if (point.ibovespa === null || point.stored_ibovespa === null || Number(point.stored_ibovespa) === 0) return null;
  return Number(point.ibovespa) / Number(point.stored_ibovespa) - 1;
}
