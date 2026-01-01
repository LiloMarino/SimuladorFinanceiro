import { useRef, useState } from "react";
import clsx from "clsx";
import { useParams } from "react-router-dom";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { Position, StockDetails } from "@/types";
import { Spinner } from "@/shared/components/ui/spinner";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { Card } from "@/shared/components/ui/card";
import { TrendingUp, TrendingDown, Plus, Minus } from "lucide-react";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
import { formatMoney } from "@/shared/lib/utils/formatting";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { StockChart } from "@/features/variable-income/components/stock-chart";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Badge } from "@/shared/components/ui/badge";
import { LoadingPage } from "@/pages/loading";
import { ErrorPage } from "@/pages/error";

type OrderOperation = "buy" | "sell";
type OrderType = "market" | "limit";
type OrderStatus = "pending" | "partial" | "filled";

interface PendingOrder {
  id: string;
  created_at: string;
  operation: OrderOperation;
  type: OrderType;
  quantity: number;
  limit_price?: number;
  status: OrderStatus;
  user_name: string;
}

export default function VariableIncomeDetailPage() {
  usePageLabel("Detalhes Renda Variável");
  const { ticker } = useParams<{ ticker: string }>();
  const [quantity, setQuantity] = useState<number>(0);
  const [operationType, setOperationType] = useState<"buy" | "sell">("buy");
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [limitPrice, setLimitPrice] = useState<number>(0);
  const shouldRefreshPosition = useRef(false);

  const { data: stock, setData: setStock, loading } = useQueryApi<StockDetails>(`/api/variable-income/${ticker}`);

  const positionQuery = useQueryApi<Position>(`/api/portfolio/${ticker}`);

  const { data: cashData, setData: setCash } = useQueryApi<{ cash: number }>("/api/portfolio/cash");
  const { cash = 0 } = cashData ?? {};

  const {
    data: pendingOrders,
    setData: setPendingOrders,
    query: refetchOrders,
  } = useQueryApi<PendingOrder[]>(`/api/variable-income/${ticker}/orders`);

  useRealtime(`stock_update:${ticker}`, ({ stock }) => {
    setStock((prev) => ({
      ...prev,
      ...stock,
      history: prev?.history ?? [],
    }));
    if (shouldRefreshPosition.current) {
      positionQuery.query();
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

  const position = positionQuery.data;
  const size = position?.size ?? 0;
  const avgPrice = position?.avg_price ?? 0;
  const isPositive = stock.change >= 0;

  const estimatedPrice = orderType === "market" ? stock.close : limitPrice;
  const estimatedTotal = quantity * estimatedPrice;

  return (
    <section id="stock-detail" className="section-content p-4">
      <Card className="p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold">{stock.ticker}</h2>
            <p className="text-muted-foreground">{stock.name}</p>
          </div>
          <div className="text-right">
            <h3 className="text-3xl font-bold text-gray-800 dark:text-gray-100">R$ {stock.close.toFixed(2)}</h3>
            <div
              className={clsx(
                "flex items-center justify-end gap-1 font-medium",
                isPositive ? "text-green-600" : "text-red-600"
              )}
            >
              {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>{stock.change_pct}</span>
              <span className="text-muted-foreground">(R$ {stock.change.toFixed(2)})</span>
            </div>
          </div>
        </div>

        {/* Chart */}
        <StockChart ticker={stock.ticker} initialData={stock.history} />

        {/* Mini Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Volume", value: stock.volume.toLocaleString() },
            { label: "Variação Dia", value: stock.change_pct, color: isPositive ? "text-green-600" : "text-red-600" },
            { label: "Mín. do Dia", value: `R$ ${stock.low.toFixed(2)}` },
            { label: "Máx. do Dia", value: `R$ ${stock.high.toFixed(2)}` },
          ].map((item, idx) => (
            <div key={idx} className="border rounded-lg p-4 bg-background hover:shadow-sm transition-shadow">
              <p className="text-muted-foreground text-sm">{item.label}</p>
              <p className={clsx("font-bold text-lg", item.color)}>{item.value}</p>
            </div>
          ))}
        </div>

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
          <Card className="flex-1 bg-background p-4 border">
            <h3 className="font-medium mb-3">Resumo</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-muted-foreground">Você possui</p>
                <p className="font-bold">
                  {size} ações ({formatMoney(size * stock.close)})
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Preço médio</p>
                <p className="font-bold">{formatMoney(avgPrice)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Lucro / Prejuízo</p>
                <p
                  className={clsx(
                    "font-bold",
                    size > 0 && stock.close - avgPrice >= 0 ? "text-green-600" : "text-red-600"
                  )}
                >
                  {formatMoney(size * (stock.close - avgPrice))}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Saldo em conta</p>
                <p className="font-bold">{formatMoney(cash)}</p>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-4 bg-background border">
          <h3 className="font-medium mb-4">Ordens Pendentes</h3>
          {pendingOrders && pendingOrders.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Tipo da Operação</TableHead>
                    <TableHead>Quantidade</TableHead>
                    <TableHead>Preço</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Usuário</TableHead>
                    <TableHead>Ação</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingOrders.map((order) => (
                    <TableRow key={order.id}>
                      <TableCell>
                        {new Date(order.created_at).toLocaleDateString("pt-BR", {
                          day: "2-digit",
                          month: "2-digit",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={order.operation === "buy" ? "default" : "destructive"}
                            className={clsx(
                              order.operation === "buy"
                                ? "bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400"
                                : "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400"
                            )}
                          >
                            {order.operation === "buy" ? "Compra" : "Venda"}
                          </Badge>
                          <Badge variant="outline" className="bg-background">
                            {order.type === "market" ? "Mercado" : "Limitada"}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">{order.quantity}</TableCell>
                      <TableCell className="font-medium">
                        {order.type === "limit" && order.limit_price ? formatMoney(order.limit_price) : "Mercado"}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={clsx(
                            order.status === "filled" &&
                              "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800",
                            order.status === "partial" &&
                              "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800",
                            order.status === "pending" &&
                              "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700"
                          )}
                        >
                          {order.status === "filled" && "Efetivada"}
                          {order.status === "partial" && "Parcial"}
                          {order.status === "pending" && "Pendente"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{order.user_name}</TableCell>
                      <TableCell>
                        {order.status !== "filled" && (
                          <button
                            onClick={() => handleCancelOrder(order.id)}
                            disabled={cancelOrderMutation.loading}
                            className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium disabled:opacity-50 transition-colors"
                          >
                            Cancelar
                          </button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-3 mb-3">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-muted-foreground"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <p className="text-muted-foreground font-medium">Nenhuma ordem pendente</p>
              <p className="text-sm text-muted-foreground mt-1">Suas ordens aparecerão aqui quando forem criadas.</p>
            </div>
          )}
        </Card>
      </Card>
    </section>
  );
}
