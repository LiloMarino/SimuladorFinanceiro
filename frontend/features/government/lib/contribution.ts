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

/** A parte da contribuição que vai ao Congresso, em reais; sem chapa na presidência, tudo vai a ele. */
export function congressAmount(monthly: number, share: number, runs: boolean) {
  return (runs ? (monthly * share) / 100 : monthly).toFixed(2);
}

/** A fatia do Congresso (0 a 100) que uma contribuição já salva representa. */
export function congressShare(contribution: string, congress: string) {
  const total = Number(contribution);
  return total > 0 ? Math.round((Number(congress) / total) * 100) : 0;
}
