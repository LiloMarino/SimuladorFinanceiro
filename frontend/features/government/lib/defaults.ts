import type { GovernmentRules } from "@/types";

/** Compatibilidade com regras de partidas antigas que ainda não tinham a expansão. */
export const DISABLED_GOVERNMENT: GovernmentRules = {
  enabled: false, difficulty: "medium", ranking: "individual", manual_selic: false,
  model_version: "government-v1", impeachment_floor: 25, impeachment_months: 3,
  campaign_scale: "8000", inflation_target: 0.03, initial_treasury: "1000000000",
  spending_inflation: 0.01, monetary_inflation: 0.25,
  electorate: [
    { name: "Investidores", weight: 0.25, position: 1.5, campaign_sensitivity: 1 },
    { name: "Empreendedores", weight: 0.30, position: 2.5, campaign_sensitivity: 1 },
    { name: "Serviços públicos", weight: 0.30, position: 4.5, campaign_sensitivity: 1 },
    { name: "Equilíbrio fiscal", weight: 0.15, position: 3, campaign_sensitivity: 0.7 },
  ], companies: [],
};
