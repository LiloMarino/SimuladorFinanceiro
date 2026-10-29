import { subMonths } from "date-fns";
import {
  displayMoney,
  displayPercent,
  displayPercentagePoints,
  displayShortMonthYear,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import { isSpending, SPENDING_LABEL } from "@/shared/lib/spending-kinds";
import type { EconomyEffect, EconomyPanel } from "@/types";

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

/** Fração em pontos percentuais com uma casa e o menos tipográfico (0.011 → "+1,1", −0.009 → "−0,9"). */
export function signedPoints(fraction: number) {
  const points = Math.round(fraction * 1000) / 10;
  if (points === 0) return POINTS_FORMAT.format(0);
  return `${points < 0 ? "−" : "+"}${POINTS_FORMAT.format(Math.abs(points))}`;
}

/** "▲ 0,3 no mês" / "▼ 0,3 no mês" / "estável no mês"; sem fechamento ainda, o aviso de que o mês não fechou. */
export function monthChangeNote(change: number | null): string {
  if (change === null) return "ainda sem fechamento";
  const points = Math.abs(Math.round(change * 1000) / 10);
  if (points === 0) return "estável no mês";
  return `${change > 0 ? "▲" : "▼"} ${POINTS_FORMAT.format(points)} no mês`;
}

/** Onde o crescimento mora hoje, contra a tendência. */
export function growthExample(trend: string): string {
  return `Quanto a economia cresceu em 12 meses. A tendência é ${displayPercent(trend, 0)}.`;
}

/** Desemprego em "de cada 100". */
export function unemploymentExample(point: EconomyPoint): string {
  const per100 = (Number(point.unemployment) * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  return `De cada 100 pessoas que procuram emprego, ${per100} não acham.`;
}

type GrowthParts = EconomyPanel["growth_parts"];

export type GrowthLine = {
  label: string;
  detail: string | null;
  value: string;
  tone: "up" | "down" | "neutral";
};

function lineTone(part: number): GrowthLine["tone"] {
  if (part > 0) return "up";
  return part < 0 ? "down" : "neutral";
}

/** As três partes que somam o alvo do crescimento, com o motivo de cada uma. */
export function growthLines(parts: GrowthParts): GrowthLine[] {
  const realRatePart = Number(parts.real_rate_part);
  const stocksPart = Number(parts.stocks_part);
  const realRate = Number(parts.real_rate);
  const neutral = Number(parts.neutral_real_rate);
  const cheapCredit = realRate < neutral;

  return [
    { label: "Tendência da economia", detail: null, value: signedPoints(Number(parts.trend)), tone: "neutral" },
    {
      label: `Juro real ${cheapCredit ? "abaixo" : "acima"} do neutro`,
      detail: `${displayPercent(realRate, 2)} contra ${displayPercent(neutral, 0)}: ${
        cheapCredit ? "crédito barato empurra" : "crédito caro freia"
      }`,
      value: signedPoints(realRatePart),
      tone: lineTone(realRatePart),
    },
    {
      label: "Bolsa em 12 meses",
      detail:
        parts.stocks === null
          ? "Sem série da bolsa nesse período: não empurra nem freia"
          : `Ibovespa ${signedPercent(Number(parts.stocks))}: empresas investem ${stocksPart >= 0 ? "mais" : "menos"}`,
      value: signedPoints(stocksPart),
      tone: lineTone(stocksPart),
    },
  ];
}

/** "+3%" / "−17%", sem casas. */
function signedPercent(fraction: number) {
  const percent = Math.round(fraction * 100);
  return `${percent < 0 ? "−" : "+"}${Math.abs(percent)}%`;
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
export const effectLabel = (effect: Pick<EconomyEffect, "kind">) =>
  isSpending(effect.kind) ? SPENDING_LABEL[effect.kind] : effect.kind;

/** A soma de um campo dos efeitos ativos (pontos de IPCA ou de SELIC). */
export const sumEffects = (effects: readonly EconomyEffect[], key: "inflation" | "selic") =>
  effects.reduce((sum, effect) => sum + Number(effect[key]), 0);

export type InflationPart = { kind: EconomyEffect["kind"]; label: string; points: number };

/** O IPCA de hoje aberto por tipo de medida: o que a história já trazia e o que cada tipo soma ou tira, do maior ao menor. */
export function inflationBreakdown(effects: readonly EconomyEffect[]): InflationPart[] {
  const byKind = new Map<EconomyEffect["kind"], number>();
  for (const effect of effects) byKind.set(effect.kind, (byKind.get(effect.kind) ?? 0) + Number(effect.inflation));
  return [...byKind]
    .map(([kind, points]) => ({ kind, label: effectLabel({ kind }), points }))
    .filter((part) => Math.abs(part.points) >= 0.005)
    .sort((a, b) => b.points - a.points);
}

/** O quanto a bolsa anda por causa das medidas: o Ibovespa da partida contra o da história (−0.039 = 3,9% abaixo). */
export function stocksEffect(point: EconomyPoint): number | null {
  if (point.ibovespa === null || point.stored_ibovespa === null || Number(point.stored_ibovespa) === 0) return null;
  return Number(point.ibovespa) / Number(point.stored_ibovespa) - 1;
}
