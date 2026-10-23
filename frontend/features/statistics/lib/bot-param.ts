import type { BotParam } from "@/types";

/** Quantas ações aparecem por extenso antes do "+N". */
const VISIBLE_TICKERS = 5;

/** O valor do parâmetro como o cartão do bot o lê: "50 dias", "20%", "PETR4, VALE3 +8". */
export function displayBotParam({ value, unit }: BotParam) {
  if (Array.isArray(value)) {
    const rest = value.length - VISIBLE_TICKERS;
    return rest > 0 ? `${value.slice(0, VISIBLE_TICKERS).join(", ")} +${rest}` : value.join(", ");
  }
  const text = typeof value === "number" ? value.toLocaleString("pt-BR") : String(value);
  if (!unit) return text;
  return unit === "%" ? `${text}%` : `${text} ${unit}`;
}
