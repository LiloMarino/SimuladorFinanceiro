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
