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

/** Casas decimais da cripto: oito, a precisão do satoshi. */
const QUANTITY_DECIMALS = 8;

/** Quantidade digitada: inteira, ou com uma vírgula e até oito casas quando o ativo é fracionável. */
export function formatQuantityInput(value: string, fractional: boolean) {
  if (!fractional) return onlyDigits(value);
  const [whole = "", ...fraction] = value
    .replace(/\./g, ",")
    .replace(/[^\d,]/g, "")
    .split(",");
  if (fraction.length === 0) return whole;
  return `${whole},${fraction.join("").slice(0, QUANTITY_DECIMALS)}`;
}

/** Quantidade pronta para o campo: vírgula decimal, sem milhar, truncada nas casas do ativo. */
export function quantityToInput(value: string | number, fractional: boolean) {
  return new Intl.NumberFormat("pt-BR", {
    useGrouping: false,
    maximumFractionDigits: fractional ? QUANTITY_DECIMALS : 0,
    roundingMode: "trunc",
  }).format(value as Intl.StringNumericLiteral | number);
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
