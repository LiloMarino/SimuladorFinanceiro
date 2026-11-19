import { normalizeNumberString } from "@/shared/lib/utils";

/** Os jeitos de ligar o impacto de preço; Personalizado libera k e T. */
export type PriceImpactMode = "OFF" | "REALISTIC" | "STRONG" | "CUSTOM";

export const PRICE_IMPACT_PRESETS = {
  REALISTIC: { label: "Realista", k: 0.02, decayDays: 20 },
  STRONG: { label: "Forte", k: 0.05, decayDays: 40 },
} as const;

export const PRICE_IMPACT_MODE_LABELS: Record<PriceImpactMode, string> = {
  OFF: "Desligado",
  REALISTIC: PRICE_IMPACT_PRESETS.REALISTIC.label,
  STRONG: PRICE_IMPACT_PRESETS.STRONG.label,
  CUSTOM: "Personalizado",
};

// Acima deste k o preço salta mais do que o histórico real mostra num dia
export const PRICE_IMPACT_WARNING_K = 0.1;
// A faixa de k que o histórico real sustenta: volatilidade diária de 1,7% a 2,6% (quartis de 81 ativo-anos) vezes Y de 0,5 a 1,5
export const PRICE_IMPACT_REALISTIC_RANGE = { min: 0.01, max: 0.04 } as const;
// A compra do exemplo do aviso, em múltiplos do volume médio diário
export const PRICE_IMPACT_WARNING_EXAMPLE_VOLUME = 4;

/** Alta do preço no pregão seguinte a uma compra de `volumeMultiple` vezes o volume médio: k·√múltiplo. */
export function priceImpactJump(k: number, volumeMultiple = PRICE_IMPACT_WARNING_EXAMPLE_VOLUME): number {
  return k * Math.sqrt(volumeMultiple);
}

/** O k do formulário passa do limiar do aviso? Campo vazio ou inválido não avisa. */
export function isPriceImpactKHigh(k: string): boolean {
  const kValue = Number(normalizeNumberString(k));
  return Number.isFinite(kValue) && kValue > PRICE_IMPACT_WARNING_K;
}

/** O modo que corresponde aos valores do formulário (k vem como "0,02"). */
export function priceImpactModeOf(enabled: boolean, k: string, decayDays: string): PriceImpactMode {
  if (!enabled) return "OFF";
  const kValue = Number(normalizeNumberString(k));
  const tValue = Number(decayDays);
  for (const mode of ["REALISTIC", "STRONG"] as const) {
    const preset = PRICE_IMPACT_PRESETS[mode];
    if (preset.k === kValue && preset.decayDays === tValue) return mode;
  }
  return "CUSTOM";
}
