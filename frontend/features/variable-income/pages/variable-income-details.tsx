import { useParams } from "react-router-dom";
import { Card } from "@/shared/components/ui/card";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { StockChart } from "@/features/variable-income/components/stock-chart";
import { LoadingPage } from "@/pages/loading";
import { ErrorPage } from "@/pages/error";
import { StockMiniStats } from "../components/stock-mini-stats";
import { StockHeader } from "../components/stock-header";
import { PositionSummaryCard } from "../components/position-summary-card";
import { PendingOrdersCard } from "../components/pending-orders-table";
import { NewOrderCard } from "../components/new-order-card";
import { usePendingOrders } from "../hooks/usePendingOrders";
import { useVariableIncomeStock } from "../hooks/queries/useVariableIncomeStock";
import { usePortfolioCash } from "@/features/portfolio/hooks/queries/usePortfolioCash";
import { usePortfolioPosition } from "@/features/portfolio/hooks/queries/usePortfolioPosition";
import { VariableIncomeStock } from "../models/VariableIncomeStock";
import { useMemo } from "react";

export default function VariableIncomeDetailPage() {
  usePageLabel("Detalhes Renda Variável");
  const { ticker } = useParams<{ ticker: string }>();
  const { data: stock, isLoading: loading } = useVariableIncomeStock(ticker);
  const { data: cashData } = usePortfolioCash();
  const { cash = 0 } = cashData ?? {};
  const pendingOrders = usePendingOrders(ticker);
  const { data: position } = usePortfolioPosition(ticker);

  const stockModel = useMemo(() => {
    if (!stock) return null;
    return new VariableIncomeStock(stock, pendingOrders);
  }, [stock, pendingOrders]);

  if (loading) {
    return <LoadingPage />;
  } else if (!stock || !stockModel) {
    return (
      <ErrorPage
        code="404"
        title="Ativo de renda variável não encontrado"
        actionHref="/variable-income"
        actionLabel="Voltar para a Renda Variável"
      />
    );
  }

  return (
    <section className="section-content p-4">
      <Card className="p-6">
        {/* Header */}
        <StockHeader stock={stock} />
        {/* Chart */}
        <StockChart ticker={stock.ticker} initialData={stock.history} />
        {/* Mini Cards */}
        <StockMiniStats stock={stock} />
        {/* Ações + Resumo */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          {/* Ações */}
          <NewOrderCard stock={stockModel} cash={cash} position={position ?? null} />

          {/* Resumo */}
          <PositionSummaryCard stock={stock} position={position ?? null} />
        </div>

        <PendingOrdersCard ticker={stock.ticker} pendingOrders={pendingOrders} />
      </Card>
    </section>
  );
}
