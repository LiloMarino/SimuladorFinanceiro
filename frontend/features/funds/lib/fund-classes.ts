import type { FundDetails } from "@/types";

type HoldingClass = FundDetails["composition"][number]["asset_class"];

/** Nome e cor (classe de fundo) de cada classe de ativo da carteira da gestora. */
export const HOLDING_CLASSES: Record<HoldingClass, { label: string; color: string }> = {
  cash: { label: "Caixa", color: "bg-chart-3" },
  stocks: { label: "Ações", color: "bg-chart-1" },
  fixed_income: { label: "Renda fixa", color: "bg-chart-2" },
  treasury: { label: "Tesouro", color: "bg-chart-4" },
};
