import { faWallet, faChartLine, faCoins, faMoneyBillWave } from "@fortawesome/free-solid-svg-icons";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import usePageLabel from "@/shared/hooks/usePageLabel";
import type { EconomicIndicators, PortfolioState, Stock } from "@/types";
import { displayPercent } from "@/shared/lib/utils/display";
import { useRealtime } from "@/shared/hooks/useRealtime";
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
  // Busca dados da carteira
  const {
    data: portfolioData,
    setData: setPortfolioData,
    loading: portfolioLoading,
    error: portfolioError,
  } = useQueryApi<PortfolioState>("/api/portfolio");

  // Busca dados econômicos
  const { data: economicIndicatorsData, loading: economicIndicatorsLoading } =
    useQueryApi<EconomicIndicators>("/api/economic-indicators");

  // Atualiza o histórico patrimonial em tempo real
  useRealtime("snapshot_update", ({ snapshot }) => {
    setPortfolioData((prev) => {
      if (!prev) return prev;

      const map = new Map(prev.patrimonial_history.map((h) => [h.snapshot_date, h]));

      map.set(snapshot.snapshot_date, {
        snapshot_date: snapshot.snapshot_date,
        total_networth: snapshot.total_networth,
        total_equity: snapshot.total_equity,
        total_fixed: snapshot.total_fixed,
        total_cash: snapshot.total_cash,
      });

      return {
        ...prev,
        patrimonial_history: Array.from(map.values()).sort((a, b) => a.snapshot_date.localeCompare(b.snapshot_date)),
      };
    });
  });

  // Busca os valores das ações e os atualiza em tempo real
  const { data: stocks, setData: setStocks } = useQueryApi<Stock[]>("/api/variable-income");
  useRealtime("stocks_update", (data) => {
    setStocks(data.stocks);
  });

  // Atualiza os valores da renda fixa em tempo real
  useRealtime("fixed_income_position_update", (data) => {
    setPortfolioData((prev) => {
      if (!prev) return prev;

      return {
        ...prev,
        fixed_income: data.positions,
      };
    });
  });

  // Atualiza o saldo em tempo real (ex.: resgates)
  useRealtime("cash_update", ({ cash }) => {
    setPortfolioData((prev) => {
      if (!prev) return prev;

      return {
        ...prev,
        cash,
      };
    });
  });

  const view = useMemo(() => {
    if (!portfolioData) return null;
    return calculatePortfolioView(portfolioData, stocks);
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
          subtitle={`${displayPercent(totalReturnPct)} desde o início`}
          icon={faWallet}
          iconBg="bg-green-100"
          color="text-green-600"
        />

        <SummaryCard
          title="Total Investido"
          value={investedValue}
          subtitle={`${displayPercent(investedPct)} do patrimônio`}
          icon={faMoneyBillWave}
          iconBg="bg-purple-100"
          color="text-purple-600"
        />

        <SummaryCard
          title="Renda Variável"
          value={variableIncomeValue}
          subtitle={`${displayPercent(variableIncomePct)} da carteira`}
          icon={faChartLine}
          iconBg="bg-blue-100"
          color="text-blue-600"
        />

        <SummaryCard
          title="Renda Fixa"
          value={fixedIncomeValue}
          subtitle={`${displayPercent(fixedIncomePct)} da carteira`}
          icon={faCoins}
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
      <EconomicIndicatorsCard loading={economicIndicatorsLoading} data={economicIndicatorsData} />

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
