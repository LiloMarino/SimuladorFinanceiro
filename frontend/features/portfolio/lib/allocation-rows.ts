import type { PortfolioState } from "@/types";

export type AllocationRow = {
  label: string;
  value: string;
  /** Fração do patrimônio, como string decimal */
  pct: string;
  /** Cor do trecho, como classe de fundo ("bg-chart-1") */
  color: string;
  /** Regra de saída do patrimônio de profissão; ausente nas classes comuns */
  exitRule?: string;
};

/** Cada patrimônio de profissão fora do caixa é uma linha com a cor do FGTS e o percentual que o servidor calcula para ele. */
export function allocationRows(portfolio: PortfolioState): AllocationRow[] {
  return [
    {
      label: "Renda variável",
      value: portfolio.variable_income_value,
      pct: portfolio.variable_income_networth_pct,
      color: "bg-chart-1",
    },
    {
      label: "Renda fixa",
      value: portfolio.fixed_income_value,
      pct: portfolio.fixed_income_networth_pct,
      color: "bg-chart-2",
    },
    { label: "Caixa", value: portfolio.cash, pct: portfolio.cash_pct, color: "bg-input" },
    ...portfolio.locked_assets.map((asset) => ({
      label: asset.kind,
      value: asset.value,
      pct: asset.networth_pct,
      color: "bg-chart-7",
      exitRule: asset.exit_rule,
    })),
  ];
}
