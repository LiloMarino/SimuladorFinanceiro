import type { FundDetails, FundSummary } from "@/types";

/** Em que ponto da vida a gestora está: fechada (antes da oferta), com a oferta aberta ou já negociada. */
export type FundStage = "closed" | "offer" | "listed";

export function fundStage(fund: Pick<FundSummary, "listed_on" | "offer_remaining">): FundStage {
  if (fund.listed_on === null) return "closed";
  return fund.offer_remaining === null ? "listed" : "offer";
}

/** O patrimônio: a soma do que a gestora tem em cada classe, a preço de hoje. */
export const netWorthOf = (fund: Pick<FundDetails, "composition">) =>
  fund.composition.reduce((sum, item) => sum + Number(item.value), 0);

/** A parte das cotas que o gestor tem (fração de 0 a 1). */
export const managerShareOf = (fund: Pick<FundDetails, "holders" | "manager_user_id">) =>
  Number(fund.holders.find((holder) => holder.user_id === fund.manager_user_id)?.share ?? 0);

/** As cotas do gestor, que dão o controle quando passam da metade. */
export const managerQuotasOf = (fund: Pick<FundDetails, "holders" | "manager_user_id">) =>
  Number(fund.holders.find((holder) => holder.user_id === fund.manager_user_id)?.quotas ?? 0);
