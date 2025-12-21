import { PortfolioPieChart } from "./portfolio-pie-chart";
import { PortfolioLineChart } from "./portfolio-line-chart";
import type { PatrimonialHistory } from "@/types";

interface PortfolioChartsProps {
  pieData: {
    name: string;
    value: number;
  }[];
  historyData: PatrimonialHistory[];
}

export function PortfolioCharts({ pieData, historyData }: PortfolioChartsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <PortfolioLineChart data={historyData} />
      <PortfolioPieChart title="Distribuição da Carteira" data={pieData} />
    </div>
  );
}
