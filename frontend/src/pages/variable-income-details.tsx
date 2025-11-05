import { useRef, useState } from "react";
import clsx from "clsx";
import { useParams } from "react-router-dom";
import { useQueryApi } from "@/hooks/useQueryApi";
import type { Position, StockDetails } from "@/types";
import { Spinner } from "@/components/ui/spinner";
import { useRealtime } from "@/hooks/useRealtime";
import { Card } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Plus, Minus } from "lucide-react";
import { StockChart } from "@/components/stock-chart";
import { useMutationApi } from "@/hooks/useMutationApi";
import { toast } from "sonner";
import { formatCash, formatPrice } from "@/lib/utils/formatting";
import usePageLabel from "@/hooks/usePageLabel";

export default function VariableIncomeDetailPage() {
  usePageLabel("Detalhes Renda Variável");
  const { ticker } = useParams<{ ticker: string }>();
  const [quantity, setQuantity] = useState<number>(0);
  const shouldRefreshPosition = useRef(false);

  const { data: stock, setData: setStock, loading } = useQueryApi<StockDetails>(`/api/variable-income/${ticker}`);

  const positionQuery = useQueryApi<Position>(`/api/portfolio/${ticker}`);

  const { data: cashData, setData: setCash } = useQueryApi<{ cash: number }>("/api/portfolio/cash");
  const { cash = 0 } = cashData ?? {};

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

  const buyMutation = useMutationApi(`/api/variable-income/${ticker}/buy`, {
    onSuccess: () => {
      toast.success("Ordem de compra enviada com sucesso!");
      setQuantity(0);
      shouldRefreshPosition.current = true;
    },
    onError: (err) => {
      toast.error(`Erro ao enviar ordem de compra: ${err.message}`);
    },
  });

  const sellMutation = useMutationApi(`/api/variable-income/${ticker}/sell`, {
    onSuccess: () => {
      toast.success("Ordem de venda enviada com sucesso!");
      setQuantity(0);
      shouldRefreshPosition.current = true;
    },
    onError: (err) => {
      toast.error(`Erro ao enviar ordem de venda: ${err.message}`);
    },
  });

  if (loading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
  } else if (!stock) {
    return <div>Stock not found</div>;
  }

  const handleBuy = async () => {
    if (!quantity || quantity <= 0) {
      toast.warning("Informe uma quantidade válida para comprar.");
      return;
    }
    await buyMutation.mutate({ quantity });
  };

  const handleSell = async () => {
    if (!quantity || quantity <= 0) {
      toast.warning("Informe uma quantidade válida para vender.");
      return;
    }
    await sellMutation.mutate({ quantity });
  };

  const position = positionQuery.data;
  const size = position?.size ?? 0;
  const avgPrice = position?.avg_price ?? 0;
  const isPositive = stock.change >= 0;

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
            <h3 className="text-3xl font-bold text-gray-800 dark:text-gray-100">R$ {stock.price.toFixed(2)}</h3>
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
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Operações */}
          <Card className="flex-1 bg-muted/40 p-4">
            <h3 className="font-medium mb-4">Operação</h3>
            <div className="flex flex-col gap-3">
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  placeholder="Quantidade"
                  value={quantity}
                  min={0}
                  onChange={(e) => {
                    const value = e.target.value === "" ? 0 : Number(e.target.value);
                    setQuantity(value >= 0 ? value : 0);
                  }}
                  className="flex-1 p-2 border rounded-md"
                />
                <button
                  className={clsx(
                    "bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md flex items-center justify-center gap-1",
                    buyMutation.loading && "opacity-70 cursor-not-allowed"
                  )}
                  onClick={handleBuy}
                  disabled={buyMutation.loading}
                >
                  {buyMutation.loading ? <Spinner className="h-4 w-4 text-white" /> : <Plus className="w-4 h-4" />}
                  Comprar
                </button>

                <button
                  className={clsx(
                    "bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md flex items-center justify-center gap-1",
                    sellMutation.loading && "opacity-70 cursor-not-allowed"
                  )}
                  onClick={handleSell}
                  disabled={sellMutation.loading}
                >
                  {sellMutation.loading ? <Spinner className="h-4 w-4 text-white" /> : <Minus className="w-4 h-4" />}
                  Vender
                </button>
              </div>

              {/* Total estimado */}
              <div className="flex flex-col gap-1 border-t pt-3 mt-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Total estimado da operação:</span>
                  <span className="font-semibold">{formatPrice(quantity * stock.price)}</span>
                </div>
                <p className="text-xs text-muted-foreground italic">
                  * O preço pode variar do mostrado, conforme atualização do mercado.
                </p>
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
                  {size} ações ({formatPrice(size * stock.price)})
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Preço médio</p>
                <p className="font-bold">{formatPrice(avgPrice)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Lucro / Prejuízo</p>
                <p
                  className={clsx(
                    "font-bold",
                    size > 0 && stock.price - avgPrice >= 0 ? "text-green-600" : "text-red-600"
                  )}
                >
                  {formatPrice(size * (stock.price - avgPrice))}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Saldo em conta</p>
                <p className="font-bold">{formatCash(cash)}</p>
              </div>
            </div>
          </Card>
        </div>
      </Card>
    </section>
  );
}
