import { useParams } from "react-router-dom";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { Position, StockDetails } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";
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

export default function VariableIncomeDetailPage() {
  usePageLabel("Detalhes Renda Variável");
  const { ticker } = useParams<{ ticker: string }>();
  const { data: stock, setData: setStock, loading } = useQueryApi<StockDetails>(`/api/variable-income/${ticker}`);
  const { data: cashData, setData: setCash } = useQueryApi<{ cash: number }>("/api/portfolio/cash");
  const { cash = 0 } = cashData ?? {};

  useRealtime(`stock_update:${ticker}`, ({ stock }) => {
    setStock((prev) => ({
      ...prev,
      ...stock,
      history: prev?.history ?? [],
    }));
  });

  useRealtime("cash_update", ({ cash }) => {
    setCash({ cash });
  });

  const { data: position, setData: setPosition } = useQueryApi<Position>(`/api/portfolio/${ticker}`);

  useRealtime(`position_update:${ticker}`, ({ position }) => {
    setPosition(position);
  });

  if (loading) {
    return <LoadingPage />;
  } else if (!stock) {
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
          <NewOrderCard stock={stock} cash={cash} position={position} />

          {/* Resumo */}
          <PositionSummaryCard stock={stock} position={position} />
        </div>

        <PendingOrdersCard ticker={stock.ticker} />
      </Card>
    </section>
  );
}
