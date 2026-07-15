import { Wallet, TrendingUp, Coins, Banknote } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { economicIndicatorsOptions } from "@/shared/lib/queries/economicIndicatorsOptions";
import { usePortfolio } from "@/features/portfolio/hooks/queries/usePortfolio";
import { useVariableIncomeStocks } from "@/features/variable-income/hooks/queries/useVariableIncomeStocks";
import { displayPercent } from "@/shared/lib/utils/display";
import { SummaryCard } from "@/features/portfolio/components/summary-card";
import { PortfolioCharts } from "../components/portfolio-charts";
import { useMemo } from "react";
import { calculatePortfolioView } from "../lib/portfolio-calculator";
import { EconomicIndicatorsCard } from "../components/economic-indicators-card";
import { VariableIncomeTable } from "../components/variable-income-table";
import { FixedIncomeTable } from "../components/fixed-income-table";
import { ErrorPage } from "@/pages/error";
import { LoadingPage } from "@/pages/loading";

export default function PortfolioPage() {
  usePageLabel("Carteira");
  // Busca dados da carteira (posições, caixa, histórico — mantida viva via WS)
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError } = usePortfolio();

  // Busca dados econômicos
  const { data: economicIndicatorsData, isLoading: economicIndicatorsLoading } = useQuery(economicIndicatorsOptions());

  // Busca os valores das ações (mantidos vivos via WS)
  const { data: stocks } = useVariableIncomeStocks();

  const view = useMemo(() => {
    if (!portfolioData) return null;
    return calculatePortfolioView(portfolioData, stocks ?? null);
  }, [portfolioData, stocks]);

  if (portfolioLoading) {
    return <LoadingPage />;
  } else if (!portfolioData || !view) {
    return (
      <ErrorPage
        code={String(portfolioError?.status) || "500"}
        title="Erro ao carregar carteira"
        message={String(portfolioError?.message)}
      />
    );
  }

  const { patrimonial_history } = portfolioData;
  const {
    variablePositions,
    fixedPositions,
    variableIncomeValue,
    fixedIncomeValue,
    variableIncomePct,
    totalNetWorth,
    investedValue,
    investedPct,
    fixedIncomePct,
    totalReturnPct,
  } = view;

  return (
    <section className="p-4 space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SummaryCard
          title="Patrimônio Total"
          value={totalNetWorth}
          subtitle={`Rentabilidade de ${displayPercent(totalReturnPct)}`}
          icon={Wallet}
          iconBg="bg-green-100"
          color="text-green-600"
        />

        <SummaryCard
          title="Total Investido"
          value={investedValue}
          subtitle={`${displayPercent(investedPct)} do patrimônio`}
          icon={Banknote}
          iconBg="bg-purple-100"
          color="text-purple-600"
        />

        <SummaryCard
          title="Renda Variável"
          value={variableIncomeValue}
          subtitle={`${displayPercent(variableIncomePct)} da carteira`}
          icon={TrendingUp}
          iconBg="bg-blue-100"
          color="text-blue-600"
        />

        <SummaryCard
          title="Renda Fixa"
          value={fixedIncomeValue}
          subtitle={`${displayPercent(fixedIncomePct)} da carteira`}
          icon={Coins}
          iconBg="bg-yellow-100"
          color="text-yellow-600"
        />
      </div>

      {/* Charts */}
      <PortfolioCharts
        variablePositions={variablePositions}
        fixedPositions={fixedPositions}
        patrimonialHistory={patrimonial_history}
      />

      {/* Economic Indicators */}
      <EconomicIndicatorsCard loading={economicIndicatorsLoading} data={economicIndicatorsData ?? null} />

      {/* Positions Tables */}
      <div className="space-y-6">
        {/* Renda Variável */}
        <VariableIncomeTable variablePositions={variablePositions} />

        {/* Renda Fixa */}
        <FixedIncomeTable fixedPositions={fixedPositions} />
      </div>
    </section>
  );
}
