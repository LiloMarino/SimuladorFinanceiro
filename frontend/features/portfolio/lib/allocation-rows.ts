import type { PortfolioState } from "@/types";
import { lockedLabel } from "@/shared/lib/locked-assets";

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

/** Cada patrimônio de profissão fora do caixa é uma linha com o nome do tipo, a cor do patrimônio travado e o percentual que o servidor calcula para ele. */
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
      label: lockedLabel(asset.kind),
      value: asset.value,
      pct: asset.networth_pct,
      color: "bg-chart-7",
      exitRule: asset.exit_rule,
    })),
  ];
}

/** Tudo o que está fora do caixa: o investido mais o patrimônio travado da profissão, com a fração do patrimônio que os dois pesam juntos. */
export function outsideCash(portfolio: PortfolioState) {
  return {
    value: Number(portfolio.invested_value) + Number(portfolio.locked_value),
    pct: Number(portfolio.invested_pct) + Number(portfolio.locked_networth_pct),
  };
}
