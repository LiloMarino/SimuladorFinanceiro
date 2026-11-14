import { TICKER_LETTERS, tickerOf } from "@/shared/lib/fund-ticker";
import type { FundTickerCheck } from "@/types";

/** A primeira cota nasce a R$ 100,00; dali em diante vale o patrimônio por cota do dia. */
export const FIRST_QUOTA_PRICE = 100;

/** Quem passa de metade das cotas governa a gestora. */
const CONTROL_SHARE = 0.5;

/** O que o gestor leva da carteira e quantas cotas recebe por isso (cotas inteiras ao preço da cota, a sobra fica na gestora). */
export function foundingSummary(cash: number, stocksValue: number, quotaPrice = FIRST_QUOTA_PRICE) {
  const taken = cash + stocksValue;
  const quotas = Math.max(0, Math.floor(taken / quotaPrice));
  return { taken, quotas, leftover: taken - quotas * quotaPrice };
}

/** Cotas necessárias para ter mais da metade do total. */
const controlThreshold = (total: number) => Math.floor(total * CONTROL_SHARE) + 1;

/** Quantas cotas faltam para o controle (0 quando já controla). */
export function quotasToControl(mine: number, total: number) {
  return Math.max(0, controlThreshold(total) - mine);
}

/** Quantas cotas o gestor vende sem cair abaixo do controle. */
export function sellableKeepingControl(mine: number, total: number) {
  return Math.max(0, Math.floor(mine - controlThreshold(total)));
}

/** A parte do gestor depois de uma oferta de `offered` cotas novas, se tudo for vendido. */
export function offerControl(mine: number, total: number, offered: number) {
  const totalAfter = total + offered;
  return {
    share: totalAfter > 0 ? mine / totalAfter : 0,
    keepsControl: mine > totalAfter * CONTROL_SHARE,
  };
}

/** Ágio (positivo) ou deságio (negativo) do preço sobre o patrimônio por cota, como fração. */
export function premium(price: number, nav: number) {
  return nav > 0 ? price / nav - 1 : 0;
}

/** Quanto do que o comprador paga é ágio: quantidade × (preço − patrimônio por cota). */
export function premiumPaid(quantity: number, price: number, nav: number) {
  return quantity * (price - nav);
}

/** As cotas e a parte do total que o jogador tem depois de comprar (`issued`: a compra emite cotas novas, como na oferta). */
export function holdingAfterBuy(mine: number, total: number, quantity: number, issued: boolean) {
  const quotas = mine + quantity;
  const totalAfter = issued ? total + quantity : total;
  return { quotas, share: totalAfter > 0 ? quotas / totalAfter : 0 };
}

/** As cotas e a parte do total que o gestor tem depois de vender (a venda só muda de dono, o total fica). */
export function holdingAfterSell(mine: number, total: number, quantity: number) {
  const quotas = Math.max(0, mine - quantity);
  return { quotas, share: total > 0 ? quotas / total : 0 };
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
