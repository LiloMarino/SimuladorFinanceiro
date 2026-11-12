import { normalizeNumberString } from "@/shared/lib/utils";
import { toCentsString } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";

/** O teto da contribuição por pessoa no início da partida, em reais; depois dela o IPCA o corrige. */
export const STARTING_CONTRIBUTION_CAP = "8000";

/** O texto digitado vira o valor em reais que a API recebe ("R$ 2.000,00" → "2000.00"). */
export function contributionAmount(text: string) {
  return normalizeNumberString(text) || "0";
}

/** O campo com `amount` reais somados ao texto digitado ("R$ 2.000,00" + 5000 → "R$ 7.000,00"), em centavos inteiros. */
export function addToContribution(text: string, amount: number) {
  const cents = Math.round(Number(contributionAmount(text)) * 100) + Math.round(amount * 100);
  return formatMoney(String(cents));
}

/** O valor em reais ("2000") como o campo mostra ("R$ 2.000,00"). */
export function contributionText(amount: string) {
  return formatMoney(toCentsString(amount));
}
