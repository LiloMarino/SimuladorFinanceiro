import { useRef } from "react";
import { useParams } from "react-router-dom";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { Order, Position, StockDetails } from "@/types";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { Card } from "@/shared/components/ui/card";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
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

  const shouldRefreshPosition = useRef(false);

  const { data: stock, setData: setStock, loading } = useQueryApi<StockDetails>(`/api/variable-income/${ticker}`);

  const { data: position, query: positionQuery } = useQueryApi<Position>(`/api/portfolio/${ticker}`);

  const { data: cashData, setData: setCash } = useQueryApi<{ cash: number }>("/api/portfolio/cash");
  const { cash = 0 } = cashData ?? {};

  const { data: pendingOrders, query: refetchOrders } = useQueryApi<Order[]>(`/api/variable-income/${ticker}/orders`);

  useRealtime(`stock_update:${ticker}`, ({ stock }) => {
    setStock((prev) => ({
      ...prev,
      ...stock,
      history: prev?.history ?? [],
    }));
    if (shouldRefreshPosition.current) {
      positionQuery();
      shouldRefreshPosition.current = false;
    }
  });

  useRealtime("cash_update", ({ cash }) => {
    setCash({ cash });
  });

  const cancelOrderMutation = useMutationApi(`/api/variable-income/${ticker}/cancel-order`, {
    onSuccess: () => {
      toast.success("Ordem cancelada com sucesso!");
      refetchOrders();
    },
    onError: (err) => {
      toast.error(`Erro ao cancelar ordem: ${err.message}`);
    },
  });

  if (loading) {
    return <LoadingPage />;
  } else if (!stock || !position) {
    return (
      <ErrorPage
        code="404"
        title="Ativo de renda variável não encontrado"
        actionHref="/variable-income"
        actionLabel="Voltar para a Renda Variável"
      />
    );
  }

  const handleCancelOrder = async (orderId: string) => {
    await cancelOrderMutation.mutate({ order_id: orderId });
  };

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
          <NewOrderCard stock={stock} refetchOrders={refetchOrders} shouldRefreshPosition={shouldRefreshPosition} />

          {/* Resumo */}
          <PositionSummaryCard position={position} stock={stock} cash={cash} />
        </div>

        <PendingOrdersCard
          pendingOrders={pendingOrders}
          onCancelOrder={handleCancelOrder}
          cancelLoading={cancelOrderMutation.loading}
        />
      </Card>
    </section>
  );
}
