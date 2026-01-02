/**
 * format.ts
 * ----------
 * Funções de formatação de input (format*) — recebem strings cruas digitadas pelo usuário
 * e retornam strings formatadas ou normalizadas (ex: "1000" → "R$ 10,00").
 *
 * 🔹 Convenção de assinatura:
 *    (value: string) => string
 */
function onlyDigits(value: string) {
  return value.replace(/\D+/g, "");
}

export function formatPositiveInteger(value: string) {
  return onlyDigits(value);
}

export function formatMoney(value: string) {
  const digits = onlyDigits(value);

  if (!digits) return "";

  const cents = Number(digits);
  const amount = cents / 100;

  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(amount);
}
