import { useRef, useState } from "react";
import clsx from "clsx";
import { useParams } from "react-router-dom";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { PendingOrder, Position, StockDetails } from "@/types";
import { Spinner } from "@/shared/components/ui/spinner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { Card } from "@/shared/components/ui/card";
import { Plus, Minus } from "lucide-react";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
import { formatMoney } from "@/shared/lib/utils/formatting";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { StockChart } from "@/features/variable-income/components/stock-chart";
import { LoadingPage } from "@/pages/loading";
import { ErrorPage } from "@/pages/error";
import { StockMiniStats } from "../components/stock-mini-stats";
import { StockHeader } from "../components/stock-header";
import { PositionSummaryCard } from "../components/position-summary-card";
import { PendingOrdersCard } from "../components/pending-orders-table";

export default function VariableIncomeDetailPage() {
  usePageLabel("Detalhes Renda Variável");
  const { ticker } = useParams<{ ticker: string }>();
  const [quantity, setQuantity] = useState<number>(0);
  const [operationType, setOperationType] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [limitPrice, setLimitPrice] = useState<number>(0);
  const shouldRefreshPosition = useRef(false);

  const { data: stock, setData: setStock, loading } = useQueryApi<StockDetails>(`/api/variable-income/${ticker}`);

  const { data: position, query: positionQuery } = useQueryApi<Position>(`/api/portfolio/${ticker}`);

  const { data: cashData, setData: setCash } = useQueryApi<{ cash: number }>("/api/portfolio/cash");
  const { cash = 0 } = cashData ?? {};

  const { data: pendingOrders, query: refetchOrders } = useQueryApi<PendingOrder[]>(
    `/api/variable-income/${ticker}/orders`
  );

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

  const executeOrderMutation = useMutationApi(`/api/variable-income/${ticker}/order`, {
    onSuccess: () => {
      toast.success("Ordem enviada com sucesso!");
      setQuantity(0);
      setLimitPrice(0);
      shouldRefreshPosition.current = true;
      refetchOrders();
    },
    onError: (err) => {
      toast.error(`Erro ao enviar ordem: ${err.message}`);
    },
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
  const handleExecuteOrder = async () => {
    if (!quantity || quantity <= 0) {
      toast.warning("Informe uma quantidade válida.");
      return;
    }

    if (orderType === "limit" && (!limitPrice || limitPrice <= 0)) {
      toast.warning("Informe um preço válido para ordem limitada.");
      return;
    }

    await executeOrderMutation.mutate({
      operation: operationType,
      type: orderType,
      quantity,
      ...(orderType === "limit" && { limit_price: limitPrice }),
    });
  };

  const handleCancelOrder = async (orderId: string) => {
    await cancelOrderMutation.mutate({ order_id: orderId });
  };

  const estimatedPrice = orderType === "market" ? stock.close : limitPrice;
  const estimatedTotal = quantity * estimatedPrice;

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
          <Card className="flex-1 bg-muted/40 p-4">
            <h3 className="font-medium">Nova Ordem</h3>
            <div className="flex flex-col gap-4">
              {/* Tipo de Operação */}
              <div>
                <label className="text-sm font-medium mb-2 block">Tipo de Operação</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="operation"
                      value="buy"
                      checked={operationType === "buy"}
                      onChange={(e) => setOperationType(e.target.value as "buy")}
                      className="w-4 h-4 text-green-600 accent-green-600"
                    />
                    <span className="text-sm">Compra</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="operation"
                      value="sell"
                      checked={operationType === "sell"}
                      onChange={(e) => setOperationType(e.target.value as "sell")}
                      className="w-4 h-4 text-red-600 accent-red-600"
                    />
                    <span className="text-sm">Venda</span>
                  </label>
                </div>
              </div>

              {/* Tipo de Ordem */}
              <div>
                <label className="text-sm font-medium mb-2 block">Tipo de Ordem</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="orderType"
                      value="market"
                      checked={orderType === "market"}
                      onChange={(e) => setOrderType(e.target.value as "market")}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">À Mercado</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="orderType"
                      value="limit"
                      checked={orderType === "limit"}
                      onChange={(e) => setOrderType(e.target.value as "limit")}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Limitada</span>
                  </label>
                </div>
              </div>

              {/* Inputs */}
              <div className="flex flex-col gap-2">
                <input
                  type="number"
                  placeholder="Quantidade"
                  value={quantity || ""}
                  min={0}
                  onChange={(e) => {
                    const value = e.target.value === "" ? 0 : Number(e.target.value);
                    setQuantity(value >= 0 ? value : 0);
                  }}
                  className="flex-1 p-2 border rounded-md bg-background"
                />

                {/* Campo condicional para preço limitado */}
                {orderType === "limit" && (
                  <input
                    type="number"
                    placeholder="Preço desejado (R$)"
                    value={limitPrice || ""}
                    min={0}
                    step={0.01}
                    onChange={(e) => {
                      const value = e.target.value === "" ? 0 : Number(e.target.value);
                      setLimitPrice(value >= 0 ? value : 0);
                    }}
                    className="flex-1 p-2 border rounded-md bg-background"
                  />
                )}

                {/* Botão único para executar */}
                <button
                  className={clsx(
                    "py-2 px-4 rounded-md font-medium text-white flex items-center justify-center gap-2 transition-colors",
                    operationType === "buy" ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700",
                    executeOrderMutation.loading && "opacity-70 cursor-not-allowed"
                  )}
                  onClick={handleExecuteOrder}
                  disabled={executeOrderMutation.loading}
                >
                  {executeOrderMutation.loading ? (
                    <Spinner className="h-4 w-4 text-white" />
                  ) : (
                    <>
                      {operationType === "buy" ? <Plus className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
                      Executar {operationType === "buy" ? "Compra" : "Venda"}
                    </>
                  )}
                </button>
              </div>

              {/* Total estimado */}
              <div className="flex flex-col gap-1 border-t pt-3 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Total estimado:</span>
                  <span className="font-semibold">{formatMoney(estimatedTotal)}</span>
                </div>
                {orderType === "limit" && (
                  <p className="text-xs text-muted-foreground italic">
                    * Ordem será executada quando o preço atingir R$ {limitPrice.toFixed(2)}
                  </p>
                )}
                {orderType === "market" && (
                  <p className="text-xs text-muted-foreground italic">
                    * O preço pode variar conforme atualização do mercado.
                  </p>
                )}
              </div>
            </div>
          </Card>

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
