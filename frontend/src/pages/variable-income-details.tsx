import { useState, useMemo } from "react";
import clsx from "clsx";
import { useParams } from "react-router-dom";
import { useQueryApi } from "@/hooks/useQueryApi";
import type { StockDetails } from "@/types";
import { Spinner } from "@/components/ui/spinner";
import { useRealtime } from "@/hooks/useRealtime";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from "recharts";
import { format } from "date-fns";
import { TrendingUp, TrendingDown, Plus, Minus } from "lucide-react";

const TIME_SCALES = ["1s", "1m", "3m", "1a", "3a", "5a", "MAX"] as const;
type TimeScale = (typeof TIME_SCALES)[number];

export default function VariableIncomeDetailPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const [selectedScale, setSelectedScale] = useState<TimeScale>("1s");
  const [quantity, setQuantity] = useState<number>(0);

  const {
    data: stock,
    setData: setStock,
    loading,
  } = useQueryApi<StockDetails>(`/api/variable-income/${ticker}`, { initialFetch: true });

  useRealtime(`stock_update:${ticker}`, (data) => {
    setStock(data.stock);
  });

  const chartData = useMemo(
    () =>
      stock?.history?.map((h) => ({
        time: h.time,
        close: h.close,
        formattedDate: format(new Date(h.time), "dd/MM"),
      })) ?? [],
    [stock?.history]
  );

  const chartMin = useMemo(() => (chartData.length ? Math.min(...chartData.map((d) => d.close)) : 0), [chartData]);
  const chartMax = useMemo(() => (chartData.length ? Math.max(...chartData.map((d) => d.close)) : 0), [chartData]);

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
        <Card className="mb-8">
          <CardHeader className="flex flex-row justify-between items-center">
            <CardTitle className="text-base font-semibold">Histórico de Preços</CardTitle>
            <div className="flex  divide-x divide-gray-300 rounded-md overflow-hidden">
              {TIME_SCALES.map((scale) => (
                <button
                  key={scale}
                  onClick={() => setSelectedScale(scale)}
                  className={clsx(
                    "px-3 py-1 text-sm transition-colors duration-200",
                    selectedScale === scale ? "bg-blue-700 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300"
                  )}
                >
                  {scale.toUpperCase()}
                </button>
              ))}
            </div>
          </CardHeader>

          <CardContent className="h-64">
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="formattedDate" stroke="#888" />
                  <YAxis stroke="#888" domain={[chartMin * 0.98, chartMax * 1.02]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--background)",
                      border: "1px solid var(--border)",
                      borderRadius: "0.5rem",
                    }}
                    formatter={(value: number) => [`R$ ${value.toFixed(2)}`, "Fechamento"]}
                    labelFormatter={(label) => `Data: ${label}`}
                  />
                  <Area
                    type="monotone"
                    dataKey="close"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    fill="url(#colorClose)"
                    activeDot={{ r: 5, fill: "#3b82f6" }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-muted-foreground">
                Nenhum dado de histórico disponível.
              </div>
            )}
          </CardContent>
        </Card>

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
