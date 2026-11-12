import type { AmountMode } from "@/shared/lib/amount-shortcuts";

/** Os tipos de campo de valor: cada um lembra o próprio modo. */
export type AmountFieldKind =
  | "treasury-buy"
  | "treasury-sell"
  | "credit-prepay"
  | "fixed-income-invest"
  | "fixed-income-redeem"
  | "donation";

const storageKey = (kind: AmountFieldKind) => `amount-mode:${kind}`;

/** O último modo escolhido para este tipo de campo; sem escolha, o `fallback` do campo. */
export function loadAmountMode(kind: AmountFieldKind, fallback: AmountMode): AmountMode {
  try {
    const saved = localStorage.getItem(storageKey(kind));
    return saved === "money" || saved === "percent" ? saved : fallback;
  } catch {
    return fallback;
  }
}

export function saveAmountMode(kind: AmountFieldKind, mode: AmountMode) {
  try {
    localStorage.setItem(storageKey(kind), mode);
  } catch {
    // Sem armazenamento (aba privada, dados bloqueados): o modo só não é lembrado
  }
}
