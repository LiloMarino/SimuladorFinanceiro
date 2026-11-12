import { contributionAmount } from "@/shared/lib/contribution";
import { formatMoney } from "@/shared/lib/utils/format";
import { shareToField } from "@/shared/lib/utils/money-field";

/** O modo dos atalhos de um campo de valor: reais fixos que somam ou porcentagem do máximo que substitui o valor. */
export type AmountMode = "money" | "percent";

/** As frações do modo %; a última é o total ("Tudo" ou "Máx"). */
export const SHARES = [0.25, 0.5, 0.75, 1] as const;

/** O modo que vale na tela: o salvo, ou o outro enquanto o Shift está seguro. */
export function visibleMode(saved: AmountMode, shiftHeld: boolean): AmountMode {
  if (!shiftHeld) return saved;
  return saved === "money" ? "percent" : "money";
}

/** Os centavos inteiros de um valor em reais; o excedente da terceira casa em diante trunca. */
const centsOf = (reais: number) => Math.floor(Number((reais * 100).toFixed(6)));

/**
 * O campo com `amount` reais somados ao texto digitado, em centavos inteiros.
 * Com `max`, a soma para no máximo e `capped` avisa que o atalho foi limitado.
 */
export function applyFixed(text: string, amount: number, max: number | undefined) {
  const sum = centsOf(Number(contributionAmount(text))) + centsOf(amount);
  const ceiling = max === undefined ? Infinity : centsOf(max);
  const capped = sum > ceiling;
  return { text: formatMoney(String(capped ? ceiling : sum)), capped };
}

/** A fração do máximo como o campo mostra, truncada nos centavos: (1000.01, 0.25) → "R$ 250,00". */
export const applyShare = (max: number, share: number) => shareToField(max, share);

/** O campo zerado. */
export const clearedAmount = () => formatMoney("0");
