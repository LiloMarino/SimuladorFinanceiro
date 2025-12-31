import { PortfolioPieChart } from "./portfolio-pie-chart";
import { PortfolioAreaChart } from "./portfolio-area-chart";
import type { PatrimonialHistory } from "@/types";

interface VariablePositionForChart {
  ticker: string;
  currentValue: number;
}

interface FixedPositionForChart {
  name: string;
  currentValue: number;
}

interface PortfolioChartsProps {
  variablePositions: VariablePositionForChart[];
  fixedPositions: FixedPositionForChart[];
  patrimonialHistory: PatrimonialHistory[];
}

export function PortfolioCharts({ variablePositions, fixedPositions, patrimonialHistory }: PortfolioChartsProps) {
  const pieData = [
    ...variablePositions.map((pos) => ({
      name: pos.ticker,
      value: pos.currentValue,
    })),
    ...fixedPositions.map((pos) => ({
      name: pos.name,
      value: pos.currentValue,
    })),
  ];
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
      <PortfolioAreaChart data={patrimonialHistory} />
      <PortfolioPieChart title="Distribuição da Carteira" data={pieData} />
    </div>
  );
}
