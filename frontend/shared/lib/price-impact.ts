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
