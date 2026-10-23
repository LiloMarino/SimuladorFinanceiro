import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { FixedIncomeOffer } from "@/types";

/** O CDB de 100% do CDI, aberto a partida inteira: liquidez diária e sem teto por jogador. */
export const isPermanentCdb = (offer: FixedIncomeOffer) => offer.daily_liquidity && offer.player_cap === null;

/** A oferta rara do mês: liquidez diária acima de 100% do CDI, com teto por jogador. */
export const isRareOffer = (offer: FixedIncomeOffer) => offer.daily_liquidity && offer.player_cap !== null;

/** "R$ 20 mil" para tetos redondos; o resto vai por extenso. */
export function displayCap(value: string) {
  const amount = Number(value);
  return amount >= 1000 && amount % 1000 === 0 ? `R$ ${amount / 1000} mil` : displayMoneyWhole(amount);
}
