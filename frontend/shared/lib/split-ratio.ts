import { displayNumber } from "@/shared/lib/utils/display";

export interface SplitDescription {
  /** `split` aumenta a quantidade de ações (2 para 1); `reverse` a reduz (grupamento, 10 para 1). */
  kind: "split" | "reverse";
  name: "Desdobramento" | "Grupamento";
  /** A razão em palavras: "2 para 1" em qualquer um dos dois sentidos. */
  label: string;
}

const MAX_DENOMINATOR = 10;
const TOLERANCE = 1e-6;

/** Razão do evento (ações depois ÷ antes) em palavras: 2 vira "2 para 1" e 0,1 vira o grupamento "10 para 1". */
export function describeSplit(ratio: string | number): SplitDescription {
  const value = Number(ratio);
  const kind = value >= 1 ? "split" : "reverse";
  const factor = value >= 1 ? value : 1 / value;
  const name = kind === "split" ? "Desdobramento" : "Grupamento";

  for (let denominator = 1; denominator <= MAX_DENOMINATOR; denominator++) {
    const numerator = Math.round(factor * denominator);
    if (Math.abs(numerator / denominator - factor) < TOLERANCE) {
      return { kind, name, label: `${numerator} para ${denominator}` };
    }
  }
  return { kind, name, label: `${displayNumber(factor)} para 1` };
}
