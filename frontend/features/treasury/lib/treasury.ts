import { addDays, differenceInMonths, format, subMonths } from "date-fns";
import {
  displayMoney,
  displayMoneyLarge,
  displayMonthName,
  displayPercent,
  displayRateLabel,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { RateIndex, TreasuryHistoryPoint } from "@/types";

/** A régua do termômetro vai de 0% a 150% de dívida ÷ PIB; passando disso o marcador fica na ponta. */
export const GAUGE_MAX_DEBT = 1.5;

/** As faixas do prêmio, com a dívida ÷ PIB (fração) em que cada uma começa. */
export const PREMIUM_BANDS = [
  { name: "Sem prêmio", from: 0, tone: "success" },
  { name: "Moderado", from: 0.5, tone: "info" },
  { name: "Alto", from: 0.8, tone: "warning" },
  { name: "Crítico", from: 1, tone: "destructive" },
] as const;

/** A cor de cada indexador: Selic azul, Prefixado ciano e IPCA+ violeta, na bolinha e na linha do gráfico. */
export const INDEX_COLORS = {
  SELIC: "var(--chart-1)",
  Prefixado: "var(--chart-7)",
  IPCA: "var(--chart-4)",
} as const;

/** A cor do ponto de cada indexador na tela e nas tabelas. */
export function indexDotClass(rateIndex: RateIndex) {
  if (rateIndex === "SELIC") return "bg-chart-1";
  if (rateIndex === "Prefixado") return "bg-chart-7";
  if (rateIndex === "IPCA") return "bg-chart-4";
  return "bg-muted-foreground";
}

/** Posição (0 a 100) do marcador na régua do termômetro. */
export const gaugePosition = (debt: number) => (Math.min(Math.max(debt, 0), GAUGE_MAX_DEBT) / GAUGE_MAX_DEBT) * 100;

/** Pontos percentuais com vírgula, sem a unidade ("0,0234" → "2,34"); zero vira "0". */
export function pointsOf(fraction: string | number, digits = 2) {
  const points = Number(fraction) * 100;
  return points === 0
    ? "0"
    : points.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

/** A taxa como o Tesouro escreve: "SELIC + 2,44%", "IPCA + 9,45%" e "12,92% ao ano". */
export function treasuryRateLabel(rateIndex: RateIndex, rate: string | number) {
  return rateIndex === "Prefixado" ? `${displayPercent(rate)} ao ano` : displayRateLabel(rateIndex, String(rate));
}

/** A parte base da taxa na legenda da barra: "SELIC + 0,10 base +", "IPCA + 7,11 base +" e "10,58 base +". */
export function baseRateCaption(rateIndex: RateIndex, base: string | number) {
  const points = pointsOf(base);
  return rateIndex === "Prefixado" ? `${points} base +` : `${rateIndex} + ${points} base +`;
}

/** Quanto da taxa é base, de 0 a 100: a barra cinza cobre essa parte e o prêmio ocupa o resto. */
export function baseShare(base: string | number, rate: string | number) {
  const total = Number(rate);
  return total <= 0 ? 100 : (Number(base) / total) * 100;
}

/** "+R$ 6.682,67" ou "−R$ 2.416,42": o sinal sempre aparece, para ganho e perda. */
export function displayGain(value: string | number) {
  const amount = Number(value);
  return `${amount < 0 ? "−" : "+"}${treasuryMoney(Math.abs(amount))}`;
}

/** Reais com centavos até a casa dos milhões; de 100 milhões para cima, na escala curta ("R$ 665,7 mi"). */
export function treasuryMoney(value: string | number) {
  return Math.abs(Number(value)) >= 100_000_000 ? displayMoneyLarge(value) : displayMoney(value);
}

const shortMonth = (date: Date) => new Intl.DateTimeFormat("pt-BR", { month: "short" }).format(date).replace(".", "");

/** "2033-03-01" → "1 mar 2033". */
export function displayDay(iso: string) {
  const date = parseLocalDate(iso);
  return `${date.getDate()} ${shortMonth(date)} ${date.getFullYear()}`;
}

/** "2031-12-31" → "dez 2031". */
export function displayMonthYear(iso: string) {
  const date = parseLocalDate(iso);
  return `${shortMonth(date)} ${date.getFullYear()}`;
}

/** Quanto falta para o vencimento em meses cheios: "2 anos e 5 meses", "7 meses", "1 ano". */
export function termLabel(maturity: string, today: string) {
  const months = Math.max(differenceInMonths(parseLocalDate(maturity), parseLocalDate(today)), 0);
  const years = Math.floor(months / 12);
  const rest = months % 12;
  const yearsText = `${years} ${years === 1 ? "ano" : "anos"}`;
  const monthsText = `${rest} ${rest === 1 ? "mês" : "meses"}`;
  if (years === 0) return monthsText;
  return rest === 0 ? yearsText : `${yearsText} e ${monthsText}`;
}

/** O dia em que as taxas do mês foram fixadas: com a próxima revisão em 1º de novembro, 30 de setembro. */
export function ratesDate(nextReview: string) {
  return addDays(subMonths(parseLocalDate(nextReview), 1), -1);
}

/** O dia das taxas em texto curto: "2030-11-01" → "31 out 2030". */
export const ratesDay = (nextReview: string) => displayDay(format(ratesDate(nextReview), "yyyy-MM-dd"));

/** A revisão acontece no fechamento do mês anterior ao dia da revisão: "2030-11-01" → "outubro". */
export function reviewMonthName(nextReview: string) {
  return displayMonthName(nextReview, -1);
}

/** O título que entra no lugar, sem o prefixo do emissor: "Tesouro Prefixado 2034" → "Prefixado 2034". */
export const shortTitleName = (name: string) => name.replace(/^Tesouro /, "");

/** Percentual sem casas quando é inteiro: 0.15 → "15%", 0.175 → "17,5%". */
export function percentOf(fraction: string | number) {
  const points = Number(fraction) * 100;
  const whole = Math.abs(points - Math.round(points)) < 1e-9;
  return displayPercent(fraction, whole ? 0 : 2, { trim: true });
}

export type HistoryRow = {
  time: number;
  closing: string;
  selic: number;
  prefixed: number | null;
  prefixedName: string | null;
  inflation: number | null;
  inflationName: string | null;
  debt: number | null;
  premium: number;
};

/** A cotação mais curta de cada indexador no mês: o Prefixado e o IPCA+ que o gráfico acompanha. */
const shortest = (point: TreasuryHistoryPoint, rateIndex: RateIndex) =>
  point.quotes
    .filter((quote) => quote.rate_index === rateIndex)
    .sort((a, b) => a.maturity_date.localeCompare(b.maturity_date))[0];

/** Linhas do gráfico: cada ponto é o fechamento do mês anterior ao `month` em que as taxas passaram a valer. */
export function historyRows(points: TreasuryHistoryPoint[]): HistoryRow[] {
  return points.map((point) => {
    const prefixed = shortest(point, "Prefixado");
    const inflation = shortest(point, "IPCA");
    const closing = addDays(parseLocalDate(point.month), -1);
    return {
      time: closing.getTime(),
      closing: format(closing, "yyyy-MM-dd"),
      selic: Number(point.selic),
      prefixed: prefixed?.effective_annual_rate == null ? null : Number(prefixed.effective_annual_rate),
      prefixedName: prefixed ? shortTitleName(prefixed.name) : null,
      inflation: inflation?.effective_annual_rate == null ? null : Number(inflation.effective_annual_rate),
      inflationName: inflation ? shortTitleName(inflation.name) : null,
      debt: point.debt === null ? null : Number(point.debt),
      premium: Number(point.premium),
    };
  });
}

/** O último dia do mês anterior à próxima revisão, quando as taxas novas são fixadas: "2030-11-01" → 31 out 2030. */
export const closingDate = (nextReview: string) => addDays(parseLocalDate(nextReview), -1);

/** "2028-03-31" → "mar/28": o rótulo do fechamento no eixo e na dica do gráfico. */
export function closingLabel(iso: string) {
  const date = parseLocalDate(iso);
  return `${shortMonth(date)}/${String(date.getFullYear()).slice(-2)}`;
}

/** "ponto" até um ponto inteiro e "pontos" acima: 0,12 ponto, 1 ponto, 2,34 pontos. */
export const pointsUnit = (fraction: string | number) => (Math.abs(Number(fraction)) * 100 > 1 ? "pontos" : "ponto");
