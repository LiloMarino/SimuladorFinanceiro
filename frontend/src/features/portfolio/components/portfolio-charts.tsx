import { Card } from "@/shared/components/ui/card";
import { PortfolioPieChart } from "./portfolio-pie-chart";

interface PortfolioChartsProps {
  pieData: {
    name: string;
    value: number;
  }[];
}

export function PortfolioCharts({ pieData }: PortfolioChartsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card className="p-6">
        <h3 className="font-semibold">Evolução do Patrimônio</h3>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
          <p className="text-gray-500">Gráfico de evolução do patrimônio</p>
        </div>
      </Card>

      <PortfolioPieChart title="Distribuição da Carteira" data={pieData} />
    </div>
  );
}
