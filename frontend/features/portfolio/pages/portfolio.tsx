import { Wallet, TrendingUp, Coins, Banknote } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { economicIndicatorsOptions } from "@/shared/lib/queries/economicIndicatorsOptions";
import { usePortfolio } from "@/features/portfolio/hooks/queries/usePortfolio";
import { usePatrimonialHistory } from "@/features/portfolio/hooks/queries/usePatrimonialHistory";
import { displayPercent } from "@/shared/lib/utils/display";
import { SummaryCard } from "@/features/portfolio/components/summary-card";
import { PortfolioCharts } from "../components/portfolio-charts";
import { EconomicIndicatorsCard } from "../components/economic-indicators-card";
import { VariableIncomeTable } from "../components/variable-income-table";
import { FixedIncomeTable } from "../components/fixed-income-table";
import { ErrorPage } from "@/pages/error";
import { LoadingPage } from "@/pages/loading";

export default function PortfolioPage() {
  usePageLabel("Carteira");
  // Busca dados da carteira (posições, caixa e totais — mantida viva via WS)
  const { data: portfolio, isLoading: portfolioLoading, error: portfolioError } = usePortfolio();
  const { data: patrimonialHistory } = usePatrimonialHistory();

  // Busca dados econômicos
  const { data: economicIndicatorsData, isLoading: economicIndicatorsLoading } = useQuery(economicIndicatorsOptions());

  if (portfolioLoading) {
    return <LoadingPage />;
  } else if (!portfolio) {
    return (
      <ErrorPage
        code={String(portfolioError?.status) || "500"}
        title="Erro ao carregar carteira"
        message={String(portfolioError?.message)}
      />
    );
  }

  return (
    <section className="p-4 space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SummaryCard
          title="Patrimônio Total"
          value={portfolio.total_networth}
          subtitle={`Rentabilidade de ${displayPercent(portfolio.total_return_pct)}`}
          icon={Wallet}
          iconBg="bg-green-100"
          color="text-green-600"
        />

        <SummaryCard
          title="Total Investido"
          value={portfolio.invested_value}
          subtitle={`${displayPercent(portfolio.invested_pct)} do patrimônio`}
          icon={Banknote}
          iconBg="bg-purple-100"
          color="text-purple-600"
        />

        <SummaryCard
          title="Renda Variável"
          value={portfolio.variable_income_value}
          subtitle={`${displayPercent(portfolio.variable_income_pct)} da carteira`}
          icon={TrendingUp}
          iconBg="bg-blue-100"
          color="text-blue-600"
        />

        <SummaryCard
          title="Renda Fixa"
          value={portfolio.fixed_income_value}
          subtitle={`${displayPercent(portfolio.fixed_income_pct)} da carteira`}
          icon={Coins}
          iconBg="bg-yellow-100"
          color="text-yellow-600"
        />
      </div>

      {/* Charts */}
      <PortfolioCharts
        variablePositions={portfolio.variable_income}
        fixedPositions={portfolio.fixed_income}
        patrimonialHistory={patrimonialHistory ?? []}
      />

      {/* Economic Indicators */}
      <EconomicIndicatorsCard loading={economicIndicatorsLoading} data={economicIndicatorsData ?? null} />

      {/* Positions Tables */}
      <div className="space-y-6">
        {/* Renda Variável */}
        <VariableIncomeTable variablePositions={portfolio.variable_income} />

        {/* Renda Fixa */}
        <FixedIncomeTable fixedPositions={portfolio.fixed_income} />
      </div>
    </section>
  );
}
