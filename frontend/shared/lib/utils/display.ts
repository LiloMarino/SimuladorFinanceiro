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

export function displayDate(date: Date | string) {
  const d = typeof date === "string" ? new Date(date) : date;

  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(d);
}

export function displayMonthYear(date: Date | string) {
  const d = typeof date === "string" ? new Date(date) : date;

  return new Intl.DateTimeFormat("pt-BR", {
    month: "short",
    year: "numeric",
  }).format(d);
}
