import type { FundOffers } from "@/types";
import { displayPercent } from "@/shared/lib/utils/display";

type OpenOffer = FundOffers["open"][number];
type ClosedOffer = FundOffers["closed"][number];
type PreferenceOffer = FundOffers["preference"][number];

/** "faltam 2 pregões", "falta 1 pregão" ou "último pregão" quando hoje fecha a venda. */
export function sessionsLeftLabel(sessionsLeft: number): string {
  if (sessionsLeft <= 0) return "último pregão";
  return sessionsLeft === 1 ? "falta 1 pregão" : `faltam ${sessionsLeft} pregões`;
}

/** Venda esgotada: não sobrou cota, mas a oferta de abertura fica na lista até o último pregão. */
export const isSoldOut = (offer: OpenOffer): boolean => Number(offer.remaining) <= 0;

/** O selo do cartão: o pregão da oferta de abertura, a sobra aberta ou a venda esgotada. */
export function openOfferBadge(offer: OpenOffer): string {
  if (isSoldOut(offer)) return "esgotada";
  if (offer.kind === "leftover" || offer.session === null) return "sobra aberta";
  return `pregão ${offer.session} de ${offer.session + offer.sessions_left}`;
}

/** Quanto falta para o prazo, ou o aviso de que a venda esgotada só encerra no fim dele. */
export function openOfferDeadline(offer: OpenOffer): string {
  return isSoldOut(offer) ? "encerra no prazo" : sessionsLeftLabel(offer.sessions_left);
}

/** Quanto da venda já saiu, de 0 a 100, para a barra do cartão. */
export function soldPercent(offer: OpenOffer): number {
  const quotas = Number(offer.quotas);
  return quotas > 0 ? ((quotas - Number(offer.remaining)) / quotas) * 100 : 0;
}

/** Quantas cotas o caixa paga ao preço da oferta, sem passar do que ainda está à venda. */
export function cashQuotas(cash: number, price: number, remaining: number): number {
  if (price <= 0) return 0;
  return Math.min(Math.floor(cash / price), Math.max(remaining, 0));
}

/** O caixa não paga tudo o que ainda está à venda. */
export function cashFallsShort(offer: OpenOffer, cash: number): boolean {
  const remaining = Number(offer.remaining);
  return remaining > 0 && cashQuotas(cash, Number(offer.price), remaining) < remaining;
}

/** A parte do cotista na emissão: os direitos dele sobre as cotas novas, que igualam a fatia que ele já tem. */
export function preferenceShare(offer: PreferenceOffer): number {
  const quotas = Number(offer.issuance_quotas);
  return quotas > 0 ? Number(offer.my_rights) / quotas : 0;
}

/** O custo de usar toda a preferência que sobra, ao preço fixo da emissão. */
export const preferenceCost = (offer: PreferenceOffer): number => Number(offer.my_left) * Number(offer.price);

/** Quanto da emissão os cotistas já compraram, de 0 a 100. */
export function holdersBoughtPercent(offer: PreferenceOffer): number {
  const quotas = Number(offer.issuance_quotas);
  return quotas > 0 ? Math.min((Number(offer.holders_bought) / quotas) * 100, 100) : 0;
}

export const closedKindLabel = (offer: ClosedOffer): string =>
  offer.kind === "issuance" ? "Emissão" : "Oferta inicial";

/** Onde o preço de hoje está em relação ao da oferta: "1,8% acima da oferta"; sem preço de hoje, nada a comparar. */
export function marketGapLabel(offer: ClosedOffer): string | null {
  if (offer.market_price === null) return null;
  const price = Number(offer.price);
  if (price <= 0) return null;
  const gap = Number(offer.market_price) / price - 1;
  if (Math.abs(gap) < 0.0005) return "igual ao da oferta";
  return `${displayPercent(Math.abs(gap), 1)} ${gap > 0 ? "acima" : "abaixo"} da oferta`;
}

/** O texto das taxas do cartão; a oferta de abertura avisa que a carteira nasce com o dinheiro da oferta. */
export function feesText(offer: OpenOffer): string {
  const management = displayPercent(offer.management_fee, 1, { trim: true });
  const performance = displayPercent(offer.performance_fee, 1, { trim: true });
  const base = `Taxa de administração de ${management} ao ano e de performance de ${performance} do que passar do CDI.`;
  return offer.kind === "initial" ? `${base} Sem histórico: a carteira começa com o dinheiro da oferta.` : base;
}
