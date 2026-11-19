import { displayMoney, displayPercent, displayQuantity } from "@/shared/lib/utils/display";
import type { FundDetails, FundDirectedIssuancePreview } from "@/types";
import type { Comanager } from "./fund-comanagers";

/** A oferta de cotas novas que espera resposta, como a página da gestora a traz. */
export type DirectedOffer = NonNullable<FundDetails["directed_issuance"]>;

/** Quem pode comprar as cotas dirigidas além do próprio gestor: os co-gestores que já operam. */
export const directedBuyers = (comanagers: Comanager[]) =>
  comanagers.filter((comanager) => comanager.status === "ACTIVE");

/** O teto da emissão: o do mercado (com limite de participação) ou só o espaço da emissão; sem teto não há dica. */
export function ceilingHint(preview: Pick<FundDirectedIssuancePreview, "room" | "manager_cap">): string | null {
  if (preview.room === null) return null;
  const room = displayQuantity(preview.room);
  if (preview.manager_cap === null) return `Até ${room} cotas nesta emissão`;
  const market = displayPercent(1 - Number(preview.manager_cap), 0, { trim: true });
  return `Seu teto: ${room} cotas, porque o mercado fica com pelo menos ${market} das cotas`;
}

/** Quantas cotas passam do teto da emissão; teto nulo nunca é ultrapassado. */
export const overCeiling = (quotas: number, room: FundDirectedIssuancePreview["room"]) =>
  room !== null && quotas > Number(room);

/** Para onde vai o dinheiro na gestora: primeiro a taxa a pagar, o resto fica no caixa. */
export function destinationNote(toPayable: string, toCash: string): string {
  if (Number(toPayable) <= 0) return `${displayMoney(toCash)} ficam no caixa`;
  return `${displayMoney(toPayable)} quitam antes a taxa a pagar; ${displayMoney(toCash)} ficam no caixa`;
}

/** A participação do comprador: "a% → b% de N cotas". */
export function shareNote(
  preview: Pick<FundDirectedIssuancePreview, "my_share_now" | "my_share_after" | "total_after">,
) {
  return `${displayPercent(preview.my_share_now, 1)} → ${displayPercent(preview.my_share_after, 1)} de ${displayQuantity(preview.total_after)} cotas`;
}

/** O preço das cotas: o maior entre o patrimônio por cota e o preço de ranking, com um exemplo de como sai. */
export function priceNote(preview: Pick<FundDirectedIssuancePreview, "nav" | "ranking_price">): string {
  return `O maior entre o patrimônio por cota (${displayMoney(preview.nav)}) e o preço de ranking (${displayMoney(preview.ranking_price)}). Com patrimônio de R$ 100,00 e ranking de R$ 120,00, sairia a R$ 120,00`;
}

/** O texto do botão: emite direto para si ou oferece a um co-gestor. */
export function directedActionLabel(quotas: number, buyerNickname: string | null): string {
  const count = quotas > 0 ? ` ${displayQuantity(String(quotas))} cotas` : "";
  if (buyerNickname === null) return `Emitir${count}`;
  return `Oferecer${count} a ${buyerNickname}`;
}
