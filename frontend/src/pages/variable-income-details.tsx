import { useState } from "react";
import clsx from "clsx";
import { useParams } from "react-router-dom";
import { useQueryApi } from "@/hooks/useQueryApi";
import type { Stock } from "@/types";
import { Spinner } from "@/components/ui/spinner";
import { useRealtime } from "@/hooks/useRealtime";

const TIME_SCALES = ["1w", "1m", "3m", "1y", "all"];

export default function VariableIncomeDetailPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const [selectedScale, setSelectedScale] = useState("1w");
  const [quantity, setQuantity] = useState<number>(0);

  const {
    data: stock,
    setData: setStock,
    loading,
  } = useQueryApi<Stock>(`/api/variable-income/${ticker}`, { initialFetch: true });

  // TODO: Avaliar performance
  //   useRealtime("stocks_update", (data) => {
  //   const stock = data.stocks.find((s) => s.ticker === ticker);
  //   if (stock) setStock(stock);
  // });
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

  const handleBuy = () => {
    console.log(`Comprar ${quantity} ações de ${stock.ticker}`);
    // integrar com API ou socket
  };

  const handleSell = () => {
    console.log(`Vender ${quantity} ações de ${stock.ticker}`);
    // integrar com API ou socket
  };
  return (
    <section id="stock-detail" className="section-content p-4">
      <div className="bg-white rounded-lg shadow p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold">{stock.ticker}</h2>
            <p className="text-gray-600">{stock.name}</p>
          </div>
          <div className="text-right">
            <h3 className="text-3xl font-bold text-gray-800">R$ {stock.price.toFixed(2)}</h3>
            <span className={clsx("font-medium", stock.change < 0 ? "text-red-500" : "text-green-500")}>
              {stock.change_pct} (R$ {stock.change.toFixed(2)})
            </span>
          </div>
        </div>

        {/* Chart e Time Scale Controls */}
        <div className="mb-8">
          <div className="flex justify-between mb-4">
            <h3 className="font-semibold">Histórico de Preços</h3>
            <div className="flex bg-gray-200 rounded-md divide-x divide-gray-300 overflow-hidden">
              {TIME_SCALES.map((scale) => (
                <button
                  key={scale}
                  onClick={() => setSelectedScale(scale)}
                  className={clsx(
                    "time-scale-btn px-3 py-1 text-sm transition-colors duration-200",
                    selectedScale === scale ? "bg-blue-700 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300"
                  )}
                >
                  {scale.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            <p className="text-gray-500">Gráfico do histórico de preços aqui</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="border rounded p-4">
            <p className="text-gray-600 text-sm">Volume</p>
            <p className="font-bold">{stock.volume}</p>
          </div>
          <div className="border rounded p-4">
            <p className="text-gray-600 text-sm">Variação Dia</p>
            <p className={clsx("font-bold", stock.change < 0 ? "text-red-500" : "text-green-500")}>
              {stock.change_pct}
            </p>
          </div>
          <div className="border rounded p-4">
            <p className="text-gray-600 text-sm">Mín. do Dia</p>
            <p className="font-bold">R$ {stock.low.toFixed(2)}</p>
          </div>
          <div className="border rounded p-4">
            <p className="text-gray-600 text-sm">Máx. do Dia</p>
            <p className="font-bold">R$ {stock.high.toFixed(2)}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 bg-gray-100 p-4 rounded-lg">
            <h3 className="font-medium mb-4">
              Você possui <span className="font-bold">450</span> ações (R$ 14.602,50)
            </h3>
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
                <i className="fas fa-plus"></i> Comprar
              </button>
              <button
                className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md flex items-center justify-center gap-1"
                onClick={handleSell}
              >
                <i className="fas fa-minus"></i> Vender
              </button>
            </div>
          </div>
          <div className="flex-1 bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Resumo</h3>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <p className="text-gray-600 text-sm">Preço Médio</p>
                <p className="font-bold">R$ 28.50</p>
              </div>
              <div>
                <p className="text-gray-600 text-sm">Lucro/Prejuízo</p>
                <p className="font-bold text-green-500">+R$ 1.780,50</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
