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

const MONEY_WHOLE_FORMAT = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});

/** Reais inteiros, sem centavos ("R$ 930.200"), para totais que o jogador lê de relance. */
export function displayMoneyWhole(value: Numeric) {
  return MONEY_WHOLE_FORMAT.format(value as Intl.StringNumericLiteral | number);
}

export function displayMoney(value: Numeric) {
  return MONEY_FORMAT.format(value as Intl.StringNumericLiteral | number);
}

/** Reais com o sinal de menos tipográfico para negativos ("−R$ 2.340,00"), como as telas de saldo. */
export function displaySignedMoney(value: Numeric) {
  const amount = Number(value);
  return `${amount < 0 ? "−" : ""}${displayMoney(Math.abs(amount))}`;
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

const QUANTITY_FORMAT = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 8 });

/** Quantidade de ativo lida da string decimal, sem zeros à direita ("0.50000000" → "0,5", "10.00000000" → "10"). */
export function displayQuantity(value: string) {
  return QUANTITY_FORMAT.format(value as Intl.StringNumericLiteral);
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

/** "2020-01-02" exibido como data local, sem o recuo de um dia do fuso. */
export const displayIsoDate = (isoDate: string) => displayDate(parseLocalDate(isoDate));

/** "2023-03-14" → "14 mar 2023", a data curta do topo. */
export function displayShortDate(date: Date | string) {
  const parts = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" }).formatToParts(
    typeof date === "string" ? parseLocalDate(date) : date,
  );
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value.replace(".", "") ?? "";
  return `${part("day")} ${part("month")} ${part("year")}`;
}

/** "2023-03-14" → "14 mar", a data curta sem o ano, para vencimentos próximos. */
export function displayDayMonth(isoDate: string) {
  const parts = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short" }).formatToParts(
    parseLocalDate(isoDate),
  );
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value.replace(".", "") ?? "";
  return `${part("day")} ${part("month")}`;
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

/** "2024-03-14" → "março"; com `monthsAhead`, o mês seguinte ("abril"). */
export function displayMonthName(isoDate: string, monthsAhead = 0) {
  const d = parseLocalDate(isoDate);
  d.setMonth(d.getMonth() + monthsAhead, 1);
  return new Intl.DateTimeFormat("pt-BR", { month: "long" }).format(d);
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

/** Tempo em ms legível: "2,5 ms", "38 ms", "11,8 s", "1 min 31 s", "2 h 14 min". */
export function displayDuration(ms: number) {
  if (ms < 10) return `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(ms)} ms`;
  if (ms < 1000) return `${Math.round(ms)} ms`;
  const seconds = ms / 1000;
  if (seconds < 60) return `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(seconds)} s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min ${String(Math.floor(seconds % 60)).padStart(2, "0")} s`;
  return `${Math.floor(minutes / 60)} h ${String(minutes % 60).padStart(2, "0")} min`;
}

/** Tamanho em bytes legível: "80 B", "5,2 KB", "120 KB", "1,55 MB". */
export function displayBytes(bytes: number) {
  if (bytes >= 1_000_000) {
    return `${new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(bytes / 1_000_000)} MB`;
  }
  if (bytes >= 100) {
    const kb = bytes / 1000;
    return `${new Intl.NumberFormat("pt-BR", { maximumFractionDigits: kb < 100 ? 1 : 0 }).format(kb)} KB`;
  }
  return `${Math.round(bytes)} B`;
}
