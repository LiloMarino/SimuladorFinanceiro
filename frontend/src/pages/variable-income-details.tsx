import { useState } from "react";
import clsx from "clsx";
import { useParams } from "react-router-dom";
import { useQueryApi } from "@/hooks/useQueryApi";
import type { StockDetails } from "@/types";
import { Spinner } from "@/components/ui/spinner";
import { useRealtime } from "@/hooks/useRealtime";
import { Card } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Plus, Minus } from "lucide-react";
import { StockChart } from "@/components/stock-chart";

export default function VariableIncomeDetailPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const [quantity, setQuantity] = useState<number>(0);

  const {
    data: stock,
    setData: setStock,
    loading,
  } = useQueryApi<StockDetails>(`/api/variable-income/${ticker}`, { initialFetch: true });

  useRealtime(`stock_update:${ticker}`, (data) => {
    setStock(data.stock);
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

  const handleBuy = () => console.log(`Comprar ${quantity} ações de ${stock.ticker}`);
  const handleSell = () => console.log(`Vender ${quantity} ações de ${stock.ticker}`);
  const isPositive = stock.change >= 0;
  const totalCompra = quantity > 0 ? quantity * stock.price : 0;

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
        <StockChart data={stock.history} />

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
                  type="number"
                  placeholder="Quantidade"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="flex-1 p-2 border rounded-md"
                />
                <button
                  className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md flex items-center justify-center gap-1"
                  onClick={handleBuy}
                >
                  <Plus className="w-4 h-4" /> Comprar
                </button>
                <button
                  className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md flex items-center justify-center gap-1"
                  onClick={handleSell}
                >
                  <Minus className="w-4 h-4" /> Vender
                </button>
              </div>

              {/* Total da compra atual */}
              <div className="flex justify-between items-center text-sm border-t pt-3 mt-2">
                <span className="text-muted-foreground">Total da compra atual:</span>
                <span className="font-semibold">R$ {totalCompra.toFixed(2)}</span>
              </div>
            </div>
          </Card>

          {/* Resumo */}
          <Card className="flex-1 bg-background p-4 border">
            <h3 className="font-medium mb-3">Resumo</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-muted-foreground">Você possui</p>
                <p className="font-bold">450 ações (R$ 14.602,50)</p>
              </div>
              <div>
                <p className="text-muted-foreground">Preço médio</p>
                <p className="font-bold">R$ 28,50</p>
              </div>
              <div>
                <p className="text-muted-foreground">Lucro / Prejuízo</p>
                <p className="font-bold text-green-600">+R$ 1.780,50</p>
              </div>
              <div>
                <p className="text-muted-foreground">Saldo em conta</p>
                <p className="font-bold">R$ 8.240,00</p>
              </div>
            </div>
          </Card>
        </div>
      </Card>
    </section>
  );
}
