import type { ReturnSources } from "@/types";

type SourceKey = keyof ReturnSources;

interface SourceInfo {
  key: SourceKey;
  label: string;
  note: string;
  /** Classe de fundo da barra; o custo usa o tom de perda. */
  bar: string;
  /** Aparece só quando o jogador teve esse fluxo. */
  optional: boolean;
}

/** As seis origens do retorno, na ordem em que a cascata soma. */
const SOURCE_INFO: SourceInfo[] = [
  {
    key: "appreciation",
    label: "Valorização das ações, FIIs e cripto",
    note: "realizada e em aberto, pelos preços em que suas ordens executaram",
    bar: "bg-chart-1",
    optional: false,
  },
  {
    key: "dividends",
    label: "Proventos",
    note: "dividendos e rendimentos de FII, isentos",
    bar: "bg-dividend-bar",
    optional: false,
  },
  {
    key: "fixed_income_interest",
    label: "Juro da renda fixa",
    note: "Tesouro e CDB, antes do IR",
    bar: "bg-chart-2",
    optional: false,
  },
  {
    key: "taxes",
    label: "Imposto de renda pago",
    note: "vendas com lucro e resgates",
    bar: "bg-destructive",
    optional: false,
  },
  {
    key: "debt_interest",
    label: "Juro de dívida",
    note: "empréstimo e cheque especial",
    bar: "bg-destructive",
    optional: true,
  },
  {
    key: "campaign",
    label: "Gastos de campanha",
    note: "doações e ações de campanha",
    bar: "bg-destructive",
    optional: true,
  },
];

interface WaterfallRow extends SourceInfo {
  value: number;
  /** Onde a barra começa e termina na cascata: o acumulado antes e depois desta parcela. */
  start: number;
  end: number;
}

export interface Waterfall {
  rows: WaterfallRow[];
  total: number;
  /** Menor e maior acumulado da cascata (o zero conta), que definem a escala das barras. */
  min: number;
  max: number;
}

/** A cascata do retorno: cada parcela começa onde a anterior terminou, e o último acumulado é o retorno da partida. */
export function buildWaterfall(sources: ReturnSources): Waterfall {
  let running = 0;
  let min = 0;
  let max = 0;
  const rows: WaterfallRow[] = [];
  for (const info of SOURCE_INFO) {
    const value = Number(sources[info.key]);
    if (info.optional && value === 0) continue;
    const start = running;
    running += value;
    min = Math.min(min, start, running);
    max = Math.max(max, start, running);
    rows.push({ ...info, value, start, end: running });
  }
  return { rows, total: running, min, max };
}

/** A parte de uma parcela no retorno da partida; sem retorno positivo a fatia não faz sentido. */
export function shareOfReturn(value: number, total: number): number | null {
  return total > 0 ? value / total : null;
}

export type PlayerGroupKey = "appreciation" | "dividends" | "fixed_income_interest" | "costs";

export const PLAYER_GROUPS: { key: PlayerGroupKey; bar: string }[] = [
  { key: "appreciation", bar: "bg-chart-1" },
  { key: "dividends", bar: "bg-dividend-bar" },
  { key: "fixed_income_interest", bar: "bg-chart-2" },
  { key: "costs", bar: "bg-destructive" },
];

export interface PlayerSourcePoint {
  key: PlayerGroupKey;
  bar: string;
  /** Pontos do retorno: a parcela dividida pelo aporte, como fração (0,056 = 5,6 pontos). */
  points: number;
}

/** As parcelas de um jogador em pontos do retorno, com imposto, juro de dívida e campanha juntos no custo. */
export function playerPoints(sources: ReturnSources, capital: number): PlayerSourcePoint[] | null {
  if (capital <= 0) return null;
  const amounts: Record<PlayerGroupKey, number> = {
    appreciation: Number(sources.appreciation),
    dividends: Number(sources.dividends),
    fixed_income_interest: Number(sources.fixed_income_interest),
    costs: Number(sources.taxes) + Number(sources.debt_interest) + Number(sources.campaign),
  };
  return PLAYER_GROUPS.map(({ key, bar }) => ({ key, bar, points: amounts[key] / capital }));
}

export interface Segment {
  point: PlayerSourcePoint;
  /** Posição e largura em % da faixa; o zero fica em `zero`. */
  start: number;
  width: number;
}

/** Os segmentos de um jogador: os positivos empilham para a direita do zero e os negativos para a esquerda. */
export function segmentLayout(points: PlayerSourcePoint[], span: number, zero: number): Segment[] {
  let positive = zero;
  let negative = zero;
  const segments: Segment[] = [];
  for (const point of points) {
    const width = (Math.abs(point.points) / span) * 100;
    if (width === 0) continue;
    if (point.points > 0) {
      segments.push({ point, start: positive, width });
      positive += width;
    } else {
      negative -= width;
      segments.push({ point, start: negative, width });
    }
  }
  return segments;
}
