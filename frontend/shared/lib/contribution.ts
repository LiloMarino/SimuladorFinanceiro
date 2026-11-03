import { normalizeNumberString } from "@/shared/lib/utils";
import { toCentsString } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";

/** O texto digitado vira o valor em reais que a API recebe ("R$ 2.000,00" → "2000.00"). */
export function contributionAmount(text: string) {
  return normalizeNumberString(text) || "0";
}

/** O valor em reais ("2000") como o campo mostra ("R$ 2.000,00"). */
export function contributionText(amount: string) {
  return formatMoney(toCentsString(amount));
}
