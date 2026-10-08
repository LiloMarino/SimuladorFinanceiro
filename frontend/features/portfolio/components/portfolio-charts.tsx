import { PortfolioPieChart } from "./portfolio-pie-chart";
import { PortfolioAreaChart } from "./portfolio-area-chart";
import type { FixedIncomePosition, PatrimonialHistory, PortfolioPosition } from "@/types";

interface PortfolioChartsProps {
  variablePositions: PortfolioPosition[];
  fixedPositions: FixedIncomePosition[];
  patrimonialHistory: PatrimonialHistory[];
}

export function PortfolioCharts({ variablePositions, fixedPositions, patrimonialHistory }: PortfolioChartsProps) {
  const pieData = [
    ...variablePositions.map((pos) => ({
      name: pos.ticker,
      value: Number(pos.current_value),
    })),
    ...fixedPositions.map((pos) => ({
      name: pos.asset.name,
      value: Number(pos.current_value),
    })),
  ];
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
      <PortfolioAreaChart data={patrimonialHistory} />
      <PortfolioPieChart title="Distribuição da Carteira" data={pieData} />
    </div>
  );
}
