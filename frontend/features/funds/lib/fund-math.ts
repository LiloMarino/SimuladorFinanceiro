import { CONTROL_SHARE } from "@/shared/lib/fund-quota";
import { TICKER_LETTERS, tickerOf } from "@/shared/lib/fund-ticker";
import type { FundTickerCheck } from "@/types";

/** A primeira cota nasce a R$ 100,00; dali em diante vale o patrimônio por cota do dia. */
export const FIRST_QUOTA_PRICE = 100;

/** O que o gestor leva da carteira e quantas cotas recebe por isso (cotas inteiras ao preço da cota, a sobra fica na gestora). */
export function foundingSummary(cash: number, stocksValue: number, quotaPrice = FIRST_QUOTA_PRICE) {
  const taken = cash + stocksValue;
  const quotas = Math.max(0, Math.floor(taken / quotaPrice));
  return { taken, quotas, leftover: taken - quotas * quotaPrice };
}

/** A parte do gestor depois de uma oferta de `offered` cotas novas, se tudo for vendido. */
export function offerControl(mine: number, total: number, offered: number) {
  const totalAfter = total + offered;
  return {
    share: totalAfter > 0 ? mine / totalAfter : 0,
    keepsControl: mine > totalAfter * CONTROL_SHARE,
  };
}

export type TickerFeedback = { tone: "neutral" | "success" | "error"; message: string };

/** A resposta sobre a sigla enquanto o jogador digita: letras incompletas, checando ou o veredito do servidor. */
export function tickerFeedback(letters: string, check: FundTickerCheck | undefined, checking: boolean): TickerFeedback {
  if (letters.length < TICKER_LETTERS) return { tone: "neutral", message: `Use ${TICKER_LETTERS} letras` };
  const ticker = tickerOf(letters);
  if (checking || !check || check.ticker !== ticker) return { tone: "neutral", message: `Conferindo ${ticker}...` };
  if (check.status === "free") return { tone: "success", message: `${ticker} está livre` };
  if (check.status === "asset") return { tone: "error", message: `${letters} já é um ativo da partida` };
  if (check.status === "fund") {
    const owner = check.owner_name ? `a gestora da ${check.owner_name}` : "outra gestora";
    return { tone: "error", message: `${ticker} é ${owner}` };
  }
  return { tone: "error", message: `Use ${TICKER_LETTERS} letras` };
}
