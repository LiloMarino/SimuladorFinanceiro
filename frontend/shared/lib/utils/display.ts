/**
 * display.ts
 * ------------
 * Funções de exibição (display*) — recebem valores já processados (ex: number, Date, etc.)
 * e retornam strings prontas para serem mostradas na UI (ex: "R$ 1.200,00").
 *
 * 🔹 Convenção de assinatura:
 *    (value: any) => string
 */

export function displayMoney(value: number) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(value);
}

const COMPACT_SCALES = [
  { threshold: 1_000_000_000_000, suffix: "T" },
  { threshold: 1_000_000_000, suffix: "B" },
  { threshold: 1_000_000, suffix: "M" },
  { threshold: 1_000, suffix: "K" },
] as const;

export function displayMoneyCompact(value: number): string {
  const abs = Math.abs(value);

  for (const { threshold, suffix } of COMPACT_SCALES) {
    if (abs >= threshold) {
      const v = value / threshold;
      const formatted = new Intl.NumberFormat("pt-BR", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 1,
      }).format(v);
      return `R$ ${formatted} ${suffix}`;
    }
  }

  return displayMoney(value);
}

export function displayPercent(value: number, digits = 2) {
  return new Intl.NumberFormat("pt-BR", {
    style: "percent",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
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
