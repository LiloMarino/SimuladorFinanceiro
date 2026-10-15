/**
 * display.ts
 * ------------
 * Funções de exibição (display*) — recebem valores já processados e retornam
 * strings prontas para serem mostradas na UI (ex: "R$ 1.200,00").
 *
 * Dinheiro, quantidades e taxas da API chegam como string decimal ("1234.567891")
 * e são formatados direto pelo Intl, que trata a string como decimal exato. Preços
 * de ação chegam como number, porque a própria fonte deles é float.
 */

import type { RateIndex } from "@/types";

type Numeric = string | number;

const MONEY_FORMAT = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  minimumFractionDigits: 2,
});

const MONEY_COMPACT_FORMAT = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  notation: "compact",
  maximumFractionDigits: 1,
});

export function displayMoney(value: Numeric) {
  return MONEY_FORMAT.format(value as Intl.StringNumericLiteral | number);
}

export function displayMoneyCompact(value: Numeric): string {
  return MONEY_COMPACT_FORMAT.format(value as Intl.StringNumericLiteral | number);
}

export function displayPercent(value: Numeric, digits = 2) {
  return new Intl.NumberFormat("pt-BR", {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value as Intl.StringNumericLiteral | number);
}

/** Diferença em pontos percentuais com sinal (0.041 → "+4,10 p.p."). */
export function displayPercentagePoints(fraction: Numeric, digits = 2) {
  const points = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    signDisplay: "exceptZero",
  }).format(Number(fraction) * 100);
  return `${points} p.p.`;
}

/** Percentual com sinal explícito (0.0141 → "+1,41%"), para variações. */
export function displaySignedPercent(value: Numeric, digits = 2) {
  return new Intl.NumberFormat("pt-BR", {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    signDisplay: "exceptZero",
  }).format(value as Intl.StringNumericLiteral | number);
}

/** Número curto com sufixo pt-BR (48200000 → "48,2 mi"), para volumes. */
export function displayCompactNumber(value: Numeric) {
  return new Intl.NumberFormat("pt-BR", { notation: "compact", maximumFractionDigits: 1 }).format(
    value as Intl.StringNumericLiteral | number,
  );
}

/** Número com casas fixas, lido da string decimal ("0.5432" → "0,54"). */
export function displayNumber(value: Numeric, digits = 2) {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value as Intl.StringNumericLiteral | number);
}

/** Número em pt-BR, sem separador de milhar (0.02 → "0,02"). */
export function displayDecimal(value: number) {
  return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 6, useGrouping: false }).format(value);
}

/** Valor em reais com 2 casas, sem separador de milhar ("1234.56"), truncado. */
export function toCentsString(value: string) {
  return new Intl.NumberFormat("en-US", {
    useGrouping: false,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    roundingMode: "trunc",
  }).format(value as Intl.StringNumericLiteral);
}

/** Valor negativo? Lê o sinal direto da string decimal. */
export function isLoss(value: string) {
  return value.trim().startsWith("-");
}

/** Taxa do título como o mercado escreve: "110,00% do CDI", "IPCA + 6,00%", "12,00% a.a.". */
export function displayRateLabel(rateIndex: RateIndex, interestRate: string) {
  switch (rateIndex) {
    case "CDI":
      return `${displayPercent(interestRate)} do CDI`;
    case "IPCA":
      return `IPCA + ${displayPercent(interestRate)}`;
    case "SELIC":
      return `SELIC + ${displayPercent(interestRate)}`;
    case "Prefixado":
      return `${displayPercent(interestRate)} a.a.`;
  }
}

/** "2020-01-02" como meia-noite local: `new Date` leria UTC e voltaria um dia no Brasil. */
export function parseLocalDate(isoDate: string): Date {
  const [year, month, day] = isoDate.split("-").map(Number);
  return new Date(year, month - 1, day);
}

export function displayDate(date: Date | string) {
  const d = typeof date === "string" ? new Date(date) : date;

  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(d);
}

/** "2023-03-14" → "14 mar 2023", a data curta do topo. */
export function displayShortDate(date: Date | string) {
  const parts = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" }).formatToParts(
    typeof date === "string" ? parseLocalDate(date) : date,
  );
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value.replace(".", "") ?? "";
  return `${part("day")} ${part("month")} ${part("year")}`;
}

/** "2023-03-14" → "mar/2023", o período compacto de listas. */
export function displayMonthSlashYear(isoDate: string) {
  const d = parseLocalDate(isoDate);
  const month = new Intl.DateTimeFormat("pt-BR", { month: "short" }).format(d).replace(".", "");
  return `${month}/${d.getFullYear()}`;
}

/** "2022-04-01" → "abr/22", o mês curto de eixos e legendas. */
export function displayShortMonthYear(value: Date | string) {
  const d = typeof value === "string" ? parseLocalDate(value) : value;
  const month = new Intl.DateTimeFormat("pt-BR", { month: "short" }).format(d).replace(".", "");
  return `${month}/${String(d.getFullYear()).slice(-2)}`;
}

/** Só o mês curto ("abr"), para colunas em que o ano aparece uma vez. */
export function displayMonthShort(isoDate: string) {
  return new Intl.DateTimeFormat("pt-BR", { month: "short" }).format(parseLocalDate(isoDate)).replace(".", "");
}

export function displayMonthYear(date: Date | string) {
  const d = typeof date === "string" ? new Date(date) : date;

  return new Intl.DateTimeFormat("pt-BR", {
    month: "short",
    year: "numeric",
  }).format(d);
}

/** ["Ana", "Bia", "Lilo"] → "Ana, Bia e Lilo". */
export function displayList(items: string[]) {
  return new Intl.ListFormat("pt-BR", { style: "long", type: "conjunction" }).format(items);
}
