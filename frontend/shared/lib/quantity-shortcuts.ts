import { quantityToInput } from "@/shared/lib/utils/format";

/** As frações dos atalhos de quantidade; a última é o total do limite. */
export const QUANTITY_SHARES = [0.25, 0.5, 1] as const;

/** O rótulo do atalho: "25%", "50%" e o nome do total. */
export const shareLabel = (share: number, maxLabel: string) => (share === 1 ? maxLabel : `${share * 100}%`);

/** A fração do limite como o campo de quantidade mostra, truncada nas casas do ativo: (1.001, 0.5, inteiro) → "500". */
export function quantityOfShare(max: number | string, share: number, fractional: boolean) {
  return quantityToInput(share === 1 ? max : Number(max) * share, fractional);
}
